from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .const import DOMAIN
from .entity import ApplianceEntity


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([Running(hass.data[DOMAIN][entry.entry_id])])


class Running(ApplianceEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, manager):
        super().__init__(manager, "running", "Programm läuft")

    @property
    def is_on(self):
        return self.manager.engine.running
