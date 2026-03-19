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
uv sync

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
    sudo apt install -y python-setuptools python3-setuptools
else
    echo "pigpio already installed, skipping."
    cd pigpio-master
fi

# ---------------------------
# 4. Start pigpio daemon
# ---------------------------
echo "⚡ Starting pigpio daemon..."
sudo pigpiod

# ---------------------------
# 5. Done
# ---------------------------
echo "✅ Installation complete!"
echo "Move to the folder with : cd ~/Desktop/RaspberryPi-Software/"
echo "Run your script with: uv run main.py"
