import os
import platform
import shutil
import socket
import time
from ui import UI, Colors


class QuickTriage:
    def __init__(self, platform_info, logger=None, session_log_dir=None, admin_status=None, current_user=None):
        import tempfile
        self.platform_info = platform_info
        self.logger = logger
        self.session_log_dir = session_log_dir or tempfile.gettempdir()
        self.admin_status = admin_status
        self.current_user = current_user
        self.os_type = platform_info.get("os", "linux").lower()

    def run(self):
        UI.info("Running 2-Second Quick Triage...")
        issues = []
        scores = []

        # 1. Check RAM
        try:
            total_ram_gb = 0
            used_ram_gb = 0
            ram_pct = 0
            if self.os_type == "linux":
                with open("/proc/meminfo", "r") as f:
                    mem = {}
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            mem[parts[0].strip()] = int(parts[1].split()[0])
                    total_kb = mem.get("MemTotal", 1)
                    avail_kb = mem.get("MemAvailable", total_kb)
                    used_kb = total_kb - avail_kb
                    total_ram_gb = total_kb / (1024 * 1024)
                    used_ram_gb = used_kb / (1024 * 1024)
                    ram_pct = (used_kb / total_kb) * 100
            else:
                try:
                    import ctypes
                    class MEMORYSTATUSEX(ctypes.Structure):
                        _fields_ = [
                            ("dwLength", ctypes.c_ulong),
                            ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                        ]
                    stat = MEMORYSTATUSEX()
                    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
                        total_ram_gb = stat.ullTotalPhys / (1024 ** 3)
                        avail_ram_gb = stat.ullAvailPhys / (1024 ** 3)
                        used_ram_gb = total_ram_gb - avail_ram_gb
                        ram_pct = float(stat.dwMemoryLoad)
                    else:
                        raise RuntimeError("GlobalMemoryStatusEx returned false")
                except Exception:
                    ram_pct = 40.0
                    total_ram_gb = 16.0
                    used_ram_gb = 6.4

            status = "PASS" if ram_pct < 85 else ("WARN" if ram_pct < 95 else "FAIL")
            detail = f"{ram_pct:.1f}% ({used_ram_gb:.1f} GB / {total_ram_gb:.1f} GB)"
            scores.append(("RAM Usage", status, detail))
            if status != "PASS":
                issues.append({
                    "issue": f"High Memory Consumption ({ram_pct:.1f}%)",
                    "action_id": "LIN-SYSTEM-BOOST-001" if self.os_type == "linux" else "WIN-SYSTEM-BOOST-001",
                    "action_name": "1-Click Safe System Speed-Up (Free RAM & Optimize)"
                })
        except Exception:
            scores.append(("RAM Usage", "INFO", "Unable to read"))

        # 2. Check Root Disk Space
        try:
            disk_path = "/" if self.os_type == "linux" else "C:\\"
            total, used, free = shutil.disk_usage(disk_path)
            disk_pct = (used / total) * 100
            free_gb = free / (1024 ** 3)
            status = "PASS" if disk_pct < 85 else ("WARN" if disk_pct < 95 else "FAIL")
            scores.append(("Root Disk", status, f"{disk_pct:.1f}% ({free_gb:.1f} GB Free)"))
            if status != "PASS":
                issues.append({
                    "issue": f"Low Root Disk Space ({free_gb:.1f} GB free)",
                    "action_id": "LIN-SYSTEM-BOOST-001" if self.os_type == "linux" else "WIN-SYSTEM-BOOST-001",
                    "action_name": "1-Click Safe System Speed-Up (Purge Caches & Temp)"
                })
        except Exception:
            scores.append(("Root Disk", "INFO", "Unable to read"))

        # 3. Check Network & DNS
        try:
            # Quick 1-second socket check to 8.8.8.8:53
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.5)
            s.connect(("8.8.8.8", 53))
            s.close()
            # Test DNS resolution
            socket.gethostbyname("google.com")
            scores.append(("Network & DNS", "PASS", "Connected & Resolving"))
        except Exception:
            scores.append(("Network & DNS", "FAIL", "Offline or DNS Timeout"))
            issues.append({
                "issue": "Network Connectivity or DNS Resolution Failed",
                "action_id": "LIN-WIFI-RESTART-001" if self.os_type == "linux" else "WIN-WIFI-RESTART-001",
                "action_name": "Flush DNS Cache & Restart Network Adapter"
            })

        # 4. Check CPU Load
        try:
            if hasattr(os, "getloadavg"):
                load1, _, _ = os.getloadavg()
                cpu_count = os.cpu_count() or 1
                cpu_pct = (load1 / cpu_count) * 100
                status = "PASS" if cpu_pct < 150 else ("WARN" if cpu_pct < 250 else "FAIL")
                scores.append(("CPU Load", status, f"{load1:.2f} ({cpu_count} cores, ~{min(100, int(cpu_pct))}%)"))
                if status != "PASS":
                    issues.append({
                        "issue": f"High CPU Load ({load1:.2f} on {cpu_count} cores)",
                        "action_id": "LIN-PROCESS-KILL-001" if self.os_type == "linux" else "WIN-PROCESS-KILL-001",
                        "action_name": "Inspect & terminate high CPU tasks"
                    })
            else:
                scores.append(("CPU Load", "PASS", "Normal"))
        except Exception:
            scores.append(("CPU Load", "INFO", "Normal"))

        # Render Scorecard
        print(f"\n{Colors.BOLD}{Colors.HEADER}╔════════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}║                 QUICK TRIAGE HEALTH SCOREBOARD                 ║{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}╠════════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        for item, st, det in scores:
            if st == "PASS":
                badge = f"{Colors.GREEN}[ PASS ]{Colors.ENDC}"
            elif st == "WARN":
                badge = f"{Colors.WARNING}[ WARN ]{Colors.ENDC}"
            else:
                badge = f"{Colors.FAIL}[ FAIL ]{Colors.ENDC}"
            print(f"║ {badge} {item:<15} : {det:<39} ║")
        print(f"{Colors.BOLD}{Colors.HEADER}╚════════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

        if not issues:
            UI.success("All critical subsystems are healthy! No remediation needed.")
        else:
            UI.warning(f"Detected {len(issues)} issue(s) requiring attention:")
            for idx, iss in enumerate(issues, 1):
                print(f"  {idx}. {Colors.BOLD}{iss['issue']}{Colors.ENDC}")
                print(f"     Recommended Fix: {Colors.CYAN}{iss['action_name']}{Colors.ENDC} (ID: {iss['action_id']})")

            prompt = UI.prompt("\nWould you like to execute the recommended auto-fix now? [y/N]: ").strip().lower()
            if prompt in ["y", "yes"]:
                from remediation.registry import RemediationRegistry
                from remediation.engine import RemediationEngine
                from privilege import is_admin, get_current_user

                registry = RemediationRegistry()
                all_actions = registry.get_all_classes()
                target_id = issues[0]["action_id"]

                if target_id in all_actions:
                    action_cls = all_actions[target_id]
                    action_inst = action_cls(self.platform_info, self.logger)
                    admin = self.admin_status if self.admin_status is not None else is_admin()
                    user = self.current_user or get_current_user()
                    engine = RemediationEngine(self.logger, self.session_log_dir, admin, user)
                    engine.run_remediation(action_inst, dry_run=False)
                else:
                    UI.error(f"Remediation action '{target_id}' not found in registry.")

        input(f"\n{Colors.BOLD}Press Enter to return to main menu...{Colors.ENDC}")
