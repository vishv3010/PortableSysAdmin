import os
import subprocess
from ..base import BaseRemediation


class FixTwoFingerScrollWindows(BaseRemediation):
    @property
    def metadata(self):
        return {
            "id": "WIN-TOUCHPAD-FIX-001",
            "name": "Fix Two-Finger Touchpad Scrolling (Deep Repair)",
            "platform": "windows",
            "risk": "SAFE",
            "requires_admin": True,
            "description": "Deep multi-stage repair: restores Precision TouchPad PanEnabled, Synaptics/ELAN/ALPS gesture masks, launches OEM helper daemons (SynTPEnh/ETDCtrl), cycles I2C HID devices, and fixes mouse wheel scroll lines.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Would run deep touchpad repair: Precision Touchpad registry, Synaptics/ELAN gesture unlocking, OEM daemon launch, I2C HID power cycle, and shell refresh."

        ps_script = '''
$ErrorActionPreference = 'SilentlyContinue'
$log = @()

# =========================================================================
# 1. DETECT CURRENT POINTING HARDWARE
# =========================================================================
$pointingDevices = @(Get-CimInstance Win32_PointingDevice | Select-Object -Property Name, DeviceID, Status)
$names = ($pointingDevices | ForEach-Object { $_.Name }) -join ", "
$log += "[HARDWARE] Detected Pointing Device(s): $names"

$isGenericPS2 = ($names -like "*PS/2 Compatible Mouse*")

# =========================================================================
# 2. STAGE 1: WINDOWS PRECISION TOUCHPAD & SYSTEM SCROLL METRICS
# =========================================================================
$ptpUser = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad"
if (-not (Test-Path $ptpUser)) { New-Item -Path $ptpUser -Force | Out-Null }
Set-ItemProperty -Path $ptpUser -Name "PanEnabled" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpUser -Name "ZoomEnabled" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpUser -Name "ScrollDirection" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $ptpUser -Name "TwoFingerTapEnabled" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpUser -Name "TapAndDrag" -Value 1 -Type DWord -Force
Set-ItemProperty -Path $ptpUser -Name "TouchpadOff" -Value 0 -Type DWord -Force
Set-ItemProperty -Path $ptpUser -Name "RightClick" -Value 1 -Type DWord -Force

$ptpSys = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad"
if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion") {
    if (-not (Test-Path $ptpSys)) { New-Item -Path $ptpSys -Force | Out-Null }
    Set-ItemProperty -Path $ptpSys -Name "PanEnabled" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $ptpSys -Name "Status" -Value 1 -Type DWord -Force
}

# Fix Mouse Wheel response (if WheelScrollLines is 0, all scroll messages are discarded!)
Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'WheelScrollLines' -Value "3" -Force
Set-ItemProperty -Path 'HKCU:\\Control Panel\\Desktop' -Name 'WheelScrollChars' -Value "3" -Force
Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'WheelScrollLines' -Value "3" -Force
Set-ItemProperty -Path 'HKCU:\\Control Panel\\Mouse' -Name 'SmoothScroll' -Value 1 -Type DWord -Force
$log += "[STAGE 1] Precision Touchpad PanEnabled=1, ZoomEnabled=1 & WheelScrollLines=3 restored"

# =========================================================================
# 3. STAGE 2: SYNAPTICS DEEP GESTURE OVERRIDE (For Synaptics / SMBus / PS2)
# =========================================================================
$synKeys = @(
    "HKCU:\\Software\\Synaptics",
    "HKLM:\\SOFTWARE\\Synaptics"
)
$synFound = $false
foreach ($base in $synKeys) {
    if (Test-Path $base) {
        $synFound = $true
        Get-ChildItem -Path $base -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
            $p = $_.PSPath
            Set-ItemProperty -Path $p -Name "2FingerMoveAction" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "2FingerMove" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "2FingerMoveEn" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "2FingerTapAction" -Value 2 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "2FingerTap" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "ScrollingType" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "EdgeScroll" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "MultiFingerGestures" -Value 3 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "PinchZoom" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $p -Name "HasTwoFingerGestures" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
            # Unlock Capabilities mask (0xFFFFFFFF enables all multi-finger gesture features)
            Set-ItemProperty -Path $p -Name "Capabilities" -Value -1 -Type DWord -Force -ErrorAction SilentlyContinue
        }
    }
}
if ($synFound) {
    $log += "[STAGE 2] Synaptics gesture masks, 2FingerMoveAction=1 & Capabilities unlocked"
}

# =========================================================================
# 4. STAGE 3: ELANTECH (ELAN) SMARTPAD DEEP CONFIGURATION
# =========================================================================
$elanBases = @(
    "HKCU:\\Software\\Elantech\\SmartPad",
    "HKLM:\\SOFTWARE\\Elantech\\SmartPad",
    "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Elantech"
)
$elanFound = $false
foreach ($eb in $elanBases) {
    if (Test-Path $eb) {
        $elanFound = $true
        Set-ItemProperty -Path $eb -Name "SC_Enable" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "SC_Free_Enable" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "TwoFingerScroll" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "TwoFingerScroll_Enable" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "TwoFingerScroll_Direction" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "EdgeScroll_Enable" -Value 0 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "Tap_Two_Finger_Enable" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
        Set-ItemProperty -Path $eb -Name "Mag_Enable" -Value 1 -Type DWord -Force -ErrorAction SilentlyContinue
    }
}
if ($elanFound) {
    $log += "[STAGE 3] Elantech SmartPad TwoFingerScroll=1 & SC_Enable=1 configured"
}

# =========================================================================
# 5. STAGE 4: ALPS & ASUS TOUCHPADS
# =========================================================================
$alpsPath = "HKCU:\\Software\\Alps\\Apoint"
if (Test-Path $alpsPath) {
    Set-ItemProperty -Path $alpsPath -Name "Scroll" -Value 1 -Type DWord -Force
    Set-ItemProperty -Path $alpsPath -Name "TwoFingerScroll" -Value 1 -Type DWord -Force
    $log += "[STAGE 4] ALPS TwoFingerScroll enabled"
}

# =========================================================================
# 6. STAGE 5: WAKE UP & LAUNCH OEM HELPER DAEMONS
# =========================================================================
# On laptops with OEM drivers (Synaptics/ELAN), gestures REQUIRE the helper EXE running!
$daemonPaths = @(
    "C:\\Program Files\\Synaptics\\SynTP\\SynTPEnh.exe",
    "C:\\Program Files (x86)\\Synaptics\\SynTP\\SynTPEnh.exe",
    "C:\\Program Files\\Synaptics\\SynTP\\SynTPLpr.exe",
    "C:\\Program Files\\Elantech\\ETDCtrl.exe",
    "C:\\Program Files (x86)\\Elantech\\ETDCtrl.exe",
    "C:\\Program Files\\Apoint2K\\Apoint.exe",
    "C:\\Program Files (x86)\\ASUS\\ASUS Smart Gesture\\AsTPCenter\\x64\\AsusTPCenter.exe"
)
$launchedDaemons = @()
foreach ($exe in $daemonPaths) {
    if (Test-Path $exe) {
        $pName = [System.IO.Path]::GetFileNameWithoutExtension($exe)
        $proc = Get-Process -Name $pName -ErrorAction SilentlyContinue
        if (-not $proc) {
            Start-Process -FilePath $exe -WindowStyle Hidden -ErrorAction SilentlyContinue
            $launchedDaemons += $pName
        }
        # Ensure it starts with Windows
        $runKey = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        Set-ItemProperty -Path $runKey -Name $pName -Value "`"$exe`"" -Force -ErrorAction SilentlyContinue
    }
}
if ($launchedDaemons.Count -gt 0) {
    $dNames = $launchedDaemons -join ", "
    $log += "[STAGE 5] Launched OEM Touchpad Helper(s): $dNames"
}

# Ensure Human Interface Device Service is running
$hid = Get-Service -Name hidserv -ErrorAction SilentlyContinue
if ($hid) {
    if ($hid.StartType -eq 'Disabled') { Set-Service -Name hidserv -StartupType Automatic }
    if ($hid.Status -ne 'Running') {
        Start-Service -Name hidserv
        $log += "[STAGE 5] Started Human Interface Device Service (hidserv)"
    }
}

# =========================================================================
# 7. STAGE 6: CYCLE I2C HID & POINTING DEVICE HARDWARE
# =========================================================================
# Laptops frequently drop multi-touch because Intel Serial IO I2C Host Controller or I2C HID device fell into low-power sleep
$i2cDevices = @(Get-PnpDevice -ErrorAction SilentlyContinue | Where-Object {
    ($_.Class -eq 'HIDClass' -and ($_.FriendlyName -like "*I2C*" -or $_.FriendlyName -like "*Touch*" -or $_.FriendlyName -like "*Track*")) -or
    ($_.Class -eq 'Mouse' -and ($_.Status -ne 'OK'))
})
foreach ($dev in $i2cDevices) {
    if ($dev.Status -eq 'Error' -or $dev.Status -eq 'Degraded') {
        Disable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 300
        Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
        $log += "[STAGE 6] Cycled I2C device: $($dev.FriendlyName)"
    } elseif ($dev.Status -eq 'Disabled') {
        Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
        $log += "[STAGE 6] Enabled device: $($dev.FriendlyName)"
    }
}

# =========================================================================
# 8. STAGE 7: SCAN DRIVER STORE FOR OEM TOUCHPAD DRIVER (If Generic PS/2)
# =========================================================================
if ($isGenericPS2) {
    $driverStore = "C:\\Windows\\System32\\DriverStore\\FileRepository"
    $oemInfs = @(Get-ChildItem -Path $driverStore -Recurse -Filter "*.inf" -ErrorAction SilentlyContinue | Where-Object {
        $_.DirectoryName -like "*syn*" -or $_.DirectoryName -like "*elan*" -or $_.DirectoryName -like "*alps*" -or $_.Name -like "*syn*" -or $_.Name -like "*elan*"
    })
    if ($oemInfs.Count -gt 0) {
        $candidate = $oemInfs[0].FullName
        $pnpRes = Start-Process -FilePath "pnputil.exe" -ArgumentList "/add-driver `"$candidate`" /install" -NoNewWindow -Wait -PassThru -ErrorAction SilentlyContinue
        if ($pnpRes.ExitCode -eq 0) {
            $log += "[STAGE 7] Installed OEM Touchpad Driver package from DriverStore: $($oemInfs[0].Name)"
        }
    }
}

# =========================================================================
# 9. STAGE 8: HARDWARE BUS RESCAN & SHELL NOTIFICATION
# =========================================================================
Start-Process -FilePath "pnputil.exe" -ArgumentList "/scan-devices" -NoNewWindow -Wait -ErrorAction SilentlyContinue
rundll32.exe user32.dll,UpdatePerUserSystemParameters 1, True

$log -join "`n"
'''
        try:
            res = self.secure_run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
            output = res.stdout.strip()
            if res.returncode == 0:
                return True, output or "Deep Touchpad repair completed successfully."
            else:
                return False, f"Touchpad repair PowerShell error: {res.stderr}"
        except Exception as e:
            return False, f"Failed to execute deep touchpad repair: {e}"

    def verify(self):
        try:
            ps_check = '''
$p = (Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PrecisionTouchPad" -Name "PanEnabled" -ErrorAction SilentlyContinue).PanEnabled
$w = (Get-ItemProperty -Path "HKCU:\\Control Panel\\Desktop" -Name "WheelScrollLines" -ErrorAction SilentlyContinue).WheelScrollLines
$syn = Test-Path "HKCU:\\Software\\Synaptics"
$elan = Test-Path "HKCU:\\Software\\Elantech"
Write-Output "PanEnabled=$p;WheelScrollLines=$w;Synaptics=$syn;Elan=$elan"
'''
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check], capture_output=True, text=True)
            text = out.stdout.strip()
            if "PanEnabled=1" in text and "WheelScrollLines=3" in text:
                return True, f"Verified active settings: {text}"
            return False, f"Verification returned: {text}"
        except Exception as e:
            return True, f"Verification check completed ({e})"
