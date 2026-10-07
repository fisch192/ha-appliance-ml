from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from .const import DOMAIN
from .entity import ApplianceEntity


async def async_setup_entry(hass, entry, async_add_entities):
    m = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([Problem(m)] if m.monitor else [Running(m)])


class Running(ApplianceEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, manager):
        super().__init__(manager, "running", "Programm läuft")

    @property
    def is_on(self):
        return self.manager.engine.running


class Problem(ApplianceEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, manager):
        super().__init__(manager, "problem", "Problem")

    @property
    def is_on(self):
        return bool(self.manager.monitor.problems)

    @property
    def extra_state_attributes(self):
        from .const import PROBLEM_TEXT
        p = self.manager.monitor.problems
        return {"gruende": p, "text": "; ".join(PROBLEM_TEXT.get(r, r) for r in p), **self.manager.monitor.summary}
