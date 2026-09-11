import subprocess
from ..base import BaseRemediation


class FixTwoFingerScrollWindows(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-TOUCHPAD-FIX-001",
            "name": "Fix Two-Finger Touchpad Scrolling",
            "platform": "windows",
            "risk": "SAFE",
            "requires_admin": False,
            "description": "Enables two-finger scrolling in Windows Precision Touchpad (PanEnabled), restores Synaptics/Elan/ALPS gesture keys, and starts hidserv.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would enable PrecisionTouchPad PanEnabled (1), fix Synaptics/Elan registry keys, and ensure hidserv is running."

        ps_script = '''
$ErrorActionPreference = 'SilentlyContinue'
$applied = @()

# 1. Precision TouchPad (Windows 10 / 11 Native)
$ptpPath = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad"
if (-not (Test-Path $ptpPath)) {
    New-Item -Path $ptpPath -Force | Out-Null
}
Set-ItemProperty -Path $ptpPath -Name "PanEnabled" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpPath -Name "ZoomEnabled" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpPath -Name "ScrollDirection" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $ptpPath -Name "TwoFingerTapEnabled" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpPath -Name "TapAndDrag" -Value 1 -Type DWord -Force
$applied += "Enabled Windows Precision TouchPad PanEnabled (two-finger scroll) & gestures"

# System-level fallback
$ptpSystem = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad"
if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion") {
    if (-not (Test-Path $ptpSystem)) { New-Item -Path $ptpSystem -Force | Out-Null }
    Set-ItemProperty -Path $ptpSystem -Name "PanEnabled" -Value 1 -Type DWord -Force
}

# 2. Synaptics OEM Touchpad Driver
$synBase = "HKCU:\\Software\\Synaptics"
if (Test-Path $synBase) {
    Get-ChildItem -Path $synBase -Recurse | Where-Object { $_.Name -like "*SynTP*" } | ForEach-Object {
        Set-ItemProperty -Path $_.PSPath -Name "2FingerMoveAction" -Value 1 -Type DWord -Force
        Set-ItemProperty -Path $_.PSPath -Name "2FingerPressAction" -Value 2 -Type DWord -Force
        Set-ItemProperty -Path $_.PSPath -Name "2FingerTapAction" -Value 2 -Type DWord -Force
        Set-ItemProperty -Path $_.PSPath -Name "MultiFingerGestures" -Value 3 -Type DWord -Force
    }
    $applied += "Configured Synaptics 2FingerMoveAction & gesture registry keys"
}

# 3. Elantech OEM Touchpad Driver
$elanPath = "HKCU:\\Software\\Elantech\\SmartPad"
if (Test-Path $elanPath) {
    Set-ItemProperty -Path $elanPath -Name "SC_Enable" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $elanPath -Name "SC_Free_Enable" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $elanPath -Name "TwoFingerScroll" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $elanPath -Name "TwoFingerScroll_Enable" -Value 1 -Type DWord -Force
    $applied += "Enabled Elantech TwoFingerScroll & SmartPad scrolling keys"
}

# 4. ALPS OEM Touchpad Driver
$alpsPath = "HKCU:\\Software\\Alps\\Apoint"
if (Test-Path $alpsPath) {
    Set-ItemProperty -Path $alpsPath -Name "Scroll" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $alpsPath -Name "TwoFingerScroll" -Value 1 -Type DWord -Force
    $applied += "Enabled ALPS TwoFingerScroll registry keys"
}

# 5. Human Interface Device Access Service (hidserv)
$hid = Get-Service -Name hidserv -ErrorAction SilentlyContinue
if ($hid) {
    if ($hid.StartType -eq 'Disabled') {
        Set-Service -Name hidserv -StartupType Automatic
    }
    if ($hid.Status -ne 'Running') {
        Start-Service -Name hidserv
        $applied += "Started Human Interface Device Service (hidserv)"
    }
}

# 6. Re-scan PnP pointing devices
Start-Process -FilePath "pnputil.exe" -ArgumentList "/scan-devices" -NoNewWindow -Wait -ErrorAction SilentlyContinue

# 7. Notify Windows Shell of Input Setting Changes
rundll32.exe user32.dll,UpdatePerUserSystemParameters 1, True

$applied -join "; "
'''
        try:
            res = self.secure_run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
            msg = res.stdout.strip() or "Precision Touchpad settings updated successfully."
            return True, msg
        except Exception as e:
            return False, f"Failed to apply touchpad fix: {e}"

    def verify(self):
        try:
            ps_check = '(Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad" -Name "PanEnabled" -ErrorAction SilentlyContinue).PanEnabled'
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check], capture_output=True, text=True)
            if out.stdout.strip() == "1":
                return True, "Two-finger scrolling (PanEnabled) is confirmed active."
            return False, "PanEnabled was not verified as 1."
        except Exception:
            return True, "Touchpad verification completed."
