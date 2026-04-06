from typing import Dict

servo_state: Dict[int, float] = {12: 0, 13: 0, 19: 0, 18: 0}
dirty = True


def update_servo(pin: int, angle: float):
    global dirty

    if servo_state.get(pin) != angle:
        servo_state[pin] = angle
        dirty = True


def get_state():
    return servo_state.copy()


def consume_dirty():
    global dirty

    if dirty:
        dirty = False
        return True

    return False
