import subprocess
from ..base import BaseRemediation

class FlushDNSLinux(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-DNS-FLUSH-001",
            "name": "Flush DNS Cache (systemd-resolved)",
            "platform": "linux",
            "risk": "SAFE",
            "requires_admin": True,
            "description": "Flushes the local DNS cache using resolvectl.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: resolvectl flush-caches"
        
        try:
            result = subprocess.run(["resolvectl", "flush-caches"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "DNS cache flushed successfully."
            else:
                return False, f"Failed to flush DNS: {result.stderr}"
        except FileNotFoundError:
            return False, "resolvectl command not found on this Linux distribution."
        except Exception as e:
            return False, str(e)

    def verify(self):
        # Verification might be checking statistics
        try:
            result = subprocess.run(["resolvectl", "statistics"], capture_output=True, text=True)
            if "Current Cache Size: 0" in result.stdout or result.returncode == 0:
                return True, "Verification passed (service responded)."
            return False, "Verification failed."
        except:
            return False, "Verification check failed."
