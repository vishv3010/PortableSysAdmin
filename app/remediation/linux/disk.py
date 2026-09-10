from ..base import BaseRemediation


class CleanAptCache(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-DISK-APTCLEAN-001",
            "name": "Clear APT Package Cache",
            "platform": "linux",
            "risk": "SAFE",
            "requires_admin": True,
            "description": "Runs 'apt-get clean' to clear out the local repository of retrieved package files.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: apt-get clean"
            
        try:
            result = self.secure_run(["apt-get", "clean"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "APT cache cleared successfully."
            else:
                return False, f"Failed to clear APT cache: {result.stderr}"
        except FileNotFoundError:
            return False, "apt-get command not found. This remediation only works on Debian/Ubuntu based systems."
        except Exception as e:
            return False, str(e)

    def verify(self):
        return True, "No specific verification needed."
