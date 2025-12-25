"""Minimal VizDoom runner for experimenting with modular enemy brains.

Modes:
- Manual (default): play with WASD + Space/LeftCtrl to shoot.
- Auto demo (--auto): runs sample brains for ~60 seconds.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path
from typing import Callable, Dict

import yaml

try:
    from vizdoom import DoomGame
except Exception as exc:
    raise SystemExit("Install vizdoom first: pip install vizdoom") from exc

# Optional: keyboard controls for manual mode
try:
    import keyboard
except Exception:
    keyboard = None  # type: ignore

from state_adapter import pack_state
from action_adapter import to_controls

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CONFIG_PATH = ROOT / "config.yaml"
MAX_TICKS = 60 * 60  # ~60 seconds at 60 tics


def load_config(path: Path) -> dict:
    """Load YAML config or exit with a helpful message."""
    if not path.exists():
        raise SystemExit(f"Config file missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_brain(path: str) -> Callable[[dict], dict]:
    """Import a brain module and return its decide function."""
    mod_path = path.replace("/", ".").removesuffix(".py")
    mod = importlib.import_module(mod_path)
    decide_fn = getattr(mod, "decide", None)
    if decide_fn is None:
        raise RuntimeError(f"Brain {path} missing decide(state)->dict")
    return decide_fn


def resolve_brains(config: dict) -> Dict[str, Callable[[dict], dict]]:
    brains_cfg = config.get("brains") or {}
    if not brains_cfg:
        raise SystemExit("No brains configured in config.yaml: add entries under 'brains'.")
    return {name: load_brain(module_path) for name, module_path in brains_cfg.items()}


def ensure_assets(config: dict):
    """Validate IWAD/PWAD paths and return expanded paths."""
    base = CONFIG_PATH.parent
    iwad_raw = config.get("iwad", "")
    pwad_raw = config.get("pwad", "")

    iwad_path = Path(iwad_raw).expanduser()
    if not iwad_path.is_absolute():
        iwad_path = base / iwad_path

    pwad_path = Path(pwad_raw).expanduser()
    if not pwad_path.is_absolute():
        pwad_path = base / pwad_path

    if not iwad_path.exists():
        raise SystemExit(
            f"IWAD not found at {iwad_path}\n"
            "Run python setup_assets.py to fetch Freedoom (freedoom2.wad) "
            "or point config.yaml: iwad to your own legal IWAD."
        )

    if not pwad_path.exists():
        print(f"[!] PWAD not found at {pwad_path}; continuing without a custom map.")
        pwad_path = None

    return iwad_path, pwad_path


def boot_game(config: dict):
    game = DoomGame()
    cfg_path = Path(__file__).resolve().parent / "basic.cfg"
    game.load_config(str(cfg_path))

    iwad_path, pwad_path = ensure_assets(config)
    game.set_doom_game_path(str(iwad_path))
    if pwad_path:
        game.set_doom_scenario_path(str(pwad_path))

    game.set_doom_map("map01")
    game.init()
    return game


def get_manual_controls() -> Dict[str, int]:
    """Poll keyboard state and build a controls dict."""
    if keyboard is None:
        raise SystemExit("Manual mode requires the 'keyboard' package. pip install -r requirements.txt")

    controls = {
        "MOVE_LEFT": int(keyboard.is_pressed("a")),
        "MOVE_RIGHT": int(keyboard.is_pressed("d")),
        "MOVE_FORWARD": int(keyboard.is_pressed("w")),
        "MOVE_BACKWARD": int(keyboard.is_pressed("s")),
        "TURN_LEFT": int(keyboard.is_pressed("left")),
        "TURN_RIGHT": int(keyboard.is_pressed("right")),
        "SPEED": int(keyboard.is_pressed("shift")),
    }
    shoot = keyboard.is_pressed("space") or keyboard.is_pressed("ctrl") or keyboard.is_pressed("left ctrl")
    controls["ATTACK"] = int(shoot)
    controls["USE"] = int(keyboard.is_pressed("e"))
    return controls


def run_manual(game: DoomGame):
    print("Manual mode: WASD to move, Space/LeftCtrl to shoot. Close window or finish level to exit.")
    while not game.is_episode_finished():
        state = game.get_state()
        if state is None:
            game.advance_action()
            continue

        controls = get_manual_controls()
        game.make_action(
            [
                controls.get("MOVE_LEFT", 0),
                controls.get("MOVE_RIGHT", 0),
                controls.get("MOVE_FORWARD", 0),
                controls.get("MOVE_BACKWARD", 0),
                controls.get("TURN_LEFT", 0),
                controls.get("TURN_RIGHT", 0),
                controls.get("SPEED", 0),
                controls.get("ATTACK", 0),
                controls.get("USE", 0),
            ],
            1,
        )

    game.close()


def run_auto_demo(game: DoomGame, config: dict):
    brains = resolve_brains(config)
    tick = 0
    # Placeholder enemy list; real wiring would sync with spawned actors.
    enemies = [
        {"id": 1, "class": "marine", "hp": 50},
        {"id": 2, "class": "imp", "hp": 60},
        {"id": 3, "class": "pinkie", "hp": 80},
    ]

    while not game.is_episode_finished():
        state = game.get_state()
        if state is None:
            game.advance_action()
            continue

        for enemy in enemies:
            packed = pack_state(state, enemy, tick)
            brain = brains.get(enemy["class"])
            try:
                out = brain(packed)
            except Exception as exc:  # keep demo running even if a brain fails
                print(f"[!] Brain error for {enemy['class']}: {exc}")
                out = {"action": "idle", "confidence": 0.0}

            controls = to_controls(out.get("action", "idle"))
            # Button order must match engine/basic.cfg available_buttons
            game.make_action(
                [
                    controls.get("MOVE_LEFT", 0),
                    controls.get("MOVE_RIGHT", 0),
                    controls.get("MOVE_FORWARD", 0),
                    controls.get("MOVE_BACKWARD", 0),
                    controls.get("TURN_LEFT", 0),
                    controls.get("TURN_RIGHT", 0),
                    controls.get("SPEED", 0),
                    controls.get("ATTACK", 0),
                    controls.get("USE", 0),
                ],
                1,
            )

        tick += 1
        if tick > MAX_TICKS:
            break

    game.close()


def main():
    parser = argparse.ArgumentParser(description="ChattyDoom barebones runner")
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Run the sample brains for a short demo instead of manual controls",
    )
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)
    game = boot_game(config)

    if args.auto:
        run_auto_demo(game, config)
    else:
        run_manual(game)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
