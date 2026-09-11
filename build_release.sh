#!/bin/bash
TARGET_DIR="${1:-release}"
RELEASE_PATH="$TARGET_DIR/PortableSysAdmin"

echo "Building Portable SysAdmin Toolkit Release into $RELEASE_PATH..."
rm -rf "$RELEASE_PATH"
mkdir -p "$RELEASE_PATH"

# Copy required directories
cp -r app "$RELEASE_PATH/"
cp -r config "$RELEASE_PATH/"
cp -r knowledge "$RELEASE_PATH/"
cp -r models "$RELEASE_PATH/"
cp -r bin "$RELEASE_PATH/" 2>/dev/null || true
cp -r scripts "$RELEASE_PATH/"
cp -r tools "$RELEASE_PATH/" 2>/dev/null || true
cp -r python_portable_linux "$RELEASE_PATH/" 2>/dev/null || true

# Ensure empty logs dir exists
mkdir -p "$RELEASE_PATH/logs"

# Copy root files
cp START.bat "$RELEASE_PATH/"
cp START.sh "$RELEASE_PATH/"
cp README.md "$RELEASE_PATH/"
cp POCKET_REFERENCE.html "$RELEASE_PATH/" 2>/dev/null || true

echo "Downloading Portable Python for Windows (3.11.8)..."
PYTHON_ZIP="python-3.11.8-embed-amd64.zip"
wget -q --show-progress "https://www.python.org/ftp/python/3.11.8/$PYTHON_ZIP" -O /tmp/$PYTHON_ZIP
if [ $? -eq 0 ]; then
    mkdir -p "$RELEASE_PATH/python_portable"
    unzip -q /tmp/$PYTHON_ZIP -d "$RELEASE_PATH/python_portable/"
    rm /tmp/$PYTHON_ZIP
    # Configure python311._pth so embedded python imports from root and app/
    if [ -f "$RELEASE_PATH/python_portable/python311._pth" ]; then
        cat << 'EOF' > "$RELEASE_PATH/python_portable/python311._pth"
python311.zip
.
..
..\app
import site
EOF
    fi
    echo "Portable Python bundled successfully!"
else
    echo "Warning: Failed to download Portable Python."
fi

# Create a STOP script
cat << 'STOP_EOF' > "$RELEASE_PATH/STOP.bat"
@echo off
echo Stopping Portable SysAdmin Toolkit...
taskkill /F /IM llama-server.exe >nul 2>&1
echo Done.
STOP_EOF

cat << 'STOP_EOF' > "$RELEASE_PATH/STOP.sh"
#!/bin/bash
echo "Stopping Portable SysAdmin Toolkit..."
pkill -f llama-server
echo "Done."
STOP_EOF
chmod +x "$RELEASE_PATH/STOP.sh"

# Ensure launcher scripts are executable
chmod +x "$RELEASE_PATH/START.sh"
chmod +x "$RELEASE_PATH/STOP.sh"

echo "Release build complete in $RELEASE_PATH/"
