#!/usr/bin/env python3
"""Lock state-machine invariants that geometry sampling does not see.

check_frames.py measures overflow and replay. It does not notice a cycle or
trigger keeping a field from the previous step, or any_low lagging a gauge
declared later in the same config. This script checks those, plus the clip
sampler and the render exit rule. Stdlib and the repo's Chrome driver only.
"""
import json, os, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import livepanel as lp
import render


def fail(msg):
    print("FAIL:", msg)
    return 1


def check_offline():
    errors = 0
    times = lp.sample_times(30, 120)
    if len(times) != 120:
        errors += fail(f"sample_times length {len(times)}")
    if any(t < 0 or t >= 30 for t in times):
        errors += fail(f"sample point outside the clip: {min(times)}..{max(times)}")
    if times[0] != 0:
        errors += fail(f"first sample {times[0]}")
    # jitter must still move a mid sample off the even grid, without leaving the clip
    if abs(times[10] - (30 * 10 / 120 + 0.013 * 10)) > 1e-9:
        errors += fail(f"jitter dropped: {times[10]}")
    if lp.sample_times(0, 3) != [0.0, 0.0, 0.0]:
        errors += fail("zero duration")
    if lp.sample_times(10, 0) != []:
        errors += fail("zero samples")
    if render.exit_code("", 0) != 0 or render.exit_code("page error", 0) != 1 or render.exit_code("", 7) != 7:
        errors += fail("render exit_code")
    return errors


def page_text(br, cfg, seeks):
    td = tempfile.mkdtemp(prefix="livepanel-contract-")
    cfgp = os.path.join(td, "c.json")
    page = os.path.join(td, "page.html")
    Path(cfgp).write_text(json.dumps(cfg), encoding="utf-8")
    lp.build_page(cfgp, page)
    br.open("file://" + os.path.abspath(page) + "?manual")
    out = []
    for t in seeks:
        br.seek(t)
        out.append((t, br.eval("document.getElementById('stage').innerText")))
    err = br.eval("window.__error||''")
    if err:
        raise RuntimeError(err)
    return out


def check_engine(chrome):
    errors = 0
    canvas = {"width": 480, "height": 200, "duration": 8, "fps": 10}
    cycle = {
        "canvas": canvas,
        "machines": {"seq": {"type": "cycle", "period": 1, "t0": 0, "values": [
            {"t": "a", "tool": "1"}, {"t": "b"}]}},
        "elements": [{"type": "text", "x": 8, "y": 28, "t": "tool={seq.tool}"}],
    }
    triggers = {
        "canvas": canvas,
        "machines": {"tr": {"type": "triggers", "period": 2, "on": 1.5, "t0": 0, "color": "pu", "items": [
            {"name": "one", "to": "ALPHA", "adv": ["aa", "bb"]},
            {"name": "two", "adv": ["cc", "dd"]}]}},
        "elements": [
            {"type": "text", "x": 8, "y": 28, "t": "to={tr.to}"},
            {"type": "text", "x": 8, "y": 64, "t": "name={tr.name}"},
        ],
    }
    gauge = {"type": "gauge", "values": [0.2, 0.9], "threshold": 0.5, "period": 1, "t0": 0, "seed": 1, "decimals": 1}
    mode = {"type": "any_low", "of": ["g"]}
    texts = [
        {"type": "text", "x": 8, "y": 28, "t": "M={mode}"},
        {"type": "text", "x": 8, "y": 64, "t": "G={g} L={g.low}"},
    ]
    any_first = {"canvas": canvas, "machines": {"mode": mode, "g": gauge}, "elements": texts}
    gauge_first = {"canvas": canvas, "machines": {"g": gauge, "mode": mode}, "elements": texts}

    with lp.Chrome(chrome, 480, 200, True) as br:
        got = dict(page_text(br, cycle, [0, 1, 2]))
        if "tool=1" not in got[0]:
            errors += fail(f"cycle t=0 {got[0]!r}")
        if got[1].strip() != "tool=":
            errors += fail(f"cycle kept a field at t=1: {got[1]!r}")
        if "tool=1" not in got[2]:
            errors += fail(f"cycle did not restore tool at t=2: {got[2]!r}")

        got = dict(page_text(br, triggers, [0.2, 2.2, 4.2]))
        if "to=ALPHA" not in got[0.2] or "name=one" not in got[0.2]:
            errors += fail(f"trigger t=0.2 {got[0.2]!r}")
        if "name=two" not in got[2.2] or "ALPHA" in got[2.2]:
            errors += fail(f"trigger kept `to` at t=2.2: {got[2.2]!r}")
        if "to=ALPHA" not in got[4.2] or "name=one" not in got[4.2]:
            errors += fail(f"trigger did not restore `to` at t=4.2: {got[4.2]!r}")

        for name, cfg in (("mode-first", any_first), ("gauge-first", gauge_first)):
            got = dict(page_text(br, cfg, [0, 2]))
            if "M=low" not in got[0] or "L=1" not in got[0]:
                errors += fail(f"{name} t=0 {got[0]!r}")
            if "M=high" not in got[2] or "G=0.9" not in got[2] or "L=1" in got[2]:
                errors += fail(f"{name} lagged at t=2: {got[2]!r}")
    return errors


def main():
    errors = check_offline()
    chrome = lp.find_exe(None, lp.CHROME_NAMES, "Chrome")
    errors += check_engine(chrome)
    if errors:
        print(f"{errors} contract check(s) failed")
        sys.exit(1)
    print("contract ok")


if __name__ == "__main__":
    main()
