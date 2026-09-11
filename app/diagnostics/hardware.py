import json
import os
import subprocess
from .base import BaseDiagnostic, DiagnosticResult


class HardwareDiagnostic(BaseDiagnostic):
    """
    Automated cross-platform audit of system peripherals & components:
      - Audio Sound Cards / DACs
      - Battery Health, Capacity & Cycle Counts
      - Input Devices (Keyboards, Mice, Touchpads)
      - USB Devices & Cameras
    """

    def run(self) -> DiagnosticResult:
        evidence = {
            "audio": self._check_audio(),
            "battery": self._check_battery(),
            "input_devices": self._check_input_devices(),
            "usb_devices": self._check_usb_devices()
        }

        status = "PASS"
        severity = "INFO"
        recommendations = []
        summary_parts = []

        # 1. Evaluate Audio
        audio_info = evidence["audio"]
        if not audio_info.get("detected", False):
            status = "WARNING"
            severity = "MEDIUM"
            recommendations.append("No active sound card detected. Verify audio drivers or hardware connections.")
            summary_parts.append("No audio device")
        else:
            count = len(audio_info.get("devices", []))
            summary_parts.append(f"{count} audio device(s)")

        # 2. Evaluate Battery
        battery_info = evidence["battery"]
        if battery_info.get("present", False):
            wear = battery_info.get("wear_percent", 0.0)
            charge = battery_info.get("charge_percent", 100)
            p_status = battery_info.get("status", "Unknown")

            if wear > 40.0:
                if status != "FAIL":
                    status = "WARNING"
                if severity in ["INFO", "LOW"]:
                    severity = "MEDIUM"
                recommendations.append(f"Battery is significantly degraded ({wear}% wear). Consider battery replacement soon.")

            if p_status.lower() == "discharging" and charge < 15:
                status = "WARNING"
                severity = "HIGH"
                recommendations.append("Battery is critically low (<15%). Connect AC power immediately.")

            summary_parts.append(f"Battery {charge}% ({p_status}, {100.0 - wear:.1f}% health)")
        elif battery_info.get("ac_powered", False):
            summary_parts.append("Desktop/AC power")
        else:
            summary_parts.append("Power: OK")

        # 3. Evaluate Input Devices
        input_info = evidence["input_devices"]
        kb_count = input_info.get("keyboards", 0)
        pointer_count = input_info.get("pointers", 0)
        if kb_count == 0 and pointer_count == 0 and not evidence["usb_devices"].get("devices", []):
            if status != "FAIL":
                status = "WARNING"
            recommendations.append("No keyboards or pointing devices detected in system hardware registry.")
        else:
            summary_parts.append(f"{kb_count} keyboard(s), {pointer_count} pointer(s)")

        message = "Hardware audit: " + ", ".join(summary_parts) + "."

        return DiagnosticResult(
            category="hardware",
            test="hardware_audit",
            status=status,
            severity=severity,
            message=message,
            evidence=evidence,
            recommended_actions=recommendations
        )

    def _check_audio(self) -> dict:
        result = {"detected": False, "devices": []}
        try:
            if self.platform == "linux":
                cards_file = "/proc/asound/cards"
                if os.path.exists(cards_file):
                    with open(cards_file, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line and line[0].isdigit():
                                parts = line.split(":", 1)
                                desc = parts[1].strip() if len(parts) > 1 else line
                                result["devices"].append(desc)
                    if result["devices"]:
                        result["detected"] = True

                if not result["devices"]:
                    out = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=2)
                    if out.returncode == 0:
                        for line in out.stdout.splitlines():
                            if line.startswith("card "):
                                result["devices"].append(line.strip())
                                result["detected"] = True

            elif self.platform == "windows":
                ps_cmd = 'Get-CimInstance Win32_SoundDevice | Select-Object -Property Name, Status, Manufacturer | ConvertTo-Json -Compress'
                out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=4)
                if out.returncode == 0 and out.stdout.strip():
                    try:
                        data = json.loads(out.stdout)
                        if isinstance(data, dict):
                            data = [data]
                        for d in data:
                            name = d.get("Name", "Unknown Audio")
                            result["devices"].append(f"{name} ({d.get('Status', 'OK')})")
                        result["detected"] = len(result["devices"]) > 0
                    except Exception:
                        pass
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Audio diagnostic error: {e}")
        return result

    def _check_battery(self) -> dict:
        result = {
            "present": False,
            "charge_percent": 0,
            "status": "Unknown",
            "wear_percent": 0.0,
            "cycle_count": None,
            "ac_powered": False
        }

        try:
            if self.platform == "linux":
                base_ps = "/sys/class/power_supply"
                if os.path.exists(base_ps):
                    # Check AC adapter
                    for item in os.listdir(base_ps):
                        if item.startswith(("AC", "ADP", "Mains")):
                            online_f = os.path.join(base_ps, item, "online")
                            if os.path.exists(online_f):
                                with open(online_f, "r") as f:
                                    result["ac_powered"] = (f.read().strip() == "1")

                    # Check Batteries
                    for item in os.listdir(base_ps):
                        if item.startswith("BAT"):
                            bdir = os.path.join(base_ps, item)
                            result["present"] = True

                            # Capacity
                            cap_f = os.path.join(bdir, "capacity")
                            if os.path.exists(cap_f):
                                with open(cap_f, "r") as f:
                                    result["charge_percent"] = int(f.read().strip())

                            # Status
                            stat_f = os.path.join(bdir, "status")
                            if os.path.exists(stat_f):
                                with open(stat_f, "r") as f:
                                    result["status"] = f.read().strip()

                            # Wear calculation (energy or charge)
                            full = 0
                            design = 0
                            for prefix in ["energy", "charge"]:
                                full_f = os.path.join(bdir, f"{prefix}_full")
                                des_f = os.path.join(bdir, f"{prefix}_full_design")
                                if os.path.exists(full_f) and os.path.exists(des_f):
                                    with open(full_f, "r") as f:
                                        full = int(f.read().strip() or 0)
                                    with open(des_f, "r") as f:
                                        design = int(f.read().strip() or 0)
                                    break

                            if design > 0 and full > 0:
                                wear = (1.0 - (full / design)) * 100.0
                                result["wear_percent"] = max(0.0, round(wear, 1))

                            # Cycle count
                            cyc_f = os.path.join(bdir, "cycle_count")
                            if os.path.exists(cyc_f):
                                with open(cyc_f, "r") as f:
                                    val = f.read().strip()
                                    if val.isdigit():
                                        result["cycle_count"] = int(val)
                            break

            elif self.platform == "windows":
                ps_cmd = 'Get-CimInstance Win32_Battery | Select-Object -Property EstimatedChargeRemaining, BatteryStatus, DesignCapacity, FullChargeCapacity | ConvertTo-Json -Compress'
                out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=4)
                if out.returncode == 0 and out.stdout.strip():
                    try:
                        data = json.loads(out.stdout)
                        if isinstance(data, list):
                            data = data[0] if data else {}
                        if data and data.get("EstimatedChargeRemaining") is not None:
                            result["present"] = True
                            result["charge_percent"] = data.get("EstimatedChargeRemaining", 0)
                            status_code = data.get("BatteryStatus", 1)
                            # Status mapping: 1=Discharging, 2=AC/Unknown, 3=Fully Charged, 6-9=Charging
                            status_map = {1: "Discharging", 2: "AC Power", 3: "Full", 6: "Charging", 7: "Charging", 8: "Charging"}
                            result["status"] = status_map.get(status_code, "Normal")
                            result["ac_powered"] = status_code != 1

                            design = data.get("DesignCapacity", 0) or 0
                            full = data.get("FullChargeCapacity", 0) or 0
                            if design > 0 and full > 0:
                                wear = (1.0 - (full / design)) * 100.0
                                result["wear_percent"] = max(0.0, round(wear, 1))
                    except Exception:
                        pass
                if not result["present"]:
                    result["ac_powered"] = True
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Battery diagnostic error: {e}")
        return result

    def _check_input_devices(self) -> dict:
        result = {"keyboards": 0, "pointers": 0, "device_names": []}
        try:
            if self.platform == "linux":
                devs_file = "/proc/bus/input/devices"
                if os.path.exists(devs_file):
                    with open(devs_file, "r") as f:
                        current_name = None
                        for line in f:
                            line = line.strip()
                            if line.startswith("N: Name="):
                                current_name = line.split("=", 1)[1].strip('"')
                            elif line.startswith("H: Handlers="):
                                handlers = line.split("=", 1)[1].split()
                                if "kbd" in handlers:
                                    result["keyboards"] += 1
                                    if current_name and current_name not in result["device_names"]:
                                        result["device_names"].append(f"[Keyboard] {current_name}")
                                if any(h.startswith("mouse") for h in handlers) or "touchpad" in (current_name or "").lower():
                                    result["pointers"] += 1
                                    if current_name and current_name not in result["device_names"]:
                                        result["device_names"].append(f"[Pointer] {current_name}")

            elif self.platform == "windows":
                ps_cmd = '@{ Kbd = @(Get-CimInstance Win32_Keyboard | Select-Object -ExpandProperty Description); Ptr = @(Get-CimInstance Win32_PointingDevice | Select-Object -ExpandProperty Description) } | ConvertTo-Json -Compress'
                out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=4)
                if out.returncode == 0 and out.stdout.strip():
                    try:
                        data = json.loads(out.stdout)
                        kbds = data.get("Kbd", [])
                        ptrs = data.get("Ptr", [])
                        if isinstance(kbds, str):
                            kbds = [kbds]
                        if isinstance(ptrs, str):
                            ptrs = [ptrs]
                        result["keyboards"] = len(kbds)
                        result["pointers"] = len(ptrs)
                        result["device_names"] = [f"[Keyboard] {k}" for k in kbds] + [f"[Pointer] {p}" for p in ptrs]
                    except Exception:
                        pass
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Input devices diagnostic error: {e}")
        return result

    def _check_usb_devices(self) -> dict:
        result = {"count": 0, "devices": []}
        try:
            if self.platform == "linux":
                out = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=2)
                if out.returncode == 0:
                    for line in out.stdout.splitlines():
                        line = line.strip()
                        if line:
                            # Strip 'Bus 001 Device 002: ID xxxx:yyyy '
                            parts = line.split(":", 2)
                            desc = parts[2].strip() if len(parts) > 2 else line
                            result["devices"].append(desc)
                    result["count"] = len(result["devices"])

            elif self.platform == "windows":
                ps_cmd = "Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq 'USB' -and $_.Status -eq 'OK' } | Select-Object -ExpandProperty Name | ConvertTo-Json -Compress"
                out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=4)
                if out.returncode == 0 and out.stdout.strip():
                    try:
                        data = json.loads(out.stdout)
                        if isinstance(data, str):
                            data = [data]
                        result["devices"] = data[:15]
                        result["count"] = len(data)
                    except Exception:
                        pass
        except Exception as e:
            if self.logger:
                self.logger.warning(f"USB diagnostic error: {e}")
        return result
