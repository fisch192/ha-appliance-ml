"""Websocket API used by the Appliance ML dashboard panel."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (CONF_ACTIVE_STATES, CONF_ACTIVITY, CONF_END_W, CONF_MAX_END, CONF_MIN_CYCLE, CONF_POWER,
                    CONF_PROGRAM, CONF_START_W, CONF_TOTAL, DOMAIN)


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_snapshot)
    websocket_api.async_register_command(hass, ws_configure)


@websocket_api.websocket_command({vol.Required("type"): "appliance_ml/snapshot"})
@callback
def ws_snapshot(hass, connection, msg):
    connection.send_result(msg["id"], [m.snapshot() for m in hass.data.get(DOMAIN, {}).values()
                                       if hasattr(m, "snapshot")])


@websocket_api.require_admin
@websocket_api.websocket_command({
    vol.Required("type"): "appliance_ml/configure",
    vol.Required("entry_id"): str,
    vol.Optional(CONF_POWER): str,
    vol.Optional(CONF_ACTIVITY): str,
    vol.Optional(CONF_ACTIVE_STATES): str,
    vol.Optional(CONF_TOTAL): str,
    vol.Optional(CONF_PROGRAM): str,
    vol.Required(CONF_START_W): vol.All(vol.Coerce(float), vol.Range(min=1, max=500)),
    vol.Required(CONF_END_W): vol.All(vol.Coerce(float), vol.Range(min=1, max=500)),
    vol.Required(CONF_MIN_CYCLE): vol.All(vol.Coerce(float), vol.Range(min=1, max=240)),
    vol.Required(CONF_MAX_END): vol.All(vol.Coerce(float), vol.Range(min=1, max=120)),
})
@callback
def ws_configure(hass, connection, msg):
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], "not_found", "Unknown entry")
        return
    sources = {k: msg[k] for k in (CONF_POWER, CONF_ACTIVITY, CONF_ACTIVE_STATES, CONF_TOTAL, CONF_PROGRAM) if msg.get(k)}
    for key in (CONF_POWER, CONF_ACTIVITY, CONF_TOTAL, CONF_PROGRAM):
        if key in sources and hass.states.get(sources[key]) is None:
            connection.send_error(msg["id"], "invalid_entity", f"{sources[key]} does not exist")
            return
    hass.config_entries.async_update_entry(
        entry, data={**entry.data, **sources},
        options={CONF_START_W: msg[CONF_START_W], CONF_END_W: msg[CONF_END_W],
                 CONF_MIN_CYCLE: msg[CONF_MIN_CYCLE], CONF_MAX_END: msg[CONF_MAX_END]})
    connection.send_result(msg["id"], {"ok": True})
