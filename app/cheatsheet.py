import json
import os
from ui import UI, Colors


class CommandFinder:
    def __init__(self, project_root):
        self.project_root = project_root
        self.db_path = os.path.join(project_root, "knowledge", "cheatsheet.json")
        self.entries = []
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = []

    def interactive_search(self, current_os="linux"):
        while True:
            print(f"\n{Colors.HEADER}{Colors.BOLD}=== INSTANT SYSADMIN COMMAND FINDER ==={Colors.ENDC}")
            print("Type any keyword (e.g. 'disk', 'port', 'dns', 'process', 'firewall', 'all')")
            print("Or type '0' or 'exit' to return to main menu.\n")
            
            query = UI.prompt("Search: ").strip().lower()
            if query in ["0", "exit", "quit", "back", ""]:
                break

            results = []
            if query == "all":
                results = self.entries
            else:
                for entry in self.entries:
                    text_blob = f"{entry.get('topic', '')} {entry.get('category', '')} {entry.get('description', '')} {entry.get('linux', '')} {entry.get('windows', '')}".lower()
                    if query in text_blob:
                        results.append(entry)

            if not results:
                print(f"{Colors.WARNING}No commands found matching '{query}'. Try: disk, port, dns, firewall, service, process, repair{Colors.ENDC}")
                continue

            print(f"\n{Colors.GREEN}Found {len(results)} matching command(s):{Colors.ENDC}\n")
            for idx, item in enumerate(results, 1):
                risk = item.get("risk", "SAFE")
                risk_color = Colors.GREEN if risk == "SAFE" else (Colors.WARNING if risk == "CONFIRMATION_REQUIRED" else Colors.FAIL)
                
                print(f"{Colors.CYAN}{idx}. [{item.get('topic', 'General')}] {item.get('description')}{Colors.ENDC} ({risk_color}{risk}{Colors.ENDC})")
                
                if current_os == "linux":
                    print(f"   {Colors.BOLD}Linux Command:{Colors.ENDC}   {Colors.GREEN}{item.get('linux')}{Colors.ENDC}")
                    print(f"   {Colors.BLUE}Windows (Alt):{Colors.ENDC}   {item.get('windows')}")
                else:
                    print(f"   {Colors.BOLD}Windows Command:{Colors.ENDC} {Colors.GREEN}{item.get('windows')}{Colors.ENDC}")
                    print(f"   {Colors.BLUE}Linux (Alt):{Colors.ENDC}     {item.get('linux')}")
                print("-" * 65)

            input(f"\n{Colors.BOLD}Press Enter to search again...{Colors.ENDC}")
