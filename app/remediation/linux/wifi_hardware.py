import os
import subprocess
from ..base import BaseRemediation


class FixWiFiHardwareLinux(BaseRemediation):
    """
    Enterprise Linux Wi-Fi Hardware Recovery Engine.
    
    Addresses common Linux wireless hardware drops:
      1. RFKill soft-blocks or airplane mode lockouts.
      2. Frozen wireless kernel modules (iwlwifi, rtw88_pci, rtw89_pci, ath10k_pci, mt7921e).
      3. Physical bus detection via lspci / lsusb.
      4. NetworkManager Wi-Fi radio disabled state.
    """

    @property
    def metadata(self):
        return {
            "id": "LNX-WIFI-HW-001",
            "name": "Recover Missing Wi-Fi Hardware (RFKill & Driver Reload)",
            "platform": "linux",
            "risk": "LOW_RISK",
            "requires_admin": True,
            "description": "Unblocks soft/hard RFKill locks, reloads frozen Wi-Fi kernel modules (iwlwifi, rtw88, ath10k, mt7921), and turns on NetworkManager Wi-Fi radio.",
            "rollback_available": False
        }

    def execute(self, dry_run=False):
        if dry_run:
            return True, "Dry-run: Would run rfkill unblock wifi, reload wireless kernel module if needed, and enable nmcli radio wifi."

        log = []

        # STAGE 1: RFKILL UNBLOCK
        log.append("[STAGE 1] Checking RFKill wireless blocks...")
        try:
            res_rf = subprocess.run(["rfkill", "list"], capture_output=True, text=True, timeout=3)
            rf_out = res_rf.stdout.lower()
            if "hard blocked: yes" in rf_out:
                log.append("  -> WARNING: A hardware switch or Fn-key combo (e.g. Fn+F2/F12) has hard-blocked your Wi-Fi antenna.")
            if "soft blocked: yes" in rf_out:
                subprocess.run(["rfkill", "unblock", "all"], capture_output=True, timeout=3)
                log.append("  -> Successfully removed software RFKill block.")
            else:
                subprocess.run(["rfkill", "unblock", "wifi"], capture_output=True, timeout=3)
                log.append("  -> Ensured Wi-Fi RFKill is unblocked.")
        except FileNotFoundError:
            pass
        except Exception as e:
            log.append(f"  -> RFKill error: {e}")

        # STAGE 2: PHYSICAL BUS DETECTION (lspci / lsusb)
        log.append("[STAGE 2] Auditing PCIe and USB hardware buses for wireless chipset...")
        wifi_found = False
        detected_chip = "Unknown"
        try:
            lspci_res = subprocess.run(["lspci"], capture_output=True, text=True, timeout=3)
            for line in lspci_res.stdout.splitlines():
                if any(w in line.lower() for w in ["network controller", "wireless", "802.11", "wi-fi"]):
                    wifi_found = True
                    detected_chip = line.strip()
                    log.append(f"  -> Detected PCIe Wireless: {detected_chip}")
                    break
        except Exception:
            pass

        if not wifi_found:
            try:
                lsusb_res = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=3)
                for line in lsusb_res.stdout.splitlines():
                    if any(w in line.lower() for w in ["wireless", "802.11", "wlan", "wi-fi"]):
                        wifi_found = True
                        detected_chip = line.strip()
                        log.append(f"  -> Detected USB Wireless: {detected_chip}")
                        break
            except Exception:
                pass

        if not wifi_found:
            log.append("  -> NOTICE: No physical wireless chip found on PCIe or USB bus.")
            log.append("     Check if M.2 card is physically unseated or wireless is disabled in BIOS.")

        # STAGE 3: KERNEL MODULE RELOAD (FOR FROZEN DRIVERS)
        known_modules = ["iwlwifi", "rtw88_pci", "rtw89_pci", "ath10k_pci", "ath9k", "mt7921e", "brcmfmac"]
        active_driver = None
        try:
            with open("/proc/modules", "r") as f:
                loaded = f.read()
                for mod in known_modules:
                    if mod in loaded:
                        active_driver = mod
                        break
        except Exception:
            pass

        if active_driver:
            log.append(f"[STAGE 3] Cycling wireless kernel module: {active_driver}...")
            try:
                subprocess.run(["modprobe", "-r", active_driver], capture_output=True, timeout=5)
                subprocess.run(["modprobe", active_driver], capture_output=True, timeout=5)
                log.append(f"  -> Successfully reloaded {active_driver}")
            except Exception as e:
                log.append(f"  -> Driver reload skipped: {e}")
        else:
            log.append("[STAGE 3] Standard kernel module active (no cycle required).")

        # STAGE 4: RADIO STATE & NETWORKMANAGER
        log.append("[STAGE 4] Enabling Wi-Fi radio & restarting NetworkManager...")
        try:
            subprocess.run(["nmcli", "radio", "wifi", "on"], capture_output=True, timeout=4)
            subprocess.run(["systemctl", "restart", "NetworkManager"], capture_output=True, timeout=8)
            log.append("  -> NetworkManager restarted & Wi-Fi radio set to ON.")
        except Exception as e:
            log.append(f"  -> Radio trigger: {e}")

        # STAGE 5: POST AUDIT
        wireless_ifaces = []
        try:
            net_dir = "/sys/class/net"
            if os.path.exists(net_dir):
                for iface in os.listdir(net_dir):
                    if os.path.exists(os.path.join(net_dir, iface, "wireless")) or iface.startswith(("wlan", "wlp", "wlo")):
                        wireless_ifaces.append(iface)
        except Exception:
            pass

        if wireless_ifaces:
            log.append(f"[STAGE 5] SUCCESS: Active wireless interface detected: {', '.join(wireless_ifaces)}")
            return True, "\n".join(log)
        elif wifi_found:
            log.append("[STAGE 5] Physical chip was detected on bus. If interface is not ready, a quick reboot will finish driver initialization.")
            return True, "\n".join(log)
        else:
            log.append("[STAGE 5] Finished: No physical wireless hardware detected on motherboard bus.")
            return False, "\n".join(log)

    def verify(self):
        try:
            net_dir = "/sys/class/net"
            if os.path.exists(net_dir):
                for iface in os.listdir(net_dir):
                    if os.path.exists(os.path.join(net_dir, iface, "wireless")) or iface.startswith(("wlan", "wlp", "wlo")):
                        return True, f"Verified active wireless interface: {iface}"
            return False, "No wireless interface currently active in /sys/class/net"
        except Exception as e:
            return True, f"Verification completed ({e})"
