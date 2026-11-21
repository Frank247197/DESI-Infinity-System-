"""DESI Infinity System - Protein Structure Analyzer (v6.2.0).

Annotates protein structure features: domains, secondary-structure
content, resolved/missing regions, and quality metrics. Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

METHODS = ("xray", "nmr", "cryo_em", "alphafold", "homology_model", "other")
SECONDARY_TYPES = ("helix", "sheet", "coil", "turn", "other")
SOURCES = ("curated", "literature", "predicted")


class ProteinStructureError(Exception):
    """Base protein structure error."""


@dataclass
class StructureDomain:
    domain_id: str
    name: str
    start_residue: int
    end_residue: int
    secondary_structure: str = "other"

    def __post_init__(self) -> None:
        if not self.domain_id or not isinstance(self.domain_id, str):
            raise ProteinStructureError("domain_id required")
        if not isinstance(self.start_residue, int) or not isinstance(self.end_residue, int):
            raise ProteinStructureError("start_residue and end_residue must be ints")
        if self.start_residue < 0 or self.end_residue <= self.start_residue:
            raise ProteinStructureError("require 0 <= start < end")
        if self.secondary_structure not in SECONDARY_TYPES:
            raise ProteinStructureError(
                f"invalid secondary_structure: {self.secondary_structure!r}")

    def length(self) -> int:
        return self.end_residue - self.start_residue


@dataclass
class ProteinStructure:
    structure_id: str
    protein_id: str
    method: str
    resolution_angstrom: float = 0.0
    residue_count: int = 0
    missing_residues: int = 0
    plddt_mean: float = 0.0
    domains: List[StructureDomain] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.structure_id or not isinstance(self.structure_id, str):
            raise ProteinStructureError("structure_id required")
        if not self.protein_id or not isinstance(self.protein_id, str):
            raise ProteinStructureError("protein_id required")
        if self.method not in METHODS:
            raise ProteinStructureError(f"invalid method: {self.method!r}")
        if self.source not in SOURCES:
            raise ProteinStructureError(f"invalid source: {self.source!r}")
        if self.resolution_angstrom < 0:
            raise ProteinStructureError("resolution_angstrom must be non-negative")
        if not 0 <= self.plddt_mean <= 100:
            raise ProteinStructureError("plddt_mean must be in [0, 100]")

    def completeness(self) -> float:
        if self.residue_count == 0:
            return 0.0
        return round(1.0 - self.missing_residues / self.residue_count, 4)

    def is_high_confidence(self) -> bool:
        return self.plddt_mean >= 70 or (0 < self.resolution_angstrom <= 2.5)


class ProteinStructureAnalyzer:
    """Structure registry with method / quality queries."""

    def __init__(self) -> None:
        self._structures: Dict[str, ProteinStructure] = {}
        self._protein_index: Dict[str, List[str]] = {}

    def add(self, structure: ProteinStructure) -> ProteinStructure:
        if structure.structure_id in self._structures:
            raise ProteinStructureError(f"duplicate structure_id: {structure.structure_id}")
        self._structures[structure.structure_id] = structure
        self._protein_index.setdefault(structure.protein_id, []).append(
            structure.structure_id)
        return structure

    def get(self, structure_id: str) -> ProteinStructure:
        try:
            return self._structures[structure_id]
        except KeyError as exc:
            raise ProteinStructureError(f"unknown structure_id: {structure_id}") from exc

    def for_protein(self, protein_id: str) -> List[ProteinStructure]:
        return [self.get(sid) for sid in self._protein_index.get(protein_id, [])]

    def by_method(self, method: str) -> List[ProteinStructure]:
        if method not in METHODS:
            raise ProteinStructureError(f"invalid method: {method!r}")
        return [s for s in self._structures.values() if s.method == method]

    def high_confidence(self) -> List[ProteinStructure]:
        return [s for s in self._structures.values() if s.is_high_confidence()]

    def best_resolution(self) -> Dict[str, object]:
        candidates = [s for s in self._structures.values()
                      if s.resolution_angstrom > 0]
        if not candidates:
            return {"structure_id": None}
        best = min(candidates, key=lambda s: s.resolution_angstrom)
        return {"structure_id": best.structure_id,
                "resolution_angstrom": best.resolution_angstrom}

    def domain_total(self, structure_id: str) -> int:
        return sum(d.length() for d in self.get(structure_id).domains)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "structures": len(self._structures),
            "proteins": len(self._protein_index),
            "high_confidence": len(self.high_confidence()),
        }


def self_test() -> bool:
    analyzer = ProteinStructureAnalyzer()
    analyzer.add(ProteinStructure(
        "S1", "P04637", "xray", resolution_angstrom=1.8,
        residue_count=200, missing_residues=10,
        domains=[
            StructureDomain("D1", "DNA-binding", 100, 200, "helix"),
            StructureDomain("D2", "tetramerization", 320, 360, "coil"),
        ]))
    analyzer.add(ProteinStructure(
        "S2", "P00533", "alphafold", plddt_mean=88.0,
        residue_count=1200, missing_residues=0,
        domains=[StructureDomain("D1", "kinase", 700, 1000, "sheet")]))
    assert len(analyzer.for_protein("P04637")) == 1
    assert len(analyzer.by_method("xray")) == 1
    assert len(analyzer.high_confidence()) == 2
    assert analyzer.best_resolution()["structure_id"] == "S1"
    assert analyzer.domain_total("S2") == 300
    assert analyzer.get("S1").completeness() == 0.95
    print("protein_structure_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
