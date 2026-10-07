# Appliance ML – learning cycle detection for washing machines, dishwashers, dryers & more

Detects when a household appliance **really** finished by learning its power curve, recognises the
running program, predicts the remaining time and ships its own dashboard panel with graphs and
configuration. Works with any power-measuring smart plug; add one entry per appliance. Pure Python, no cloud, no extra dependencies.

![Appliance ML panel](docs/panel.png)
*(example data)*

## Why
Many machines keep sending small power pulses (here: 25–35 W every ~5 min, for up to 18 min)
after the last spin. A fixed "idle for N minutes" rule is restarted by every pulse and reports
the end 5–20 min late. Appliance ML measures how long the machine is quiet *inside* a program and
ends the cycle after a learned quiet time (default 3 min, then 1.5 × the longest in-program pause).
On 12 real programs the alert came 2.7–4.5 min after the last spin (median ~3 min).

## Supported appliances
| Type | Start / quiet threshold | Quiet time before "finished" | Status |
|---|---|---|---|
| Washing machine | 45 W / 45 W | learned, 2–10 min (starts at 3) | **validated** on 12 recorded programs |
| Dishwasher | 15 W / 10 W | learned, 5–30 min (starts at 10) | preset + synthetic tests, needs real data |
| Tumble dryer | 30 W / 20 W | learned, 4–20 min (starts at 7) | preset + synthetic tests, needs real data |
| Oven / other | 60 W / 40 W · 20 W / 10 W | learned | generic starting point |

The presets are only starting points: every device learns its own quiet time and its own programs.
Thresholds can be changed per device in the panel. Dishwasher/dryer presets are unvalidated – please
open an issue with a power curve if yours misbehaves.

## Features
* **Finish detection** from the power curve, self-adjusting.
* **Program recognition**: finished cycles are clustered with dynamic time warping (DTW) on the
  per-minute power curve; the running cycle is matched with an open-ended DTW → program,
  remaining time, progress. A recognised program with lots of runtime left needs a longer quiet time.
* **Learns from history**: on first setup it replays the recorder history (30 days by default).
* **Dashboard panel** (sidebar "Appliance ML"): live power graph, current cycle vs. learned program,
  learned programs (rename / delete), run list, and configuration (power sensor, thresholds,
  *Learn from history*, *Reset*).
* Entities (names follow your Home Assistant language, English and German included): `binary_sensor … program running`, `sensor … status (idle / running / finishing) / program / remaining time / progress / last run duration / last run energy / learned quiet time`.
* Events: `appliance_ml_cycle_started`, `appliance_ml_cycle_finished` (`appliance`, `entry`, `program`, `duration_min`, `energy_kwh`, `new_program`).

## Quick start (5 minutes)

**1. Install**
HACS → ⋮ → *Custom repositories* → add `https://github.com/fisch192/ha-appliance-ml`, category *Integration* → install **Appliance ML** → restart Home Assistant.
(Manual: copy `custom_components/appliance_ml` into `<config>/custom_components/` and restart.)

**2. Make sure Home Assistant can see the power of your appliance**
You need *one* of these – pick what you have:

| Your situation | What to use |
|---|---|
| Smart plug that measures power (Shelly, Tasmota, Zigbee, TP-Link, Fritz!DECT, …) between wall and washing machine | the plug's **power sensor** (W). Best accuracy. |
| Built-in machine without plug, but integrated in HA (e.g. Home Connect / Bosch / Siemens dishwasher) | its **run-state entity** (`run`, `ready`, …) **plus** your **house total power** sensor. The appliance's own consumption is learned from the difference. |

Any entity works – it does not have to be flagged as a "power" sensor (kW values are converted automatically).

**3. Add the appliance**
*Settings → Devices & services → Add integration → Appliance ML.*
Choose the appliance type (washing machine, dishwasher, dryer, …), a name and the power sensor (or the run-state + house power). Repeat for each appliance.

**4. Open the "Appliance ML" side menu**
After the first appliance a new entry **Appliance ML** appears in the Home Assistant sidebar. From there you can add more appliances with the step-by-step wizard (*+ Add appliance*): pick the type → choose *Smart plug* or *No plug* → pick the sensor from a live list (the value of the right plug jumps when you switch the machine on; search by name, device or entity id, or tick *Show all entities*).

**5. Just use the machine**
Nothing else to configure. History from the recorder (30 days) is imported right away, every new run is learned automatically.
After the first complete run the program shows up in the panel; after 2–3 runs the program is recognised while it runs and the remaining time becomes accurate.

## The side menu: what you see

| Tab | Content |
|---|---|
| **Overview** | live power, detected program, remaining time and progress, power graph of the last 3 hours, current run drawn over the learned program, list of runs |
| **What it learned** | for every program: typical power curve with its spread, duration and energy of every run, number of runs and how reliable the recognition is; rename programs (“Eco 50 °C”) or delete them; learned quiet time before “finished” |
| **Settings** | choose any entity as power source, thresholds, *Learn from history*, *Reset learning*, remove the appliance |
| **+ Add appliance** | the setup wizard described above |

## Dishwasher & washing machine – recommended setup
* **Washing machine:** smart plug with power measurement (validated on 12 real programs, alert ≈ 3 min after the last spin).
* **Dishwasher:** if it is not behind a plug, use *No plug*: run-state entity (Home Connect `Operation state` – states `run`/`running`), your **house total power** sensor, optional program entity (`Active program`). The energy per program is learned from the house-power difference, runs disturbed by other big loads are detected and ignored.

## Troubleshooting
* *The finished alert never comes / comes too early* → *Settings*: lower/raise the quiet threshold (W) to just above your machine's standby pulses; the quiet time then adapts by itself.
* *Nothing is learned* → check that the chosen entity really changes while the machine runs (Overview graph). The recorder must be enabled to import history.
* *Wrong sensor chosen* → *Settings → Power sensor*, any entity can be selected, then *Learn from history*.

## YAML setup (optional)
```yaml
appliance_ml:
  - name: Washing machine
    appliance_type: washing_machine   # washing_machine | dishwasher | dryer | oven | other
    power_entity: sensor.washer_power
```
The entry is created once on startup and can afterwards be changed in the panel.

## Appliances without their own power sensor (estimated mode)
If a machine has no metering plug, use `activity_entity` (an entity whose state says it is running,
e.g. a Home Connect operation state) plus `total_power_entity` (house/circuit power). The integration
learns the appliance's share from the change in total power while it runs. Optional `program_entity`
reports the program name.
```yaml
appliance_ml:
  - name: Dishwasher
    appliance_type: dishwasher
    activity_entity: sensor.dishwasher_operation_state
    active_states: run,running
    total_power_entity: sensor.house_power
```

## Monitor types (fridge, baseload)
`fridge` and `baseload` do not detect programs; they watch energy use, compressor duty and standby
power and fire `appliance_ml_problem` / `appliance_ml_problem_cleared` events when something drifts
(e.g. compressor running continuously, no power readings).

## Notification example
See `packages/appliance_ml_notify.yaml` (event-triggered automation).

## Services
`appliance_ml.learn_from_history`, `appliance_ml.rename_program`, `appliance_ml.delete_program`, `appliance_ml.reset_learning`.

## Tuning
Start/quiet thresholds default to 45 W (above the machine's standby pulses, below real work);
change them in the panel. If your machine has long soak pauses with very low power, the
learned quiet time adapts after a few cycles.

## Development
`python3 tests/test_engine.py` replays 12 recorded washing-machine programs (`tests/recorded_cycles.json`); `python3 tests/test_appliances.py` uses synthetic dishwasher/dryer curves; `tests/test_estimator.py` and `tests/test_monitor.py` cover estimated mode and the monitors.
`tests/ha/` runs the integration against a real Home Assistant core (`pip install pytest-homeassistant-custom-component`, then `pytest tests/ha`).
`python3 tests/replay.py` prints, per program, the delay between last spin and alert.
The Home Assistant glue (config flow, entities, websocket API, panel registration) is tested against a real Home Assistant core (2026.2); the panel was rendered in a headless browser with mock data.

License: MIT
