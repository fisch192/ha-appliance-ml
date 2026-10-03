from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfEnergy, UnitOfTime

from .const import DOMAIN
from .entity import WasherEntity


async def async_setup_entry(hass, entry, async_add_entities):
    m = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([Status(m), Program(m), Remaining(m), Progress(m), LastDuration(m),
                        LastEnergy(m), EndDelay(m)])


class Status(WasherEntity, SensorEntity):
    _attr_icon = "mdi:washing-machine"

    def __init__(self, m):
        super().__init__(m, "status", "Status")

    @property
    def native_value(self):
        e = self.manager.engine
        if not e.running:
            return "Bereit"
        return "Schleudern/Ende" if e.quiet_since is not None else "Läuft"

    @property
    def extra_state_attributes(self):
        e = self.manager.engine
        return {"programme": {p.id: p.name for p in e.programs}, "gelernte_zyklen": len(e.history)}


class Program(WasherEntity, SensorEntity):
    _attr_icon = "mdi:format-list-bulleted"

    def __init__(self, m):
        super().__init__(m, "program", "Programm")

    @property
    def native_value(self):
        mt = self.manager.engine.match
        if self.manager.engine.running:
            return mt["name"] if mt and mt["confidence"] >= 0.3 else "wird erkannt…"
        lc = self.manager.last_cycle
        return lc["name"] if lc else None

    @property
    def extra_state_attributes(self):
        mt = self.manager.engine.match
        return {"sicherheit": mt["confidence"]} if mt and self.manager.engine.running else {}


class Remaining(WasherEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, m):
        super().__init__(m, "remaining", "Restzeit")

    @property
    def native_value(self):
        e = self.manager.engine
        mt = e.match
        if e.running and mt and mt["confidence"] >= 0.3:
            return round(mt["remaining_s"] / 60)
        return 0 if not e.running else None


class Progress(WasherEntity, SensorEntity):
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:progress-clock"

    def __init__(self, m):
        super().__init__(m, "progress", "Fortschritt")

    @property
    def native_value(self):
        e = self.manager.engine
        mt = e.match
        if e.running and mt and mt["confidence"] >= 0.3:
            return round(mt["progress"] * 100)
        return 0 if not e.running else None


class LastDuration(WasherEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, m):
        super().__init__(m, "last_duration", "Letzte Laufzeit")

    @property
    def native_value(self):
        lc = self.manager.last_cycle
        return round(lc["duration_s"] / 60) if lc else None


class LastEnergy(WasherEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2

    def __init__(self, m):
        super().__init__(m, "last_energy", "Letzter Verbrauch")

    @property
    def native_value(self):
        lc = self.manager.last_cycle
        return round(lc["energy_wh"] / 1000, 3) if lc else None


class EndDelay(WasherEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-cog-outline"

    def __init__(self, m):
        super().__init__(m, "end_delay", "Gelernte Ruhezeit für Programmende")

    @property
    def native_value(self):
        return round(self.manager.engine.end_delay_s)
