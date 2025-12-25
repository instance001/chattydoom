"""
Imp harasser: prefers mid-range fireballs, dances when pressured.
Uses a simple cooldown to avoid spamming fireballs every tick.
"""

_last_shot_tick = {}


def _can_cast(enemy_id: int, tick: int, cooldown: int = 8) -> bool:
    last = _last_shot_tick.get(enemy_id, -cooldown)
    if tick - last >= cooldown:
        _last_shot_tick[enemy_id] = tick
        return True
    return False


def decide(state: dict) -> dict:
    los = state["player"]["los"]
    dist = state["player"]["dist"]
    tick = state["tick"]
    enemy_id = state["enemy"]["id"]

    if los and 6 <= dist <= 14 and _can_cast(enemy_id, tick):
        return {"action": "shoot_fireball", "confidence": 0.85}

    if dist < 5:
        # too close: sidestep hard
        direction = "right" if tick % 2 == 0 else "left"
        return {"action": f"strafe_{direction}", "confidence": 0.7}

    # default mid-range wiggle
    direction = "left" if tick % 3 else "right"
    return {"action": f"strafe_{direction}_shoot", "confidence": 0.6}
