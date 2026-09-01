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

    def pre_flight(self) -> Tuple[bool, str]:
        """
        Optional: Check if the required binaries or conditions are met before execution.
        Default is to pass if not explicitly implemented.
        """
        return True, "Pre-flight checks passed (default)."

    def rollback(self) -> Tuple[bool, str]:
        """
        Optional: Reverses the execution. Required if rollback_available is True in metadata.
        """
        return False, "Rollback not supported for this action."

    def secure_run(self, cmd_args: list, **kwargs):
        """
        Hardening (SEC-003): Securely resolves the absolute path of the binary
        to prevent $PATH hijacking attacks.
        """
        import shutil
        binary = shutil.which(cmd_args[0])
        if not binary:
            raise FileNotFoundError(f"Binary '{cmd_args[0]}' not found in secure path.")
        
        secure_cmd = [binary] + cmd_args[1:]
        return subprocess.run(secure_cmd, **kwargs)
