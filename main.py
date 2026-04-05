import json
import select
import socket
import threading
from typing import Dict

import pigpio

import utils
from web.ws_server import start_ws_server

# =========================================================
# CONFIG
# =========================================================

HOST: str = "0.0.0.0"

# =========================================================
# PIGPIO SETUP
# =========================================================

pi = pigpio.pi()

if not pi.connected:
    raise RuntimeError("pigpio daemon not running")

utils.initialize_servos(pi)
utils.set_servos_to_zero(pi)

# =========================================================
# SERVO UTILS
# =========================================================


def move_servo(pin: int, value: float, port: int) -> None:
    """
    Move a servo connected to a given pin using a normalized value.
    """
    utils.move_servo(pi, pin, value, port)


# =========================================================
# UDP SETUP
# =========================================================

sockets: Dict[socket.socket, int] = {}

for port in utils.PORT_SERVO_MAP:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, port))

    sockets[sock] = port

print("Listening UDP on ports:", list(utils.PORT_SERVO_MAP.keys()))

# =========================================================
# MAIN LOOP
# =========================================================

try:
    ws_thread = threading.Thread(target=start_ws_server, daemon=True)
    ws_thread.start()

    print("WebSocket server started on port 3000")

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

            servo_map = utils.PORT_SERVO_MAP[port]

            for finger, value in command.items():
                if finger not in servo_map:
                    continue

                try:
                    value = float(value)
                except ValueError:
                    continue

                pin = servo_map[finger]
                move_servo(pin, value, port)

except KeyboardInterrupt:
    print("\nStopping.", end=" ")

finally:
    for port in utils.PORT_SERVO_MAP:
        for pin in utils.PORT_SERVO_MAP[port].values():
            pi.set_servo_pulsewidth(pin, 0)

    pi.stop()

    for sock in sockets:
        sock.close()

    print("Clean exit.")
