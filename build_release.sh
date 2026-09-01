#!/bin/bash
echo "Building Portable SysAdmin Toolkit Release..."
rm -rf release/PortableSysAdmin
mkdir -p release/PortableSysAdmin

# Copy required directories
cp -r app release/PortableSysAdmin/
cp -r config release/PortableSysAdmin/
cp -r knowledge release/PortableSysAdmin/
cp -r models release/PortableSysAdmin/
cp -r bin release/PortableSysAdmin/ 2>/dev/null || true
cp -r scripts release/PortableSysAdmin/
cp -r tools release/PortableSysAdmin/ 2>/dev/null || true
cp -r python_portable_linux release/PortableSysAdmin/ 2>/dev/null || true

# Ensure empty logs dir exists
mkdir -p release/PortableSysAdmin/logs

# Copy root files
cp START.bat release/PortableSysAdmin/
cp START.sh release/PortableSysAdmin/
cp README.md release/PortableSysAdmin/

echo "Downloading Portable Python for Windows (3.11.8)..."
PYTHON_ZIP="python-3.11.8-embed-amd64.zip"
wget -q --show-progress "https://www.python.org/ftp/python/3.11.8/$PYTHON_ZIP" -O /tmp/$PYTHON_ZIP
if [ $? -eq 0 ]; then
    mkdir -p release/PortableSysAdmin/python_portable
    unzip -q /tmp/$PYTHON_ZIP -d release/PortableSysAdmin/python_portable/
    rm /tmp/$PYTHON_ZIP
    echo "Portable Python bundled successfully!"
else
    echo "Warning: Failed to download Portable Python."
fi

# Create a STOP script
cat << 'STOP_EOF' > release/PortableSysAdmin/STOP.bat
@echo off
echo Stopping Portable SysAdmin Toolkit...
taskkill /F /IM llama-server.exe >nul 2>&1
echo Done.
STOP_EOF

cat << 'STOP_EOF' > release/PortableSysAdmin/STOP.sh
#!/bin/bash
echo "Stopping Portable SysAdmin Toolkit..."
pkill -f llama-server
echo "Done."
STOP_EOF
chmod +x release/PortableSysAdmin/STOP.sh

# Ensure launcher scripts are executable
chmod +x release/PortableSysAdmin/START.sh
chmod +x release/PortableSysAdmin/STOP.sh

echo "Release build complete in release/PortableSysAdmin/"
