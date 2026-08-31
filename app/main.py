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
from remediation.engine import RemediationEngine
from remediation.linux.network import FlushDNSLinux
from remediation.windows.network import FlushDNSWindows

def clear_screen(platform_os):
    os.system('cls' if platform_os == 'windows' else 'clear')

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
        clear_screen(platform_info['os'])
        print("====================================================")
        print("        PORTABLE SYSADMIN TOOLKIT")
        print("====================================================")
        print("System:")
        print(f"  OS       : {platform_info['os']} ({platform_info['release']})")
        print(f"  Hostname : {platform_info['hostname']}")
        print(f"  User     : {current_user} (Admin: {admin_status})")
        print(f"  Session  : {session_id}")
        print("----------------------------------------------------")
        print("1. Quick System Diagnostic")
        print("2. Network Diagnostic")
        print("3. Remediation Menu")
        print("4. Generate Report")
        print("0. Exit")
        print("----------------------------------------------------")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            print("\n[INFO] Running System Diagnostic...")
            diag = SystemDiagnostic(platform_info, logger)
            result = diag.run()
            print(result.to_json())
            
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(result.to_json() + "\n")
                
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            print("\n[INFO] Running Network Diagnostic...")
            diag = NetworkDiagnostic(platform_info, logger)
            result = diag.run()
            print(result.to_json())
            
            with open(os.path.join(session_log_dir, 'diagnostics.json'), 'a') as f:
                f.write(result.to_json() + "\n")
                
            input("\nPress Enter to continue...")
            

        elif choice == '3':
            print("\n[REMEDIATION MENU]")
            print("1. Flush DNS Cache (Dry Run)")
            print("2. Flush DNS Cache (Execute)")
            print("0. Back")
            r_choice = input("Select: ")
            
            if r_choice in ['1', '2']:
                dry = (r_choice == '1')
                engine = RemediationEngine(logger, session_log_dir, admin_status, current_user)
                if platform_info['os'] == 'linux':
                    rem = FlushDNSLinux(platform_info, logger)
                else:
                    rem = FlushDNSWindows(platform_info, logger)
                
                engine.run_remediation(rem, dry_run=dry)
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

        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid option.")
            time.sleep(1)

if __name__ == "__main__":
    main()
