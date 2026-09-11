import io
import math
import os
import platform
import select
import struct
import subprocess
import sys
import tempfile
import time
import wave

from ui import Colors, UI
from diagnostics.hardware import HardwareDiagnostic


class HardwareTester:
    """
    Interactive Hardware & Peripherals Diagnostic Suite:
      - Audio Sound Output & Speaker Test
      - Real-Time Interactive Keyboard Matrix Test
      - Battery Health, Capacity & Wear Deep-Dive
      - Connected Peripherals & USB Audit
      - Full-Screen Display Dead-Pixel & Color Check
    """

    def __init__(self, platform_info, logger=None):
        self.platform_info = platform_info
        self.logger = logger
        self.os_type = platform_info.get("os", "linux").lower()

    def run_menu(self):
        while True:
            UI.clear_screen(self.os_type)
            print(f"""
{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════════╗
║             HARDWARE & PERIPHERALS DIAGNOSTIC SUITE                  ║
╚══════════════════════════════════════════════════════════════════════╝{Colors.ENDC}
  {Colors.GREEN}[1]{Colors.ENDC} 🔊 Audio Output & Speaker Test (Plays Left/Right Tone)
  {Colors.GREEN}[2]{Colors.ENDC} ⌨️  Interactive Keyboard Key-Press & Matrix Test
  {Colors.GREEN}[3]{Colors.ENDC} 🔋 Battery Health, Wear Level & Power Deep-Dive
  {Colors.GREEN}[4]{Colors.ENDC} 🔌 Connected Peripherals, Input & USB Device Audit
  {Colors.GREEN}[5]{Colors.ENDC} 🖥️  Display RGB Color & Dead-Pixel Test
  {Colors.CYAN}[6]{Colors.ENDC} 🩺 Run Full Automated Hardware Audit (Summary)
  
  {Colors.BOLD}{Colors.YELLOW}[7]{Colors.ENDC} 🔄 Safe Audio & Peripheral Driver/Service Reset (Instant Fix)
  {Colors.BOLD}{Colors.CYAN}[8]{Colors.ENDC} 👆 Fix Two-Finger Touchpad Scrolling (1-Click Auto-Fix)
  
  {Colors.FAIL}[0]{Colors.ENDC} Back to Main Menu
""")
            choice = UI.prompt("Select a hardware test: ").strip()

            if choice == '1':
                self.test_audio()
            elif choice == '2':
                self.test_keyboard()
            elif choice == '3':
                self.test_battery()
            elif choice == '4':
                self.test_peripherals()
            elif choice == '5':
                self.test_display()
            elif choice == '6':
                self.test_automated_audit()
            elif choice == '7':
                self.reset_audio_and_peripherals()
            elif choice == '8':
                self.fix_touchpad_scroll()
            elif choice in ['0', 'back', 'q', 'exit']:
                break
            else:
                UI.error("Invalid choice.")
                time.sleep(1)

    # =========================================================================
    # 1. AUDIO TEST
    # =========================================================================
    def test_audio(self):
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 🔊 AUDIO SPEAKER & OUTPUT TEST ==={Colors.ENDC}")
        print("This test verifies audio output devices and plays a dual-frequency chime (C5 & E5).")
        print("Please ensure your speakers or headphones are turned on.\n")

        # Step 1: Detect audio devices
        diag = HardwareDiagnostic(self.platform_info, self.logger)
        audio_info = diag._check_audio()

        if audio_info.get("detected"):
            UI.success(f"Detected Audio Subsystem: {', '.join(audio_info.get('devices', []))}")
        else:
            UI.warning("No audio sound cards found in system registry.")

        UI.info("Generating and playing dual-tone test chime...")
        played = self._play_test_tone()

        if not played:
            UI.error("Could not invoke native audio playback utility.")
        else:
            UI.info("Audio playback command dispatched.")

        ans = UI.prompt("\nDid you hear the audio sound through your speakers/headphones? [y/N]: ").strip().lower()
        if ans in ['y', 'yes']:
            UI.success("Audio Output Diagnostic: PASS - Speakers and sound pipeline working properly.")
            input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")
        else:
            UI.error("Audio Output Diagnostic: FAIL - No sound heard.")
            print("\nTroubleshooting Suggestions:")
            print("  • Check hardware volume knob and mute keys.")
            print("  • Check if default audio output sink is set correctly (PulseAudio/PipeWire/Windows Sound).")
            print("  • Restart Windows Audio service (AudioSrv) or Linux sound daemons.")
            
            fix_ans = UI.prompt("\nWould you like to run the Safe Audio Subsystem Reset now to fix this? [Y/n]: ").strip().lower()
            if fix_ans not in ['n', 'no']:
                self.reset_audio_and_peripherals()
                retry = UI.prompt("\nWould you like to replay the audio chime test? [y/N]: ").strip().lower()
                if retry in ['y', 'yes']:
                    self.test_audio()
                    return
            else:
                input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    def _play_test_tone(self) -> bool:
        """Plays a pure in-memory generated dual-tone WAV chime without third-party libraries."""
        # 1. Generate 16-bit 44.1kHz PCM chime
        sample_rate = 44100
        duration = 0.7  # 700ms total
        num_samples = int(sample_rate * duration)
        buf = io.BytesIO()

        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                # Dual tone: 523.25 Hz (C5) for first half, 659.25 Hz (E5) for second half
                freq = 523.25 if t < 0.35 else 659.25
                phase = (t % 0.35) / 0.35
                envelope = math.sin(math.pi * phase)  # smooth swell/fade
                sample = int(32767.0 * 0.45 * envelope * math.sin(2.0 * math.pi * freq * t))
                frames.extend(struct.pack('<h', sample))
            wf.writeframes(frames)

        wav_data = buf.getvalue()

        if self.os_type == "windows":
            # Write temp WAV and use winsound or PowerShell
            try:
                temp_wav = os.path.join(tempfile.gettempdir(), "sysadmin_audio_test.wav")
                with open(temp_wav, "wb") as f:
                    f.write(wav_data)
                try:
                    import winsound
                    winsound.PlaySound(temp_wav, winsound.SND_FILENAME)
                    return True
                except Exception:
                    ps_cmd = f"(New-Object Media.SoundPlayer '{temp_wav}').PlaySync()"
                    p = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], timeout=3)
                    return p.returncode == 0
            except Exception:
                try:
                    import winsound
                    winsound.Beep(523, 300)
                    winsound.Beep(659, 350)
                    return True
                except Exception:
                    return False

        else:
            # Linux: Try pw-play, paplay, aplay
            temp_wav = "/tmp/sysadmin_audio_test.wav"
            try:
                with open(temp_wav, "wb") as f:
                    f.write(wav_data)

                # Handle sudo/root privilege dropping for user audio daemon access
                sudo_user = os.environ.get("SUDO_USER")
                prefix = []
                if sudo_user and os.getuid() == 0:
                    prefix = ["sudo", "-u", sudo_user]

                for player in ["pw-play", "paplay", "aplay"]:
                    if shutil_which(player):
                        cmd = prefix + [player, temp_wav]
                        try:
                            p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
                            if p.returncode == 0:
                                return True
                        except Exception:
                            continue

                # Fallback: speaker-test tone
                if shutil_which("speaker-test"):
                    subprocess.run(["speaker-test", "-t", "sine", "-f", "600", "-l", "1"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
                    return True
            except Exception:
                pass
            return False

    # =========================================================================
    # 2. KEYBOARD TEST
    # =========================================================================
    def test_keyboard(self):
        UI.clear_screen(self.os_type)
        print(f"""
{Colors.HEADER}=== ⌨️  INTERACTIVE KEYBOARD & MATRIX TEST ==={Colors.ENDC}
Instructions:
  • Press keys across your keyboard (Letters, Numbers, Space, Enter, Backspace, Arrows).
  • Watch the key registry update in real time with key name and hex code.
  • Press {Colors.BOLD}ESC{Colors.ENDC} or type {Colors.BOLD}'q'{Colors.ENDC} three times consecutively to finish.
""")
        if not sys.stdin.isatty():
            UI.warning("Interactive keyboard matrix test requires an interactive console/TTY.")
            input("\nPress Enter to return...")
            return

        pressed_keys = set()
        q_count = 0
        total_keystrokes = 0
        start_time = time.time()

        print(f"{Colors.CYAN}Ready! Start pressing keys on your keyboard...{Colors.ENDC}\n")
        print("┌" + "─"*58 + "┐")
        print(f"│ {'KEY REGISTERED':<20} │ {'CODE':<15} │ {'TOTAL STROKES':<15} │")
        print("├" + "─"*58 + "┤")

        try:
            while True:
                key_info = self._read_single_key()
                if not key_info:
                    continue

                total_keystrokes += 1
                name, code_hex = key_info
                pressed_keys.add(name)

                # Exit condition: ESC or 3 Qs
                if name == "ESC":
                    break
                if name.lower() == "q":
                    q_count += 1
                    if q_count >= 3:
                        break
                else:
                    q_count = 0

                disp_name = f"{name[:18]}"
                print(f"│ {Colors.GREEN}{disp_name:<20}{Colors.ENDC} │ {code_hex:<15} │ {total_keystrokes:<15} │")

        except KeyboardInterrupt:
            pass

        print("└" + "─"*58 + "┘")
        duration = round(time.time() - start_time, 1)

        print(f"\n{Colors.HEADER}Keyboard Test Summary:{Colors.ENDC}")
        print(f"  • Total Keystrokes Detected: {Colors.BOLD}{total_keystrokes}{Colors.ENDC}")
        print(f"  • Unique Keys Verified:      {Colors.BOLD}{len(pressed_keys)}{Colors.ENDC}")
        print(f"  • Test Duration:             {duration} seconds")

        if total_keystrokes >= 5:
            UI.success("Keyboard Matrix Diagnostic: PASS - Keys are responsive with active event dispatching.")
        elif total_keystrokes > 0:
            UI.warning("Keyboard Matrix Diagnostic: PARTIAL - Tested fewer than 5 keys.")
        else:
            UI.error("Keyboard Matrix Diagnostic: FAIL - No keystrokes detected.")

        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    def _read_single_key(self):
        """Cross-platform single character read from console."""
        if self.os_type == "windows":
            try:
                import msvcrt
                ch = msvcrt.getwch()
                if ch in ('\x00', '\xe0'):
                    ch2 = msvcrt.getwch()
                    special_map = {
                        'H': 'Up Arrow', 'P': 'Down Arrow', 'K': 'Left Arrow', 'M': 'Right Arrow',
                        ';': 'F1', '<': 'F2', '=': 'F3', '>': 'F4', '?': 'F5', '@': 'F6'
                    }
                    name = special_map.get(ch2, f"Special_{ord(ch2)}")
                    return (name, f"0xE0 0x{ord(ch2):02X}")
                if ch == '\x1b':
                    return ("ESC", "0x1B")
                if ch == '\r':
                    return ("Enter", "0x0D")
                if ch == '\t':
                    return ("Tab", "0x09")
                if ch == '\b':
                    return ("Backspace", "0x08")
                if ch == ' ':
                    return ("Space", "0x20")
                return (ch, f"0x{ord(ch):02X}")
            except Exception:
                return None
        else:
            # Linux raw terminal read
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    # Check if arrow key or escape
                    r, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if r:
                        seq = sys.stdin.read(2)
                        seq_map = {
                            '[A': 'Up Arrow', '[B': 'Down Arrow', '[C': 'Right Arrow', '[D': 'Left Arrow',
                            '[H': 'Home', '[F': 'End', '[2~': 'Insert', '[3~': 'Delete'
                        }
                        name = seq_map.get(seq, f"EscapeSeq_{seq}")
                        return (name, f"0x1B {seq}")
                    return ("ESC", "0x1B")
                if ch == '\r' or ch == '\n':
                    return ("Enter", "0x0A")
                if ch == '\t':
                    return ("Tab", "0x09")
                if ch == '\x7f' or ch == '\b':
                    return ("Backspace", "0x7F")
                if ch == ' ':
                    return ("Space", "0x20")
                return (ch, f"0x{ord(ch):02X}")
            except Exception:
                return None
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    # =========================================================================
    # 3. BATTERY TEST
    # =========================================================================
    def test_battery(self):
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 🔋 BATTERY HEALTH, WEAR & POWER STATUS ==={Colors.ENDC}\n")

        diag = HardwareDiagnostic(self.platform_info, self.logger)
        bat = diag._check_battery()

        if not bat.get("present"):
            if bat.get("ac_powered"):
                UI.info("Power Configuration: Desktop / Fixed Workstation on AC Power.")
                print("No rechargeable internal battery found. System runs on external line power.")
            else:
                UI.warning("No battery subsystem detected.")
        else:
            charge = bat.get("charge_percent", 0)
            status = bat.get("status", "Unknown")
            wear = bat.get("wear_percent", 0.0)
            health = max(0.0, round(100.0 - wear, 1))
            cycles = bat.get("cycle_count")
            ac = bat.get("ac_powered", False)

            # Health Badge
            if health >= 80:
                health_badge = f"{Colors.GREEN}EXCELLENT ({health}% remaining capacity){Colors.ENDC}"
            elif health >= 60:
                health_badge = f"{Colors.CYAN}GOOD ({health}% remaining capacity){Colors.ENDC}"
            elif health >= 40:
                health_badge = f"{Colors.WARNING}MODERATELY WORN ({health}% remaining capacity){Colors.ENDC}"
            else:
                health_badge = f"{Colors.FAIL}CRITICALLY DEGRADED ({health}% remaining capacity){Colors.ENDC}"

            # Charge progress bar
            bar_len = 30
            filled = int(bar_len * (charge / 100.0))
            bar_str = "█" * filled + "░" * (bar_len - filled)
            bar_color = Colors.GREEN if charge > 30 else (Colors.WARNING if charge > 15 else Colors.FAIL)

            print(f"  • Current Charge:    {bar_color}[{bar_str}] {charge}%{Colors.ENDC}")
            print(f"  • Power State:       {Colors.BOLD}{status}{Colors.ENDC} {'(AC Adapter Plugged In)' if ac else '(Running on Battery)'}")
            print(f"  • Battery Health:    {health_badge}")
            print(f"  • Wear Level:        {Colors.BOLD}{wear}%{Colors.ENDC} capacity degradation from factory design")
            if cycles is not None:
                print(f"  • Battery Cycles:    {Colors.BOLD}{cycles}{Colors.ENDC} complete charge cycles")

            print("\n" + "-"*50)
            if wear > 40:
                UI.warning("Recommendation: Battery wear exceeds 40%. Expect shortened unplugged runtime.")
            elif status.lower() == "discharging" and charge < 20:
                UI.error("Recommendation: Connect charger immediately to avoid abrupt shutdown.")
            else:
                UI.success("Battery is operating within healthy parameters.")

        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    # =========================================================================
    # 4. PERIPHERALS AUDIT
    # =========================================================================
    def test_peripherals(self):
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 🔌 CONNECTED PERIPHERALS & USB AUDIT ==={Colors.ENDC}\n")

        diag = HardwareDiagnostic(self.platform_info, self.logger)
        res = diag.run()
        ev = res.evidence

        # 1. Input Devices
        print(f"{Colors.BOLD}[INPUT DEVICES & CONTROLLERS]{Colors.ENDC}")
        devs = ev.get("input_devices", {}).get("device_names", [])
        if devs:
            for d in devs:
                print(f"  • {Colors.CYAN}{d}{Colors.ENDC}")
        else:
            print("  • Standard integrated keyboard & pointer registered.")

        # 2. Audio Devices
        print(f"\n{Colors.BOLD}[AUDIO SOUNDCARDS & DACs]{Colors.ENDC}")
        audio_devs = ev.get("audio", {}).get("devices", [])
        if audio_devs:
            for a in audio_devs:
                print(f"  • {Colors.GREEN}{a}{Colors.ENDC}")
        else:
            print("  • None detected.")

        # 3. USB Devices
        print(f"\n{Colors.BOLD}[USB HUBS, BRIDGES & PERIPHERALS]{Colors.ENDC}")
        usb_devs = ev.get("usb_devices", {}).get("devices", [])
        yellow = getattr(Colors, "YELLOW", Colors.WARNING)
        if usb_devs:
            for u in usb_devs:
                try:
                    print(f"  • {yellow}{u}{Colors.ENDC}")
                except Exception:
                    print(f"  • {u}")
        else:
            print("  • No external USB devices enumerated.")

        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    # =========================================================================
    # 5. DISPLAY SCREEN TEST
    # =========================================================================
    def test_display(self):
        UI.clear_screen(self.os_type)
        print(f"""
{Colors.HEADER}=== 🖥️  DISPLAY RGB COLOR & DEAD-PIXEL TEST ==={Colors.ENDC}
This test fills your console window with solid test colors:
  1. RED      (Checks green/blue subpixel defects)
  2. GREEN    (Checks red/blue subpixel defects)
  3. BLUE     (Checks red/green subpixel defects)
  4. WHITE    (Checks for dead pixels & backlight uniformity)
  5. BLACK    (Checks for stuck pixels & backlight bleed)

Instructions:
  • Press {Colors.BOLD}Enter{Colors.ENDC} to cycle to the next color pattern.
  • Inspect your screen visually for discolored dots or uneven bleeding.
  • Type {Colors.BOLD}'q'{Colors.ENDC} and press Enter to exit anytime.
""")
        if not sys.stdin.isatty():
            UI.warning("Display color test requires an interactive console/TTY.")
            input("\nPress Enter to return...")
            return

        input("Press Enter to begin color test...")

        colors = [
            ("RED", "\033[41m\033[37m"),
            ("GREEN", "\033[42m\033[30m"),
            ("BLUE", "\033[44m\033[37m"),
            ("WHITE", "\033[47m\033[30m"),
            ("BLACK", "\033[40m\033[37m")
        ]

        for name, ansi_bg in colors:
            UI.clear_screen(self.os_type)
            # Print full screen of background color
            for _ in range(20):
                print(f"{ansi_bg}{' ' * 75}{Colors.ENDC}")
            print(f"{ansi_bg} [DISPLAY TEST: {name} SCREEN] - Look closely for stuck/dead pixels. {' '*16}{Colors.ENDC}")
            for _ in range(4):
                print(f"{ansi_bg}{' ' * 75}{Colors.ENDC}")

            ans = input("\n[Enter = Next Color, 'q' = Finish]: ").strip().lower()
            if ans == 'q':
                break

        UI.clear_screen(self.os_type)
        UI.success("Display Color Test completed.")
        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    # =========================================================================
    # 6. AUTOMATED AUDIT
    # =========================================================================
    def test_automated_audit(self):
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 🩺 FULL HARDWARE AUDIT REPORT ==={Colors.ENDC}\n")
        diag = HardwareDiagnostic(self.platform_info, self.logger)
        res = diag.run()
        print(res.to_json())

        print("\n" + "-"*50)
        if res.status == "PASS":
            UI.success(f"Hardware Status: {res.message}")
        else:
            UI.warning(f"Hardware Status: {res.message}")

        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    # =========================================================================
    # 7. SAFE AUDIO & PERIPHERAL RESET
    # =========================================================================
    def reset_audio_and_peripherals(self):
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 🔄 SAFE AUDIO & PERIPHERAL SUBSYSTEM RESET ==={Colors.ENDC}\n")
        print("Safety Guarantee: 100% Non-Destructive. Never touches personal files or driver binaries.")
        print("Actions: Restarts audio services/daemons & triggers Plug-and-Play bus re-enumeration.\n")

        if self.os_type == "windows":
            from remediation.windows.audio_reset import RestartWindowsAudioAndPnP
            action = RestartWindowsAudioAndPnP(self.platform_info, self.logger)
            UI.info("Stopping & restarting Windows Audio services (AudioSrv)...")
            success, msg = action.execute(dry_run=False)
            if success:
                UI.success(msg)
            else:
                UI.warning(msg)
            print(f"\n{Colors.CYAN}[TIP] Display Driver Frozen or Glitching?{Colors.ENDC}")
            print(f"  Press {Colors.BOLD}Win + Ctrl + Shift + B{Colors.ENDC} to instantly restart your Windows graphics driver without rebooting!")
        else:
            from remediation.linux.audio_reset import RestartLinuxAudioAndUdev
            action = RestartLinuxAudioAndUdev(self.platform_info, self.logger)
            UI.info("Restarting user sound daemons (PipeWire/PulseAudio) & rescanning hardware buses...")
            success, msg = action.execute(dry_run=False)
            if success:
                UI.success(msg)
            else:
                UI.warning(msg)

        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    # =========================================================================
    # 8. FIX TOUCHPAD TWO-FINGER SCROLL
    # =========================================================================
    def fix_touchpad_scroll(self):
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 👆 FIX TWO-FINGER TOUCHPAD SCROLLING (1-CLICK FIX) ==={Colors.ENDC}\n")
        print("Diagnoses and repairs the #1 most common laptop touchpad issue:")
        print("  • Windows 10/11 Precision Touchpad PanEnabled registry flags")
        print("  • Synaptics, Elantech & ALPS OEM driver gesture keys")
        print("  • Human Interface Device Service (hidserv) state")
        print("  • Linux GNOME GSettings & X11/libinput scroll method properties\n")

        UI.info("Applying multi-touch touchpad repair...")

        if self.os_type == "windows":
            from remediation.windows.touchpad import FixTwoFingerScrollWindows
            action = FixTwoFingerScrollWindows(self.platform_info, self.logger)
            success, msg = action.execute(dry_run=False)
            verified, v_msg = action.verify()

            if success:
                UI.success("Touchpad deep repair pipeline completed successfully!")
                print("\n" + "-"*50)
                for line in msg.split("\n"):
                    if line.strip():
                        print(f"  {line.strip()}")
                print("-"*50)
                if verified:
                    UI.success(v_msg)

                # Prompt to restart Windows Explorer to refresh window hooks
                ans = UI.prompt("\nWould you like to restart Windows Explorer now to apply new mouse hooks instantly? [Y/n]: ").strip().lower()
                if ans not in ['n', 'no']:
                    UI.info("Restarting Windows Explorer shell...")
                    try:
                        subprocess.run("taskkill /f /im explorer.exe && start explorer.exe", shell=True, timeout=5)
                        UI.success("Windows Explorer shell restarted.")
                    except Exception:
                        pass
            else:
                UI.error(f"Failed to apply touchpad fix: {msg}")

            # Offer live scroll test
            ans_test = UI.prompt("\nWould you like to open the Live Two-Finger Scroll Test Zone? [Y/n]: ").strip().lower()
            if ans_test not in ['n', 'no']:
                self.test_touchpad_scroll_live()
                return

        else:
            from remediation.linux.touchpad import FixTwoFingerScrollLinux
            action = FixTwoFingerScrollLinux(self.platform_info, self.logger)
            success, msg = action.execute(dry_run=False)
            verified, v_msg = action.verify()

            if success:
                UI.success(msg)
                if verified:
                    UI.success(v_msg)
            else:
                UI.error(f"Failed to apply Linux touchpad fix: {msg}")

            ans_test = UI.prompt("\nWould you like to open the Live Two-Finger Scroll Test Zone? [Y/n]: ").strip().lower()
            if ans_test not in ['n', 'no']:
                self.test_touchpad_scroll_live()
                return

        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")

    def test_touchpad_scroll_live(self):
        """Displays a scrollable text area so the user can verify two-finger scrolling."""
        UI.clear_screen(self.os_type)
        print(f"\n{Colors.HEADER}=== 👆 LIVE TWO-FINGER SCROLL TEST ZONE ==={Colors.ENDC}\n")
        print("Instructions: Place two fingers on your touchpad and scroll up and down.\n")
        for i in range(1, 41):
            if i % 5 == 0:
                print(f"  [Line {i:02d}] {Colors.GREEN}🚀 >>> TWO-FINGER SCROLL IS WORKING! <<< 🚀{Colors.ENDC}")
            else:
                print(f"  [Line {i:02d}] Keep scrolling with two fingers to test smooth motion...")
        print(f"\n{Colors.CYAN}If you were able to scroll smoothly through lines 1 to 40, your touchpad gestures are active!{Colors.ENDC}")
        input(f"\n{Colors.BOLD}Press Enter to return to Hardware Menu...{Colors.ENDC}")


def shutil_which(cmd: str) -> bool:
    import shutil
    return shutil.which(cmd) is not None
