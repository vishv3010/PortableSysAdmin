#!/bin/bash
echo "Building Portable SysAdmin Toolkit Release..."
rm -rf release/PortableSysAdmin
mkdir -p release/PortableSysAdmin

# Copy required directories
cp -r app release/PortableSysAdmin/
cp -r config release/PortableSysAdmin/
cp -r knowledge release/PortableSysAdmin/
cp -r models release/PortableSysAdmin/

# Ensure empty logs dir exists
mkdir -p release/PortableSysAdmin/logs

# Copy root files
cp START.bat release/PortableSysAdmin/
cp START.sh release/PortableSysAdmin/
cp README.md release/PortableSysAdmin/

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

echo "Release build complete in release/PortableSysAdmin/"
