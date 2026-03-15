import json
import select
import socket
import time

import RPi.GPIO as GPIO

# =========================================================
# CONFIG
# =========================================================

HOST = "0.0.0.0"

PORT_SERVO_MAP = {
    5000: {
        "index": 13,
        "middle": 12,
    },
    5001: {
        "index": 19,
        "middle": 18,
    },
}

PWM_FREQ = 50
SERVO_DELAY = 0.02


# =========================================================
# GPIO SETUP
# =========================================================

GPIO.setmode(GPIO.BCM)

PWM = {}

for port in PORT_SERVO_MAP:
    for pin in PORT_SERVO_MAP[port].values():
        GPIO.setup(pin, GPIO.OUT)

        pwm = GPIO.PWM(pin, PWM_FREQ)
        pwm.start(0)

        PWM[pin] = pwm


# =========================================================
# SERVO UTILS
# =========================================================


def clamp(v, vmin, vmax):
    return max(vmin, min(vmax, v))


def value_to_angle(value):
    """
    Map -1 → 1 to 0° → 180°
    """
    value = clamp(value, -1.0, 1.0)
    return (value + 1) * 90


def angle_to_duty(angle):
    return 2 + (angle / 18)


def move_servo(pin, value):

    angle = value_to_angle(value)
    duty = angle_to_duty(angle)

    pwm = PWM[pin]

    pwm.ChangeDutyCycle(duty)
    time.sleep(SERVO_DELAY)
    pwm.ChangeDutyCycle(0)


# =========================================================
# UDP SETUP
# =========================================================

sockets = {}

for port in PORT_SERVO_MAP:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, port))

    sockets[sock] = port

print("Listening on:", list(PORT_SERVO_MAP.keys()))


# =========================================================
# MAIN LOOP
# =========================================================

try:
    while True:
        readable, _, _ = select.select(sockets.keys(), [], [])

        for sock in readable:
            data, addr = sock.recvfrom(1024)
            port = sockets[sock]

            try:
                command = json.loads(data.decode())
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
    print("Stopping...")


finally:
    for pwm in PWM.values():
        pwm.stop()

    GPIO.cleanup()

    for sock in sockets:
        sock.close()

    print("GPIO cleaned")
