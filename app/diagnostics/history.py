import json
import os
from datetime import datetime


class DiagnosticHistory:
    """
    Tracks the historical state of diagnostics over the course of a session.
    This allows diagnostics to detect sustained issues vs transient spikes.
    """
    def __init__(self, session_log_dir):
        self.history_file = os.path.join(session_log_dir, "history.json")
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as f:
                json.dump([], f)

    def append_record(self, diagnostic_result):
        """Appends a new diagnostic record with a timestamp."""
        record = diagnostic_result.to_dict()
        from datetime import timezone
        record['timestamp'] = datetime.now(timezone.utc).astimezone().isoformat()
        
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            history.append(record)
            
            # Keep only the last 100 records to prevent infinite growth
            if len(history) > 100:
                history = history[-100:]
                
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass

    def get_recent(self, category: str, test: str, limit: int = 5):
        """
        Retrieves the last N records for a specific category and test.
        Useful for checking if a warning condition is sustained.
        """
        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            # Filter matches
            matches = [r for r in history if r.get('category') == category and r.get('test') == test]
            return matches[-limit:]
        except Exception:
            return []

    def is_sustained_failure(self, category: str, test: str, required_count: int = 3) -> bool:
        """
        Returns True if the last `required_count` runs of this test were ALL FAIL or WARNING.
        """
        recent = self.get_recent(category, test, limit=required_count)
        if len(recent) < required_count:
            return False # Not enough history yet
            
        for r in recent:
            if r.get('status') not in ['FAIL', 'WARNING']:
                return False
        return True
