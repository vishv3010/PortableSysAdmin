# Changelog

All notable changes to the **PortableSysAdmin** project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-10

### Added
- **1-Click Safe System Speed-Up & RAM Optimizer (`SafeSystemSpeedUp`)**:
  - Drops clean kernel memory pagecaches safely after running `sync` to eliminate data loss risk.
  - Defragments free memory pools (`compact_memory`).
  - Vacuums bloated `systemd-journald` logs down to 100MB to stop I/O thrashing.
  - Clears package installer archives (`apt-get clean`, `dnf clean`).
  - Purges stale temporary files (>24h) and user thumbnail caches.
  - Windows standby memory trimming and PowerShell garbage collection.
  - Flushes DNS resolver caches (`resolvectl`, `ipconfig`).
  - Unthrottles CPU clock frequency from battery `powersave` to `performance`.
- **Thermal & "Ghost CPU" Diagnostics (`ThermalDiagnostic`)**:
  - Live hardware temperature reading across all thermal zones.
  - Diagnosis and recovery for PROCHOT downclocking lockups (0.79 GHz CPU throttles).
- **Universal 1-Line Installers**:
  - `install.sh` for Linux (`curl -sSL ... | sudo bash`).
  - `install.ps1` for Windows (`irm ... | iex`).
- **Debian Packaging Tooling (`build_deb.sh`)**:
  - Builds clean, standalone `portablesysadmin_*.deb` packages for `sudo apt install`.
- **GitHub Actions CI Pipeline**:
  - Cross-platform automated compilation and smoke test runner for Linux and Windows.
- **MIT License**: Open-source license for global public use.
