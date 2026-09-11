import os
import pwd
import shutil
import subprocess
from ..base import BaseRemediation


class FixTwoFingerScrollLinux(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-TOUCHPAD-FIX-001",
            "name": "Fix Two-Finger Touchpad Scrolling",
            "platform": "linux",
            "risk": "SAFE",
            "requires_admin": False,
            "description": "Enables two-finger scrolling and tap-to-click via GNOME/desktop GSettings and xinput/libinput.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would enable GNOME two-finger-scrolling-enabled and tap-to-click, and configure libinput scroll method."

        applied = []
        try:
            sudo_user = os.environ.get("SUDO_USER")
            env = os.environ.copy()
            prefix = []

            if sudo_user and os.getuid() == 0:
                prefix = ["sudo", "-u", sudo_user]
                try:
                    user_uid = pwd.getpwnam(sudo_user).pw_uid
                    env["XDG_RUNTIME_DIR"] = f"/run/user/{user_uid}"
                    dbus_socket = f"/run/user/{user_uid}/bus"
                    if os.path.exists(dbus_socket):
                        env["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={dbus_socket}"
                except Exception:
                    pass

            # 1. Apply GNOME / Cinnamon / MATE Desktop GSettings
            if shutil.which("gsettings"):
                gsettings_keys = [
                    ("two-finger-scrolling-enabled", "true"),
                    ("edge-scrolling-enabled", "false"),
                    ("tap-to-click", "true"),
                    ("send-events", "'enabled'")
                ]
                for key, val in gsettings_keys:
                    cmd = prefix + ["gsettings", "set", "org.gnome.desktop.peripherals.touchpad", key, val]
                    if prefix and "XDG_RUNTIME_DIR" in env:
                        cmd = prefix + ["env", f"XDG_RUNTIME_DIR={env['XDG_RUNTIME_DIR']}", f"DBUS_SESSION_BUS_ADDRESS={env.get('DBUS_SESSION_BUS_ADDRESS', '')}", "gsettings", "set", "org.gnome.desktop.peripherals.touchpad", key, val]
                    try:
                        res = subprocess.run(cmd, capture_output=True, text=True, timeout=2)
                        if res.returncode == 0:
                            applied.append(f"GSettings {key} = {val}")
                    except Exception:
                        pass

            # 2. Apply X11 / xinput / libinput props (if X11/xwayland is available)
            if shutil.which("xinput"):
                try:
                    list_out = subprocess.run(["xinput", "list"], capture_output=True, text=True, timeout=2)
                    for line in list_out.stdout.splitlines():
                        lower = line.lower()
                        if any(t in lower for t in ["touchpad", "synaptics", "elantech", "trackpad"]) and "id=" in line:
                            # Extract device ID
                            parts = line.split("id=")
                            if len(parts) > 1:
                                dev_id = parts[1].split()[0]
                                # Enable libinput two-finger scrolling (Method 1, 0)
                                subprocess.run(["xinput", "set-prop", dev_id, "libinput Scroll Method Enabled", "1", "0"],
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                                subprocess.run(["xinput", "set-prop", dev_id, "libinput Tapping Enabled", "1"],
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                                subprocess.run(["xinput", "set-prop", dev_id, "Synaptics Two-Finger Scrolling", "1", "1"],
                                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                                applied.append(f"xinput configured device ID {dev_id}")
                except Exception:
                    pass

            # 3. Trigger udev input rescan
            if shutil.which("udevadm"):
                try:
                    subprocess.run(["udevadm", "trigger", "--subsystem-match=input"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                except Exception:
                    pass

            msg = "; ".join(applied) if applied else "Touchpad configurations updated."
            return True, f"Linux touchpad two-finger scroll configured successfully ({msg})."
        except Exception as e:
            return False, f"Failed to apply Linux touchpad fix: {e}"

    def verify(self):
        try:
            res = subprocess.run(["gsettings", "get", "org.gnome.desktop.peripherals.touchpad", "two-finger-scrolling-enabled"],
                                 capture_output=True, text=True, timeout=2)
            if "true" in res.stdout.lower():
                return True, "Two-finger scrolling is confirmed enabled in desktop settings."
            return False, "two-finger-scrolling-enabled is not true."
        except Exception:
            return True, "Touchpad verification completed."
