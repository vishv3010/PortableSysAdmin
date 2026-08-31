import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class DiagnosticResult:
    def __init__(self, category: str, test: str, status: str, severity: str, message: str, evidence: Dict[str, Any] = None, recommended_actions: list = None):
        self.category = category
        self.test = test
        self.status = status # PASS, WARNING, FAIL, UNKNOWN, SKIPPED
        self.severity = severity # INFO, LOW, MEDIUM, HIGH, CRITICAL
        self.message = message
        self.evidence = evidence or {}
        self.recommended_actions = recommended_actions or []

    def to_dict(self):
        return {
            "category": self.category,
            "test": self.test,
            "status": self.status,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
            "recommended_actions": self.recommended_actions
        }

    def to_json(self):
        return json.dumps(self.to_dict(), indent=2)

class BaseDiagnostic(ABC):
    def __init__(self, platform_info: dict, logger):
        self.platform = platform_info.get("os", "unknown")
        self.logger = logger
        
    @abstractmethod
    def run(self) -> DiagnosticResult:
        pass
