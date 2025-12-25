# Maps brain actions to engine controls (stubbed for MVP)
VALID = {
    "idle": {},
    "shoot": {"ATTACK": 1},
    "shoot_fireball": {"ATTACK": 1},   # placeholder for imp
    "strafe_left": {"MOVE_LEFT": 1},
    "strafe_right": {"MOVE_RIGHT": 1},
    "charge_forward": {"MOVE_FORWARD": 1},
    "retreat": {"MOVE_BACKWARD": 1},
    "turn_left": {"TURN_LEFT": 1},
    "turn_right": {"TURN_RIGHT": 1},
    "use": {"USE": 1},
    "sprint": {"SPEED": 1},
    "strafe_left_shoot": {"MOVE_LEFT":1, "ATTACK":1},
    "strafe_right_shoot": {"MOVE_RIGHT":1, "ATTACK":1},
}

def to_controls(action_name: str):
    return VALID.get(action_name, {})
