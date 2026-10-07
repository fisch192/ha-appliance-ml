from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (CONF_ACTIVE_STATES, CONF_ACTIVITY, CONF_END_W, CONF_MAX_END, CONF_MIN_CYCLE, CONF_MODE,
                    CONF_POWER, CONF_PROGRAM, CONF_START_W, CONF_TOTAL, CONF_TYPE, DEFAULT_ACTIVE_STATES,
                    DOMAIN, PRESETS)


class ApplianceMLConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._data: dict = {}

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._data = dict(user_input)
            return await (self.async_step_metered() if user_input[CONF_MODE] == "metered"
                          else self.async_step_estimated())
        schema = vol.Schema({
            vol.Required("name", default="Washing machine"): str,
            vol.Required(CONF_TYPE, default="washing_machine"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(PRESETS), translation_key="appliance_type")),
            vol.Required(CONF_MODE, default="metered"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=["metered", "estimated"], translation_key="mode")),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_metered(self, user_input=None):
        if user_input is not None:
            data = {**self._data, **user_input}
            await self.async_set_unique_id(data[CONF_POWER])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=data["name"], data=data)
        schema = vol.Schema({vol.Required(CONF_POWER): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["sensor", "number", "input_number"]))})
        return self.async_show_form(step_id="metered", data_schema=schema)

    async def async_step_estimated(self, user_input=None):
        if user_input is not None:
            data = {**self._data, **user_input}
            await self.async_set_unique_id(data[CONF_ACTIVITY])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=data["name"], data=data)
        schema = vol.Schema({
            vol.Required(CONF_ACTIVITY): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "binary_sensor", "switch", "select", "input_boolean"])),
            vol.Required(CONF_ACTIVE_STATES, default=DEFAULT_ACTIVE_STATES): str,
            vol.Required(CONF_TOTAL): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "number", "input_number"])),
            vol.Optional(CONF_PROGRAM): selector.EntitySelector(
                selector.EntitySelectorConfig(domain=["sensor", "select", "input_select"])),
        })
        return self.async_show_form(step_id="estimated", data_schema=schema)

    async def async_step_import(self, user_input):
        """YAML: appliance_ml: [{name, appliance_type, power_entity | activity_entity + total_power_entity}]"""
        data = dict(user_input)
        data[CONF_MODE] = "metered" if CONF_POWER in data else "estimated"
        await self.async_set_unique_id(data.get(CONF_POWER) or data[CONF_ACTIVITY])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=data["name"], data=data)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return ApplianceMLOptionsFlow()


class ApplianceMLOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        o = self.config_entry.options
        pre = PRESETS[self.config_entry.data.get(CONF_TYPE, "washing_machine")]
        schema = vol.Schema({
            vol.Required(CONF_START_W, default=o.get(CONF_START_W, pre["start_w"])): vol.Coerce(float),
            vol.Required(CONF_END_W, default=o.get(CONF_END_W, pre["end_w"])): vol.Coerce(float),
            vol.Required(CONF_MIN_CYCLE, default=o.get(CONF_MIN_CYCLE, pre["min_cycle_min"])): vol.Coerce(float),
            vol.Required(CONF_MAX_END, default=o.get(CONF_MAX_END, pre["max_end_min"])): vol.Coerce(float),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
