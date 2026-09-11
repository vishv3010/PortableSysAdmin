import os


# ANSI Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class UI:
    @staticmethod
    def clear_screen(platform_os):
        os.system('cls' if platform_os == 'windows' else 'clear')

    @staticmethod
    def print_banner(platform_info, session_id, admin_status):
        banner = fr"""
{Colors.CYAN}{Colors.BOLD}
  _____           _        _     _        
 |  __ \         | |      | |   | |       
 | |__) |__  _ __| |_ __ _| |__ | | ___   
 |  ___/ _ \| '__| __/ _` | '_ \| |/ _ \  
 | |  | (_) | |  | || (_| | |_) | |  __/  
 |_|   \___/|_|   \__\__,_|_.__/|_|\___|  
                                          
      SYSADMIN TROUBLESHOOTING TOOLKIT
{Colors.ENDC}
"""
        print(banner)
        print(f"{Colors.BLUE}[+] System: {Colors.ENDC}{platform_info['os'].capitalize()} ({platform_info['release']})")
        print(f"{Colors.BLUE}[+] Host:   {Colors.ENDC}{platform_info['hostname']}")
        
        privilege_color = Colors.GREEN if admin_status else Colors.WARNING
        priv_text = "ROOT/ADMIN" if admin_status else "STANDARD USER"
        print(f"{Colors.BLUE}[+] Access: {Colors.ENDC}{privilege_color}{priv_text}{Colors.ENDC}")
        print(f"{Colors.BLUE}[+] Session:{Colors.ENDC} {session_id}")
        print(f"{Colors.CYAN}" + "="*50 + f"{Colors.ENDC}\n")

    @staticmethod
    def info(msg):
        print(f"{Colors.CYAN}[INFO]{Colors.ENDC} {msg}")

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {msg}")

    @staticmethod
    def warning(msg):
        print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

    @staticmethod
    def error(msg):
        print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")
        
    @staticmethod
    def prompt(msg):
        return input(f"{Colors.BOLD}{msg}{Colors.ENDC} ")

    @staticmethod
    def print_menu():
        menu = f"""
{Colors.BOLD}AVAILABLE MODULES:{Colors.ENDC}
  {Colors.GREEN}[1]{Colors.ENDC} Run Deep System Diagnostics (CPU/RAM/Disk/Security)
  {Colors.GREEN}[2]{Colors.ENDC} Run Network Diagnostics
  {Colors.GREEN}[3]{Colors.ENDC} Open Remediation Engine (Auto-Fixes)
  {Colors.GREEN}[4]{Colors.ENDC} Generate Enterprise HTML Report
  {Colors.HEADER}[5]{Colors.ENDC} Ask AI For Root Cause Analysis
  
  {Colors.CYAN}[6]{Colors.ENDC} Quick Triage & Auto-Doctor (Instant 2-Sec Check & 1-Click Fix)
  {Colors.CYAN}[7]{Colors.ENDC} Instant SysAdmin Command Finder (Offline Cheatsheet)
  {Colors.CYAN}[8]{Colors.ENDC} Open HTML Pocket Reference Guide (Browser)
  
  {Colors.BOLD}{Colors.GREEN}[9]{Colors.ENDC} 🚀 1-Click Safe System Speed-Up (Zero Data Loss RAM/Disk/CPU Boost)
  {Colors.BOLD}{Colors.CYAN}[10]{Colors.ENDC} 🎧 Hardware & Peripherals Check (Audio, Keyboard, Battery, USB)
  
  {Colors.FAIL}[0]{Colors.ENDC} Exit Toolkit
"""
        print(menu)
