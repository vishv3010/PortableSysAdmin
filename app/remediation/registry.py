import importlib
import inspect
import os
import pkgutil

from .base import BaseRemediation


class RemediationRegistry:
    def __init__(self):
        self._registry = {}
        self._load_all()

    def _load_all(self):
        # We need to discover modules in the windows and linux subpackages
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        for platform_dir in ['windows', 'linux']:
            platform_path = os.path.join(base_dir, platform_dir)
            if not os.path.exists(platform_path):
                continue
                
            for _, module_name, _ in pkgutil.iter_modules([platform_path]):
                full_module_name = f"remediation.{platform_dir}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                    self._register_from_module(module)
                except ImportError:
                    pass

    def _register_from_module(self, module):
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseRemediation) and obj is not BaseRemediation:
                try:
                    # Instantiate temporarily with empty dependencies to read metadata
                    temp_inst = obj({}, None)
                    action_id = temp_inst.metadata.get("id")
                    if action_id:
                        self._registry[action_id] = obj
                except Exception:
                    pass

    def get_remediation_class(self, action_id):
        return self._registry.get(action_id)

    def get_all_classes(self):
        return self._registry.copy()
