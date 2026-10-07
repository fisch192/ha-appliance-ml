"""Energy estimation for appliances WITHOUT their own power meter.

Inputs: the house total power and the appliance's own run state (e.g. Home Connect
`run`/`ready`). The tracker subtracts a learned house baseline to obtain the appliance's
own power, and learns per-program curves and energy from every cycle. Cycles disturbed by
other loads (kettle, oven ...) are recognised by their implausible energy and are not learned;
once a program is known, the own power is also capped by what that program normally draws.
"""
from __future__ import annotations

import math
from collections import deque

from .engine import Engine

IDLE_WINDOW_S = 1200.0       # baseline: low percentile of the last 20 min before the start
BASELINE_Q = 0.10


class DerivedTracker:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.samples: deque[tuple[float, float]] = deque()   # (ts, total W)
        self.total = 0.0
        self.baseline = 0.0
        self.active = False
        self._clip_rate = 0.0

    # ---- baseline ---------------------------------------------------------------
    def _trim(self, ts: float):
        while len(self.samples) > 2 and self.samples[1][0] < ts - IDLE_WINDOW_S:
            self.samples.popleft()

    def idle_baseline(self, ts: float) -> float:
        """Time-weighted 10 % quantile of the house power in the last IDLE_WINDOW_S."""
        if not self.samples:
            return self.total
        pts = list(self.samples) + [(ts, self.samples[-1][1])]
        spans = []
        for (t0, v), (t1, _) in zip(pts, pts[1:]):
            lo = max(t0, ts - IDLE_WINDOW_S)
            if t1 > lo:
                spans.append((v, t1 - lo))
        if not spans:
            return self.total
        spans.sort()
        total_w = sum(d for _, d in spans)
        acc = 0.0
        for v, d in spans:
            acc += d
            if acc >= BASELINE_Q * total_w:
                return v
        return spans[-1][0]

    # ---- inputs -------------------------------------------------------------------
    def feed_total(self, ts: float, watts: float) -> list[dict]:
        if not math.isfinite(watts) or watts < 0:
            return []
        self.samples.append((ts, watts))
        self._trim(ts)
        self.total = watts
        if self.engine.running and self.engine.external:
            self.baseline = min(self.baseline, watts)          # other loads left -> lower baseline
            self.engine.clip_ws += self._clip_rate * max(0.0, ts - self.engine._seg_ts)
            self.engine.advance_external(ts, self._own_power(ts, watts))
        return []

    def _own_power(self, ts: float, total: float) -> float:
        net = max(0.0, total - self.baseline)
        cap = self.engine.expected_power(ts - self.engine.start_ts)
        self._clip_rate = 0.0
        if cap is not None and net > 1.35 * cap + 50.0:
            self._clip_rate = net - (1.35 * cap + 50.0)
            net = 1.35 * cap + 50.0                 # ignore other loads on top of a known program
        return net

    def set_hint(self, name: str | None):
        if name and name.lower() not in ("unknown", "unavailable", "none", ""):
            self.engine.hint = name
        elif not self.engine.running:
            self.engine.hint = None

    def set_active(self, ts: float, active: bool, hint: str | None = None) -> list[dict]:
        events: list[dict] = []
        if active and not self.active:
            self.baseline = self.idle_baseline(ts)
            self.engine.begin_external(ts, hint if hint and hint.lower() not in ("unknown", "unavailable", "none") else None)
            self.engine.advance_external(ts, self._own_power(ts, self.total))
            events.append({"type": "started", "start": ts})
        elif not active and self.active:
            events += self.engine.end_external(ts)
        self.active = active
        return events

    @property
    def own_power(self) -> float:
        e = self.engine
        return round(e._power, 1) if e.running and e.external else 0.0
