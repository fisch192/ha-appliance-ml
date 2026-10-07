from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTime

from .const import DOMAIN
from .entity import ApplianceEntity


async def async_setup_entry(hass, entry, async_add_entities):
    m = hass.data[DOMAIN][entry.entry_id]
    if m.monitor:
        async_add_entities([MonNumber(m, "energy", "Energie 24 h", "energy_kwh", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY),
                            MonNumber(m, "usual_energy", "Üblich 24 h", "usual_energy_kwh", UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY),
                            MonNumber(m, "duty", "Laufanteil 24 h", "duty", PERCENTAGE, None, 100),
                            MonNumber(m, "starts", "Starts 24 h", "starts", None, None),
                            MonNumber(m, "base", "Grundlast", "base_w" if m.monitor.cfg.kind == "fridge" else "min_w", UnitOfPower.WATT, SensorDeviceClass.POWER),
                            MonNumber(m, "usual_base", "Übliche Grundlast", "usual_base_w" if m.monitor.cfg.kind == "fridge" else "usual_min_w", UnitOfPower.WATT, SensorDeviceClass.POWER),
                            MonReason(m)])
        return
    ents = [Status(m), Program(m), Remaining(m), Progress(m), LastDuration(m), LastEnergy(m)]
    if m.mode == "estimated":
        ents += [EstPower(m), EstEnergy(m)]
    else:
        ents.append(EndDelay(m))
    async_add_entities(ents)


class Status(ApplianceEntity, SensorEntity):
    def __init__(self, m):
        super().__init__(m, "status", "Status")
        self._attr_icon = m.icon

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


class Program(ApplianceEntity, SensorEntity):
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


class Remaining(ApplianceEntity, SensorEntity):
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


class Progress(ApplianceEntity, SensorEntity):
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


class LastDuration(ApplianceEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, m):
        super().__init__(m, "last_duration", "Letzte Laufzeit")

    @property
    def native_value(self):
        lc = self.manager.last_cycle
        return round(lc["duration_s"] / 60) if lc else None


class LastEnergy(ApplianceEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2

    def __init__(self, m):
        super().__init__(m, "last_energy", "Letzter Verbrauch")

    @property
    def native_value(self):
        lc = self.manager.last_cycle
        return round(lc["energy_wh"] / 1000, 3) if lc else None


class EndDelay(ApplianceEntity, SensorEntity):
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_icon = "mdi:timer-cog-outline"

    def __init__(self, m):
        super().__init__(m, "end_delay", "Gelernte Ruhezeit für Programmende")

    @property
    def native_value(self):
        return round(self.manager.engine.end_delay_s)


class EstPower(ApplianceEntity, SensorEntity):
    """Appliance's own power, estimated from house power minus the learned baseline."""
    _attr_device_class = SensorDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, m):
        super().__init__(m, "est_power", "Geschätzte Leistung")

    @property
    def native_value(self):
        return self.manager.tracker.own_power

    @property
    def extra_state_attributes(self):
        t = self.manager.tracker
        return {"hausgrundlast_w": round(t.baseline), "hausleistung_w": round(t.total)}


class EstEnergy(ApplianceEntity, SensorEntity):
    """Lifetime estimated energy – can be used in the Energy dashboard (no power meter needed)."""
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 3

    def __init__(self, m):
        super().__init__(m, "est_energy", "Geschätzte Energie")

    @property
    def native_value(self):
        return round(self.manager.engine.total_est_wh / 1000, 4)


class MonNumber(ApplianceEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, m, key, name, field, unit, device_class, scale=1):
        super().__init__(m, f"mon_{key}", name)
        self._field, self._scale = field, scale
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_icon = m.icon
        if device_class is None:
            self._attr_suggested_display_precision = 0

    @property
    def native_value(self):
        v = self.manager.monitor.summary.get(self._field)
        return None if v is None else round(v * self._scale, 3)


class MonReason(ApplianceEntity, SensorEntity):
    _attr_icon = "mdi:heart-pulse"

    def __init__(self, m):
        super().__init__(m, "mon_reason", "Gesundheit")

    @property
    def native_value(self):
        mon = self.manager.monitor
        if mon.summary.get("learning"):
            return "Lernt (%s/5 Tage)" % min(5, mon.summary.get("ref_days", 0))
        return "OK" if not mon.problems else "Auffällig"

    @property
    def extra_state_attributes(self):
        from .const import PROBLEM_TEXT
        return {"gruende": self.manager.monitor.problems,
                "text": "; ".join(PROBLEM_TEXT.get(r, r) for r in self.manager.monitor.problems)}
