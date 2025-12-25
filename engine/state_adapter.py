# Converts VizDoom state into compact dicts for brains.
# This stays conservative and falls back to heuristics when data is missing.
from math import hypot

# Order must match engine/basic.cfg available_game_variables
_VAR_ORDER = [
    "POSITION_X",
    "POSITION_Y",
    "POSITION_Z",
    "ANGLE",
    "VELOCITY_X",
    "VELOCITY_Y",
    "HEALTH",
    "ARMOR",
    "AMMO2",
    "AMMO4",
]


def _extract_vars(vd_state):
    values = list(getattr(vd_state, "game_variables", []) or [])
    return {name: values[idx] for idx, name in enumerate(_VAR_ORDER) if idx < len(values)}


def _approx_dist(enemy_obj, tick):
    # Pseudo-distance so brains can branch without real actor plumbing
    base = 6.0 + (enemy_obj.get("id", 0) % 3) * 2.0
    wobble = ((tick // 10) % 5) - 2  # range -2..2
    return max(1.5, base + wobble)


def _approx_los(enemy_obj, tick):
    # Alternate LOS to encourage varied behavior in stubs
    return ((tick // 20) + enemy_obj.get("id", 0)) % 3 != 0


def pack_state(vd_state, enemy_obj, tick):
    vars_map = _extract_vars(vd_state)
    speed = hypot(vars_map.get("VELOCITY_X", 0.0), vars_map.get("VELOCITY_Y", 0.0))
    return {
        "tick": tick,
        "enemy": {
            "id": enemy_obj.get("id", 0),
            "class": enemy_obj.get("class", "marine"),
            "hp": enemy_obj.get("hp", 50),
        },
        # Target = the player from the enemy's POV
        "player": {
            "los": _approx_los(enemy_obj, tick),
            "dist": _approx_dist(enemy_obj, tick),
            "health": vars_map.get("HEALTH", 100),
            "armor": vars_map.get("ARMOR", 0),
            "ammo": {"shells": vars_map.get("AMMO2", 0), "cells": vars_map.get("AMMO4", 0)},
            "pos": (
                vars_map.get("POSITION_X", 0.0),
                vars_map.get("POSITION_Y", 0.0),
                vars_map.get("POSITION_Z", 0.0),
            ),
            "angle": vars_map.get("ANGLE", 0.0),
            "speed": speed,
        },
        "env": {
            "has_cover": False,  # TODO: wire to map queries when actors are hooked up
            "seed": tick,
        },
    }
