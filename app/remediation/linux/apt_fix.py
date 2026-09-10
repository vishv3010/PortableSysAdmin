from ..base import BaseRemediation


class FixBrokenPackages(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-APT-FIX-001",
            "name": "Fix Broken APT Packages",
            "platform": "linux",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Runs 'apt-get install -f' and 'dpkg --configure -a' to fix interrupted installations.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: dpkg --configure -a && apt-get install -f -y"
            
        try:
            # First configure any unpacked but unconfigured packages
            self.secure_run(["dpkg", "--configure", "-a"], capture_output=True, text=True)
            
            # Then attempt to fix broken dependencies
            result = self.secure_run(["apt-get", "install", "-f", "-y"], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, "Broken packages repaired successfully."
            else:
                return False, f"Failed to fix packages: {result.stderr}"
        except FileNotFoundError:
            return False, "apt-get or dpkg command not found."
        except Exception as e:
            return False, str(e)

    def verify(self):
        return True, "Manual verification recommended."
