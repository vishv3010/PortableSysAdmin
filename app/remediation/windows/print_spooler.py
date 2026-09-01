import subprocess
from ..base import BaseRemediation

class RestartPrintSpooler(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-PRINT-RESTART-001",
            "name": "Restart Print Spooler",
            "platform": "windows",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Restarts the Windows Print Spooler service to clear stuck print jobs.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run PowerShell command: Restart-Service -Name Spooler -Force"
            
        try:
            result = self.secure_run(["powershell", "-Command", "Restart-Service -Name Spooler -Force"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "Print Spooler restarted successfully."
            else:
                return False, f"Failed to restart Print Spooler: {result.stderr}"
        except Exception as e:
            return False, str(e)

    def verify(self):
        try:
            result = self.secure_run(["powershell", "-Command", "(Get-Service -Name Spooler).Status"], capture_output=True, text=True)
            if "Running" in result.stdout:
                return True, "Print Spooler is running."
            return False, "Print Spooler is not running."
        except:
            return False, "Verification check failed."
