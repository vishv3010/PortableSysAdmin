import subprocess

from .base import BaseDiagnostic, DiagnosticResult


class NetworkDiagnostic(BaseDiagnostic):
    def run(self) -> DiagnosticResult:
        evidence = {}
        status = "PASS"
        severity = "INFO"
        message = "Network connectivity is healthy."
        
        try:
            if self.platform == "windows":
                cmd = ["ping", "-n", "2", "8.8.8.8"]
            else:
                cmd = ["ping", "-c", "2", "8.8.8.8"]
                
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            evidence["ping_stdout"] = result.stdout
            
            if result.returncode != 0:
                status = "FAIL"
                severity = "HIGH"
                message = "Internet connectivity (ping 8.8.8.8) failed."
                
        except Exception as e:
            self.logger.error(f"Network ping test failed: {e!s}")
            status = "FAIL"
            severity = "HIGH"
            message = f"Network test threw an error: {e!s}"
            
        return DiagnosticResult(
            category="network",
            test="internet_ping",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence
        )
