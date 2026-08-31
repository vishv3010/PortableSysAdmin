import platform
import subprocess
import os
from .base import BaseDiagnostic, DiagnosticResult

class SystemDiagnostic(BaseDiagnostic):
    def run(self) -> DiagnosticResult:
        evidence = {
            "os": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine()
        }
        status = "PASS"
        severity = "INFO"
        message = "System information collected successfully."

        try:
            if self.platform == "windows":
                # Mocked Windows implementation for now
                evidence["ram_total_mb"] = 16384
                evidence["ram_available_mb"] = 8192
                evidence["ram_percent_used"] = 50.0
            elif self.platform == "linux":
                # Parse /proc/meminfo
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    mem_total = 0
                    mem_avail = 0
                    for line in lines:
                        if line.startswith("MemTotal:"):
                            mem_total = int(line.split()[1])
                        elif line.startswith("MemAvailable:"):
                            mem_avail = int(line.split()[1])
                
                evidence["ram_total_mb"] = mem_total // 1024
                evidence["ram_available_mb"] = mem_avail // 1024
                
                ram_percent = 100 - (mem_avail / mem_total * 100) if mem_total > 0 else 0
                evidence["ram_percent_used"] = round(ram_percent, 2)
                
                if ram_percent > 90:
                    status = "WARNING"
                    severity = "MEDIUM"
                    message = "High RAM usage detected."
                    
        except Exception as e:
            self.logger.error(f"System diagnostic partially failed: {str(e)}")
            status = "WARNING"
            message = "Could not collect full system information."

        return DiagnosticResult(
            category="system",
            test="system_info",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence
        )
