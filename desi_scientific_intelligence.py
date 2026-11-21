# DESI∞ INFINITY SYSTEM — Scientific Intelligence Core
# Version: 6.2.0
# Module: desi_scientific_intelligence.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Scientific Intelligence Core"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

class ScientificIntelligence:
    """Coordinates registered scientific modules through a simple interface."""

    def __init__(self):
        self.modules = {}

    def register(self, name: str, module) -> None:
        if not name or name in self.modules:
            raise ValueError("Module name must be unique and non-empty.")
        self.modules[name] = module

    def list_modules(self) -> list[str]:
        return sorted(self.modules)

    def run(self, name: str, function_name: str, *args, **kwargs):
        if name not in self.modules:
            raise KeyError(f"Unknown module: {name}")
        module = self.modules[name]
        function = getattr(module, function_name, None)
        if not callable(function):
            raise AttributeError(
                f"{function_name!r} is not callable on {name!r}."
            )
        return function(*args, **kwargs)
