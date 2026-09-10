import os
import subprocess

from .base import BaseDiagnostic, DiagnosticResult


class ProcessDiagnostic(BaseDiagnostic):
    def run(self) -> DiagnosticResult:
        status = "PASS"
        severity = "INFO"
        message = "Process resource usage is normal."
        evidence = {}
        high_usage_detected_now = False

        try:
            if self.platform == "linux":
                # Get top 5 processes by memory and CPU
                cmd = ["ps", "-eo", "pid,cmd,%mem,%cpu", "--sort=-%mem"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                top_procs = lines[:6] # header + 5 procs
                evidence["top_memory_processes"] = top_procs
                
                # Check for runaways and suspicious paths
                suspicious = []
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            cmd_path = " ".join(parts[1:-2])
                            mem = float(parts[-2])
                            cpu = float(parts[-1])
                            
                            # High consumption check
                            if mem > 80.0 or cpu > 90.0:
                                high_usage_detected_now = True
                                
                            # Suspicious path check
                            if "/tmp/" in cmd_path or "/dev/shm/" in cmd_path:
                                suspicious.append(line)
                        except Exception: pass
                        
                if suspicious:
                    evidence["suspicious_processes"] = suspicious
                    status = "WARNING"
                    severity = "HIGH"
                    message = f"Found {len(suspicious)} suspicious process(es) running from temporary directories."

            elif self.platform == "windows":
                # Get top processes via PowerShell
                cmd = ["powershell", "-Command", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, CPU, WorkingSet"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                evidence["top_processes"] = result.stdout.strip().split('\n')
                
                # Suspicious check for Windows (e.g. running from Temp)
                cmd_suspicious = ["powershell", "-Command", "Get-WmiObject Win32_Process | Where-Object { $_.Path -match 'AppData\\\\Local\\\\Temp' } | Select-Object Name, Path"]
                result_susp = subprocess.run(cmd_suspicious, capture_output=True, text=True)
                if result_susp.stdout.strip():
                    evidence["suspicious_processes"] = result_susp.stdout.strip().split('\n')
                    status = "WARNING"
                    severity = "HIGH"
                    message = "Found suspicious process(es) running from Temp directory."
                
                if "100" in result.stdout:
                    high_usage_detected_now = True
                    
            if high_usage_detected_now:
                if status == "PASS":
                    status = "WARNING"
                    severity = "MEDIUM"
                    message = "High resource consumption detected in a process right now."
                
                # Check history!
                from .history import DiagnosticHistory
                log_dir = os.path.dirname(self.logger.handlers[0].baseFilename) if self.logger.handlers else ""
                if log_dir:
                    session_dir = os.path.dirname(log_dir)
                    hist = DiagnosticHistory(session_dir)
                    if hist.is_sustained_failure("system", "top_processes", required_count=2):
                        status = "FAIL"
                        severity = "HIGH"
                        message = "SUSTAINED high resource consumption detected over multiple checks. This is a severe issue."
                        
        except Exception as e:
            status = "WARNING"
            message = f"Process check failed: {e}"

        return DiagnosticResult(
            category="system",
            test="top_processes",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence
        )
