#!/bin/bash
set -e

echo "🚀 Starting installation for Between Threads - Raspberry Pi Software"

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
cd RaspberryPi-Software

# ---------------------------
# 2. Install dependencies with uv
# ---------------------------
echo "📦 Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "🔄 Synchronizing dependencies..."
~/.local/bin/uv sync

# ---------------------------
# 3. Install pigpio (from source)
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
echo "⚡ Creating pigpiod service..."

sudo tee /etc/systemd/system/pigpiod.service > /dev/null <<EOL
[Unit]
Description=Pigpio Daemon
After=network.target

[Service]
User=root
ExecStartPre=/bin/bash -c 'killall pigpiod || true'
ExecStart=/usr/local/bin/pigpiod -l
Type=simple
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOL

# ---------------------------
# 5. Create app service
# ---------------------------
echo "⚙️ Creating app service..."

sudo tee /etc/systemd/system/between-threads.service > /dev/null <<EOL
[Unit]
Description=Between Threads Service
After=network.target pigpiod.service
Requires=pigpiod.service

[Service]
User=$USER
WorkingDirectory=/home/$USER/Desktop/RaspberryPi-Software
ExecStart=/bin/bash -c 'cd /home/$USER/Desktop/RaspberryPi-Software && /home/$USER/.local/bin/uv run main.py'
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# ---------------------------
# 6. Enable services
# ---------------------------
echo "🚀 Enabling services..."

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl enable pigpiod
sudo systemctl start pigpiod

sudo systemctl enable between-threads.service
sudo systemctl start between-threads.service

# ---------------------------
# 7. Done
# ---------------------------
echo "✅ Installation complete!"
echo "Your app + pigpio will now run automatically on boot 🚀"
