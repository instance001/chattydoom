# ChattyDoom Barebones (v0.1)

A 60-second VizDoom sandbox for experimenting with modular enemy brains. It ships with a tiny E1M1-style arena placeholder, three sample enemies, and a minimal runner that calls Python brains on each tick.

## What you'll get
- Three sample brains in `brains/` (marine, imp, pinkie) wired through `config.yaml`, with more believable behaviors and internal cooldowns.
- Config-driven IWAD/PWAD/music paths; defaults point to Freedoom plus a placeholder map.
- VizDoom config in `engine/basic.cfg` for quick windowed runs, exposing useful game variables to brains.
- AGPL-licensed code and no bundled id Software assets.

## Quickstart
1. Install Python 3.10+.
2. Create a virtualenv and install deps:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Grab Freedoom automatically (from the official Freedoom GitHub releases):
   - Run: `python setup_assets.py`
   (Downloads the latest release, extracts `freedoom2.wad` into `assets/iwad/`, and updates `config.yaml`.)
4. Place a small PWAD in `assets/maps/demo_e1m1.wad` (or update `config.yaml` to point elsewhere).
5. Run the game:
   - Manual mode (default): `python engine/vizdoom_runner.py` — WASD + arrows to move/turn, Shift to sprint, Space/LeftCtrl to shoot, E to use/switch.
   - Auto demo: `python engine/vizdoom_runner.py --auto`
6. The runner auto-drives a stub set of three enemies for roughly 60 seconds. If the IWAD is missing you will get a clear error and exit; missing PWADs are warned and skipped.

## Config notes
- `config.yaml` controls IWAD/PWAD paths, music loops, and the mapping from enemy class to brain module.
- `budgets` is a placeholder for future tick/time quotas if you want to throttle expensive brains.
- Brains must expose `decide(state: dict) -> dict` returning at least `{"action": <name>, "confidence": <0..1>}`; see `brains/` for examples.
- Actions are mapped to VizDoom controls in `engine/action_adapter.py`.

## Modding
- Swap brains: add a new module under `brains/` and register it in `config.yaml`.
- Swap maps: drop your PWAD in `assets/maps/` and point `config.yaml.pwad` to it.
- Audio: place appropriately licensed loops in `assets/music/` and wire in `config.yaml`. Keep attribution files with the assets.
- The `engine/state_adapter.py` currently falls back to heuristics for LOS/dist; it already exposes player position/angle/health/armor/ammo if the config exports them—wire in real actor queries when you add proper enemy hooks.

## Repo structure
- `engine/` — VizDoom runner and adapters; extend here for richer state/action plumbing.
- `brains/` — sample enemy brains with tiny decision policies.
- `assets/` — empty folders for IWAD, PWAD, music, and sfx (kept out of git via `.gitignore`).
- `config.yaml` — single place to point at assets and brains.

## Troubleshooting
- Missing IWAD/PWAD: the runner prints a path reminder and exits.
- VizDoom install issues: try `pip install vizdoom --no-binary :all:` if wheels are unavailable for your platform.
- Black window or no movement: verify your PWAD has a `MAP01` lump or change `game.set_doom_map()` in `engine/vizdoom_runner.py`.

## Licensing
- Code: AGPL-3.0-only (see `LICENSE`). If you run modified builds over a network, you must offer the source per AGPLv3 section 13.
- IWAD: use Freedoom or other legal IWADs you own; we do not ship id Software assets.
- User-added maps/music/sfx: include their required licenses or credits alongside the files.
