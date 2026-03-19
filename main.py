import json
import select
import socket
from typing import Dict

import pigpio

# =========================================================
# CONFIG
# =========================================================

HOST: str = "0.0.0.0"

PORT_SERVO_MAP: Dict[int, Dict[str, int]] = {
    5000: {
        "index": 12,
        "middle": 18,
    },
    5001: {
        "index": 13,
        "middle": 19,
    },
}

# Pulsewidth range for servos (in microseconds)
SERVO_MIN: int = 500
SERVO_MAX: int = 2500

# =========================================================
# PIGPIO SETUP
# =========================================================

pi = pigpio.pi()

if not pi.connected:
    raise RuntimeError("pigpio daemon not running")

# Initialize all servo pins
for port in PORT_SERVO_MAP:
    for pin in PORT_SERVO_MAP[port].values():
        pi.set_mode(pin, pigpio.OUTPUT)

print("Servos initialized")

# =========================================================
# SERVO UTILS
# =========================================================


def clamp(value: float, vmin: float, vmax: float) -> float:
    """Clamp a value between vmin and vmax."""
    return max(vmin, min(vmax, value))


def value_to_pulse(value: float) -> int:
    """
    Convert a normalized value (-1 to 1) to a servo pulsewidth.
    """
    value = clamp(value, -1.0, 1.0)
    normalized = (value + 1) / 2
    pulse = SERVO_MIN + normalized * (SERVO_MAX - SERVO_MIN)
    return int(pulse)


def move_servo(pin: int, value: float) -> None:
    """
    Move a servo connected to a given pin using a normalized value.
    """
    pulse = value_to_pulse(value)
    pi.set_servo_pulsewidth(pin, pulse)


# =========================================================
# UDP SETUP
# =========================================================

sockets: Dict[socket.socket, int] = {}

for port in PORT_SERVO_MAP:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, port))

    sockets[sock] = port

print("Listening UDP on ports:", list(PORT_SERVO_MAP.keys()))

# =========================================================
# MAIN LOOP
# =========================================================

try:
    while True:
        readable, _, _ = select.select(list(sockets.keys()), [], [])

        for sock in readable:
            data, addr = sock.recvfrom(1024)
            port = sockets[sock]

            try:
                command: Dict[str, float] = json.loads(data.decode())
                print(command)
            except json.JSONDecodeError:
                print("Invalid JSON:", data)
                continue

            servo_map = PORT_SERVO_MAP[port]

            for finger, value in command.items():
                if finger not in servo_map:
                    continue

                try:
                    value = float(value)
                except ValueError:
                    continue

                pin = servo_map[finger]
                move_servo(pin, value)

except KeyboardInterrupt:
    print("\nStopping.", end=" ")

finally:
    # Stop all servos
    for port in PORT_SERVO_MAP:
        for pin in PORT_SERVO_MAP[port].values():
            pi.set_servo_pulsewidth(pin, 0)

    pi.stop()

    # Close all sockets
    for sock in sockets:
        sock.close()

    print("Clean exit.")
