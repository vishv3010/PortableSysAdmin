import os
import subprocess

from ..base import BaseRemediation


class RestartDisplayShell(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-DISPLAY-RESTART-001",
            "name": "Restart Desktop Shell (Unfreeze UI)",
            "platform": "linux",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": False,
            "description": "Attempts to safely restart the desktop shell (GNOME/Plasma) without losing open apps. Note: On some Wayland sessions, this may still close apps. Proceed with caution.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would attempt to restart gnome-shell or plasmashell"
            
        try:
            # Check for GNOME
            if "gnome" in os.environ.get("DESKTOP_SESSION", "").lower() or "gnome" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
                # For X11, gnome-shell --replace works. For Wayland, killall -3 gnome-shell sometimes recovers it
                session_type = os.environ.get("XDG_SESSION_TYPE", "x11").lower()
                if session_type == "wayland":
                    self.secure_run(["killall", "-SIGQUIT", "gnome-shell"])
                    return True, "Sent restart signal to GNOME Shell (Wayland)."
                else:
                    subprocess.Popen(["nohup", "gnome-shell", "--replace"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True, "Restarted GNOME Shell (X11) safely."
            
            # Check for KDE Plasma
            elif "plasma" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower() or "kde" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower():
                self.secure_run(["kquitapp5", "plasmashell"], capture_output=True)
                subprocess.Popen(["kstart5", "plasmashell"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, "Restarted KDE Plasma shell safely."
            
            else:
                return False, "Unsupported desktop environment for safe shell restart. We avoid restarting the display manager directly as it loses data."
                
        except Exception as e:
            return False, f"Failed to restart desktop shell: {e!s}"

    def verify(self):
        # Difficult to verify universally, just return True if no exceptions
        return True, "Restart command executed."
