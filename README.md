# Between Threads - Raspberry Pi Software

This repository contains the software running on a Raspberry Pi 3 Model B v1.2. It handles UDP data reception and hardware PWM control using `pigpio` for servo motors to actuate the marionette.

## Features

- **UDP Reception**: Listens on configurable ports for JSON commands.
- **High-precision PWM Control**: Uses `pigpio` for stable and accurate servo control.
- **Finger Mapping**: Associates fingers (index, middle) to specific GPIO pins.
- **Web API**: Control scripts and receive real-time updates via WebSocket ([API Documentation](API_DOCUMENTATION.md)).

## Prerequisites

- Raspberry Pi 3 Model B v1.2
- PWM-compatible servo motors (e.g., SG90)
- Python >= 3.10
- `pigpio` daemon

## Installation

Run the install script which will **clone the repo, install dependencies, compile pigpio, and create systemd services** for automatic startup:

```bash
curl -LsSf https://raw.githubusercontent.com/Between-Threads-Project/RaspberryPi-Software/main/install.sh | sh
```

### What the install script does

1. Clones the repository into ~/Desktop/RaspberryPi-Software.
2. Installs the uv dependency manager and syncs Python dependencies.
3. Downloads, compiles, and installs pigpio.
4. Creates two systemd services:
    - pigpiod-custom.service → runs the pigpio daemon automatically at boot.
    -	between-threads.service → runs the main Python script and restarts if it crashes.
5. Enables and starts both services automatically.

> [!NOTE]
> After installation, both services will run automatically on boot. No manual sudo pigpiod is required.

### Check service status

```bash
sudo systemctl status pigpiod-custom
sudo systemctl status between-threads
```

### Restart services

```bash
sudo systemctl restart pigpiod-custom
sudo systemctl restart between-threads
```

### 4. Configure GPIO pins

Default GPIO pin mapping:

- **Port 5000**:
  - Index: GPIO 12
  - Middle: GPIO 18
- **Port 5001**:
  - Index: GPIO 13
  - Middle: GPIO 19

> [!IMPORTANT]
> Servo motors on port 5001 have their rotation inverted. A positive value will rotate them in the opposite direction compared to port 5000.

Modify `PORT_SERVO_MAP` in `utils.py` if needed.

### 5. Run the script

```bash
cd ~/Desktop/RaspberryPi-Software/
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

- Values are mapped from `[-1, 1]` to pulse widths (`500µs → 2500µs`).
- This corresponds roughly to the servo range (~0° to 180°).
- `pigpio` ensures stable PWM signals (no jitter).
- **Port 5001**: Servo rotation is inverted for this port.

## Configuration

### Parameters in `utils.py`

- `HOST`: Listening address (default: `"0.0.0.0"`).
- `PORT_SERVO_MAP`: Maps UDP ports to GPIO pins.
- `SERVO_MIN`: Minimum pulse width (default: `500`).
- `SERVO_MAX`: Maximum pulse width (default: `2500`).

## Troubleshooting

- **`pigpio daemon not running`**: Run `sudo pigpiod`.
- **Servo motors not moving**: Check GPIO connections and power supply (5V).
- **Network issues**: Ensure the UDP port is accessible and the firewall is configured.

## License

MIT License - See [LICENSE.md](LICENSE.md) for details
