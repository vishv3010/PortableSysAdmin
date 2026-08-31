#!/bin/bash
echo "===================================================="
echo "        PORTABLE SYSADMIN TOOLKIT LAUNCHER"
echo "===================================================="

# Determine the directory where START.sh is located
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$PROJECT_ROOT"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed or not in PATH."
    exit 1
fi

# Launch the main application
echo "[INFO] Starting Toolkit..."
python3 app/main.py
