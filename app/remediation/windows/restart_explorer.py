from ..base import BaseRemediation


class RestartExplorer(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-EXPLORER-RESTART-001",
            "name": "Restart Windows Explorer (Unfreeze UI)",
            "platform": "windows",
            "risk": "SAFE",
            "requires_admin": False,
            "description": "Restarts explorer.exe to fix a frozen taskbar or screen without closing your apps or losing data.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: taskkill /f /im explorer.exe and start explorer.exe"
            
        try:
            # Kill explorer
            self.secure_run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, text=True)
            # Start explorer
            self.secure_run(["powershell", "-Command", "Start-Process explorer.exe"], capture_output=True, text=True)
            
            return True, "Windows Explorer restarted successfully. Your apps are safe."
        except Exception as e:
            return False, f"Failed to restart explorer: {e!s}"

    def verify(self):
        try:
            result = self.secure_run(["tasklist", "/fi", "imagename eq explorer.exe"], capture_output=True, text=True)
            if "explorer.exe" in result.stdout:
                return True, "explorer.exe is running."
            return False, "explorer.exe is not running."
        except Exception:
            return False, "Verification check failed."
