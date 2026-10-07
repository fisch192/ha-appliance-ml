"""Websocket API used by the Appliance ML dashboard panel."""
from __future__ import annotations

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from .const import (PRESETS, CONF_TYPE, CONF_ACTIVE_STATES, CONF_ACTIVITY, CONF_END_W, CONF_MAX_END, CONF_MIN_CYCLE, CONF_POWER,
                    CONF_PROGRAM, CONF_START_W, CONF_TOTAL, DOMAIN)


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_snapshot)
    websocket_api.async_register_command(hass, ws_configure)
    websocket_api.async_register_command(hass, ws_add)
    websocket_api.async_register_command(hass, ws_remove)


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


@websocket_api.require_admin
@websocket_api.websocket_command({
    vol.Required("type"): "appliance_ml/add",
    vol.Required("name"): vol.All(str, vol.Length(min=1, max=60)),
    vol.Required("appliance_type"): vol.In(list(PRESETS)),
    vol.Optional(CONF_POWER): str,
    vol.Optional(CONF_ACTIVITY): str,
    vol.Optional(CONF_ACTIVE_STATES): str,
    vol.Optional(CONF_TOTAL): str,
    vol.Optional(CONF_PROGRAM): str,
})
@websocket_api.async_response
async def ws_add(hass, connection, msg):
    """Create an appliance from the panel's setup wizard (metered or estimated)."""
    data = {"name": msg["name"].strip(), CONF_TYPE: msg["appliance_type"]}
    for key in (CONF_POWER, CONF_ACTIVITY, CONF_ACTIVE_STATES, CONF_TOTAL, CONF_PROGRAM):
        if msg.get(key):
            data[key] = msg[key].strip()
    if (CONF_POWER in data) == (CONF_ACTIVITY in data):
        connection.send_error(msg["id"], "invalid_format", "choose a power sensor OR a run-state entity")
        return
    if CONF_ACTIVITY in data and CONF_TOTAL not in data:
        connection.send_error(msg["id"], "invalid_format", "estimated mode needs the house total power sensor")
        return
    for key in (CONF_POWER, CONF_ACTIVITY, CONF_TOTAL, CONF_PROGRAM):
        if key in data and hass.states.get(data[key]) is None:
            connection.send_error(msg["id"], "invalid_entity", f"{data[key]} does not exist")
            return
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "import"}, data=data)
    if result.get("type") != "create_entry":
        connection.send_error(msg["id"], "not_created", str(result.get("reason") or "could not create"))
        return
    connection.send_result(msg["id"], {"entry_id": result["result"].entry_id})


@websocket_api.require_admin
@websocket_api.websocket_command({vol.Required("type"): "appliance_ml/remove", vol.Required("entry_id"): str})
@websocket_api.async_response
async def ws_remove(hass, connection, msg):
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], "not_found", "Unknown entry")
        return
    await hass.config_entries.async_remove(entry.entry_id)
    connection.send_result(msg["id"], {"ok": True})
