import time

import pigpio
import requests

SERVO_MIN: int = 500
SERVO_MAX: int = 2500

PORT_SERVO_MAP = {
    5000: {
        "index": 12,
        "middle": 18,
    },
    5001: {
        "index": 13,
        "middle": 19,
    },
}

# reverse map: pin -> name
PIN_NAME_MAP = {
    pin: name for port in PORT_SERVO_MAP for name, pin in PORT_SERVO_MAP[port].items()
}

API_URL = "http://localhost:8000/state"
SEND_INTERVAL = 0.1  # seconds

_last_sent = {}
_last_time = 0


def clamp(value: float, vmin: float, vmax: float) -> float:
    """Clamp a value between `vmin` and `vmax`."""
    return max(vmin, min(vmax, value))


def value_to_pulse(value: float) -> int:
    """
    Convert a normalized value (-0.7 to 1) to a servo pulsewidth.
    """
    value = clamp(value, -0.7, 1.0)
    normalized = (value + 0.7) / 1.7
    pulse = SERVO_MIN + normalized * (SERVO_MAX - SERVO_MIN)
    return int(pulse)


def move_servo(pi, pin: int, value: float, port: int) -> None:
    """
    Move a servo connected to a given pin using a normalized value.
    If port is 5001, invert the control.
    """
    global _last_sent, _last_time

    if port == 5000:
        value = -value + 0.3

    pulse = value_to_pulse(value)
    pi.set_servo_pulsewidth(pin, pulse)

    name = PIN_NAME_MAP.get(pin, f"servo_{pin}")
    now = time.time()

    should_send = (name not in _last_sent or abs(_last_sent[name] - value) > 0.01) and (
        now - _last_time > SEND_INTERVAL
    )

    if should_send:
        _last_sent[name] = value
        _last_time = now

        try:
            requests.post(
                API_URL,
                json={
                    "servos": {
                        name: {
                            "value": round(value, 3),
                            "pulse": pulse,
                        }
                    }
                },
                timeout=0.05,
            )
        except Exception:
            pass  # never crash servo loop


def set_servos_to_neutral(pi):
    """
    Set all servos to neutral (≈90°).
    """
    # 0.0 is the neutral position in the normalized range
    for port in PORT_SERVO_MAP:
        for pin in PORT_SERVO_MAP[port].values():
            move_servo(pi, pin, 0.0, port)

    print("All servos set to 90°")


def set_servos_to_zero(pi):
    """
    Set all servos to 0°.
    """
    for port in PORT_SERVO_MAP:
        for pin in PORT_SERVO_MAP[port].values():
            move_servo(pi, pin, -0.7, port)

    print("All servos set to 0°")


def set_servos_to_full(pi):
    """
    Set all servos to 180°.
    """
    for port in PORT_SERVO_MAP:
        for pin in PORT_SERVO_MAP[port].values():
            move_servo(pi, pin, 1.0, port)

    print("All servos set to 180°")


def initialize_servos(pi):
    """
    Initialize all servo pins.
    """
    for port in PORT_SERVO_MAP:
        for pin in PORT_SERVO_MAP[port].values():
            pi.set_mode(pin, pigpio.OUTPUT)

    print("Servos initialized")
