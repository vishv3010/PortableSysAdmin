import subprocess

from ui import UI

from ..base import BaseRemediation


class KillProcess(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "LIN-PROCESS-KILL-001",
            "name": "Kill High-Resource or Suspicious Process",
            "platform": "linux",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": False, # Could require admin for root processes, but user processes are fine
            "description": "Lists top CPU/RAM consuming processes and allows you to safely kill one.",
            "rollback_available": False
        }

    def __init__(self, platform_info, logger):
        super().__init__(platform_info, logger)
        self.target_pid = None

    def execute(self, dry_run=False):
        # 1. Show top processes
        try:
            cmd = ["ps", "-eo", "pid,user,%mem,%cpu,cmd", "--sort=-%cpu"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            
            print("\n--- Top Resource Consuming Processes ---")
            for i, line in enumerate(lines[:10]):
                print(f"{line}")
            print("----------------------------------------")
            
            pid_str = UI.prompt("\nEnter the PID of the process to kill (or leave empty to cancel): ")
            if not pid_str.strip() or not pid_str.strip().isdigit():
                return False, "Process kill cancelled or invalid PID entered."
                
            self.target_pid = pid_str.strip()
            
            if dry_run:
                return True, f"Would run: kill -9 {self.target_pid}"
                
            kill_res = self.secure_run(["kill", "-9", self.target_pid], capture_output=True, text=True)
            if kill_res.returncode == 0:
                return True, f"Process {self.target_pid} terminated successfully."
            else:
                return False, f"Failed to terminate {self.target_pid}. You might need Admin/Root privileges."
                
        except Exception as e:
            return False, str(e)

    def verify(self):
        if not self.target_pid:
            return False, "No PID was selected."
        try:
            # Check if PID is still running
            cmd = ["ps", "-p", self.target_pid]
            result = subprocess.run(cmd, capture_output=True, text=True)
            # if output has more than 1 line (header + process), it's still running
            if len(result.stdout.strip().split('\n')) > 1:
                return False, f"Process {self.target_pid} is still running."
            return True, f"Process {self.target_pid} is no longer running."
        except Exception:
            return False, "Verification failed."
