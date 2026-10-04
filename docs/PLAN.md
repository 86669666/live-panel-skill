# live-panel plan

Single-stream work on `work/main` of the fork. Upstream is pull-only. No force-push, no merge or push to `main`, no release tags, no secrets, no generated media dumps.

## Audit

Baseline `8a70aa2`. `scripts/check_frames.py` (120 samples, `--repeat`) is clean on all three examples with the system Chrome and ffmpeg. Geometry and replay are in good shape.

Frame sampling does not catch a state machine that keeps a field from the previous step. Two cases were wrong:

- `cycle` and `triggers` left the previous step's fields in place (`tool`, `to`, and anything else the next step omits).
- `any_low` read gauges from the previous seek when it was declared first, so the legend could disagree with the bars for that frame.

Rounded `path` corners (`r`) still draw a curve while packets follow the sharp polyline. On the three `r: 8` bends in `examples/agent-architecture` that is a few pixels. Leave it until a before/after frame check shows it is worth the motion change.

## This slice

- Clear step fields that the current `cycle` or `triggers` item does not have, and bring them back when a later step has them again.
- Run `any_low` after the other machines in the same `seek`, so key order in `machines` does not matter.
- Keep `check_frames.py` sample times inside the clip.
- Make `render.py` exit non-zero when the page reports an error after frames have started, and close ffmpeg if Chrome fails mid-render.
- `scripts/check_contract.py` locks the cases above. It does not replace `check_frames.py`.

## Checks

```bash
python3 scripts/check_contract.py
python3 scripts/check_frames.py --config examples/codex-agents/config.json --out-dir /tmp/lp-codex --repeat
```

Run the same frame check for `examples/airbnb/config.json` and `examples/agent-architecture/config.json`. Do not commit `/tmp` output, mp4s, or frame dumps.

## Next

Do not add a theme, a fourth example, or a browser stack unless a real config cannot say what it needs. The corner-following packet path is the only motion change still worth a later, checked slice.
