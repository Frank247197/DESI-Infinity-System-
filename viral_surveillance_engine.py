"""DESI Infinity System - Viral Surveillance Engine (v6.2.0).

Structured registry for viral surveillance systems (e.g., GISAID, Nextstrain,
national networks) with data coverage types, update frequency, and
geographic scope. Research metadata only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

DATA_TYPES = ("genomic", "case_counts", "mortality", "seroprevalence",
              "wastewater", "hospitalization", "other")
UPDATE_FREQUENCIES = ("real_time", "daily", "weekly", "monthly",
                      "irregular", "unknown")
SOURCES = ("curated", "literature", "predicted")


class SurveillanceError(Exception):
    """Base surveillance error."""


@dataclass
class SurveillanceSystem:
    system_id: str
    name: str
    data_types: List[str] = field(default_factory=list)
    update_frequency: str = "unknown"
    geographic_scope: List[str] = field(default_factory=list)
    is_public: bool = True
    url_or_accession: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.system_id or not isinstance(self.system_id, str):
            raise SurveillanceError("system_id required")
        if not self.name or not isinstance(self.name, str):
            raise SurveillanceError("name required")
        if self.update_frequency not in UPDATE_FREQUENCIES:
            raise SurveillanceError(
                f"invalid update_frequency: {self.update_frequency!r}")
        if self.source not in SOURCES:
            raise SurveillanceError(f"invalid source: {self.source!r}")
        for dt in self.data_types:
            if dt not in DATA_TYPES:
                raise SurveillanceError(f"invalid data_type: {dt!r}")


class ViralSurveillanceEngine:
    """Registry with data-type and geographic queries."""

    def __init__(self) -> None:
        self._systems: Dict[str, SurveillanceSystem] = {}
        self._data_index: Dict[str, List[str]] = {}

    def add(self, system: SurveillanceSystem) -> SurveillanceSystem:
        if system.system_id in self._systems:
            raise SurveillanceError(f"duplicate system_id: {system.system_id}")
        self._systems[system.system_id] = system
        for dt in system.data_types:
            self._data_index.setdefault(dt, []).append(system.system_id)
        return system

    def get(self, system_id: str) -> SurveillanceSystem:
        try:
            return self._systems[system_id]
        except KeyError as exc:
            raise SurveillanceError(f"unknown system_id: {system_id}") from exc

    def by_data_type(self, data_type: str) -> List[SurveillanceSystem]:
        if data_type not in DATA_TYPES:
            raise SurveillanceError(f"invalid data_type: {data_type!r}")
        return [self.get(s) for s in self._data_index.get(data_type, [])]

    def by_frequency(self, frequency: str) -> List[SurveillanceSystem]:
        if frequency not in UPDATE_FREQUENCIES:
            raise SurveillanceError(f"invalid update_frequency: {frequency!r}")
        return [s for s in self._systems.values()
                if s.update_frequency == frequency]

    def real_time_systems(self) -> List[SurveillanceSystem]:
        return self.by_frequency("real_time")

    def genomic_systems(self) -> List[SurveillanceSystem]:
        return self.by_data_type("genomic")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "systems": len(self._systems),
            "data_types": len(self._data_index),
            "real_time": len(self.real_time_systems()),
        }


def self_test() -> bool:
    engine = ViralSurveillanceEngine()
    engine.add(SurveillanceSystem(
        "GISAID", "GISAID EpiCoV", ["genomic"], "daily", ["global"]))
    engine.add(SurveillanceSystem(
        "NEXTSTRAIN", "Nextstrain", ["genomic", "case_counts"],
        "real_time", ["global"]))
    engine.add(SurveillanceSystem(
        "CDC_ILI", "CDC Influenza-like Illness", ["case_counts",
                                                  "hospitalization"],
        "weekly", ["USA"]))
    assert len(engine.by_data_type("genomic")) == 2
    assert len(engine.real_time_systems()) == 1
    assert len(engine.by_frequency("weekly")) == 1
    assert len(engine.genomic_systems()) == 2
    print("viral_surveillance_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
