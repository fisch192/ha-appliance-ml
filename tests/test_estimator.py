"""Simulation: dishwasher WITHOUT power meter inside a noisy house (fridge, standby, noise)."""
import random, sys, unittest
from pathlib import Path
import types
PKG = Path(__file__).parents[1] / "custom_components" / "appliance_ml"
pkg = types.ModuleType("appliance_ml"); pkg.__path__ = [str(PKG)]       # skip __init__ (needs Home Assistant)
sys.modules["appliance_ml"] = pkg
from appliance_ml.engine import Config, Engine
from appliance_ml.estimator import DerivedTracker

PROGRAMS = {   # minute-resolution own power (W)
    "Eco":      [(10, 1800), (25, 60), (12, 1800), (30, 40), (8, 120), (15, 5)],
    "Intensiv": [(12, 2000), (20, 80), (18, 2000), (25, 50), (10, 2000), (20, 5)],
    "Schnell":  [(8, 1900), (12, 70), (8, 1900), (5, 60)],
}


def own_curve(name):
    out = []
    for mins, w in PROGRAMS[name]:
        out += [w] * mins
    return out


def truth_wh(name):
    return sum(own_curve(name)) / 60.0


def simulate(sequence, seed=1, kettle_in=()):
    """sequence: list of program names. kettle_in: indexes of cycles with a 2 kW kettle during the run."""
    rnd = random.Random(seed)
    cfg = Config(start_w=30, end_w=20, min_cycle_s=900, min_peak_w=100)
    eng = Engine(cfg)
    trk = DerivedTracker(eng)
    t, events = 0.0, []

    fridge = {"on": False, "until": 0.0}

    def house(ts):                       # random fridge compressor (on 10-14 min, off 20-26 min) + 140 W standby
        if ts >= fridge["until"]:
            fridge["on"] = not fridge["on"]
            fridge["until"] = ts + 60 * (rnd.uniform(10, 14) if fridge["on"] else rnd.uniform(20, 26))
        return 140 + (120 if fridge["on"] else 0) + rnd.uniform(-8, 8)

    def run_idle(minutes):
        nonlocal t
        for _ in range(int(minutes * 6)):
            trk.feed_total(t, house(t)); t += 10

    run_idle(30)
    for i, name in enumerate(sequence):
        curve = own_curve(name)
        events += trk.set_active(t, True, name)
        k0 = rnd.randint(10, len(curve) - 10) if i in kettle_in else 10**9
        for m in range(len(curve)):
            for s in range(6):
                extra = 2000 if k0 <= m < k0 + 4 else 0
                trk.feed_total(t, house(t) + curve[m] + extra); t += 10
        events += trk.set_active(t, False)
        run_idle(rnd.uniform(30, 70))
    return eng, [e for e in events if e["type"] == "finished"]


class EstimatorTests(unittest.TestCase):
    def test_learns_true_energy_per_program(self):
        seq = ["Eco", "Intensiv", "Schnell"] * 4
        eng, fin = simulate(seq)
        self.assertEqual(len(fin), len(seq))
        for prog in eng.programs:
            self.assertAlmostEqual(prog.energy_wh / truth_wh(prog.name), 1.0, delta=0.12, msg=prog.name)

    def test_cycles_disturbed_by_other_loads_are_not_learned(self):
        seq = ["Eco"] * 7
        eng, fin = simulate(seq, kettle_in={4, 6})
        disturbed = [f["disturbed"] for f in fin]
        self.assertEqual(disturbed, [False, False, False, False, True, False, True])
        eco = eng.programs[0]
        self.assertAlmostEqual(eco.energy_wh / truth_wh("Eco"), 1.0, delta=0.08)
        for f in fin:                      # reported energy of a disturbed cycle = typical energy
            self.assertAlmostEqual(f["energy_wh"] / truth_wh("Eco"), 1.0, delta=0.15)

    def test_known_program_caps_foreign_load_in_live_power(self):
        eng, _ = simulate(["Eco"] * 4)
        trk = DerivedTracker(eng)
        trk.total = 150.0
        t = 5e6
        trk.samples.append((t - 600, 150.0)); trk.samples.append((t, 150.0))
        trk.set_active(t, True, "Eco")
        for k in range(1, 7):
            trk.feed_total(t + k * 10, 150.0 + 1800)       # first heating
        for k in range(7, 30):
            trk.feed_total(t + k * 10, 150.0 + 1800 + 2000)  # kettle on top
        self.assertLess(eng._power, 1.35 * 2000 + 120)   # kettle (2 kW) is cut off
        self.assertGreater(eng._power, 1000)

    def test_program_name_from_appliance_is_used_and_predicts_remaining(self):
        eng, _ = simulate(["Eco", "Intensiv", "Eco", "Intensiv", "Eco"])
        eng.begin_external(9e6, "Intensiv")
        eng.advance_external(9e6 + 30 * 60, 500.0)
        m = eng.match
        self.assertEqual(m["name"], "Intensiv")
        self.assertAlmostEqual(m["remaining_s"] / 60, 105 - 30, delta=6)

    def test_unknown_programs_are_clustered_without_hint(self):
        # the engine learns program types from the curve alone when the appliance gives no name
        rnd = random.Random(3)
        eng = Engine(Config(start_w=30, end_w=20, min_cycle_s=900, min_peak_w=100))
        trk = DerivedTracker(eng)
        t = 0.0
        names = []
        for name in ["Eco", "Intensiv", "Schnell", "Eco", "Intensiv", "Schnell"]:
            for _ in range(180): trk.feed_total(t, 140 + rnd.uniform(-5, 5)); t += 10
            trk.set_active(t, True, None)
            for w in own_curve(name):
                for _ in range(6): trk.feed_total(t, 140 + w + rnd.uniform(-5, 5)); t += 10
            names += [e["name"] for e in trk.set_active(t, False) if e["type"] == "finished"]
        self.assertEqual(names[0], names[3]); self.assertEqual(names[1], names[4]); self.assertEqual(names[2], names[5])
        self.assertEqual(len(set(names)), 3)

    def test_total_energy_counter_grows_monotonically(self):
        eng, fin = simulate(["Eco", "Schnell"])
        expected = truth_wh("Eco") + truth_wh("Schnell")
        self.assertAlmostEqual(eng.total_est_wh / expected, 1.0, delta=0.12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
