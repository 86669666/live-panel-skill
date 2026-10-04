# live-panel plan

Single-stream work on `work/main` of the fork. Upstream is pull-only. No force-push, no merge or push to `main`, no release tags, no secrets, no generated media dumps.

## Audit

`050976e` is on `origin/work/main`. The three examples pass geometry and replay. Machine fields clear between steps, and `any_low` no longer depends on key order.

`gauge` still compared its hash with the previous raw hash. A run of equal hashes all moved to the same next index, so the bar and the log held one value for two periods. On `examples/codex-agents` `jev0` that is t=24.4s to 27.8s (0.87 twice). `jev1` and `jev2` do not repeat inside the 30s clip.

Rounded `path` corners (`r`) still draw a curve while packets follow the sharp polyline. On the three `r: 8` bends that is under 3px, inside a 10px packet. Leave it.

## This slice

- Choose the gauge index from the index that was actually shown last step, anchored before the clip so call order does not matter.
- `scripts/check_contract.py` locks the `jev0` collision: 0.87, then 0.97, then 0.52.

## Checks

```bash
python3 scripts/check_contract.py
python3 scripts/check_frames.py --config examples/codex-agents/config.json --out-dir /tmp/lp-codex --repeat
```

Run the same frame check for `examples/airbnb/config.json` and `examples/agent-architecture/config.json`. Do not commit `/tmp` output, mp4s, or frame dumps.

## Next

Do not add a theme, a fourth example, or a browser stack unless a real config cannot say what it needs. The corner-following packet path stays deferred until a frame check shows the few pixels are worth a motion change.
