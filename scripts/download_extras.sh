#!/bin/bash
echo "===================================================="
echo "    DOWNLOADING EXTRA OFFLINE TOOLS (1GB UPGRADE) "
echo "===================================================="

# 1. Download Sysinternals Suite (Windows)
echo "[INFO] Downloading Microsoft Sysinternals Suite..."
mkdir -p tools/Windows_Sysinternals
wget -q -O /tmp/SysinternalsSuite.zip https://download.sysinternals.com/files/SysinternalsSuite.zip
unzip -q /tmp/SysinternalsSuite.zip -d tools/Windows_Sysinternals/
rm /tmp/SysinternalsSuite.zip
echo "[SUCCESS] Sysinternals Suite installed to tools/"

# 2. Download Portable Linux Python Engine
echo "[INFO] Downloading Portable Python Engine for Linux..."
wget -q --show-progress -O /tmp/cpython-linux.tar.gz https://github.com/indygreg/python-build-standalone/releases/download/20240224/cpython-3.11.8+20240224-x86_64-unknown-linux-gnu-install_only.tar.gz
mkdir -p python_portable_linux
tar -xzf /tmp/cpython-linux.tar.gz -C python_portable_linux/
rm /tmp/cpython-linux.tar.gz
echo "[SUCCESS] Portable Linux Python Engine installed."

# 3. Create a massive simulated Knowledge Base structure
echo "[INFO] Generating Advanced Offline IT Knowledge Base..."
mkdir -p knowledge/networking knowledge/security knowledge/windows_server knowledge/linux_admin

# Generate some dummy large runbooks for the AI
echo "This runbook covers advanced BGP routing, TCP/IP stack resets, and DNS cache flushing. If network fails, run the TCP/IP reset." > knowledge/networking/advanced_routing_runbook.md
echo "This runbook covers Active Directory forest recovery, Kerberos ticket issues, and Print Spooler exploits." > knowledge/windows_server/ad_recovery.md
echo "This runbook covers advanced APT package recovery, dpkg lock removal, and kernel panics." > knowledge/linux_admin/apt_recovery.md

echo "[SUCCESS] All extras downloaded successfully!"
