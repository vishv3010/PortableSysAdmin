#!/bin/bash
# 1-Line Installer for Portable SysAdmin (Linux / Ubuntu / Debian)
set -e

echo "===================================================="
echo "    PORTABLE SYSADMIN TOOLKIT - LINUX INSTALLER     "
echo "===================================================="

# Require root
if [ "$EUID" -ne 0 ]; then
    echo "[INFO] Elevating to root privileges..."
    exec sudo bash "$0" "$@"
fi

INSTALL_DIR="/usr/share/portablesysadmin"
BIN_LINK="/usr/bin/portablesysadmin"
DESKTOP_FILE="/usr/share/applications/portablesysadmin.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# Ensure Python 3
if ! command -v python3 &>/dev/null; then
    echo "[INFO] Installing Python 3..."
    apt-get update && apt-get install -y python3
fi

echo "[INFO] Installing to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/app" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/config" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/knowledge" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/scripts" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/POCKET_REFERENCE.html" "$INSTALL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

mkdir -p "$INSTALL_DIR/logs"
chmod 777 "$INSTALL_DIR/logs"

# Clean pycache
find "$INSTALL_DIR" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Launcher script
echo "[INFO] Creating global command $BIN_LINK..."
cat << 'EOF' > "$BIN_LINK"
#!/bin/bash
INSTALL_DIR="/usr/share/portablesysadmin"
if [ "$EUID" -ne 0 ]; then
    exec sudo "$0" "$@"
fi
cd "$INSTALL_DIR"
exec python3 "$INSTALL_DIR/app/main.py" "$@"
EOF
chmod 755 "$BIN_LINK"

# Desktop shortcut
cat << 'EOF' > "$DESKTOP_FILE"
[Desktop Entry]
Name=Portable SysAdmin
Comment=System Diagnostic, Troubleshooting & 1-Click Speed-Up Toolkit
Exec=gnome-terminal -- /usr/bin/portablesysadmin
Terminal=true
Type=Application
Categories=System;Utility;Settings;
Icon=utilities-system-monitor
EOF
chmod 644 "$DESKTOP_FILE"

echo "===================================================="
echo "    INSTALLATION COMPLETE!                          "
echo "===================================================="
echo "You can now run the tool from anywhere by typing:"
echo "  portablesysadmin"
echo ""
echo "Or launch it from your Desktop Applications menu."
echo "To uninstall anytime, run: sudo rm -rf $INSTALL_DIR $BIN_LINK $DESKTOP_FILE"
echo "===================================================="
