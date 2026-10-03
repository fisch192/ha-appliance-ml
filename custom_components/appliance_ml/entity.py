from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN


class ApplianceEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, manager, key: str, name: str):
        self.manager = manager
        self._attr_unique_id = f"{manager.entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, manager.entry.entry_id)},
                                            name=manager.entry.title, manufacturer="Appliance ML")

    async def async_added_to_hass(self):
        self.async_on_remove(async_dispatcher_connect(self.hass, self.manager.signal, self._refresh))

    @callback
    def _refresh(self):
        self.async_write_ha_state()
