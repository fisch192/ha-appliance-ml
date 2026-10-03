from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (CONF_END_W, CONF_MAX_END, CONF_MIN_CYCLE, CONF_POWER, CONF_START_W, CONF_TYPE,
                    DOMAIN, PRESETS)


class ApplianceMLConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_POWER])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input["name"], data=user_input)
        schema = vol.Schema({
            vol.Required("name", default="Washing machine"): str,
            vol.Required(CONF_TYPE, default="washing_machine"): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(PRESETS), translation_key="appliance_type")),
            vol.Required(CONF_POWER): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power")),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

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
