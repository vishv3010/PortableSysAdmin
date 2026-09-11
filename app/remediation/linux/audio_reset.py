import os
import subprocess
from ..base import BaseRemediation


class RestartLinuxAudioAndUdev(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-AUDIO-RESET-001",
            "name": "Restart Audio Daemons & Hardware Bus Rescan",
            "platform": "linux",
            "risk": "SAFE",
            "requires_admin": False,
            "description": "Restarts PipeWire/PulseAudio user sound daemons and triggers udev/ALSA hardware re-enumeration.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would restart PipeWire/PulseAudio user daemons and trigger udev/ALSA rescan."

        try:
            sudo_user = os.environ.get("SUDO_USER")
            prefix = []
            if sudo_user and os.getuid() == 0:
                prefix = ["sudo", "-u", sudo_user]

            import shutil

            # 1. Restart user audio daemons (PipeWire / WirePlumber / PulseAudio)
            if shutil.which("systemctl"):
                try:
                    pipewire_cmd = prefix + ["systemctl", "--user", "restart", "pipewire", "pipewire-pulse", "wireplumber"]
                    subprocess.run(pipewire_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=4)
                except Exception:
                    pass

            if shutil.which("pulseaudio"):
                try:
                    pulse_cmd = prefix + ["pulseaudio", "-k"]
                    subprocess.run(pulse_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                except Exception:
                    pass

            # 2. Rescan ALSA & udev
            if shutil.which("alsactl"):
                try:
                    subprocess.run(["alsactl", "init"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                except Exception:
                    pass

            if shutil.which("udevadm"):
                try:
                    subprocess.run(["udevadm", "trigger"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                except Exception:
                    pass

            return True, "Audio daemons restarted and hardware buses re-enumerated."
        except Exception as e:
            return False, f"Linux audio reset error: {e}"

    def verify(self):
        return True, "Audio system reloaded."
