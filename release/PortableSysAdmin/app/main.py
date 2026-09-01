import os
import sys
import time
import json
from logger import setup_logger
from platform_detect import get_platform_info
from privilege import is_admin, get_current_user
from diagnostics.system import SystemDiagnostic
from diagnostics.network import NetworkDiagnostic
from reports.html_report import ReportGenerator
from ai.backend import AIAnalyzer
import os
from remediation.engine import RemediationEngine
from remediation.engine import RemediationEngine
from remediation.registry import RemediationRegistry
from diagnostics.disk import DiskDiagnostic
from ui import UI, Colors

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
            history = DiagnosticHistory(session_log_dir)
            
            UI.info("Running System Diagnostic...")
            diag = SystemDiagnostic(platform_info, logger)
            result = diag.run()
            print(result.to_json())
            history.append_record(result)
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(json.dumps(result.to_dict()) + "\n")
                
            UI.info("Running Disk Diagnostic...")
            disk_diag = DiskDiagnostic(platform_info, logger)
            disk_result = disk_diag.run()
            print(disk_result.to_json())
            history.append_record(disk_result)
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(json.dumps(disk_result.to_dict()) + "\n")
                
            UI.info("Running Process Diagnostic...")
            from diagnostics.process import ProcessDiagnostic
            proc_diag = ProcessDiagnostic(platform_info, logger)
            proc_result = proc_diag.run()
            print(proc_result.to_json())
            history.append_record(proc_result)
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(json.dumps(proc_result.to_dict()) + "\n")

            UI.info("Running Security Diagnostic...")
            from diagnostics.security import SecurityDiagnostic
            sec_diag = SecurityDiagnostic(platform_info, logger)
            sec_result = sec_diag.run()
            print(sec_result.to_json())
            history.append_record(sec_result)
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(json.dumps(sec_result.to_dict()) + "\n")
                
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
            print("\n[INFO] Generating HTML Report...")
            generator = ReportGenerator(session_log_dir, project_root, platform_info)
            out_file = generator.generate()
            print(f"[SUCCESS] Report generated: {out_file}")
            
            # Try to open it in a browser if possible
            import webbrowser
            try:
                webbrowser.open(f"file://{out_file}")
            except:
                pass
            
            input("\nPress Enter to continue...")


        elif choice == '5':
            UI.info("Initializing Offline AI Brain...")
            analyzer = AIAnalyzer(project_root, logger)
            if not analyzer.is_enabled():
                UI.error("AI Analysis is disabled in config.")
                input("\nPress Enter to continue...")
                continue
                
            diag_path = os.path.join(session_log_dir, 'diagnostics.json')
            if not os.path.exists(diag_path):
                UI.warning("No diagnostics found. Please run Option 1 or 2 first.")
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
            
            # Seed the conversation history with the initial context so the AI remembers the logs
            conversation_history = [
                {"role": "system", "content": "You are a helpful IT SysAdmin Assistant. You have just analyzed the user's system diagnostics. Answer their follow-up questions clearly and concisely."},
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

        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid option.")
            time.sleep(1)

if __name__ == "__main__":
    main()
