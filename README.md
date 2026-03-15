# Marionette Control System - Raspberry Pi Software

This repository contains the software running on a Raspberry Pi 3 Model B v1.2. It handles UDP data reception and PWM control for servo motors to actuate a marionette.

## Features

- **UDP Reception**: Listens on configurable ports for JSON commands.
- **PWM Control**: Converts received values into PWM signals for servo motors.
- **Finger Mapping**: Associates fingers (index, middle) to specific GPIO pins.

## Prerequisites

- Raspberry Pi 3 Model B v1.2
- PWM-compatible servo motors (e.g., SG90)
- Python >=3.13
- `RPi.GPIO` library

## Installation

### 1. Clone the repository

```bash
cd ~
git clone <REPO_URL>
cd RaspberryPi-Software
```

### 2. Install dependencies with uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

### 3. Configure GPIO pins

Default GPIO pin mapping:
- **Port 5000**:
  - Index: GPIO 13
  - Middle: GPIO 12
- **Port 5001**:
  - Index: GPIO 19
  - Middle: GPIO 18

Modify `PORT_SERVO_MAP` in `main.py` if needed.

### 4. Run the script

```bash
uv run main.py
```

## Usage

### Send UDP commands

Expected JSON format: `{"index": 0.5, "middle": -0.3}`
Values range from `-1.0` to `1.0`.

Example using `netcat`:
```bash
echo '{"index": 0.5, "middle": -0.3}' | nc -u -w1 <RASPBERRY_IP> 5000
```

### Servo motor control

- Values are converted to angles (0° to 180°).
- A delay of `SERVO_DELAY` (0.02s) is applied for smooth movements.

## Configuration

### Parameters in `main.py`

- `HOST`: Listening address (default: `"0.0.0.0"`).
- `PORT_SERVO_MAP`: Maps UDP ports to GPIO pins.
- `PWM_FREQ`: PWM frequency (default: 50 Hz).
- `SERVO_DELAY`: Delay between movements (default: 0.02s).

## Troubleshooting

- **`RPi.GPIO` error**: Ensure the script is run with root privileges or the user has GPIO access.
- **Servo motors not moving**: Check GPIO connections and power supply (5V).
- **Network issues**: Ensure the UDP port is accessible and the firewall is configured.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
