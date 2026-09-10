from ..base import BaseRemediation


class RestartCups(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-PRINT-RESTART-001",
            "name": "Restart Print Service (CUPS)",
            "platform": "linux",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Restarts the CUPS print service to resolve stuck print queues.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: systemctl restart cups"
            
        try:
            result = self.secure_run(["systemctl", "restart", "cups"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "CUPS print service restarted successfully."
            else:
                return False, f"Failed to restart CUPS: {result.stderr}"
        except FileNotFoundError:
            return False, "systemctl command not found."
        except Exception as e:
            return False, str(e)

    def verify(self):
        try:
            result = self.secure_run(["systemctl", "is-active", "cups"], capture_output=True, text=True)
            if "active" in result.stdout:
                return True, "CUPS is active."
            return False, "CUPS is not active."
        except Exception:
            return False, "Verification check failed."
