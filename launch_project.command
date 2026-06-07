#!/bin/bash

# 1. Navigate to the exact project folder securely
cd "$(dirname "$0")" || exit

echo "🚀 CO-FOUNDER MEMORY SYSTEM IGNITION"
echo "=========================================="

# 2. Force the Mac to use your specific project environment
source .venv/bin/activate

# 3. Lock the Python path to the root folder so 'scripts' can find 'graph'
export PYTHONPATH="$(pwd)"

# 4. Boot the Smart Midnight Loop Daemon in the background
echo "🌙 Spinning up Midnight Daemon Watcher..."
python scripts/run_midnight_loop.py &

# 5. Boot your Live Chat Interactive Console in the foreground
echo "💬 Opening Interactive Manual Terminal Chat..."
python run_manual.py

# 6. Keep the window open cleanly using Mac's native zsh shell
zsh