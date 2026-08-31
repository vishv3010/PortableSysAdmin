import json
import subprocess
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

class BaseRemediation(ABC):
    def __init__(self, platform_info: dict, logger):
        self.platform = platform_info.get("os", "unknown")
        self.logger = logger

    @property
    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Must return: id, name, platform, risk, requires_admin, description, rollback_available
        """
        pass

    @abstractmethod
    def execute(self, dry_run: bool = False) -> Tuple[bool, str]:
        """
        Returns (success_boolean, message)
        """
        pass

    @abstractmethod
    def verify(self) -> Tuple[bool, str]:
        """
        Returns (success_boolean, message)
        """
        pass
