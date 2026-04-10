import json
import select
import socket
import threading
from typing import Dict, Optional

import pigpio

import core.utils as utils


def main(stop_event: Optional[threading.Event] = None):
    HOST: str = "0.0.0.0"

    pi = pigpio.pi()

    if not pi.connected:
        raise RuntimeError("pigpio daemon not running")

    utils.initialize_servos(pi)
    utils.set_servos_to_zero(pi)

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
        while True:
            if stop_event and stop_event.is_set():
                print("Stop signal received")
                break

            readable, _, _ = select.select(list(sockets.keys()), [], [], 0.1)

            for sock in readable:
                data, _ = sock.recvfrom(1024)
                port = sockets[sock]

                try:
                    command: Dict[str, float] = json.loads(data.decode())
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
                    utils.move_servo(pi, pin, value, port)

    finally:
        print("Cleaning up...")

        for port in utils.PORT_SERVO_MAP:
            for pin in utils.PORT_SERVO_MAP[port].values():
                pi.set_servo_pulsewidth(pin, 0)

        pi.stop()

        for sock in sockets:
            sock.close()

        print("Clean exit.")


if __name__ == "__main__":
    main()
