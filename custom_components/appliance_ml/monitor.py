"""Health monitor for always-on cyclic loads (fridge, freezer) and for the house base load.

Learns what is normal from the device's own history (rolling 24 h windows of the last 3 weeks) and
reports when the last 24 h deviate: energy or compressor duty-cycle up (door ajar, dirty coil, failing
seal/compressor), higher base/standby power, compressor running continuously, compressor not starting,
or no data. Slow seasonal drift does not trigger because the reference is the recent median.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import median

HOUR = 3600
DAY = 86400
KEEP_HOURS = 24 * 45
MIN_REF_WINDOWS = 5
REF_WINDOWS = 21


@dataclass
class MonitorConfig:
    kind: str = "fridge"            # "fridge" | "baseload"
    on_w: float = 10.0              # compressor counts as running above this
    sensitivity: float = 1.0        # >1 = more tolerant (thresholds scaled)


class CycleMonitor:
    def __init__(self, cfg: MonitorConfig | None = None):
        self.cfg = cfg or MonitorConfig()
        self.hours: dict[int, dict] = {}
        self.power: float | None = None
        self.last_ts: float | None = None
        self.on_since: float | None = None
        self.problems: list[str] = []
        self.last_alert_ts = 0.0
        self.last_eval = 0.0
        self.summary: dict = {}

    # ---- input --------------------------------------------------------------------
    def _bucket(self, h: int) -> dict:
        b = self.hours.get(h)
        if b is None:
            b = self.hours[h] = {"wh": 0.0, "on_s": 0.0, "off_ws": 0.0, "off_s": 0.0, "cov_s": 0.0,
                                 "starts": 0, "max_on_s": 0.0, "minp": None}
            for old in [k for k in self.hours if k < h - KEEP_HOURS]:
                del self.hours[old]
        return b

    def _integrate(self, t0: float, t1: float, p: float):
        on = p > self.cfg.on_w
        t = t0
        while t < t1:
            h = int(t // HOUR)
            seg = min(t1, (h + 1) * HOUR)
            dt = seg - t
            b = self._bucket(h)
            b["wh"] += p * dt / HOUR
            b["cov_s"] += dt
            if on:
                b["on_s"] += dt
            else:
                b["off_ws"] += p * dt
                b["off_s"] += dt
            t = seg

    def feed(self, ts: float, power: float) -> list[dict]:
        if not math.isfinite(power) or power < 0:
            return []
        if self.last_ts is not None and self.power is not None and ts > self.last_ts:
            gap = ts - self.last_ts
            if gap <= 3 * HOUR:                         # longer gaps = no data (not integrated)
                self._integrate(self.last_ts, ts, self.power)
        was_on = self.power is not None and self.power > self.cfg.on_w
        now_on = power > self.cfg.on_w
        b = self._bucket(int(ts // HOUR))
        b["minp"] = power if b["minp"] is None else min(b["minp"], power)
        if now_on and not was_on:
            b["starts"] += 1
            self.on_since = ts
        elif was_on and not now_on and self.on_since is not None:
            h = self._bucket(int(ts // HOUR))
            h["max_on_s"] = max(h["max_on_s"], ts - self.on_since)
            self.on_since = None
        self.power, self.last_ts = power, ts
        return []

    # ---- evaluation -----------------------------------------------------------------
    def _window(self, t0: float, t1: float) -> dict | None:
        h0, h1 = int(t0 // HOUR), int(t1 // HOUR)
        agg = {"wh": 0.0, "on_s": 0.0, "off_ws": 0.0, "off_s": 0.0, "cov_s": 0.0, "starts": 0, "max_on_s": 0.0}
        mins = []
        for h in range(h0, h1):
            b = self.hours.get(h)
            if not b:
                continue
            for k in ("wh", "on_s", "off_ws", "off_s", "cov_s", "starts"):
                agg[k] += b[k]
            agg["max_on_s"] = max(agg["max_on_s"], b["max_on_s"])
            if b["minp"] is not None:
                mins.append(b["minp"])
        span = (h1 - h0) * HOUR
        if span <= 0 or agg["cov_s"] < 0.8 * span:
            return None
        agg["duty"] = agg["on_s"] / agg["cov_s"]
        agg["base_w"] = (agg["off_ws"] / agg["off_s"]) if agg["off_s"] > 0 else None
        agg["min_w"] = median(mins) if mins else None
        agg["avg_on_w"] = None
        agg["wh_per_day"] = agg["wh"] * DAY / agg["cov_s"]
        agg["starts_per_day"] = agg["starts"] * DAY / agg["cov_s"]
        return agg

    def windows(self, now: float, n: int = REF_WINDOWS) -> list[dict]:
        out = []
        for k in range(1, n + 1):
            w = self._window(now - DAY * (k + 1), now - DAY * k)
            if w:
                out.append(w)
        return out

    def evaluate(self, now: float) -> list[dict]:
        self.last_eval = now
        cur = self._window(now - DAY, now)
        ref = self.windows(now)
        reasons: list[str] = []
        s = self.cfg.sensitivity
        self.summary = {"learning": len(ref) < MIN_REF_WINDOWS, "ref_days": len(ref)}
        # no data
        if self.last_ts is None or now - self.last_ts > 3 * HOUR:
            if self.last_ts is not None or True:
                reasons.append("no_data")
        if cur:
            self.summary.update({"energy_kwh": round(cur["wh_per_day"] / 1000, 3), "duty": round(cur["duty"], 3),
                                 "starts": round(cur["starts_per_day"]), "base_w": None if cur["base_w"] is None else round(cur["base_w"], 1),
                                 "min_w": None if cur["min_w"] is None else round(cur["min_w"], 1)})
        if cur and len(ref) >= MIN_REF_WINDOWS:
            E = median(w["wh_per_day"] for w in ref)
            D = median(w["duty"] for w in ref)
            MX = median(w["max_on_s"] for w in ref)
            ST = median(w["starts_per_day"] for w in ref)
            offs = [w["base_w"] for w in ref if w["base_w"] is not None]
            mins = [w["min_w"] for w in ref if w["min_w"] is not None]
            self.summary.update({"usual_energy_kwh": round(E / 1000, 3), "usual_duty": round(D, 3),
                                 "usual_starts": round(ST), "usual_base_w": round(median(offs), 1) if offs else None,
                                 "usual_min_w": round(median(mins), 1) if mins else None})
            if self.cfg.kind == "baseload":
                if mins and cur["min_w"] is not None:
                    m = median(mins)
                    if cur["min_w"] > max(1.2 * m * s, m + 25 * s):
                        reasons.append("base_up")
            else:
                if cur["wh_per_day"] > 1.35 * E * s and cur["wh_per_day"] - E > 80 * s:
                    reasons.append("energy_up")
                if D > 0 and cur["duty"] > 1.4 * D * s and cur["duty"] - D > 0.10 * s:
                    reasons.append("duty_up")
                if offs and cur["base_w"] is not None:
                    o = median(offs)
                    if cur["base_w"] > max(1.5 * o * s, o + 5 * s):
                        reasons.append("base_up")
                if self.on_since is not None and now - self.on_since > max(3 * MX, 2 * HOUR):
                    reasons.append("running_continuously")
                if ST >= 4 and self.last_ts and self.power is not None and self.power <= self.cfg.on_w:
                    last_on = max((h for h, b in self.hours.items() if b["on_s"] > 0), default=None)
                    if last_on is not None:
                        idle_h = (now - (last_on + 1) * HOUR) / HOUR
                        usual_off_h = DAY / ST / HOUR
                        if idle_h > max(5 * usual_off_h, 8):
                            reasons.append("not_cycling")
        events: list[dict] = []
        if reasons and set(reasons) != set(self.problems):
            if now - self.last_alert_ts > 6 * HOUR or not self.problems:
                events.append({"type": "problem", "reasons": reasons, "summary": dict(self.summary)})
                self.last_alert_ts = now
        elif not reasons and self.problems:
            events.append({"type": "cleared"})
        self.problems = reasons
        return events

    def tick(self, now: float) -> list[dict]:
        if now - self.last_eval < 600:
            return []
        return self.evaluate(now)

    def daily_series(self, now: float, n: int = 30) -> list[dict]:
        """Rolling-24 h values for the chart (oldest first)."""
        out = []
        for k in range(n, -1, -1):
            w = self._window(now - DAY * (k + 1), now - DAY * k)
            out.append({"age_days": k, "kwh": None if not w else round(w["wh_per_day"] / 1000, 3),
                        "duty": None if not w else round(w["duty"], 3)})
        return out

    # ---- persistence ----------------------------------------------------------------
    def dump(self) -> dict:
        return {"hours": {str(h): b for h, b in self.hours.items()}, "problems": self.problems,
                "last_alert_ts": self.last_alert_ts}

    def load(self, data: dict):
        self.hours = {int(h): b for h, b in data.get("hours", {}).items()}
        self.problems = data.get("problems", [])
        self.last_alert_ts = data.get("last_alert_ts", 0.0)
