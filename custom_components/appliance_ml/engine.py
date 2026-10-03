"""Pure-python washing-machine cycle engine (no Home Assistant imports).

Learns from the power curve of every finished program:
* end detection: how long the machine may stay quiet *inside* a program is
  learned from past cycles, so the finish message fires shortly after the last
  spin instead of waiting for the machine to power itself off,
* program recognition: finished cycles are clustered with dynamic time warping
  (DTW) on the per-minute power curve; a running cycle is matched against the
  learned programs with an open-ended DTW to predict program and remaining time.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import median

BIN_S = 60


@dataclass
class Config:
    start_w: float = 45.0        # above this for start_s = program running
    start_s: float = 60.0
    end_w: float = 45.0          # below this = quiet (standby pulses are < 40 W)
    min_end_s: float = 120.0
    default_end_s: float = 180.0
    max_end_s: float = 600.0
    min_cycle_s: float = 900.0
    min_peak_w: float = 150.0
    max_cycle_s: float = 86400.0
    match_threshold: float = 0.033   # normalised DTW distance for "same program"
    max_exemplars: int = 5
    max_cycles: int = 60


def _f(x: float) -> float:
    return math.log1p(max(x, 0.0)) / 8.0


def dtw(a: list[float], b: list[float]) -> float:
    """Normalised DTW distance with a Sakoe-Chiba band."""
    n, m = len(a), len(b)
    if not n or not m:
        return 1.0
    band = max(abs(n - m), int(0.25 * max(n, m))) + 2
    inf = float("inf")
    prev = [inf] * (m + 1)
    prev[0] = 0.0
    for i in range(1, n + 1):
        cur = [inf] * (m + 1)
        lo, hi = max(1, i - band), min(m, i + band)
        for j in range(lo, hi + 1):
            c = abs(a[i - 1] - b[j - 1])
            cur[j] = c + min(prev[j], prev[j - 1], cur[j - 1])
        prev = cur
    return prev[m] / (n + m)


def prefix_match(live: list[float], proto: list[float]) -> tuple[float, int]:
    """Open-end DTW: best distance of `live` against any prefix of `proto`.

    Returns (distance, index in proto that corresponds to the live end)."""
    n, m = len(live), len(proto)
    inf = float("inf")
    band = int(0.3 * max(n, m)) + 3
    prev = [inf] * (m + 1)
    prev[0] = 0.0
    for i in range(1, n + 1):
        cur = [inf] * (m + 1)
        lo, hi = max(1, i - band), min(m, i + band)
        for j in range(lo, hi + 1):
            c = abs(live[i - 1] - proto[j - 1])
            cur[j] = c + min(prev[j], prev[j - 1], cur[j - 1])
        prev = cur
    best, bj = inf, m
    for j in range(1, m + 1):
        if prev[j] < inf and prev[j] / (n + j) < best:
            best, bj = prev[j] / (n + j), j
    return best, bj


@dataclass
class Program:
    id: str
    name: str
    exemplars: list[list[float]] = field(default_factory=list)
    durations: list[float] = field(default_factory=list)
    energies: list[float] = field(default_factory=list)

    @property
    def duration_s(self) -> float:
        return median(self.durations) if self.durations else 0.0

    @property
    def energy_wh(self) -> float:
        return median(self.energies) if self.energies else 0.0

    def to_dict(self):
        return self.__dict__.copy()


class Engine:
    def __init__(self, config: Config | None = None):
        self.cfg = config or Config()
        self.programs: list[Program] = []
        self.inner_quiets: list[float] = []      # max in-cycle quiet per past cycle
        self.history: list[dict] = []
        self.reset_run()
        self._last_ts: float | None = None
        self._power = 0.0
        self._above_since: float | None = None

    # ---- learned parameters -------------------------------------------------
    @property
    def end_delay_s(self) -> float:
        if len(self.inner_quiets) < 3:
            return self.cfg.default_end_s
        recent = sorted(self.inner_quiets[-20:])
        p90 = recent[min(len(recent) - 1, int(0.9 * len(recent)))]
        return min(self.cfg.max_end_s, max(self.cfg.min_end_s, 1.5 * p90 + 15))

    # ---- run state ---------------------------------------------------------
    def reset_run(self):
        self.running = False
        self.start_ts = 0.0
        self.energy_ws = 0.0
        self.peak = 0.0
        self.quiet_since: float | None = None
        self.last_big_ts = 0.0
        self.max_inner_quiet = 0.0
        self.bins: dict[int, float] = {}       # minute index -> Ws
        self._seg_ts = 0.0
        self.match: dict | None = None
        self._match_at = 0.0

    def _accumulate(self, t0: float, t1: float, p: float):
        """Integrate held power p over [t0, t1) into energy and minute bins."""
        if t1 <= t0:
            return
        self.energy_ws += p * (t1 - t0)
        t = t0
        while t < t1:
            idx = int((t - self.start_ts) // BIN_S)
            nxt = min(t1, self.start_ts + (idx + 1) * BIN_S)
            self.bins[idx] = self.bins.get(idx, 0.0) + p * (nxt - t)
            t = nxt

    def series(self, upto: float | None = None) -> list[float]:
        end = upto if upto is not None else self._last_ts or self.start_ts
        n = int((end - self.start_ts) // BIN_S) + 1
        out = []
        for i in range(max(n, 0)):
            span = min(BIN_S, end - (self.start_ts + i * BIN_S))
            out.append(self.bins.get(i, 0.0) / span if span > 0 else 0.0)
        return out

    # ---- input -------------------------------------------------------------
    def feed(self, ts: float, power: float) -> list[dict]:
        """New power reading at ts. Returns list of events."""
        events = self.tick(ts)
        if not math.isfinite(power) or power < 0:
            return events
        if self.running:
            self._accumulate(self._seg_ts, ts, self._power)
            self._seg_ts = ts
            self.peak = max(self.peak, power)
            if power >= self.cfg.end_w:
                if self.quiet_since is not None:
                    self.max_inner_quiet = max(self.max_inner_quiet, ts - self.quiet_since)
                    self.quiet_since = None
                self.last_big_ts = ts
            elif self.quiet_since is None:
                self.quiet_since = ts
        else:
            if power > self.cfg.start_w:
                if self._above_since is None:
                    self._above_since = ts
            else:
                self._above_since = None
        self._power = power
        self._last_ts = ts
        return events

    def tick(self, ts: float) -> list[dict]:
        """Advance time with the last power value held."""
        events: list[dict] = []
        if self._last_ts is not None and ts < self._last_ts:
            return events
        if self.running:
            self._accumulate(self._seg_ts, ts, self._power)
            self._seg_ts = ts
            self._last_ts = ts
            if ts - self.start_ts > self.cfg.max_cycle_s:
                self.reset_run()
                return [{"type": "discarded", "reason": "stale"}]
            self._update_match(ts)
            if self.quiet_since is not None and ts - self.quiet_since >= self._required_quiet():
                events += self._finish(self.quiet_since, ts)
        else:
            if (self._above_since is not None and self._power > self.cfg.start_w
                    and ts - self._above_since >= self.cfg.start_s):
                self._begin(self._above_since, ts)
                events.append({"type": "started", "start": self.start_ts})
            self._last_ts = ts if self._last_ts is None or ts > self._last_ts else self._last_ts
        return events

    def _begin(self, start: float, now: float):
        self.reset_run()
        self.running = True
        self.start_ts = start
        self._seg_ts = start
        self.last_big_ts = now
        self.peak = self._power
        self._accumulate(start, now, self._power)
        self._seg_ts = now
        self._above_since = None

    def _required_quiet(self) -> float:
        """Quiet time needed before declaring the end. Longer while the
        recognised program says that a lot of runtime is still to come."""
        base = self.end_delay_s
        m = self.match
        if m and m["confidence"] >= 0.5 and m["remaining_s"] > 0.35 * m["duration_s"]:
            return min(self.cfg.max_end_s, max(base, 420.0))
        return base

    # ---- program recognition ------------------------------------------------
    def _update_match(self, ts: float):
        if not self.programs or ts - self._match_at < 60:
            return
        self._match_at = ts
        live = [_f(x) for x in self.series(ts)]
        if len(live) < 6:
            return
        best = None
        for prog in self.programs:
            for ex in prog.exemplars:
                d, j = prefix_match(live, [_f(x) for x in ex])
                if best is None or d < best[0]:
                    best = (d, j, prog, len(ex))
        if not best:
            return
        d, j, prog, n_ex = best
        conf = max(0.0, 1.0 - d / (self.cfg.match_threshold * 1.5))
        total = prog.duration_s or n_ex * BIN_S
        elapsed = ts - self.start_ts
        remaining = max(0.0, min(total - elapsed, (n_ex - j) * BIN_S))
        self.match = {"program": prog.id, "name": prog.name, "confidence": round(conf, 2),
                      "remaining_s": remaining, "duration_s": total,
                      "progress": min(1.0, elapsed / total) if total else 0.0}

    def _classify(self, series: list[float]) -> tuple[Program | None, float]:
        f = [_f(x) for x in series]
        best, bd = None, float("inf")
        for prog in self.programs:
            for ex in prog.exemplars:
                if not (0.7 <= len(ex) / max(len(series), 1) <= 1.43):
                    continue
                d = dtw(f, [_f(x) for x in ex])
                if d < bd:
                    best, bd = prog, d
        return best, bd

    # ---- finish ------------------------------------------------------------
    def _finish(self, end_ts: float, now: float) -> list[dict]:
        duration = end_ts - self.start_ts
        series = self.series(end_ts)
        energy = self.energy_ws / 3600.0
        peak, inner = self.peak, self.max_inner_quiet
        self.reset_run()
        if duration < self.cfg.min_cycle_s or peak < self.cfg.min_peak_w:
            return [{"type": "discarded", "reason": "too_short", "duration_s": duration}]
        prog, dist = self._classify(series)
        learned = prog is not None and dist <= self.cfg.match_threshold
        if not learned:
            prog = Program(id=f"p{len(self.programs) + 1}", name=f"Programm {len(self.programs) + 1}")
            self.programs.append(prog)
        prog.exemplars.append(series)
        prog.exemplars = prog.exemplars[-self.cfg.max_exemplars:]
        prog.durations = (prog.durations + [duration])[-20:]
        prog.energies = (prog.energies + [energy])[-20:]
        self.inner_quiets = (self.inner_quiets + [inner])[-50:]
        rec = {"start": end_ts - duration, "end": end_ts,
               "duration_s": duration, "energy_wh": round(energy, 1), "peak_w": peak,
               "program": prog.id, "name": prog.name, "new_program": not learned}
        self.history = (self.history + [rec])[-self.cfg.max_cycles:]
        return [{"type": "finished", "detected_at": now, **rec}]

    def delete_program(self, program_id: str):
        self.programs = [p for p in self.programs if p.id != program_id]
        self.history = [h for h in self.history if h["program"] != program_id]

    # ---- persistence ---------------------------------------------------------
    def dump(self) -> dict:
        return {"programs": [p.to_dict() for p in self.programs],
                "inner_quiets": self.inner_quiets, "history": self.history}

    def load(self, data: dict):
        self.programs = [Program(**p) for p in data.get("programs", [])]
        self.inner_quiets = data.get("inner_quiets", [])
        self.history = data.get("history", [])
