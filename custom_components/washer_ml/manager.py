from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (CONF_END_W, CONF_MIN_CYCLE, CONF_POWER, CONF_START_W, EVENT_FINISHED,
                    EVENT_STARTED, SIGNAL)
from .engine import Config, Engine

_LOGGER = logging.getLogger(__name__)


class WasherManager:
    def __init__(self, hass: HomeAssistant, entry):
        self.hass, self.entry = hass, entry
        self.power_entity = entry.data[CONF_POWER]
        o = entry.options
        self.engine = Engine(Config(
            start_w=o.get(CONF_START_W, 45), end_w=o.get(CONF_END_W, 45),
            min_cycle_s=o.get(CONF_MIN_CYCLE, 15) * 60))
        self.store = Store(hass, 1, f"washer_ml.{entry.entry_id}")
        self.last_cycle: dict | None = None
        self._dirty = False
        self._unsubs = []

    @property
    def signal(self) -> str:
        return SIGNAL.format(self.entry.entry_id)

    async def async_start(self):
        data = await self.store.async_load()
        if data:
            self.engine.load(data)
            self.last_cycle = self.engine.history[-1] if self.engine.history else None
        elif not self.engine.programs:
            self.hass.async_create_task(self.async_learn_from_history(30))
        self._unsubs.append(async_track_state_change_event(
            self.hass, [self.power_entity], self._on_state))
        self._unsubs.append(async_track_time_interval(self.hass, self._on_tick, timedelta(seconds=15)))
        state = self.hass.states.get(self.power_entity)
        if state:
            self._ingest(state.state, state.last_updated.timestamp())

    async def async_stop(self):
        for u in self._unsubs:
            u()
        await self.store.async_save(self.engine.dump())

    # ---- live data ---------------------------------------------------------
    @callback
    def _on_state(self, event: Event):
        new = event.data.get("new_state")
        if new:
            self._ingest(new.state, new.last_updated.timestamp())

    def _ingest(self, raw, ts):
        try:
            power = float(raw)
        except (TypeError, ValueError):
            return
        if not math.isfinite(power):
            return
        self._handle(self.engine.feed(ts, power))

    @callback
    def _on_tick(self, now: datetime):
        self._handle(self.engine.tick(now.timestamp()))
        if self.engine.running:
            async_dispatcher_send(self.hass, self.signal)
        if self._dirty:
            self._dirty = False
            self.store.async_delay_save(self.engine.dump, 10)

    def _handle(self, events: list[dict]):
        for ev in events:
            if ev["type"] == "started":
                self.hass.bus.async_fire(EVENT_STARTED, {"entry": self.entry.title})
            elif ev["type"] == "finished":
                self.last_cycle = ev
                self._dirty = True
                self.hass.bus.async_fire(EVENT_FINISHED, {
                    "entry": self.entry.title, "program": ev["name"],
                    "duration_min": round(ev["duration_s"] / 60), "energy_kwh": round(ev["energy_wh"] / 1000, 2),
                    "new_program": ev["new_program"]})
        if events:
            async_dispatcher_send(self.hass, self.signal)

    # ---- learning from the recorder ---------------------------------------------
    async def async_learn_from_history(self, days: int = 30, reset: bool = False):
        from homeassistant.components.recorder import get_instance, history

        end = dt_util.utcnow()
        start = end - timedelta(days=days)

        def fetch():
            return history.get_significant_states(
                self.hass, start, end, [self.power_entity],
                include_start_time_state=True, significant_changes_only=False,
                no_attributes=True).get(self.power_entity, [])

        states = await get_instance(self.hass).async_add_executor_job(fetch)
        fresh = Engine(self.engine.cfg)
        if not reset:
            fresh.load(self.engine.dump())
        known = {e["end"] for e in fresh.history}
        count = 0
        for st in states:
            try:
                p = float(st.state)
            except ValueError:
                continue
            for ev in fresh.feed(st.last_updated.timestamp(), p):
                count += ev["type"] == "finished" and ev["end"] not in known
        fresh.tick(end.timestamp())
        if not fresh.running:
            self.engine = fresh
        self.last_cycle = self.engine.history[-1] if self.engine.history else None
        await self.store.async_save(self.engine.dump())
        _LOGGER.info("washer_ml learned from %s states, %s new cycles", len(states), count)
        async_dispatcher_send(self.hass, self.signal)

    async def async_rename_program(self, program_id: str, name: str):
        for p in self.engine.programs:
            if p.id == program_id:
                p.name = name
        for rec in self.engine.history:
            if rec["program"] == program_id:
                rec["name"] = name
        await self.store.async_save(self.engine.dump())
        async_dispatcher_send(self.hass, self.signal)

    async def async_delete_program(self, program_id: str):
        self.engine.delete_program(program_id)
        self.last_cycle = self.engine.history[-1] if self.engine.history else None
        await self.store.async_save(self.engine.dump())
        async_dispatcher_send(self.hass, self.signal)

    def snapshot(self) -> dict:
        e = self.engine
        st = self.hass.states.get(self.power_entity)
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
        return {
            "entry_id": self.entry.entry_id, "name": self.entry.title,
            "power_entity": self.power_entity,
            "power": float(st.state) if st and st.state.replace(".", "", 1).replace("-", "", 1).isdigit() else None,
            "config": {"start_w": e.cfg.start_w, "end_w": e.cfg.end_w, "min_cycle_min": e.cfg.min_cycle_s / 60},
            "running": e.running, "end_delay_s": round(e.end_delay_s), "live": live,
            "programs": [{"id": p.id, "name": p.name, "count": len(p.durations),
                          "duration_min": round(p.duration_s / 60), "energy_wh": round(p.energy_wh),
                          "curve": [round(x) for x in (p.exemplars[-1] if p.exemplars else [])]}
                         for p in e.programs],
            "history": e.history[-30:][::-1],
        }

    async def async_reset(self):
        self.engine = Engine(self.engine.cfg)
        self.last_cycle = None
        await self.store.async_save(self.engine.dump())
        async_dispatcher_send(self.hass, self.signal)
