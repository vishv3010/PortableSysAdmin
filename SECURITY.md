# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Safety Guarantee

PortableSysAdmin is engineered with strict SysAdmin safety controls:
1. **Zero Data Loss Policy:** No user documents, home directories, or active desktop files are ever deleted or modified.
2. **Execution Hardening:** Absolute binary path resolution (`shutil.which`) is enforced to prevent `$PATH` hijacking attacks.
3. **Audit Logging:** Every proposed, dry-run, and executed remediation action is written to `logs/session_*/actions.json`.

## Reporting a Vulnerability

If you discover a security vulnerability or potential unsafe command execution within PortableSysAdmin, please do **NOT** disclose it publicly via GitHub Issues.

Instead, please report it privately to the maintainer:
- **Maintainer:** Vishv Patel ([@vishv3010](https://github.com/vishv3010))
- **Email:** Report via GitHub Security Advisories tab or private profile contact.

We will acknowledge receipt within 48 hours and work with you on a coordinated fix.
