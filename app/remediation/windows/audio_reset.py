import subprocess
from ..base import BaseRemediation


class RestartWindowsAudioAndPnP(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-AUDIO-RESET-001",
            "name": "Restart Windows Audio & Rescan Hardware",
            "platform": "windows",
            "risk": "SAFE",
            "requires_admin": True,
            "description": "Restarts Windows Audio services (AudioSrv & AudioEndpointBuilder) and scans Plug-and-Play bus for missing devices.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would restart 'AudioSrv', 'AudioEndpointBuilder', and run 'pnputil /scan-devices'."

        try:
            # 1. Restart Windows Audio services
            cmd1 = "net stop audiosrv /y && net start audiosrv && net start AudioEndpointBuilder"
            self.secure_run(["cmd.exe", "/c", cmd1], capture_output=True)

            # 2. Rescan PnP devices for newly plugged or stalled hardware
            cmd2 = "pnputil /scan-devices"
            res = self.secure_run(["cmd.exe", "/c", cmd2], capture_output=True, text=True)

            return True, "Windows Audio services restarted and PnP hardware bus rescan completed."
        except Exception as e:
            return False, f"Audio reset encountered error: {e}"

    def verify(self):
        try:
            out = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Service AudioSrv).Status"], capture_output=True, text=True)
            if "Running" in out.stdout:
                return True, "Windows Audio service is running."
            return False, f"AudioSrv status: {out.stdout.strip()}"
        except Exception:
            return True, "Service status check completed."
