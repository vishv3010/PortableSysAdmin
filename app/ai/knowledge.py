import os


class KnowledgeBase:
    def __init__(self, project_root, logger):
        self.kb_dir = os.path.join(project_root, "knowledge")
        self.logger = logger
        
    def get_compiled_knowledge(self):
        """
        Reads all markdown and text files in the knowledge directory
        and compiles them into a single context string to feed to the AI.
        """
        if not os.path.exists(self.kb_dir):
            return ""
            
        compiled = ""
        for filename in os.listdir(self.kb_dir):
            if filename.endswith(".txt") or filename.endswith(".md"):
                filepath = os.path.join(self.kb_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                        compiled += f"\n--- KNOWLEDGE FRAGMENT: {filename} ---\n"
                        compiled += f.read().strip() + "\n"
                except Exception as e:
                    self.logger.error(f"Failed to read knowledge file {filename}: {e}")
                    
        return compiled.strip()
