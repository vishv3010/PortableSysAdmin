# Contributing to PortableSysAdmin

First off, thank you for considering contributing to PortableSysAdmin! 🙌

## How Can I Contribute?

### Reporting Bugs
- Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/vishv3010/PortableSysAdmin/issues).
- If you're unable to find an open issue addressing the problem, open a new one using the **Bug report** template.

### Suggesting Enhancements
- Open an issue using the **Feature request** template.
- Explain why this enhancement would be useful to other SysAdmins.

### Adding New Remediation Actions
1. Inherit from `BaseRemediation` in `app/remediation/base.py`.
2. Define `metadata`:
   - `id`: unique ID (e.g. `LIN-DISK-CLEAN-002`)
   - `name`: Human-readable name
   - `platform`: `linux` or `windows`
   - `risk`: `SAFE`, `CONFIRMATION_REQUIRED`, or `DANGEROUS`
   - `requires_admin`: `True` or `False`
3. Implement `execute(self, dry_run=False)` and `verify(self)`.
4. Place the file inside `app/remediation/linux/` or `app/remediation/windows/`.
   *The dynamic `RemediationRegistry` will auto-discover your action without editing core files.*

## Development Setup

```bash
git clone https://github.com/vishv3010/PortableSysAdmin.git
cd PortableSysAdmin

# Run locally on Linux
./START.sh

# Run locally on Windows
START.bat
```

## Pull Request Process

1. Fork the repo and create your branch from `master`.
2. Ensure all Python files compile cleanly: `python3 -m py_compile app/*.py app/*/*.py`.
3. Submit your Pull Request with a clear description of the change.
