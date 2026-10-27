#!/bin/bash
echo "===================================================="
echo "        PORTABLE SYSADMIN TOOLKIT LAUNCHER"
echo "===================================================="

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
PROJECT_ROOT="$(cd "$(dirname "$SCRIPT_PATH")" >/dev/null 2>&1 && pwd)"
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/app:$PYTHONPATH"

# Check for root, elevate if needed
if [ "$EUID" -ne 0 ]; then
    echo "[INFO] Administrator/root privileges recommended."
    if command -v sudo >/dev/null 2>&1; then
        echo "[INFO] Requesting elevated privileges via sudo..."
        if sudo -v 2>/dev/null; then
            exec sudo bash "$SCRIPT_PATH" "$@"
        fi
        echo "[WARNING] Sudo elevation was declined or unavailable."
        echo "[WARNING] Running with standard user privileges."
        echo "[WARNING] Note: Hardware repairs and system remediation will require root rights."
        echo ""
    fi
fi

# Define cleanup trap to ensure background AI processes are terminated on exit
cleanup() {
    pkill -f llama-server 2>/dev/null || true
    rm -f /tmp/llama-server 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Ensure clean state at startup
cleanup

echo "[INFO] Offline AI ready on-demand (0% CPU background footprint at startup)."


# Check for Python
if [ -x "$PROJECT_ROOT/python_portable_linux/python/bin/python3" ]; then
    echo "[INFO] Using bundled Portable Python for Linux."
    PYTHON_EXE="$PROJECT_ROOT/python_portable_linux/python/bin/python3"
elif [ -x "$PROJECT_ROOT/python_portable_linux/python/bin/python3.11" ]; then
    echo "[INFO] Using bundled Portable Python for Linux."
    PYTHON_EXE="$PROJECT_ROOT/python_portable_linux/python/bin/python3.11"
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
"$PYTHON_EXE" "$PROJECT_ROOT/app/main.py"

# Cleanup AI Server when UI closes
cleanup
echo "[INFO] Goodbye!"
