#!/bin/bash
set -e

echo "🚀 Starting installation for Between Threads - Raspberry Pi Software"

APP_DIR="$HOME/Desktop/RaspberryPi-Software"
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
UV_PATH="$HOME/.local/bin/uv"

echo "📦 Checking if uv is installed..."

if [ -f "$UV_PATH" ]; then
    echo "✅ uv already installed at $UV_PATH"
else
    echo "⬇️ Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "🔄 Synchronizing dependencies..."
"$UV_PATH" sync

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
# 5. Enable + start services
# ---------------------------
echo "🔄 Enabling services..."

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl enable ${SERVICE_PIGPIO}

sudo systemctl start ${SERVICE_PIGPIO}

# ---------------------------
# 6. Status
# ---------------------------
echo "📊 Services status:"
sudo systemctl status ${SERVICE_PIGPIO} --no-pager

# ---------------------------
# 7. Done
# ---------------------------
echo "✅ Installation complete!"
echo "🚀 pigpiod + your app are now running and will start automatically on boot"
