#!/bin/bash
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$PROJECT_ROOT"

VERSION="1.0.0"
PACKAGE_NAME="portablesysadmin"
BUILD_DIR="$PROJECT_ROOT/build/deb"
DEB_FILE="${PACKAGE_NAME}_${VERSION}_all.deb"

echo "===================================================="
echo "    BUILDING DEBIAN / UBUNTU PACKAGE (.DEB)         "
echo "===================================================="
echo "[+] Package : $PACKAGE_NAME"
echo "[+] Version : $VERSION"
echo "[+] Target  : $DEB_FILE"

# 1. Clean previous build
rm -rf "$BUILD_DIR" "$DEB_FILE"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/share/$PACKAGE_NAME"
mkdir -p "$BUILD_DIR/usr/share/applications"

# 2. Copy source files (excluding heavy models & cache)
echo "[+] Copying application files..."
cp -r app "$BUILD_DIR/usr/share/$PACKAGE_NAME/"
cp -r config "$BUILD_DIR/usr/share/$PACKAGE_NAME/"
cp -r knowledge "$BUILD_DIR/usr/share/$PACKAGE_NAME/"
cp -r scripts "$BUILD_DIR/usr/share/$PACKAGE_NAME/"
cp POCKET_REFERENCE.html "$BUILD_DIR/usr/share/$PACKAGE_NAME/" 2>/dev/null || true
cp README.md "$BUILD_DIR/usr/share/$PACKAGE_NAME/" 2>/dev/null || true

# Ensure logs directory exists
mkdir -p "$BUILD_DIR/usr/share/$PACKAGE_NAME/logs"
chmod 777 "$BUILD_DIR/usr/share/$PACKAGE_NAME/logs"

# Clean pycache from build
find "$BUILD_DIR" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.pyc" -delete 2>/dev/null || true

# 3. Create CLI Launcher (/usr/bin/portablesysadmin)
echo "[+] Generating CLI binary launcher (/usr/bin/$PACKAGE_NAME)..."
cat << 'EOF' > "$BUILD_DIR/usr/bin/portablesysadmin"
#!/bin/bash
# Portable SysAdmin Toolkit System Launcher
INSTALL_DIR="/usr/share/portablesysadmin"

# Check if run with root, elevate if needed
if [ "$EUID" -ne 0 ]; then
    echo "[INFO] SysAdmin Toolkit requires elevated privileges for full diagnostics and fixes."
    exec sudo "$0" "$@"
fi

cd "$INSTALL_DIR"
exec python3 "$INSTALL_DIR/app/main.py" "$@"
EOF
chmod 755 "$BUILD_DIR/usr/bin/portablesysadmin"

# 4. Create Desktop Entry (App Menu integration)
echo "[+] Generating desktop entry..."
cat << 'EOF' > "$BUILD_DIR/usr/share/applications/portablesysadmin.desktop"
[Desktop Entry]
Name=Portable SysAdmin
Comment=System Diagnostic, Troubleshooting & 1-Click Speed-Up Toolkit
Exec=gnome-terminal -- /usr/bin/portablesysadmin
Terminal=true
Type=Application
Categories=System;Utility;Settings;
Icon=utilities-system-monitor
EOF
chmod 644 "$BUILD_DIR/usr/share/applications/portablesysadmin.desktop"

# 5. Create Debian Control File
echo "[+] Generating DEBIAN/control file..."
cat << EOF > "$BUILD_DIR/DEBIAN/control"
Package: $PACKAGE_NAME
Version: $VERSION
Section: admin
Priority: optional
Architecture: all
Depends: python3 (>= 3.8), procps
Maintainer: Portable SysAdmin Team <admin@company.com>
Description: SysAdmin Troubleshooting, Diagnostics & 1-Click Safe Speed-Up Toolkit
 A portable, enterprise-grade system administration toolkit.
 Includes automated diagnostic checks, 1-click zero-data-loss system speed-up,
 RAM optimizer, network auto-fix, and hardware thermal diagnostics.
EOF

# 6. Build the .deb package
echo "[+] Building package with dpkg-deb..."
dpkg-deb --build "$BUILD_DIR" "$DEB_FILE"

# Clean build directory
rm -rf "$BUILD_DIR"

echo "===================================================="
echo "    BUILD SUCCESSFUL!                               "
echo "===================================================="
echo "Output package: $PROJECT_ROOT/$DEB_FILE"
echo ""
echo "To install on any Ubuntu/Debian laptop, run:"
echo "  sudo apt install ./$DEB_FILE"
echo ""
echo "Once installed, launch it from any terminal by typing:"
echo "  portablesysadmin"
echo ""
echo "To uninstall anytime:"
echo "  sudo apt remove $PACKAGE_NAME"
echo "===================================================="
