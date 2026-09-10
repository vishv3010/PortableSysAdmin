# Portable SysAdmin AI & System Optimization Toolkit

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)]()
[![Safety](https://img.shields.io/badge/Safety-100%25%20Zero%20Data%20Loss-success.svg)]()

A professional, portable SysAdmin Diagnostic, Troubleshooting, Remediation, 1-Click Safe Speed-Up, and Local AI Assistant Toolkit. Engineered for system administrators, IT support technicians, and power users on both **Linux** and **Windows**.

---

## ⚡ 1-Line Quick Installation (Install Anywhere in 3 Seconds)

Install and run on any machine instantly without cloning or manual configuration:

### 🐧 Linux (Ubuntu / Debian / Mint / Pop!_OS)
Open any terminal and run:
```bash
curl -sSL https://raw.githubusercontent.com/vishv3010/PortableSysAdmin/master/install.sh | sudo bash
```

### 🪟 Windows (10 / 11 / Server)
Open PowerShell as Administrator and run:
```powershell
irm https://raw.githubusercontent.com/vishv3010/PortableSysAdmin/master/install.ps1 | iex
```

*Once installed, simply type **`portablesysadmin`** in any terminal/CMD, or click the desktop shortcut!*

---

## 💾 Portable USB Usage (Zero-Install Mode)

You can also run directly from any USB flash drive without installing:

* **Linux:**
  ```bash
  chmod +x START.sh
  ./START.sh
  ```
* **Windows:** Double-click **`START.bat`** (or Run as Administrator).

---

## 📦 Debian / Ubuntu Package (`.deb`)

To install using standard `apt`:
```bash
# Build the package (or grab portablesysadmin_1.0.0_all.deb from Releases)
./build_deb.sh

# Install with apt
sudo apt install ./portablesysadmin_1.0.0_all.deb
```

---

## 🌟 Key Features

### 1. 🚀 1-Click Safe System Speed-Up & RAM Optimizer
* **100% Zero Data Loss Guarantee:** Never terminates user apps (Word, Excel, Chrome, Teams, code editors) and never touches personal files.
* **Flushes dirty buffers (`sync`)** before dropping clean pagecache and dentries to instantly free gigabytes of RAM.
* **Defragments memory pools** (`compact_memory`) for snappy application allocations.
* **Vacuums bloated system logs** (`journalctl --vacuum-size=100M`) and purges package installer caches.
* **Unthrottles CPU frequency** by switching stuck `powersave` governors to `performance`.
* **Displays real-time Before & After scorecard** showing exact RAM freed, disk space recovered, and temperature changes.

### 2. 🩺 2-Second Quick Triage & Auto-Doctor
* Rapidly inspects RAM utilization, Root Disk headroom, CPU Load average, and DNS connectivity.
* Identifies bottlenecks and provides a 1-click prompt to execute automated remediation.

### 3. 🌡️ Thermal & "Ghost CPU" Diagnostics
* Diagnoses the **Thermal PROCHOT Illusion** where laptops appear stuck at 100% CPU with no active process because heat throttled the CPU clock down to 0.79 GHz.
* Reads live hardware core temperatures across all thermal zones.
* Identifies and stops memory thrashing that causes continuous SSD and bus heat generation.

### 4. 🛡️ Enterprise Remediation Engine
* Safe, audited auto-fixes categorized by strict risk policies (`SAFE`, `CONFIRMATION_REQUIRED`, `DANGEROUS`).
* Full **Dry-Run mode** to inspect proposed command executions before running.
* Handles process kills, network resets, Wi-Fi driver restarts, display shell recovery, and package manager repairs.

### 5. 📊 Enterprise HTML Reports & Online AI Prompt
* Generates interactive, standalone HTML diagnostic health reports.
* Includes a 1-click **Copy AI Prompt** button designed to paste full diagnostic briefs directly into ChatGPT or Claude with 0% CPU consumption.

### 6. 🤖 Offline Local AI Assistant
* On-demand, private, offline GGUF local model integration via `llama.cpp` for secure environments with zero internet access.

### 7. 📖 Offline SysAdmin Pocket Reference
* Embedded offline searchable cheatsheet containing vital CLI commands for networking, disk management, process inspection, and system rescue.

---

## 🛡️ Enterprise Safety & Audit Model

Every remediation action and speed-up execution is recorded in an immutable audit trail (`logs/session_<id>/actions.json`), including:
* ISO-8601 UTC timestamp
* User and privilege status
* Pre- and post-optimization telemetry
* Verification outputs

---

## 📋 Requirements
* **Python 3.8+** (Standard library only; zero external pip dependencies required).
* **Linux:** Ubuntu, Debian, Linux Mint, or derivatives.
* **Windows:** Windows 10, Windows 11, or Windows Server.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE) — free for personal, enterprise, and educational use by anyone in the world.
