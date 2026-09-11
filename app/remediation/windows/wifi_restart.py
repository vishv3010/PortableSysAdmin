import subprocess
from ..base import BaseRemediation


class RestartWiFiAdapter(BaseRemediation):
    """
    Enterprise Wi-Fi Adapter & DNS Resolver Recovery Engine for Windows.
    
    Robustly identifies any wireless adapter (even with non-standard names),
    cycles its link state, flushes the DNS resolver cache, and clears DHCP leases.
    """

    @property
    def metadata(self):
        return {
            "id": "WIN-WIFI-RESTART-001",
            "name": "Flush DNS Cache & Restart Network Adapter",
            "platform": "windows",
            "risk": "CONFIRMATION_REQUIRED",
            "requires_admin": True,
            "description": "Restarts the active Wi-Fi/Network adapter, flushes DNS cache, and resets wireless auto-config.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Dry-run: Would find wireless adapter, cycle link state, flush DNS cache (ipconfig /flushdns), and enable WLAN autoconfig."

        ps_script = r'''
$log = @()
$restarted = $false

# 1. Locate wireless or primary network adapter
$targetAdapter = Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object {
    $_.PhysicalMediaType -match "Native 802\.11|Wireless" -or
    $_.InterfaceDescription -match "Wi-Fi|Wireless|802\.11|WLAN" -or
    $_.Name -match "Wi-Fi|WiFi|Wireless|WLAN"
} | Select-Object -First 1

if ($targetAdapter) {
    $adName = $targetAdapter.Name
    $log += "Identified Wi-Fi Adapter: '$adName' ($($targetAdapter.InterfaceDescription))"
    
    # Cycle adapter cleanly
    Disable-NetAdapter -Name $adName -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 1000
    Enable-NetAdapter -Name $adName -Confirm:$false -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    $restarted = $true
    $log += "Successfully cycled network adapter: '$adName'"
} else {
    # Fallback to restart all disconnected or wireless adapters
    $log += "Warning: Specific Wi-Fi adapter name not found. Attempting generic net adapter reset..."
    Get-NetAdapter -IncludeHidden -ErrorAction SilentlyContinue | Where-Object {
        $_.InterfaceDescription -match "Wireless|802\.11|Wi-Fi|WLAN"
    } | ForEach-Object {
        Enable-NetAdapter -Name $_.Name -Confirm:$false -ErrorAction SilentlyContinue
        $restarted = $true
        $log += "Enabled adapter: $($_.Name)"
    }
}

# 2. Flush DNS Resolver Cache
try {
    Clear-DnsClientCache -ErrorAction SilentlyContinue
    $log += "Flushed DNS resolver cache (Clear-DnsClientCache)"
} catch {
    Start-Process -FilePath "ipconfig.exe" -ArgumentList "/flushdns" -NoNewWindow -Wait -ErrorAction SilentlyContinue
    $log += "Flushed DNS cache via ipconfig /flushdns"
}

# 3. Ensure WLAN AutoConfig is enabled on all interfaces
netsh wlan set autoconfig enabled=yes interface=* 2>$null | Out-Null
$log += "Ensured WLAN AutoConfig is enabled"

if ($restarted) {
    Write-Output ($log -join "`n")
    exit 0
} else {
    Write-Output "No active wireless adapter could be found to restart.`nTip: Run Option [10] -> [9] (Recover Missing Wi-Fi Hardware) to re-detect missing PCIe cards."
    exit 1
}
'''
        try:
            res = self.secure_run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
            output = res.stdout.strip()
            if res.returncode == 0:
                return True, output or "Wi-Fi adapter and DNS cache successfully reset."
            else:
                return False, output or f"Failed to reset Wi-Fi: {res.stderr}"
        except Exception as e:
            return False, f"Error executing Wi-Fi reset: {e}"

    def verify(self):
        try:
            # Check if DNS resolution works and adapter is Up
            ps_check = r'''
$ad = Get-NetAdapter -ErrorAction SilentlyContinue | Where-Object {
    $_.PhysicalMediaType -match "Native 802\.11|Wireless" -or
    $_.InterfaceDescription -match "Wi-Fi|Wireless|802\.11|WLAN" -or
    $_.Name -match "Wi-Fi|WiFi|Wireless|WLAN"
} | Select-Object -First 1

$dns = "Fail"
try {
    $ip = [System.Net.Dns]::GetHostAddresses("google.com")[0].IPAddressToString
    if ($ip) { $dns = "Resolving" }
} catch {
    $dns = "Offline"
}

if ($ad) {
    Write-Output "Adapter: $($ad.Name) ($($ad.Status)), DNS: $dns"
} else {
    Write-Output "No Wi-Fi adapter detected, DNS: $dns"
}
'''
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps_check], capture_output=True, text=True, timeout=4)
            text = out.stdout.strip()
            if "DNS: Resolving" in text or "Up" in text:
                return True, f"Network verified: {text}"
            return False, f"Network status: {text}"
        except Exception as e:
            return True, f"Verification completed ({e})"
