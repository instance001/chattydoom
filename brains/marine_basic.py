"""
Grunt marine: favors strafing while shooting, backs off when low on HP.
Expects state["player"]["los"] (bool) and state["player"]["dist"] (float).
"""


def decide(state: dict) -> dict:
    los = state["player"]["los"]
    dist = state["player"]["dist"]
    hp = state["enemy"]["hp"]
    tick = state["tick"]

    # Low health? try to retreat if close
    if hp < 25 and dist < 6:
        return {"action": "retreat", "confidence": 0.8}

    if not los:
        # sweep left/right to reacquire
        direction = "left" if tick % 2 == 0 else "right"
        return {"action": f"strafe_{direction}", "confidence": 0.5}

    if dist > 9:
        # close distance with side-fire
        direction = "left" if tick % 3 else "right"
        return {"action": f"strafe_{direction}_shoot", "confidence": 0.75}

    if dist > 4:
        # mid-range dueling
        direction = "right" if tick % 2 == 0 else "left"
        return {"action": f"strafe_{direction}_shoot", "confidence": 0.85}

    # up close: stop and dump shots
    return {"action": "shoot", "confidence": 0.9}
