# AGENTS — _ii

Short routing guide for AI agents working in `_ii`.

## What This Project Is

`_ii` is a **live terminal visual engine** for VJ performances. It runs a Python curses-based controller (`_ii.py`) alongside a terminal visual renderer (`visuals.py`) to produce ANSI/Unicode art for fullscreen projection at live events.

Built for real-time performance: hot-reload via `os.execv()`, BPM sync, 25+ visual modes, multi-output (TTY, pygame, framebuffer), projection mapping, audio/camera reactivity, and OSC/MIDI control.

## Ecosystem Position

```
di.iiii platform (dob-0/di.iiii)   ← spatial editor platform
    └── br_id_ge (/home/nooo/br_id_ge)  ← tele-symbiotic performance prototype
            └── _ii (this repo)          ← live visual engine for br_id_ge shows
```

`_ii` is the **visual performance layer** for br_id_ge events. Its `config.json` is event-specific (currently: MUTATION 2 @ Hayfilm). It runs as systemd services on a dedicated Debian machine (TTY1 for visuals, tmux `ii` session for controller, port 7777 for web portal).

## Start Here

1. `README.md` — operator guide, quick start, full mode list
2. `CLAUDE.md` — code structure, hot-reload notes, how to add a mode
3. `AI_CONTEXT.md` — comprehensive project context for AI agents
4. `config.json` — event config (symbol sets, mode params, show text)

## Key Files

| File | Role |
|------|------|
| `_ii.py` | Controller — curses UI, node graph evaluator, manual overrides |
| `visuals.py` | Renderer — ANSI terminal output, mode dispatch, hot-reload |
| `modes/*.py` | 25+ visual mode classes (ORDER field controls palette position) |
| `architecture.py` | Shared config, mode auto-discovery via `pkgutil.walk_packages()` |
| `audio.py` | Mic-level/BPM detection (optional) |
| `node_lib.py` | Signal nodes: AudioLevel, CameraMotion, ArtNetOut, etc. |
| `fx.py` | FX rack — glitch, kaleido, echo, slice, shutter |
| `cues.py` | Performance cue system (snapshots of control state) |
| `map_server.py` | Web portal at port 7777 (130KB single-file HTML/CSS/JS) |
| `ii_runtime/` | Clean typed scaffold (dataclasses, 11 unit tests, 3 modes) |
| `live/` | Headless layer: bash/awk ANSI engines, GLSL shaders, SuperCollider |
| `config.json` | Event metadata, symbol sets, mode params (edit per show) |

## IPC Pattern

Controller → visuals via `control.json`. Visuals → controller via `status.json`. Both written atomically. Do not read mid-write; check for partial JSON.

## Hot Reload

Both `_ii.py` and `visuals.py` use `os.execv()` to self-replace when their source file changes. Terminal stays open. State is lost on reload but modes reinitialize cleanly. Edit a file → save → reload is instant.

## Adding a Mode

1. Create `modes/my_mode.py` inheriting `modes.base.Mode`
2. Set `NAME`, `ORDER`, `PARAMS` class attributes
3. Implement `render(self, grid, t, params) → list[list[str]]`
4. No registration needed — `architecture.py` auto-discovers via `pkgutil`

## Services (Debian machine)

```bash
sudo systemctl start ii-visuals   # TTY1 full-screen ANSI output
sudo systemctl start ii-ctrl      # tmux 'ii' session — curses controller
sudo systemctl start ii-web       # port 7777 — web portal
```

## Sync & Deploy

```bash
bash scripts/sync.sh "message"    # pull → commit → push → SSH restart on Debian
```

## Validation

```bash
python3 -m pytest tests/          # 11 unit tests (ii_runtime only)
python3 -m py_compile _ii.py visuals.py architecture.py   # syntax check
bash -n scripts/sync.sh           # shell script syntax check
```

## What Not To Touch

- `control.json`, `status.json` — runtime IPC files, gitignored
- `live/out/` — generated renders, gitignored
- `mappings/FINAL.xml` — Resolume export, do not auto-edit

## One-Line Summary

`_ii` is a real-time terminal VJ engine for br_id_ge live shows. Start with `README.md`, edit `modes/` for new visuals, edit `config.json` for event content, use `scripts/sync.sh` to deploy.
