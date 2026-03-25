import pigpio

# Pulsewidth range for servos (in microseconds)
SERVO_MIN: int = 500
SERVO_MAX: int = 2500

# Servo pin configuration
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
    if port == 5000:
        value = -value + 0.3

    pulse = value_to_pulse(value)
    pi.set_servo_pulsewidth(pin, pulse)


def set_servos_to_neutral(pi):
    """
    Set all servos to 90° (neutral position).
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
