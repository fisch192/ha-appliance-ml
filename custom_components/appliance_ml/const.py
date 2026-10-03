DOMAIN = "appliance_ml"
CONF_POWER = "power_entity"
CONF_START_W = "start_w"
CONF_END_W = "end_w"
CONF_MIN_CYCLE = "min_cycle_min"
SIGNAL = f"{DOMAIN}_update_{{}}"
EVENT_STARTED = f"{DOMAIN}_cycle_started"
EVENT_FINISHED = f"{DOMAIN}_cycle_finished"
CONF_TYPE = "appliance_type"
CONF_MAX_END = "max_end_min"

# Starting points per device type; the quiet time before "finished" is then learned
# from the device's own curve (clamped to min_end_s..max_end_s).
# washing_machine was validated on recorded data; the others are conservative defaults.
PRESETS = {
    "washing_machine": {"icon": "mdi:washing-machine", "start_w": 45, "end_w": 45, "min_cycle_min": 15,
                        "min_end_s": 120, "default_end_s": 180, "max_end_min": 10, "min_peak_w": 150},
    "dishwasher": {"icon": "mdi:dishwasher", "start_w": 15, "end_w": 10, "min_cycle_min": 20,
                   "min_end_s": 300, "default_end_s": 600, "max_end_min": 30, "min_peak_w": 100},
    "dryer": {"icon": "mdi:tumble-dryer", "start_w": 30, "end_w": 20, "min_cycle_min": 15,
              "min_end_s": 240, "default_end_s": 420, "max_end_min": 20, "min_peak_w": 150},
    "oven": {"icon": "mdi:stove", "start_w": 60, "end_w": 40, "min_cycle_min": 10,
             "min_end_s": 180, "default_end_s": 300, "max_end_min": 15, "min_peak_w": 300},
    "other": {"icon": "mdi:power-plug", "start_w": 20, "end_w": 10, "min_cycle_min": 10,
              "min_end_s": 180, "default_end_s": 300, "max_end_min": 15, "min_peak_w": 50},
}
