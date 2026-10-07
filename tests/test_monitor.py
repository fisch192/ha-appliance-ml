"""Synthetic fridge: compressor 70 W on 10-14 min, off 22-28 min at 2 W (matches the real plug: ~16 W mean)."""
import random, sys, types, unittest
from pathlib import Path
PKG = Path(__file__).parents[1] / "custom_components" / "appliance_ml"
pkg = types.ModuleType("appliance_ml"); pkg.__path__ = [str(PKG)]
sys.modules["appliance_ml"] = pkg
from appliance_ml.monitor import CycleMonitor, MonitorConfig

DAY = 86400


class Fridge:
    def __init__(self, seed=1, on_w=70.0, off_w=2.0, on_min=(10, 14), off_min=(22, 28)):
        self.r = random.Random(seed)
        self.on_w, self.off_w, self.on_min, self.off_min = on_w, off_w, on_min, off_min
        self.on, self.until = False, 0.0

    def power(self, ts):
        if ts >= self.until:
            self.on = not self.on
            lo, hi = self.on_min if self.on else self.off_min
            self.until = ts + 60 * self.r.uniform(lo, hi)
        return (self.on_w if self.on else self.off_w) + self.r.uniform(-1, 1)


def run(days, fridge, mon, t0=0.0, events=None, step=30, outage=None):
    t = t0
    end = t0 + days * DAY
    while t < end:
        if not (outage and outage[0] <= t < outage[1]):
            mon.feed(t, fridge.power(t))
        for e in mon.tick(t):
            if events is not None:
                events.append((t, e))
        t += step
    return t


class MonitorTests(unittest.TestCase):
    def learn(self, days=25, **kw):
        mon = CycleMonitor(MonitorConfig(kind="fridge", on_w=10))
        f = Fridge(**kw)
        ev = []
        t = run(days, f, mon, events=ev)
        return mon, f, t, ev

    def test_normal_operation_raises_no_alert(self):
        mon, f, t, ev = self.learn(30)
        self.assertEqual([e for _, e in ev if e["type"] == "problem"], [])
        self.assertFalse(mon.summary["learning"])
        self.assertAlmostEqual(mon.summary["energy_kwh"], 0.58, delta=0.08)

    def test_slow_seasonal_drift_is_tolerated(self):
        mon = CycleMonitor(MonitorConfig(on_w=10))
        r = random.Random(5); t = 0.0; ev = []
        for day in range(35):               # on-time grows 25 % over 35 days
            f = Fridge(seed=day, on_min=(10 * (1 + day / 140), 14 * (1 + day / 140)))
            t = run(1, f, mon, t0=t, events=ev)
        self.assertEqual([e for _, e in ev if e["type"] == "problem"], [])

    def test_door_ajar_raises_duty_alert_within_a_day(self):
        mon, f, t, ev = self.learn(25)
        ev.clear()
        bad = Fridge(seed=9, off_min=(8, 11))             # compressor works much more
        run(2, bad, mon, t0=t, events=ev)
        probs = [e for _, e in ev if e["type"] == "problem"]
        self.assertTrue(probs)
        self.assertTrue({"duty_up", "energy_up"} & set(probs[0]["reasons"]), probs[0]["reasons"])
        self.assertLess(ev[0][0] - t, 1.2 * DAY)

    def test_higher_base_load_is_reported(self):
        mon, f, t, ev = self.learn(25)
        ev.clear()
        run(2, Fridge(seed=3, off_w=8.0), mon, t0=t, events=ev)        # standby 2 W -> 8 W (still below the 10 W on-threshold)
        reasons = {r for _, e in ev if e["type"] == "problem" for r in e["reasons"]}
        self.assertIn("base_up", reasons)

    def test_compressor_running_continuously(self):
        mon, f, t, ev = self.learn(25)
        ev.clear()
        stuck = Fridge(seed=4, on_min=(400, 400))
        run(0.3, stuck, mon, t0=t, events=ev)
        reasons = {r for _, e in ev if e["type"] == "problem" for r in e["reasons"]}
        self.assertIn("running_continuously", reasons)

    def test_missing_data_is_reported_and_clears(self):
        mon, f, t, ev = self.learn(25)
        ev.clear()
        run(1, f, mon, t0=t, events=ev, outage=(t + 3600, t + DAY))     # plug offline for 23 h
        self.assertIn("no_data", {r for _, e in ev if e["type"] == "problem" for r in e["reasons"]})

    def test_no_alerts_while_still_learning(self):
        mon = CycleMonitor(MonitorConfig(on_w=10))
        ev = []
        run(3, Fridge(seed=2, off_min=(5, 6)), mon, events=ev)
        self.assertEqual([r for _, e in ev if e["type"] == "problem" for r in e["reasons"] if r != "no_data"], [])

    def test_house_base_load_monitor(self):
        mon = CycleMonitor(MonitorConfig(kind="baseload", on_w=10_000))
        r = random.Random(1); t = 0.0; ev = []
        def house(ts, base):
            h = (ts / 3600) % 24
            return base + (1500 if 18 <= h < 19 else 0) + (250 if 7 <= h < 8 else 0) + r.uniform(-5, 5)
        while t < 25 * DAY:
            mon.feed(t, house(t, 130)); [ev.append(e) for e in mon.tick(t)]; t += 60
        self.assertEqual([e for e in ev if e["type"] == "problem" and "base_up" in e["reasons"]], [])
        t0 = t
        while t < t0 + 2 * DAY:
            mon.feed(t, house(t, 210)); [ev.append(e) for e in mon.tick(t)]; t += 60
        self.assertTrue([e for e in ev if e["type"] == "problem" and "base_up" in e["reasons"]])

    def test_persistence(self):
        mon, f, t, ev = self.learn(10)
        m2 = CycleMonitor(); m2.load(mon.dump())
        self.assertEqual(len(m2.hours), len(mon.hours))


if __name__ == "__main__":
    unittest.main(verbosity=2)
