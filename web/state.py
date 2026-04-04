from typing import Dict

servo_state: Dict[int, float] = {}


def update_servo(pin: int, angle: float):
    servo_state[pin] = angle


def get_state():
    return servo_state
