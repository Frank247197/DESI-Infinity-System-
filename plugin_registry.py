# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - MODULAR PLUGIN REGISTRY
# Dynamic Extension Management & Lifecycle Isolation
# ============================================================

from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

VALID_MATURITY_TIERS = {
    "IMPLEMENTED_AND_TESTED",
    "IMPLEMENTED_UNVALIDATED",
    "EXPERIMENTAL_PROTOTYPE",
    "SIMULATION_MODEL"
}

@dataclass
class PluginMetadata:
    """Metadata descriptor enforcing architectural governance and maturity tracking."""
    name: str
    version: str
    domain: str
    maturity_tier: str
    description: str
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PluginRegistry:
    """
    [CALC] Central modular registry allowing DESI-Infinity subsystems 
    (Genomics, Neuroscience, Nanomedicine, Physics) to register and 
    execute isolated extensions without modifying core engine code.
    """
    def __init__(self):
        self._plugins: Dict[str, Callable] = {}
        self._metadata: Dict[str, PluginMetadata] = {}

    def register(
        self,
        name: str,
        version: str,
        domain: str,
        maturity_tier: str,
        description: str = ""
    ) -> Callable:
        """Decorator to register a module or scientific function into the DESI-Infinity ecosystem."""
        if maturity_tier not in VALID_MATURITY_TIERS:
            raise ValueError(
                f"Invalid maturity tier '{maturity_tier}'. Must be one of: {VALID_MATURITY_TIERS}"
            )
        if not name or not version:
            raise ValueError("Plugin name and version cannot be empty.")

        def decorator(func: Callable) -> Callable:
            if name in self._plugins:
                raise KeyError(f"Plugin '{name}' is already registered. Unregister first to update.")
            
            self._plugins[name] = func
            self._metadata[name] = PluginMetadata(
                name=name,
                version=version,
                domain=domain.upper(),
                maturity_tier=maturity_tier,
                description=description
            )
            return func
        return decorator

    def execute(self, name: str, *args, allow_experimental: bool = False, **kwargs) -> Dict[str, Any]:
        """Executes a registered plugin with strict maturity-tier safety checks."""
        if name not in self._plugins:
            raise KeyError(f"Plugin '{name}' not found in DESI-Infinity registry.")

        meta = self._metadata[name]
        if meta.maturity_tier in {"EXPERIMENTAL_PROTOTYPE", "IMPLEMENTED_UNVALIDATED"} and not allow_experimental:
            raise PermissionError(
                f"Execution blocked: '{name}' is classified as {meta.maturity_tier}. "
                f"Pass allow_experimental=True to override."
            )

        result = self._plugins[name](*args, **kwargs)
        return {
            "plugin": meta.name,
            "version": meta.version,
            "domain": meta.domain,
            "classification": meta.maturity_tier,
            "output": result
        }

    def list_plugins(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists all registered modules, optionally filtered by scientific domain."""
        entries = []
        for meta in self._metadata.values():
            if domain is None or meta.domain == domain.upper():
                entries.append({
                    "name": meta.name,
                    "version": meta.version,
                    "domain": meta.domain,
                    "maturity_tier": meta.maturity_tier,
                    "registered_at": meta.registered_at
                })
        return entries


if __name__ == "__main__":
    print("=" * 60)
    print("DESI∞ MODULAR PLUGIN REGISTRY VERIFICATION [CALC]")
    print("=" * 60)

    registry = PluginRegistry()

    @registry.register(
        name="gc_content_analyzer",
        version="5.0.0",
        domain="GENOMICS",
        maturity_tier="IMPLEMENTED_AND_TESTED",
        description="Backward-compatible GC content calculator."
    )
    def calc_gc(seq: str) -> float:
        seq = seq.upper()
        if not seq:
            return 0.0
        return round(((seq.count("G") + seq.count("C")) / len(seq)) * 100.0, 2)

    @registry.register(
        name="neuro_synapse_experimental",
        version="0.1.0-alpha",
        domain="NEUROSCIENCE",
        maturity_tier="EXPERIMENTAL_PROTOTYPE",
        description="Experimental synaptic plasticity model."
    )
    def test_synapse(voltage_mv: float) -> float:
        return voltage_mv * 1.15

    # 1. Execute verified production module
    res = registry.execute("gc_content_analyzer", "ATGCGCGTAA")
    print(f"\n[1] Verified Plugin Execution:")
    print(f"  Plugin         : {res['plugin']} (v{res['version']})")
    print(f"  Classification : {res['classification']}")
    print(f"  Result         : {res['output']}% GC")

    # 2. Verify experimental safety guard
    try:
        registry.execute("neuro_synapse_experimental", -70.0)
    except PermissionError as e:
        print(f"\n[2] Safety Guard Active (Blocked unapproved experimental run):")
        print(f"  Guard Message  : {e}")
