import subprocess
from ..base import BaseRemediation

class ResetNetworkStack(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-NET-RESET-001",
            "name": "Reset TCP/IP Network Stack",
            "platform": "windows",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Resets the TCP/IP stack (netsh int ip reset) and Winsock to fix deep network corruption.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: netsh int ip reset && netsh winsock reset"
            
        try:
            # Reset TCP/IP
            self.secure_run(["netsh", "int", "ip", "reset"], capture_output=True, text=True)
            # Reset Winsock
            result = self.secure_run(["netsh", "winsock", "reset"], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "TCP/IP and Winsock stack reset. A reboot may be required."
            else:
                return False, f"Failed to reset network stack: {result.stderr}"
        except Exception as e:
            return False, str(e)

    def verify(self):
        return True, "Reboot recommended to complete verification."
