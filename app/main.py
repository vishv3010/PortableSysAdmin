import json
import os
import sys
import time

# Ensure application directory and project root are in sys.path for cross-platform imports
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_APP_DIR)
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(1, _PROJECT_ROOT)

from ai.backend import AIAnalyzer
from diagnostics.disk import DiskDiagnostic
from diagnostics.network import NetworkDiagnostic
from diagnostics.system import SystemDiagnostic
from logger import setup_logger
from platform_detect import get_platform_info
from privilege import get_current_user, is_admin
from remediation.engine import RemediationEngine
from remediation.registry import RemediationRegistry
from reports.html_report import ReportGenerator
from ui import UI, Colors


def copy_to_clipboard(text: str, platform_os: str) -> bool:
    import subprocess
    try:
        if platform_os == "linux":
            for cmd in [['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input'], ['wl-copy']]:
                try:
                    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    p.communicate(text.encode('utf-8'))
                    if p.returncode == 0:
                        return True
                except FileNotFoundError:
                    continue
        elif platform_os == "windows":
            p = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            p.communicate(text.encode('utf-8'))
            if p.returncode == 0:
                return True
    except Exception:
        pass
    return False


def open_in_browser(target_url_or_file: str, platform_os: str) -> bool:
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and platform_os == "linux":
        import subprocess
        try:
            env_vars = []
            for var in ["DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS"]:
                if var in os.environ:
                    env_vars.append(f"{var}={os.environ[var]}")
            cmd = ["sudo", "-u", sudo_user]
            if env_vars:
                cmd += ["env"] + env_vars
            cmd += ["xdg-open", target_url_or_file]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass

    import webbrowser
    try:
        webbrowser.open(target_url_or_file)
        return True
    except Exception:
        return False


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Setup Logging & Session
    logger, session_id, session_log_dir = setup_logger(project_root)
    logger.info("Starting Portable SysAdmin Toolkit")
    
    # 2. Platform & Privilege Detection
    platform_info = get_platform_info()
    admin_status = is_admin()
    current_user = get_current_user()
    
    while True:
        UI.clear_screen(platform_info['os'])
        UI.print_banner(platform_info, session_id, admin_status)
        UI.print_menu()
        
        choice = UI.prompt("Select a module: ")
        
        if choice == '1':
            from diagnostics.history import DiagnosticHistory
            from diagnostics.process import ProcessDiagnostic
            from diagnostics.security import SecurityDiagnostic
            from diagnostics.thermal import ThermalDiagnostic
            
            history = DiagnosticHistory(session_log_dir)
            
            diagnostics_to_run = [
                ("System", SystemDiagnostic),
                ("Disk", DiskDiagnostic),
                ("Process", ProcessDiagnostic),
                ("Security", SecurityDiagnostic),
                ("Thermal", ThermalDiagnostic),
            ]
            
            for name, diag_class in diagnostics_to_run:
                UI.info(f"Running {name} Diagnostic...")
                diag = diag_class(platform_info, logger)
                result = diag.run()
                print(result.to_json())
                history.append_record(result)
                with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                    f.write(json.dumps(result.to_dict()) + "\n")
                
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            print("\n[INFO] Running Network Diagnostic...")
            diag = NetworkDiagnostic(platform_info, logger)
            result = diag.run()
            print(result.to_json())
            
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(json.dumps(result.to_dict()) + "\n")
                
            input("\nPress Enter to continue...")
            

        elif choice == '3':
            registry = RemediationRegistry()
            available = registry.get_all_classes()
            
            # Filter by platform
            platform_actions = []
            for action_id, cls in available.items():
                # We instantiate briefly with None logger to read metadata
                temp = cls(platform_info, None)
                if temp.metadata['platform'] == platform_info['os']:
                    platform_actions.append(temp)
            
            print("\n[REMEDIATION MENU]")
            if not platform_actions:
                print("No remediation actions available for this platform.")
                input("\nPress Enter to continue...")
                continue
                
            for idx, action in enumerate(platform_actions):
                print(f"{idx+1}. {action.metadata['name']} (ID: {action.metadata['id']})")
            print("0. Back")
            
            r_choice = input("Select an action to run: ")
            
            if r_choice.isdigit() and 1 <= int(r_choice) <= len(platform_actions):
                selected_action_cls = available[platform_actions[int(r_choice)-1].metadata['id']]
                # Instantiate properly with logger
                selected_action = selected_action_cls(platform_info, logger)
                
                print(f"\nSelected: {selected_action.metadata['name']}")
                print("1. Dry Run")
                print("2. Execute")
                print("0. Cancel")
                exec_choice = input("Select mode: ")
                
                if exec_choice in ['1', '2']:
                    dry = (exec_choice == '1')
                    engine = RemediationEngine(logger, session_log_dir, admin_status, current_user)
                    engine.run_remediation(selected_action, dry_run=dry)
                
            input("\nPress Enter to continue...")


        elif choice == '4':
            print("\n[INFO] Generating Enterprise HTML Report & Online AI Prompt...")
            generator = ReportGenerator(session_log_dir, project_root, platform_info)
            out_file = generator.generate()
            prompt_file = os.path.join(session_log_dir, "ai_prompt.txt")
            print(f"[SUCCESS] Report generated: {out_file}")
            if os.path.exists(prompt_file):
                print(f"[SUCCESS] Online AI Prompt exported: {prompt_file}")
                print("[TIP] Open the HTML report to 1-click copy the prompt for ChatGPT/Claude (0% CPU)!")
            
            # Open report in browser
            open_in_browser(out_file, platform_info.get("os", "linux"))
            input("\nPress Enter to continue...")


        elif choice == '5':
            diag_path = os.path.join(session_log_dir, 'diagnostics.json')
            if not os.path.exists(diag_path):
                UI.warning("No diagnostics found. Please run Option 1 or 2 first.")
                input("\nPress Enter to continue...")
                continue

            generator = ReportGenerator(session_log_dir, project_root, platform_info)
            prompt_file = os.path.join(session_log_dir, "ai_prompt.txt")
            if not os.path.exists(prompt_file):
                generator.generate()

            print(f"\n{Colors.HEADER}=== AI DIAGNOSTIC ASSISTANT ==={Colors.ENDC}")
            print(f"  {Colors.GREEN}[1]{Colors.ENDC} 📋 Copy Diagnostic Prompt for Online AI (ChatGPT / Claude) [0% CPU, Recommended]")
            print(f"  {Colors.GREEN}[2]{Colors.ENDC} 🚀 Open ChatGPT in Browser")
            print(f"  {Colors.GREEN}[3]{Colors.ENDC} 🟣 Open Claude in Browser")
            print(f"  {Colors.WARNING}[4]{Colors.ENDC} 🖥️ Run Offline Local AI (llama.cpp) [CPU Intensive on laptops]")
            print(f"  {Colors.FAIL}[0]{Colors.ENDC} Back to Main Menu")

            sub_choice = UI.prompt("\nSelect mode: ")

            if sub_choice == '1':
                if os.path.exists(prompt_file):
                    with open(prompt_file, 'r') as f:
                        content = f.read()
                    copied = copy_to_clipboard(content, platform_info.get("os", "linux"))
                    if copied:
                        UI.success("Complete diagnostic brief copied to clipboard! Paste it directly into ChatGPT (Ctrl+V).")
                    else:
                        UI.info(f"Diagnostic brief saved to: {prompt_file}")
                        UI.info("You can open this text file or copy it from the HTML Report (Option 4).")
                input("\nPress Enter to return to main menu...")
                continue

            elif sub_choice == '2':
                open_in_browser("https://chatgpt.com", platform_info.get("os", "linux"))
                UI.success("Opening ChatGPT in your browser! Copy your prompt using Option 1 or the HTML Report.")
                input("\nPress Enter to return to main menu...")
                continue

            elif sub_choice == '3':
                open_in_browser("https://claude.ai", platform_info.get("os", "linux"))
                UI.success("Opening Claude in your browser! Copy your prompt using Option 1 or the HTML Report.")
                input("\nPress Enter to return to main menu...")
                continue

            elif sub_choice == '4':
                UI.info("Initializing Offline AI Brain...")
                analyzer = AIAnalyzer(project_root, logger)
                if not analyzer.is_enabled():
                    UI.error("AI Analysis is disabled in config.")
                    input("\nPress Enter to continue...")
                    continue

                diagnostics = []
                with open(diag_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            diagnostics.append(json.loads(line))

                UI.info("AI is analyzing diagnostics. Please wait...")
                result = analyzer.analyze_diagnostics(diagnostics)

                print(f"\n{Colors.HEADER}=== AI DIAGNOSIS ==={Colors.ENDC}")
                print(f"Diagnosis: {result.get('diagnosis')}")
                print(f"Confidence: {result.get('confidence')}")
                print(f"Reason: {result.get('reason')}")
                print(f"Recommended Fix: {result.get('recommended_action_id')}")
                print(f"{Colors.HEADER}===================={Colors.ENDC}\n")

                # --- INTERACTIVE CHAT MODE ---
                UI.success("Interactive Chat Mode Enabled. Type 'exit' to return to menu.")

                conversation_history = [
                    {"role": "system", "content": "You are a helpful IT SysAdmin Assistant. Answer clearly and concisely in 1 to 3 sentences."},
                    {"role": "assistant", "content": f"My initial diagnosis was: {result.get('diagnosis')}. The recommended fix is {result.get('recommended_action_id')}. How can I help you further?"}
                ]

                while True:
                    user_input = UI.prompt("\nYou: ")
                    if user_input.lower() in ['exit', 'quit', '0', 'back']:
                        break

                    print(f"{Colors.CYAN}AI is thinking...{Colors.ENDC}")
                    ai_response, conversation_history = analyzer.chat(user_input, conversation_history)
                    print(f"\n{Colors.HEADER}AI:{Colors.ENDC} {ai_response}")

                input("\nPress Enter to return to main menu...")

        elif choice == '6':
            from triage import QuickTriage
            triage = QuickTriage(platform_info, logger)
            triage.run()

        elif choice == '7':
            from cheatsheet import CommandFinder
            finder = CommandFinder(project_root)
            finder.interactive_search(platform_info.get("os", "linux"))

        elif choice == '8':
            ref_path = os.path.join(project_root, "POCKET_REFERENCE.html")
            UI.info(f"Opening Offline Pocket Reference: {ref_path}")
            sudo_user = os.environ.get("SUDO_USER")
            opened = False
            if sudo_user and platform_info.get("os") == "linux":
                import subprocess
                try:
                    env_vars = []
                    for var in ["DISPLAY", "XAUTHORITY", "WAYLAND_DISPLAY", "DBUS_SESSION_BUS_ADDRESS"]:
                        if var in os.environ:
                            env_vars.append(f"{var}={os.environ[var]}")
                    cmd = ["sudo", "-u", sudo_user]
                    if env_vars:
                        cmd += ["env"] + env_vars
                    cmd += ["xdg-open", ref_path]
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    opened = True
                except Exception:
                    pass
            if not opened:
                import webbrowser
                webbrowser.open(f"file://{ref_path}")
            input("\nPress Enter to return to main menu...")

        elif choice == '9':
            from speed_up import SafeSystemSpeedUp
            booster = SafeSystemSpeedUp(platform_info, logger, admin_status, session_log_dir)
            booster.run_interactive()

        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid option.")
            time.sleep(1)

if __name__ == "__main__":
    main()
