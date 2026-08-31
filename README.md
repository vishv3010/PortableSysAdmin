# Portable SysAdmin AI & Automation Toolkit

A professional, portable USB-based SysAdmin Diagnostic, Troubleshooting, Remediation, and Local AI Assistant Toolkit.

## Overview
This toolkit is designed to be run from a portable USB drive (or locally during development) to assist system administrators in diagnosing and remediating Windows and Linux machines safely.

## Architecture
- **Orchestration**: Python handles UI, logging, and state.
- **Diagnostics**: Modular Python classes that execute commands and return structured JSON.
- **Safety**: A strict remediation engine classifies actions as SAFE, CONFIRMATION REQUIRED, or DANGEROUS.
- **AI**: (Planned for later phases) A local, offline GGUF model that analyzes JSON diagnostic data to recommend actions without arbitrary command execution.

## Requirements
- Python 3.8+ (Linux/Mac) or bundled portable Python (Windows)
- Works offline by default

## Usage
Run the appropriate launcher for your system:

- **Windows**: `START.bat`
- **Linux**: `./START.sh`

## Safety Model
The system enforces a strict security policy. No destructive commands or unauthorized AI-generated commands are executed. Every action is audited and logged under `logs/`.

## Roadmap
- [x] Phase 1 - Minimum Viable Tool (Diagnostics & UI)
- [ ] Phase 2 - Remediation Engine
- [ ] Phase 3 - Reporting
- [ ] Phase 4 - Knowledge Base
- [ ] Phase 5 - Local AI
- [ ] Phase 6 - AI + Remediation Integration
- [ ] Phase 7 - Portable Release
