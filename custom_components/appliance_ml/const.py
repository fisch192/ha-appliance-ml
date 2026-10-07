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
    "fridge": {"icon": "mdi:fridge", "monitor": True, "kind": "fridge", "start_w": 10, "end_w": 10, "min_cycle_min": 1,
               "min_end_s": 180, "default_end_s": 300, "max_end_min": 15, "min_peak_w": 5},
    "baseload": {"icon": "mdi:home-lightning-bolt", "monitor": True, "kind": "baseload", "start_w": 10000,
                 "end_w": 10000, "min_cycle_min": 1, "min_end_s": 180, "default_end_s": 300, "max_end_min": 15,
                 "min_peak_w": 5},
    "other": {"icon": "mdi:power-plug", "start_w": 20, "end_w": 10, "min_cycle_min": 10,
              "min_end_s": 180, "default_end_s": 300, "max_end_min": 15, "min_peak_w": 50},
}

CONF_MODE = "mode"                      # "metered" (own power sensor) | "estimated" (house power + run state)
CONF_ACTIVITY = "activity_entity"       # estimated: entity whose state says "running"
CONF_ACTIVE_STATES = "active_states"    # estimated: states meaning running, comma separated
CONF_TOTAL = "total_power_entity"       # estimated: house (or circuit) total power in W
CONF_PROGRAM = "program_entity"         # estimated: optional entity that reports the program name
DEFAULT_ACTIVE_STATES = "run,running,active,on"

PROBLEM_TEXT = {
    "energy_up": "Energy use of the last 24 h is clearly above normal",
    "duty_up": "Compressor runs much more than usual",
    "base_up": "Base/standby power is higher than usual",
    "running_continuously": "Compressor has been running continuously for too long",
    "not_cycling": "Compressor has not started for much longer than usual",
    "no_data": "No power readings (plug offline?)",
}
EVENT_PROBLEM = f"{DOMAIN}_problem"
EVENT_PROBLEM_CLEARED = f"{DOMAIN}_problem_cleared"

VERSION = "1.3.1"
