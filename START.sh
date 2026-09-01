#!/bin/bash
echo "===================================================="
echo "        PORTABLE SYSADMIN TOOLKIT LAUNCHER"
echo "===================================================="

# Determine the directory where START.sh is located
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$PROJECT_ROOT"

# Start the AI Server in the background if it exists
if [ -f "$PROJECT_ROOT/bin/llama-server" ]; then
    echo "[INFO] Booting offline AI Brain in the background (Optimized for CPU)..."
    "$PROJECT_ROOT/bin/llama-server" -m "$PROJECT_ROOT/models/model.gguf" --port 8080 -t 4 -c 2048 -b 512 > /dev/null 2>&1 &
    SERVER_PID=$!
    # Wait 3 seconds for server to spin up
    sleep 3
else
    echo "[WARNING] Local AI Server not found in bin/. AI analysis will fallback to mocked logic."
fi

# Check for Python
if [ -f "$PROJECT_ROOT/python_portable_linux/python/bin/python3" ]; then
    echo "[INFO] Using bundled Portable Python for Linux."
    PYTHON_EXE="$PROJECT_ROOT/python_portable_linux/python/bin/python3"
elif command -v python3 &>/dev/null; then
    PYTHON_EXE="python3"
elif command -v python &>/dev/null; then
    PYTHON_EXE="python"
else
    echo "[ERROR] Python is not installed or not in PATH, and portable python is missing."
    exit 1
fi

# Launch the main application
echo "[INFO] Starting Toolkit UI..."
"$PYTHON_EXE" app/main.py

# Cleanup AI Server when UI closes
if [ ! -z "$SERVER_PID" ]; then
    echo "[INFO] Shutting down AI Server..."
    kill $SERVER_PID 2>/dev/null
fi
echo "[INFO] Goodbye!"
