"""
Pinkie demon: flanks until it's close, then commits to a charge.
Will occasionally retreat if badly hurt mid-charge.
"""


def decide(state: dict) -> dict:
    dist = state["player"]["dist"]
    los = state["player"]["los"]
    hp = state["enemy"]["hp"]
    tick = state["tick"]

    if hp < 20 and dist < 3:
        return {"action": "retreat", "confidence": 0.7}

    if not los and dist > 5:
        direction = "left" if (tick // 10) % 2 == 0 else "right"
        return {"action": f"strafe_{direction}", "confidence": 0.5}

    if dist > 6:
        # close distance with a flank bias
        direction = "left" if tick % 2 == 0 else "right"
        return {"action": f"strafe_{direction}", "confidence": 0.6}

    # in striking range
    return {"action": "charge_forward", "confidence": 0.95}
