import os
import subprocess

from .base import BaseDiagnostic, DiagnosticResult


class ThermalDiagnostic(BaseDiagnostic):
    def run(self) -> DiagnosticResult:
        evidence = {}
        status = "PASS"
        severity = "INFO"
        message = "System temperature is normal."

        try:
            if self.platform == "linux":
                temperatures = []
                # Try to read from sysfs
                thermal_dir = "/sys/class/thermal"
                if os.path.exists(thermal_dir):
                    for zone in os.listdir(thermal_dir):
                        if zone.startswith("thermal_zone"):
                            temp_file = os.path.join(thermal_dir, zone, "temp")
                            type_file = os.path.join(thermal_dir, zone, "type")
                            if os.path.exists(temp_file) and os.path.exists(type_file):
                                with open(type_file, 'r') as f:
                                    zone_type = f.read().strip()
                                with open(temp_file, 'r') as f:
                                    try:
                                        # usually in millidegrees Celsius
                                        temp_c = int(f.read().strip()) / 1000.0
                                        temperatures.append({"zone": zone_type, "temperature_C": temp_c})
                                    except ValueError:
                                        pass
                
                evidence["temperatures"] = temperatures
                
                high_temp_detected = False
                for t in temperatures:
                    if t["temperature_C"] > 85.0:
                        high_temp_detected = True
                        break
                        
                if high_temp_detected:
                    status = "WARNING"
                    severity = "HIGH"
                    message = "High thermal temperature detected! System may be overheating."
                    
            elif self.platform == "windows":
                # WMI can read temperatures but usually requires Administrator
                # MSReport - WmiMonitorThermal
                cmd = ["powershell", "-Command", "Get-WmiObject msacpi_thermalzonetemperature -namespace 'root/wmi' -ErrorAction SilentlyContinue | Select-Object InstanceName, CurrentTemperature"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')[2:] # skip header
                    temperatures = []
                    high_temp_detected = False
                    for line in lines:
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 2:
                                try:
                                    # Temperature is in tenths of degrees Kelvin
                                    temp_k = float(parts[-1]) / 10.0
                                    temp_c = temp_k - 273.15
                                    name = " ".join(parts[:-1])
                                    temperatures.append({"zone": name, "temperature_C": temp_c})
                                    if temp_c > 85.0:
                                        high_temp_detected = True
                                except Exception: pass
                                
                    evidence["temperatures"] = temperatures
                    if high_temp_detected:
                        status = "WARNING"
                        severity = "HIGH"
                        message = "High thermal temperature detected! System may be overheating."
                else:
                    evidence["note"] = "Thermal reading not supported or requires Administrator privileges on this Windows machine."
                    
        except Exception as e:
            self.logger.error(f"Thermal diagnostic failed: {e!s}")
            status = "WARNING"
            message = "Could not collect thermal information."

        return DiagnosticResult(
            category="hardware",
            test="thermal_check",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence
        )
