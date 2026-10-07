from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (CONF_ACTIVE_STATES, CONF_ACTIVITY, CONF_END_W, CONF_MAX_END, CONF_MIN_CYCLE, CONF_MODE,
                    CONF_POWER, CONF_PROGRAM, CONF_START_W, CONF_TOTAL, CONF_TYPE, DEFAULT_ACTIVE_STATES, DOMAIN,
                    EVENT_FINISHED, EVENT_PROBLEM, EVENT_PROBLEM_CLEARED, EVENT_STARTED, PRESETS,
                    PROBLEM_TEXT, SIGNAL)
from .engine import Config, Engine
from .estimator import DerivedTracker
from .monitor import CycleMonitor, MonitorConfig

_LOGGER = logging.getLogger(__name__)


class ApplianceManager:
    def __init__(self, hass: HomeAssistant, entry):
        self.hass, self.entry = hass, entry
        d = entry.data
        self.mode = d.get(CONF_MODE, "metered")
        self.power_entity = d.get(CONF_POWER)              # metered
        self.activity_entity = d.get(CONF_ACTIVITY)        # estimated
        self.total_entity = d.get(CONF_TOTAL)
        self.program_entity = d.get(CONF_PROGRAM)
        self.active_states = {s.strip().lower() for s in d.get(CONF_ACTIVE_STATES, DEFAULT_ACTIVE_STATES).split(",") if s.strip()}
        o = entry.options
        self.type = entry.data.get(CONF_TYPE, "washing_machine")
        pre = PRESETS.get(self.type, PRESETS["other"])
        self.icon = pre["icon"]
        self.engine = Engine(Config(
            start_w=o.get(CONF_START_W, pre["start_w"]), end_w=o.get(CONF_END_W, pre["end_w"]),
            min_cycle_s=o.get(CONF_MIN_CYCLE, pre["min_cycle_min"]) * 60,
            min_end_s=pre["min_end_s"], default_end_s=pre["default_end_s"],
            max_end_s=o.get(CONF_MAX_END, pre["max_end_min"]) * 60, min_peak_w=pre["min_peak_w"]))
        self.tracker = DerivedTracker(self.engine) if self.mode == "estimated" else None
        self.monitor = CycleMonitor(MonitorConfig(kind=pre.get("kind", "fridge"),
                                                  on_w=o.get(CONF_START_W, pre["start_w"]))) if pre.get("monitor") else None
        self.store = Store(hass, 1, f"appliance_ml.{entry.entry_id}")
        self.last_cycle: dict | None = None
        self._dirty = False
        self._unsubs = []

    def _dump(self) -> dict:
        d = self.engine.dump()
        if self.monitor:
            d["monitor"] = self.monitor.dump()
        return d

    @property
    def signal(self) -> str:
        return SIGNAL.format(self.entry.entry_id)

    async def async_start(self):
        data = await self.store.async_load()
        if data:
            self.engine.load(data)
            if self.monitor:
                self.monitor.load(data.get("monitor", {}))
            self.last_cycle = self.engine.history[-1] if self.engine.history else None
        elif not self.engine.programs and not (self.monitor and self.monitor.hours):
            self.hass.async_create_task(self.async_learn_from_history(30))
        watched = [self.power_entity] if self.mode == "metered" else \
            [e for e in (self.total_entity, self.program_entity, self.activity_entity) if e]
        self._unsubs.append(async_track_state_change_event(self.hass, watched, self._on_state))
        self._unsubs.append(async_track_time_interval(self.hass, self._on_tick, timedelta(seconds=15)))
        for ent in watched:                     # initial values (program/total first, activity last)
            state = self.hass.states.get(ent)
            if state:
                self._dispatch_state(ent, state)

    async def async_stop(self):
        for u in self._unsubs:
            u()
        await self.store.async_save(self._dump())

    # ---- live data ---------------------------------------------------------
    @callback
    def _on_state(self, event: Event):
        new = event.data.get("new_state")
        if new:
            self._dispatch_state(event.data["entity_id"], new)

    def _dispatch_state(self, entity_id, state):
        ts = state.last_updated.timestamp()
        if self.mode == "metered":
            self._ingest(state.state, ts)
            return
        self._ingest_estimated(entity_id, state.state, ts)

    def _scale(self, entity_id) -> float:
        """Any entity can be the power source: convert kW / mW readings to W."""
        st = self.hass.states.get(entity_id) if entity_id else None
        return {"kW": 1000.0, "mW": 0.001, "MW": 1e6}.get(st.attributes.get("unit_of_measurement") if st else None, 1.0)

    def _ingest_estimated(self, entity_id, raw, ts):
        tr = self.tracker
        if entity_id == self.total_entity:
            try:
                w = float(raw) * self._scale(entity_id)
            except (TypeError, ValueError):
                return
            self._handle(tr.feed_total(ts, w))
        elif entity_id == self.program_entity:
            tr.set_hint(raw)
        elif entity_id == self.activity_entity:
            prog = self.hass.states.get(self.program_entity) if self.program_entity else None
            if raw in ("unknown", "unavailable"):
                return
            self._handle(tr.set_active(ts, str(raw).strip().lower() in self.active_states,
                                       prog.state if prog else None))

    def _ingest(self, raw, ts):
        try:
            power = float(raw) * self._scale(self.power_entity)
        except (TypeError, ValueError):
            return
        if not math.isfinite(power):
            return
        if self.monitor:
            self.monitor.feed(ts, power)
            return
        self._handle(self.engine.feed(ts, power))

    @callback
    def _on_tick(self, now: datetime):
        if self.monitor:
            self._handle_monitor(self.monitor.tick(now.timestamp()))
            if self._dirty_monitor(now):
                self.store.async_delay_save(self._dump, 10)
            async_dispatcher_send(self.hass, self.signal)
            return
        if self.mode == "estimated":
            if self.engine.running and self.engine.external:
                self.engine.advance_external(now.timestamp(), self.engine._power)
        else:
            self._handle(self.engine.tick(now.timestamp()))
        if self.engine.running:
            async_dispatcher_send(self.hass, self.signal)
        if self._dirty:
            self._dirty = False
            self.store.async_delay_save(self._dump, 10)

    _last_monitor_save = 0.0

    def _dirty_monitor(self, now) -> bool:
        if now.timestamp() - self._last_monitor_save > 900:
            self._last_monitor_save = now.timestamp()
            return True
        return False

    def _handle_monitor(self, events: list[dict]):
        for ev in events:
            if ev["type"] == "problem":
                self.hass.bus.async_fire(EVENT_PROBLEM, {
                    "entry": self.entry.title, "appliance": self.type, "reasons": ev["reasons"],
                    "text": "; ".join(PROBLEM_TEXT.get(r, r) for r in ev["reasons"]), "summary": ev["summary"]})
            elif ev["type"] == "cleared":
                self.hass.bus.async_fire(EVENT_PROBLEM_CLEARED, {"entry": self.entry.title, "appliance": self.type})

    def _handle(self, events: list[dict]):
        for ev in events:
            if ev["type"] == "started":
                self.hass.bus.async_fire(EVENT_STARTED, {"entry": self.entry.title, "appliance": self.type})
            elif ev["type"] == "finished":
                self.last_cycle = ev
                self._dirty = True
                self.hass.bus.async_fire(EVENT_FINISHED, {
                    "entry": self.entry.title, "appliance": self.type, "program": ev["name"],
                    "duration_min": round(ev["duration_s"] / 60), "energy_kwh": round(ev["energy_wh"] / 1000, 2),
                    "new_program": ev["new_program"]})
        if events:
            async_dispatcher_send(self.hass, self.signal)

    # ---- learning from the recorder ---------------------------------------------
    async def async_learn_from_history(self, days: int = 30, reset: bool = False):
        from homeassistant.components.recorder import get_instance, history

        try:
            get_instance(self.hass)
        except KeyError:
            return                          # recorder not loaded: learn from live data only

        end = dt_util.utcnow()
        start = end - timedelta(days=days)
        if self.mode == "estimated":
            await self._learn_estimated(start, end, reset)
            return
        if self.monitor:
            await self._learn_monitor(start, end, reset)
            return

        def fetch():
            return history.get_significant_states(
                self.hass, start, end, [self.power_entity],
                include_start_time_state=True, significant_changes_only=False,
                no_attributes=True).get(self.power_entity, [])

        states = await get_instance(self.hass).async_add_executor_job(fetch)
        fresh = Engine(self.engine.cfg)
        if not reset:
            fresh.load(self._dump())
        known = {e["end"] for e in fresh.history}
        count = 0
        for st in states:
            try:
                p = float(st.state) * self._scale(self.power_entity)
            except ValueError:
                continue
            for ev in fresh.feed(st.last_updated.timestamp(), p):
                count += ev["type"] == "finished" and ev["end"] not in known
        fresh.tick(end.timestamp())
        if not fresh.running:
            self.engine = fresh
        self.last_cycle = self.engine.history[-1] if self.engine.history else None
        await self.store.async_save(self._dump())
        _LOGGER.info("appliance_ml learned from %s states, %s new cycles", len(states), count)
        async_dispatcher_send(self.hass, self.signal)

    async def _learn_monitor(self, start, end, reset: bool):
        from homeassistant.components.recorder import get_instance, history

        def fetch():
            return history.get_significant_states(self.hass, start, end, [self.power_entity],
                                                  include_start_time_state=True,
                                                  significant_changes_only=False, no_attributes=True)

        states = (await get_instance(self.hass).async_add_executor_job(fetch)).get(self.power_entity, [])
        fresh = CycleMonitor(self.monitor.cfg)
        if not reset:
            fresh.load(self.monitor.dump())
        for st in states:
            try:
                fresh.feed(st.last_updated.timestamp(), float(st.state) * self._scale(self.power_entity))
            except ValueError:
                continue
        fresh.evaluate(end.timestamp())
        fresh.problems = []                        # replaying the past must not raise alerts
        self.monitor = fresh
        await self.store.async_save(self._dump())
        async_dispatcher_send(self.hass, self.signal)

    async def _learn_estimated(self, start, end, reset: bool):
        from homeassistant.components.recorder import get_instance, history

        ents = [e for e in (self.total_entity, self.program_entity, self.activity_entity) if e]

        def fetch():
            return history.get_significant_states(self.hass, start, end, ents,
                                                  include_start_time_state=True,
                                                  significant_changes_only=False, no_attributes=True)

        data = await get_instance(self.hass).async_add_executor_job(fetch)
        events = sorted(((s.last_updated.timestamp(), e, s.state) for e in ents for s in data.get(e, [])),
                        key=lambda x: x[0])
        fresh = Engine(self.engine.cfg)
        if not reset:
            fresh.load(self._dump())
        trk = DerivedTracker(fresh)
        hint, count = None, 0
        for ts, ent, raw in events:
            if ent == self.total_entity:
                try:
                    trk.feed_total(ts, float(raw) * self._scale(self.total_entity))
                except ValueError:
                    pass
            elif ent == self.program_entity:
                hint = raw
                trk.set_hint(raw)
            elif raw not in ("unknown", "unavailable"):
                evs = trk.set_active(ts, str(raw).strip().lower() in self.active_states, hint)
                count += sum(1 for e in evs if e["type"] == "finished")
        if not (fresh.running and fresh.external):
            self.engine = fresh
            self.tracker = DerivedTracker(fresh)
            self.tracker.samples = trk.samples
            self.tracker.total = trk.total
            self.tracker.active = trk.active
        self.last_cycle = self.engine.history[-1] if self.engine.history else None
        await self.store.async_save(self._dump())
        _LOGGER.info("appliance_ml (estimated) learned from %s state changes, %s cycles", len(events), count)
        async_dispatcher_send(self.hass, self.signal)

    async def async_rename_program(self, program_id: str, name: str):
        for p in self.engine.programs:
            if p.id == program_id:
                p.name = name
        for rec in self.engine.history:
            if rec["program"] == program_id:
                rec["name"] = name
        await self.store.async_save(self._dump())
        async_dispatcher_send(self.hass, self.signal)

    async def async_delete_program(self, program_id: str):
        self.engine.delete_program(program_id)
        self.last_cycle = self.engine.history[-1] if self.engine.history else None
        await self.store.async_save(self._dump())
        async_dispatcher_send(self.hass, self.signal)

    def snapshot(self) -> dict:
        e = self.engine
        graph_entity = self.power_entity
        power = None
        if self.mode == "estimated":
            from homeassistant.helpers import entity_registry as er
            graph_entity = er.async_get(self.hass).async_get_entity_id(
                "sensor", DOMAIN, f"{self.entry.entry_id}_est_power") or self.total_entity
            power = self.tracker.own_power
        st = self.hass.states.get(self.power_entity) if self.power_entity else None
        live = None
        if e.running:
            proto = None
            mt = e.match
            if mt:
                prog = next((p for p in e.programs if p.id == mt["program"]), None)
                proto = prog.exemplars[-1] if prog and prog.exemplars else None
            live = {"start": e.start_ts, "series": [round(x) for x in e.series()],
                    "quiet_since": e.quiet_since, "match": mt, "prototype": [round(x) for x in proto] if proto else None,
                    "energy_wh": round(e.energy_ws / 3600, 1)}
        mon = None
        if self.monitor:
            now = dt_util.utcnow().timestamp()
            self.monitor.evaluate(now) if now - self.monitor.last_eval > 60 else None
            mon = {"summary": self.monitor.summary, "problems": self.monitor.problems,
                   "texts": [PROBLEM_TEXT.get(r, r) for r in self.monitor.problems],
                   "daily": self.monitor.daily_series(now), "kind": self.monitor.cfg.kind}
        return {
            "monitor": mon,
            "entry_id": self.entry.entry_id, "name": self.entry.title, "type": self.type,
            "mode": self.mode, "power_entity": graph_entity,
            "sources": {"power_entity": self.power_entity, "activity_entity": self.activity_entity,
                        "active_states": ",".join(sorted(self.active_states)),
                        "total_power_entity": self.total_entity, "program_entity": self.program_entity},
            "baseline_w": round(self.tracker.baseline) if self.tracker else None,
            "est_energy_kwh": round(self.engine.total_est_wh / 1000, 3) if self.tracker else None,
            "power": power if self.mode == "estimated" else
                     (float(st.state) * self._scale(self.power_entity) if st and st.state.replace(".", "", 1).replace("-", "", 1).isdigit() else None),
            "config": {"start_w": e.cfg.start_w, "end_w": e.cfg.end_w, "min_cycle_min": e.cfg.min_cycle_s / 60,
                       "max_end_min": e.cfg.max_end_s / 60},
            "running": e.running, "end_delay_s": round(e.end_delay_s), "live": live,
            "programs": [{"id": p.id, "name": p.name, "count": len(p.durations),
                          "duration_min": round(p.duration_s / 60), "energy_wh": round(p.energy_wh),
                          "curve": [round(x) for x in (p.exemplars[-1] if p.exemplars else [])],
                          "model": [round(x) for x in p.model_curve(0.5)],
                          "band_lo": [round(x) for x in p.model_curve(0.1)],
                          "band_hi": [round(x) for x in p.model_curve(0.9)],
                          "durations_min": [round(d / 60, 1) for d in p.durations[-20:]],
                          "energies_wh": [round(x) for x in p.energies[-20:]]}
                         for p in e.programs],
            "history": e.history[-30:][::-1],
        }

    async def async_reset(self):
        if self.monitor:
            self.monitor = CycleMonitor(self.monitor.cfg)
        self.engine = Engine(self.engine.cfg)
        self.last_cycle = None
        await self.store.async_save(self._dump())
        async_dispatcher_send(self.hass, self.signal)
