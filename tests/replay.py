import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "custom_components" / "appliance_ml"))
from engine import Engine

def replay(cycles, engine=None, gap=3600):
    e = engine or Engine()
    out, t0 = [], 1_000_000.0
    for c in cycles:
        pts = [(t0 + t, v) for t, v in c["points"]]
        last_big = max(t for t, v in pts if v > 45)
        evs = []
        for t, v in pts:
            evs += e.feed(t, v)
        t = pts[-1][0]
        while t < pts[-1][0] + 1200 and not any(x["type"] == "finished" for x in evs):
            t += 15
            evs += e.tick(t)
        fin = [x for x in evs if x["type"] == "finished"]
        poweroff = next((tt for tt, v in pts if tt > last_big and v == 0.0), None)
        out.append((c["start"], fin[0] if fin else None, last_big, poweroff, t0))
        t0 = pts[-1][0] + gap
    return e, out

if __name__ == "__main__":
    cycles = json.loads((Path(__file__).parent / "recorded_cycles.json").read_text())
    e, out = replay(cycles)
    for start, fin, last_big, off, t0 in out:
        if not fin:
            print(start, "NOT FINISHED"); continue
        print(start[5:16], fin["name"], "new" if fin["new_program"] else "   ",
              "dur %3.0f min" % (fin["duration_s"] / 60), "%4.0f Wh" % fin["energy_wh"],
              "| alert %3.0f s after last spin" % (fin["detected_at"] - last_big),
              "| power-off %s" % ("%4.0f s" % (off - last_big) if off else "  -  "))
    print("learned end delay: %.0f s, programs: %d" % (e.end_delay_s, len(e.programs)))
