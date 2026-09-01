import subprocess
from .base import BaseDiagnostic, DiagnosticResult

class SecurityDiagnostic(BaseDiagnostic):
    def run(self) -> DiagnosticResult:
        status = "PASS"
        severity = "INFO"
        message = "Firewall is active."
        evidence = {}

        try:
            if self.platform == "linux":
                # Check ufw status
                result = subprocess.run(["ufw", "status"], capture_output=True, text=True)
                evidence["ufw_status"] = result.stdout.strip()
                if "inactive" in result.stdout.lower():
                    status = "WARNING"
                    severity = "HIGH"
                    message = "Linux UFW Firewall is inactive."
                elif result.returncode != 0:
                    status = "WARNING"
                    severity = "MEDIUM"
                    message = "Could not determine UFW Firewall status."
            elif self.platform == "windows":
                # Check windows firewall
                cmd = ["netsh", "advfirewall", "show", "currentprofile"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                evidence["firewall_status"] = result.stdout.strip()
                if "State" in result.stdout and "OFF" in result.stdout.upper():
                    status = "WARNING"
                    severity = "HIGH"
                    message = "Windows Firewall is currently OFF."
        except Exception as e:
            status = "WARNING"
            message = f"Security check failed: {e}"

        return DiagnosticResult(
            category="security",
            test="firewall_status",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence
        )
