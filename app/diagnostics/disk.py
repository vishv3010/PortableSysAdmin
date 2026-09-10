import os
import shutil

from .base import BaseDiagnostic, DiagnosticResult


class DiskDiagnostic(BaseDiagnostic):
    def run(self) -> DiagnosticResult:
        evidence = {}
        status = "PASS"
        severity = "INFO"
        message = "Disk space is healthy."

        try:
            # Check the root drive based on platform
            path = "C:\\" if self.platform == "windows" else "/"
            
            if os.path.exists(path):
                total, used, free = shutil.disk_usage(path)
                
                total_gb = total // (2**30)
                used_gb = used // (2**30)
                free_gb = free // (2**30)
                
                percent_used = round((used / total) * 100, 2) if total > 0 else 0
                
                evidence = {
                    "path": path,
                    "total_gb": total_gb,
                    "used_gb": used_gb,
                    "free_gb": free_gb,
                    "percent_used": percent_used
                }
                
                if percent_used > 90:
                    status = "FAIL"
                    severity = "HIGH"
                    message = f"Critical! Disk space is over 90% used on {path}."
                elif percent_used > 80:
                    status = "WARNING"
                    severity = "MEDIUM"
                    message = f"Warning: Disk space is over 80% used on {path}."
            else:
                status = "WARNING"
                severity = "MEDIUM"
                message = f"Could not locate root path {path}."

        except Exception as e:
            self.logger.error(f"Disk diagnostic failed: {e!s}")
            status = "WARNING"
            message = "Could not collect disk information."

        return DiagnosticResult(
            category="disk",
            test="disk_usage",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence
        )
