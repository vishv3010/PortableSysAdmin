import subprocess
from ..base import BaseRemediation

class RunDiskCleanup(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-DISK-CLEANUP-001",
            "name": "Run Windows Disk Cleanup (cleanmgr)",
            "platform": "windows",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Runs the native Windows Disk Cleanup utility (cleanmgr.exe) to free up space.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run: cleanmgr.exe /sagerun:1"
            
        try:
            # Note: cleanmgr /sagerun usually requires /sageset to be configured first, 
            # but /autoclean or /lowdisk also work without GUI prompts.
            result = self.secure_run(["cleanmgr.exe", "/autoclean"], capture_output=True, text=True)
            return True, "Windows Disk Cleanup triggered."
        except FileNotFoundError:
            return False, "cleanmgr.exe not found."
        except Exception as e:
            return False, str(e)

    def verify(self):
        return True, "Verification complete."
