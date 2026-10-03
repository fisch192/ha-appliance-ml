from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_END_W, CONF_MIN_CYCLE, CONF_POWER, CONF_START_W, DOMAIN


class WasherMLConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_POWER])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input["name"], data=user_input)
        schema = vol.Schema({
            vol.Required("name", default="Waschmaschine"): str,
            vol.Required(CONF_POWER): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="sensor", device_class="power")),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return WasherMLOptionsFlow()


class WasherMLOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        o = self.config_entry.options
        schema = vol.Schema({
            vol.Required(CONF_START_W, default=o.get(CONF_START_W, 45)): vol.Coerce(float),
            vol.Required(CONF_END_W, default=o.get(CONF_END_W, 45)): vol.Coerce(float),
            vol.Required(CONF_MIN_CYCLE, default=o.get(CONF_MIN_CYCLE, 15)): vol.Coerce(float),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
