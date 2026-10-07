from __future__ import annotations

from pathlib import Path

import voluptuous as vol
from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from . import websocket_api
from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.helpers import config_validation as cv

from .const import (CONF_ACTIVE_STATES, CONF_ACTIVITY, CONF_POWER, CONF_PROGRAM, CONF_TOTAL, CONF_TYPE,
                    DEFAULT_ACTIVE_STATES, DOMAIN, PRESETS)
from .manager import ApplianceManager

PLATFORMS = ["sensor", "binary_sensor"]
PANEL_URL = "appliance-ml"
STATIC_URL = "/appliance_ml_static"
VERSION = "1.2.0"


def _one_mode(item: dict) -> dict:
    if (CONF_POWER in item) == (CONF_ACTIVITY in item):
        raise vol.Invalid("use either power_entity (metered) or activity_entity + total_power_entity (estimated)")
    if CONF_ACTIVITY in item and CONF_TOTAL not in item:
        raise vol.Invalid("estimated mode needs total_power_entity")
    return item


_ITEM = vol.All(vol.Schema({
    vol.Required("name"): cv.string,
    vol.Optional(CONF_TYPE, default="washing_machine"): vol.In(list(PRESETS)),
    vol.Optional(CONF_POWER): cv.entity_id,
    vol.Optional(CONF_ACTIVITY): cv.entity_id,
    vol.Optional(CONF_ACTIVE_STATES, default=DEFAULT_ACTIVE_STATES): cv.string,
    vol.Optional(CONF_TOTAL): cv.entity_id,
    vol.Optional(CONF_PROGRAM): cv.entity_id,
}), _one_mode)
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.All(cv.ensure_list, [_ITEM])}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Optional YAML: appliance_ml: [{name, appliance_type, power_entity}] (imported once)."""
    for item in config.get(DOMAIN, []):
        hass.async_create_task(hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_IMPORT}, data=item))
    return True


async def _async_register_panel(hass: HomeAssistant) -> None:
    if hass.data.setdefault(f"{DOMAIN}_panel", False):
        return
    hass.data[f"{DOMAIN}_panel"] = True
    websocket_api.async_register(hass)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "frontend"), False)])
    await panel_custom.async_register_panel(
        hass, webcomponent_name="appliance-ml-panel", frontend_url_path=PANEL_URL,
        module_url=f"{STATIC_URL}/appliance-ml-panel.js?v={VERSION}",
        sidebar_title="Appliance ML", sidebar_icon="mdi:washing-machine",
        require_admin=False, config={})


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    manager = ApplianceManager(hass, entry)
    await manager.async_start()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = manager
    await _async_register_panel(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(lambda h, e: h.config_entries.async_reload(e.entry_id)))

    def managers(call: ServiceCall):
        wanted = call.data.get("entry_id")
        return [m for k, m in hass.data.get(DOMAIN, {}).items() if wanted in (None, k)]

    async def learn(call: ServiceCall):
        for m in managers(call):
            await m.async_learn_from_history(call.data["days"], call.data["reset"])

    async def rename(call: ServiceCall):
        for m in managers(call):
            await m.async_rename_program(call.data["program_id"], call.data["name"])

    async def delete(call: ServiceCall):
        for m in managers(call):
            await m.async_delete_program(call.data["program_id"])

    async def reset(call: ServiceCall):
        for m in managers(call):
            await m.async_reset()

    if not hass.services.has_service(DOMAIN, "learn_from_history"):
        opt = {vol.Optional("entry_id"): str}
        hass.services.async_register(DOMAIN, "learn_from_history", learn, vol.Schema({
            **opt, vol.Optional("days", default=30): vol.All(int, vol.Range(min=1, max=365)),
            vol.Optional("reset", default=False): bool}))
        hass.services.async_register(DOMAIN, "rename_program", rename, vol.Schema({
            vol.Required("entry_id"): str, vol.Required("program_id"): str, vol.Required("name"): str}))
        hass.services.async_register(DOMAIN, "delete_program", delete, vol.Schema({
            vol.Required("entry_id"): str, vol.Required("program_id"): str}))
        hass.services.async_register(DOMAIN, "reset_learning", reset, vol.Schema({vol.Required("entry_id"): str}))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        await hass.data[DOMAIN].pop(entry.entry_id).async_stop()
    return ok
