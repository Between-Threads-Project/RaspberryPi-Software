#!/bin/bash
set -e

echo "🚀 Starting installation for Between Threads - Raspberry Pi Software"

APP_DIR="$HOME/Desktop/RaspberryPi-Software"
SERVICE_APP="between-threads"
SERVICE_PIGPIO="pigpiod-custom"
USER_NAME=$(whoami)

# ---------------------------
# 1. Clone repository
# ---------------------------
echo "📂 Cloning repository..."
cd ~/Desktop/

if [ -d "RaspberryPi-Software" ]; then
    echo "Existing folder found, removing..."
    rm -rf RaspberryPi-Software
fi

git clone https://github.com/Between-Threads-Project/RaspberryPi-Software
cd "$APP_DIR"

# ---------------------------
# 2. Install uv + dependencies
# ---------------------------
echo "📦 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "🔄 Synchronizing dependencies..."
~/.local/bin/uv sync

# ---------------------------
# 3. Install pigpio
# ---------------------------
echo "💾 Installing pigpio..."
cd ~

if [ ! -d "pigpio-master" ]; then
    wget -O pigpio-master.zip https://github.com/joan2937/pigpio/archive/master.zip
    unzip pigpio-master.zip
    cd pigpio-master
    make
    sudo make install
else
    echo "pigpio already installed, skipping build."
fi

# ---------------------------
# 4. Create pigpiod service
# ---------------------------
echo "⚙️ Creating pigpiod service..."

sudo tee /etc/systemd/system/${SERVICE_PIGPIO}.service > /dev/null <<EOF
[Unit]
Description=Pigpio Daemon
After=network.target

[Service]
ExecStart=/usr/local/bin/pigpiod
Type=forking
PIDFile=/run/pigpio.pid
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ---------------------------
# 5. Create app service
# ---------------------------
echo "⚙️ Creating app service..."

sudo tee /etc/systemd/system/${SERVICE_APP}.service > /dev/null <<EOF
[Unit]
Description=Marionnette Service
After=${SERVICE_PIGPIO}.service
Requires=${SERVICE_PIGPIO}.service

[Service]
User=${USER_NAME}
WorkingDirectory=/home/${USER_NAME}/Desktop/RaspberryPi-Software

ExecStart=/bin/bash -c "uv run main.py"

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# ---------------------------
# 6. Enable + start services
# ---------------------------
echo "🔄 Enabling services..."

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl enable ${SERVICE_PIGPIO}
sudo systemctl enable ${SERVICE_APP}

sudo systemctl start ${SERVICE_PIGPIO}
sleep 2
sudo systemctl start ${SERVICE_APP}

# ---------------------------
# 7. Status
# ---------------------------
echo "📊 Services status:"
sudo systemctl status ${SERVICE_PIGPIO} --no-pager
sudo systemctl status ${SERVICE_APP} --no-pager

# ---------------------------
# 8. Done
# ---------------------------
echo "✅ Installation complete!"
echo "🚀 pigpiod + your app are now running and will start automatically on boot"
