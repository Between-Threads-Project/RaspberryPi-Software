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

#--------------------------
# 4. Launch pigpio daemon
# -------------------------
sudo pigpiod

# ---------------------------
# 5. Done
# ---------------------------
echo "✅ Installation complete!"
echo "Your app + pigpio will now run automatically on boot 🚀"
