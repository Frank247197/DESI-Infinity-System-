"""DESI Infinity System - Pathogen Evolution Engine (v6.2.0).

Models evolutionary pressures and lineage dynamics: substitution rate,
selection pressure, lineage expansion timing. Research-only simulations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

SELECTION_TYPES = ("positive", "purifying", "neutral", "balancing", "unknown")
SOURCES = ("curated", "literature", "predicted")


class PathogenEvolutionError(Exception):
    """Base pathogen evolution error."""


@dataclass
class EvolutionaryPressure:
    pressure_id: str
    pathogen_id: str
    selection_type: str = "unknown"
    target_genes: List[str] = field(default_factory=list)
    substitution_rate_per_site_year: Optional[float] = None
    driver: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pressure_id or not isinstance(self.pressure_id, str):
            raise PathogenEvolutionError("pressure_id required")
        if not self.pathogen_id or not isinstance(self.pathogen_id, str):
            raise PathogenEvolutionError("pathogen_id required")
        if self.selection_type not in SELECTION_TYPES:
            raise PathogenEvolutionError(f"invalid selection_type: {self.selection_type!r}")
        if self.source not in SOURCES:
            raise PathogenEvolutionError(f"invalid source: {self.source!r}")
        if self.substitution_rate_per_site_year is not None:
            v = self.substitution_rate_per_site_year
            if not isinstance(v, (int, float)) or v < 0:
                raise PathogenEvolutionError(
                    "substitution_rate_per_site_year must be non-negative or None")


@dataclass
class LineageExpansion:
    lineage_id: str
    pathogen_id: str
    origin_region: str = ""
    first_detected: str = ""
    peak_frequency: float = 0.0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.lineage_id or not isinstance(self.lineage_id, str):
            raise PathogenEvolutionError("lineage_id required")
        if not self.pathogen_id or not isinstance(self.pathogen_id, str):
            raise PathogenEvolutionError("pathogen_id required")
        if not 0.0 <= float(self.peak_frequency) <= 1.0:
            raise PathogenEvolutionError("peak_frequency must be in [0, 1]")
        if self.source not in SOURCES:
            raise PathogenEvolutionError(f"invalid source: {self.source!r}")


class PathogenEvolutionEngine:
    """Registry + analysis of evolutionary pressures and lineage expansions."""

    def __init__(self) -> None:
        self._pressures: Dict[str, EvolutionaryPressure] = {}
        self._lineages: Dict[str, LineageExpansion] = {}

    def add_pressure(self, pressure: EvolutionaryPressure) -> EvolutionaryPressure:
        if pressure.pressure_id in self._pressures:
            raise PathogenEvolutionError(f"duplicate pressure_id: {pressure.pressure_id}")
        self._pressures[pressure.pressure_id] = pressure
        return pressure

    def add_lineage(self, lineage: LineageExpansion) -> LineageExpansion:
        if lineage.lineage_id in self._lineages:
            raise PathogenEvolutionError(f"duplicate lineage_id: {lineage.lineage_id}")
        self._lineages[lineage.lineage_id] = lineage
        return lineage

    def pressures_for(self, pathogen_id: str) -> List[EvolutionaryPressure]:
        return [p for p in self._pressures.values() if p.pathogen_id == pathogen_id]

    def lineages_for(self, pathogen_id: str) -> List[LineageExpansion]:
        return [l for l in self._lineages.values() if l.pathogen_id == pathogen_id]

    def positive_selection_pressures(self) -> List[EvolutionaryPressure]:
        return [p for p in self._pressures.values() if p.selection_type == "positive"]

    def highest_substitution_rate(self) -> Optional[EvolutionaryPressure]:
        candidates = [p for p in self._pressures.values()
                      if p.substitution_rate_per_site_year is not None]
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.substitution_rate_per_site_year or 0.0)

    def dominant_lineages(self, pathogen_id: str, threshold: float = 0.5
                          ) -> List[LineageExpansion]:
        return [l for l in self.lineages_for(pathogen_id) if l.peak_frequency >= threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "pressures": len(self._pressures),
            "lineages": len(self._lineages),
            "pathogens": len({p.pathogen_id for p in self._pressures.values()}
                             | {l.pathogen_id for l in self._lineages.values()}),
        }


def self_test() -> bool:
    engine = PathogenEvolutionEngine()
    engine.add_pressure(EvolutionaryPressure(
        "PR1", "NCBITaxon:2697049", "positive",
        ["S"], substitution_rate_per_site_year=1.1e-3,
        driver="immune selection"))
    engine.add_pressure(EvolutionaryPressure(
        "PR2", "NCBITaxon:2697049", "purifying",
        ["RdRp"], substitution_rate_per_site_year=2.0e-4,
        driver="functional_constraint"))
    engine.add_lineage(LineageExpansion(
        "L1", "NCBITaxon:2697049", "UK", "2020-09", 0.75))
    engine.add_lineage(LineageExpansion(
        "L2", "NCBITaxon:2697049", "South Africa", "2020-10", 0.35))
    assert len(engine.pressures_for("NCBITaxon:2697049")) == 2
    assert len(engine.positive_selection_pressures()) == 1
    assert engine.highest_substitution_rate().pressure_id == "PR1"
    assert len(engine.dominant_lineages("NCBITaxon:2697049")) == 1
    assert engine.stats()["pressures"] == 2
    print("pathogen_evolution_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
