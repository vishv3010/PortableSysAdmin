import os
import ctypes
import platform
import getpass

def is_admin():
    """
    Check if the current user has administrator/root privileges.
    """
    sys_name = platform.system().lower()
    if sys_name == "windows":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        # Linux/macOS
        return os.geteuid() == 0

def get_current_user():
    return getpass.getuser()
