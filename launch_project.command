#!/bin/bash

# Navigate to the exact folder where this command script lives
cd "$(dirname "$0")"

echo "🚀 CO-FOUNDER MEMORY SYSTEM IGNITION"
echo "=========================================="

# 1. Activate your Python Virtual Environment if you have one (Optional)
# source .venv/bin/activate

# 2. Boot the Smart Midnight Loop Daemon in a background terminal process
echo "🌙 Spinning up Midnight Daemon Watcher..."
python3 scripts/run_midnight_loop.py &

# 3. Boot your Live Chat Interactive Console immediately in the foreground
echo "💬 Opening Interactive Manual Terminal Chat..."
python3 run_manual.py

# Keep window open if the live chat exits cleanly
bash