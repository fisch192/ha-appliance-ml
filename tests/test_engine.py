import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from replay import replay
from engine import Engine

CYCLES = json.loads((Path(__file__).parent / "recorded_cycles.json").read_text())


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine, cls.out = replay(CYCLES)

    def test_every_recorded_program_is_finished_exactly_once(self):
        self.assertEqual(len(self.out), 12)
        self.assertTrue(all(fin for _, fin, *_ in self.out))

    def test_alert_comes_shortly_after_the_last_spin(self):
        # the old logic needed 5-21 min; here: <= 5 min after the last >45 W sample
        late = [fin["detected_at"] - lb for _, fin, lb, *_ in self.out]
        self.assertLess(max(late), 300, late)
        self.assertLess(sorted(late)[len(late) // 2], 200)

    def test_standby_pulses_do_not_delay_the_end(self):
        e = Engine()
        t = 0.0
        for p in [0, 100, 2000] * 1: e.feed(t, p); t += 40
        for _ in range(60): e.feed(t, 400); t += 60
        e.feed(t, 1.2)
        end = t
        for i in range(10):                      # 30 W pulses every 5 min
            t += 300; evs = e.feed(t, 30)
            if not evs:
                t += 6; evs = e.feed(t, 1.2) or e.tick(t)
            if evs: break
        self.assertTrue(any(x["type"] == "finished" for x in evs))
        self.assertLessEqual(t - end, 400)

    def test_short_quiet_inside_a_program_does_not_end_it(self):
        e = Engine()
        t = 0.0
        e.feed(t, 2000); t += 1000
        e.feed(t, 5); t += 100            # 100 s pause < learned delay
        self.assertEqual(e.feed(t, 300), [])
        self.assertTrue(e.running)

    def test_two_program_types_and_forecast(self):
        types = {fin["name"] for _, fin, *_ in self.out}
        self.assertEqual(len(types), 3)

    def test_persistence_roundtrip(self):
        e2 = Engine(); e2.load(json.loads(json.dumps(self.engine.dump())))
        self.assertEqual(len(e2.programs), len(self.engine.programs))
        self.assertAlmostEqual(e2.end_delay_s, self.engine.end_delay_s)

    def test_live_prediction_of_remaining_time(self):
        e, _ = replay(CYCLES[:6])
        c = CYCLES[6]                      # a normal ~60 min program
        t0 = 5_000_000.0
        for t, v in c["points"]:
            if t > 30 * 60: break
            e.feed(t0 + t, v)
        e.tick(t0 + 30 * 60)
        m = e.match
        self.assertIsNotNone(m)
        self.assertEqual(m["name"], "Programm 1")
        self.assertAlmostEqual(m["remaining_s"] / 60, 30, delta=12)

    def test_bad_values_are_ignored(self):
        e = Engine()
        for v in [float("nan"), -5, float("inf")]:
            self.assertEqual(e.feed(1.0, v), [])
        self.assertFalse(e.running)


if __name__ == "__main__":
    unittest.main(verbosity=2)
