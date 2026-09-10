import subprocess

from ui import UI

from ..base import BaseRemediation


class KillProcess(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-PROCESS-KILL-001",
            "name": "Kill High-Resource or Suspicious Process",
            "platform": "windows",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": False,
            "description": "Lists top CPU/RAM consuming processes and allows you to safely kill one.",
            "rollback_available": False
        }

    def __init__(self, platform_info, logger):
        super().__init__(platform_info, logger)
        self.target_pid = None

    def execute(self, dry_run=False):
        try:
            # 1. Show top processes
            cmd = ["powershell", "-Command", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Id, Name, CPU, WorkingSet"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            print("\n--- Top Resource Consuming Processes ---")
            print(result.stdout.strip())
            print("----------------------------------------")
            
            pid_str = UI.prompt("\nEnter the Id (PID) of the process to kill (or leave empty to cancel): ")
            if not pid_str.strip() or not pid_str.strip().isdigit():
                return False, "Process kill cancelled or invalid PID entered."
                
            self.target_pid = pid_str.strip()
            
            if dry_run:
                return True, f"Would run: taskkill /F /PID {self.target_pid}"
                
            kill_res = self.secure_run(["taskkill", "/F", "/PID", self.target_pid], capture_output=True, text=True)
            if kill_res.returncode == 0:
                return True, f"Process {self.target_pid} terminated successfully."
            else:
                return False, f"Failed to terminate {self.target_pid}. You might need Admin privileges."
                
        except Exception as e:
            return False, str(e)

    def verify(self):
        if not self.target_pid:
            return False, "No PID was selected."
        try:
            cmd = ["tasklist", "/FI", f"PID eq {self.target_pid}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "No tasks are running" in result.stdout or "INFO: " in result.stdout:
                return True, f"Process {self.target_pid} is no longer running."
            return False, f"Process {self.target_pid} is still running."
        except Exception:
            return False, "Verification failed."
