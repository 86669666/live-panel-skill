# live-panel

Config-driven animated architecture diagrams. One JSON file drives `assets/template.html`. Python scripts are stdlib only.

## Checks

- `python3 scripts/check_contract.py` — machine fields match the current frame, sample times stay inside the clip, render exit status.
- `python3 scripts/check_frames.py --config <example>/config.json --out-dir <dir> --repeat` — overflow, overlap, and replay. Needs Chrome and ffmpeg on `PATH`.

Both are local. Do not add a pip or browser dependency for a check the stdlib scripts can do.

## Rules

- The template is generic. New diagrams are new configs, not template forks.
- Numbers on screen are either sourced or marked illustrative. Keep the credit line.
- Do not commit rendered mp4s, frame dumps, credentials, or font files.
- `examples/codex-agents/` and `examples/agent-architecture/` recreate other people's designs. Don't restyle them to suit a code change.
