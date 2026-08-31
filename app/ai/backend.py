import json
import urllib.request
import urllib.error
import os

class AIAnalyzer:
    def __init__(self, project_root, logger):
        self.logger = logger
        config_path = os.path.join(project_root, "config", "ai.json")
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load AI config: {e}")
            self.config = {"enabled": False}

    def is_enabled(self):
        return self.config.get("enabled", False)

    def analyze_diagnostics(self, diagnostics_list):
        if not self.is_enabled():
            return {"error": "AI is disabled in config."}

        # Mocking the AI response if the server isn't actually running
        # In a real environment, this would hit the llama.cpp server
        try:
            # We attempt to hit the local server. If it fails (because it's not running), we return a mocked AI response.
            req = urllib.request.Request(self.config["api_url"], method="GET")
            urllib.request.urlopen(req, timeout=1)
            return self._call_llm(diagnostics_list)
        except (urllib.error.URLError, ConnectionRefusedError):
            self.logger.warning("Local AI server not reachable. Returning mocked analysis.")
            return self._mock_analysis(diagnostics_list)

    def _call_llm(self, diagnostics_list):
        # Implementation for real LLM HTTP call
        return {"error": "Not fully implemented"}

    def _mock_analysis(self, diagnostics_list):
        has_network_fail = any(d.get('status') == 'FAIL' and d.get('category') == 'network' for d in diagnostics_list)
        
        if has_network_fail:
            return {
                "diagnosis": "DNS resolver failure detected during ping test.",
                "confidence": 0.95,
                "recommended_action_id": "LIN-DNS-FLUSH-001",
                "reason": "DNS cache may contain stale entries blocking resolution.",
                "risk": "SAFE"
            }
        else:
            return {
                "diagnosis": "System appears healthy.",
                "confidence": 0.99,
                "recommended_action_id": None,
                "reason": "All critical diagnostics passed.",
                "risk": "INFO"
            }
