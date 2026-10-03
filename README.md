# Washer ML – learning washing-machine recognition for Home Assistant

Detects when a washing machine **really** finished by learning its power curve, recognises the
running program, predicts the remaining time and ships its own dashboard panel with graphs and
configuration. Works with any power-measuring smart plug. Pure Python, no cloud, no extra dependencies.

![Washer ML panel](docs/panel.png)
*(example data)*

## Why
Many machines keep sending small power pulses (here: 25–35 W every ~5 min, for up to 18 min)
after the last spin. A fixed "idle for N minutes" rule is restarted by every pulse and reports
the end 5–20 min late. Washer ML measures how long the machine is quiet *inside* a program and
ends the cycle after a learned quiet time (default 3 min, then 1.5 × the longest in-program pause).
On 12 real programs the alert came 2.7–4.5 min after the last spin (median ~3 min).

## Features
* **Finish detection** from the power curve, self-adjusting.
* **Program recognition**: finished cycles are clustered with dynamic time warping (DTW) on the
  per-minute power curve; the running cycle is matched with an open-ended DTW → program,
  remaining time, progress. A recognised program with lots of runtime left needs a longer quiet time.
* **Learns from history**: on first setup it replays the recorder history (30 days by default).
* **Dashboard panel** (sidebar "Washer ML"): live power graph, current cycle vs. learned program,
  learned programs (rename / delete), run list, and configuration (power sensor, thresholds,
  *Learn from history*, *Reset*).
* Entities: `binary_sensor … running`, `sensor … status / program / remaining / progress / last duration / last energy / learned quiet time`.
* Events: `washer_ml_cycle_started`, `washer_ml_cycle_finished` (`program`, `duration_min`, `energy_kwh`, `new_program`).

## Install
**HACS:** HACS → ⋮ → Custom repositories → add `https://github.com/fisch192/ha-washer-ml` (category *Integration*) → install → restart.
**Manual:** copy `custom_components/washer_ml` to `<config>/custom_components/`, restart.

Then *Settings → Devices & services → Add integration → Washer ML*, pick your power sensor
(W). Requires the recorder (default) for learning from history.

## Notification example
See `packages/washer_ml_notify.yaml` (event-triggered automation).

## Services
`washer_ml.learn_from_history`, `washer_ml.rename_program`, `washer_ml.delete_program`, `washer_ml.reset_learning`.

## Tuning
Start/quiet thresholds default to 45 W (above the machine's standby pulses, below real work);
change them in the panel. If your machine has long soak pauses with very low power, the
learned quiet time adapts after a few cycles.

## Development
`python3 tests/test_engine.py` replays 12 recorded programs (`tests/recorded_cycles.json`).
`python3 tests/replay.py` prints, per program, the delay between last spin and alert.
The Home Assistant glue (config flow, entities, panel) was developed against HA 2026.x; the
engine is covered by tests, the integration layer was checked syntactically and the panel was
rendered in a headless browser with mock data.

License: MIT
