"""Synthetic curves (NOT recorded data) for the dishwasher / dryer presets.

They check that the presets neither end a program during the typical long low-power
phases nor wait forever afterwards. Real curves should be added when available."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "custom_components" / "appliance_ml"))
from engine import Config, Engine
from const import PRESETS


def cfg(kind):
    p = PRESETS[kind]
    return Config(start_w=p["start_w"], end_w=p["end_w"], min_cycle_s=p["min_cycle_min"] * 60,
                  min_end_s=p["min_end_s"], default_end_s=p["default_end_s"],
                  max_end_s=p["max_end_min"] * 60, min_peak_w=p["min_peak_w"])


def run(engine, phases, t0=0.0, tail_s=3600):
    """phases: [(watts, seconds)]. Returns (events, end_of_last_active_phase)."""
    t, evs, last_active = t0, [], t0
    for watts, secs in phases:
        evs += engine.feed(t, watts)
        step = 15
        for k in range(int(secs // step)):
            evs += engine.tick(t + (k + 1) * step)
        t += secs
        if watts > engine.cfg.end_w:
            last_active = t
    evs += engine.feed(t, 1.0)
    for k in range(int(tail_s // 15)):
        evs += engine.tick(t + (k + 1) * 15)
    return evs, last_active


class ApplianceTests(unittest.TestCase):
    def test_dishwasher_pauses_do_not_end_program(self):
        e = Engine(cfg("dishwasher"))
        phases = [(2000, 600), (100, 60), (3, 300), (2000, 900), (3, 480), (120, 60), (2000, 600), (4, 2400)]
        evs, last_active = run(e, phases)
        fin = [x for x in evs if x["type"] == "finished"]
        self.assertEqual(len(fin), 1)
        self.assertGreater(fin[0]["end"], last_active - 1)       # not before the last heating
        self.assertLess(fin[0]["detected_at"] - last_active, 15 * 60)

    def test_dryer_heater_cycling_and_cooldown(self):
        e = Engine(cfg("dryer"))
        phases = []
        for _ in range(12):
            phases += [(2000, 240), (150, 40)]       # heater on, fan only
        phases += [(150, 600), (2, 60)]               # cool-down tumbling
        evs, last_active = run(e, phases)
        fin = [x for x in evs if x["type"] == "finished"]
        self.assertEqual(len(fin), 1)
        self.assertLess(fin[0]["detected_at"] - last_active, 10 * 60)

    def test_short_blip_is_not_a_program(self):
        for kind in PRESETS:
            e = Engine(cfg(kind))
            evs, _ = run(e, [(500, 120), (1, 60)])
            self.assertFalse([x for x in evs if x["type"] == "finished"], kind)


if __name__ == "__main__":
    unittest.main(verbosity=2)
