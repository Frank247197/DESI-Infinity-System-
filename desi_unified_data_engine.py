# DESI∞ INFINITY SYSTEM — Unified Data Engine
# Version: 6.2.0
# Module: desi_unified_data_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Unified Data Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

from datetime import datetime, timezone

class UnifiedDataEngine:
    """Stores named research datasets with basic metadata and provenance."""

    def __init__(self):
        self._datasets = {}

    def add_dataset(
        self,
        name: str,
        data,
        source: str = "unspecified"
    ) -> dict:
        if not name or name in self._datasets:
            raise ValueError("Dataset name must be unique and non-empty.")
        record = {
            "name": name,
            "data": data,
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "system_version": SYSTEM_VERSION
        }
        self._datasets[name] = record
        return self.metadata(name)

    def get_dataset(self, name: str):
        if name not in self._datasets:
            raise KeyError(name)
        return self._datasets[name]["data"]

    def metadata(self, name: str) -> dict:
        if name not in self._datasets:
            raise KeyError(name)
        record = self._datasets[name]
        return {
            key: value
            for key, value in record.items()
            if key != "data"
        }

    def list_datasets(self) -> list[str]:
        return sorted(self._datasets)
