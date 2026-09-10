from ..base import BaseRemediation


class RestartNetworkManager(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-WIFI-RESTART-001",
            "name": "Restart Network Manager",
            "platform": "linux",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Restarts the NetworkManager service in Ubuntu to fix dropped WiFi/Ethernet connections.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: systemctl restart NetworkManager"
            
        try:
            result = self.secure_run(["systemctl", "restart", "NetworkManager"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "NetworkManager restarted successfully."
            else:
                return False, f"Failed to restart NetworkManager: {result.stderr}"
        except Exception as e:
            return False, str(e)

    def verify(self):
        try:
            result = self.secure_run(["systemctl", "is-active", "NetworkManager"], capture_output=True, text=True)
            if "active" in result.stdout:
                return True, "NetworkManager is active."
            return False, "NetworkManager is not active."
        except Exception:
            return False, "Verification check failed."
