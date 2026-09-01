import subprocess
from ..base import BaseRemediation

class RestartWiFiAdapter(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-WIFI-RESTART-001",
            "name": "Restart WiFi Adapter",
            "platform": "windows",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Disables and re-enables the Wi-Fi network adapter to resolve connection drops.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run PowerShell commands to Disable and Enable NetAdapter '*Wi-Fi*'"
            
        try:
            # Disable (using wildcard in case it is named "Wi-Fi" or "WiFi")
            self.secure_run(["powershell", "-Command", "Disable-NetAdapter -Name '*Wi-Fi*' -Confirm:$false"], capture_output=True)
            # Enable
            result = self.secure_run(["powershell", "-Command", "Enable-NetAdapter -Name '*Wi-Fi*' -Confirm:$false"], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "WiFi Adapter restarted successfully."
            else:
                return False, f"Failed to restart WiFi Adapter: {result.stderr}"
        except Exception as e:
            return False, str(e)

    def verify(self):
        return True, "Please check if WiFi reconnected."
