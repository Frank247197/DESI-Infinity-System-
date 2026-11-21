"""DESI Infinity System - Immune Cell Intelligence (v6.2.0).

Cellular-level immune intelligence: surface markers, cytokine secretion,
lineage, and functional programs. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

LINEAGES = ("myeloid", "lymphoid", "erythroid", "unknown")
FUNCTIONAL_PROGRAMS = ("phagocytosis", "cytotoxicity", "antigen_presentation",
                       "antibody_secretion", "cytokine_secretion",
                       "immune_suppression", "tissue_repair", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ImmuneCellError(Exception):
    """Base immune cell error."""


@dataclass
class ImmuneCellProfile:
    cell_id: str
    name: str
    lineage: str = "unknown"
    surface_markers: List[str] = field(default_factory=list)
    secreted_cytokines: List[str] = field(default_factory=list)
    functional_programs: List[str] = field(default_factory=list)
    tissue_resident: bool = False
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.cell_id or not isinstance(self.cell_id, str):
            raise ImmuneCellError("cell_id required")
        if not self.name or not isinstance(self.name, str):
            raise ImmuneCellError("name required")
        if self.lineage not in LINEAGES:
            raise ImmuneCellError(f"invalid lineage: {self.lineage!r}")
        if self.source not in SOURCES:
            raise ImmuneCellError(f"invalid source: {self.source!r}")
        for fp in self.functional_programs:
            if fp not in FUNCTIONAL_PROGRAMS:
                raise ImmuneCellError(f"invalid functional_program: {fp!r}")


class ImmuneCellIntelligence:
    """Cell profile registry with marker / cytokine / program queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, ImmuneCellProfile] = {}
        self._marker_index: Dict[str, List[str]] = {}
        self._cytokine_index: Dict[str, List[str]] = {}
        self._program_index: Dict[str, List[str]] = {}

    def add(self, profile: ImmuneCellProfile) -> ImmuneCellProfile:
        if profile.cell_id in self._profiles:
            raise ImmuneCellError(f"duplicate cell_id: {profile.cell_id}")
        self._profiles[profile.cell_id] = profile
        for m in profile.surface_markers:
            self._marker_index.setdefault(m, []).append(profile.cell_id)
        for c in profile.secreted_cytokines:
            self._cytokine_index.setdefault(c, []).append(profile.cell_id)
        for p in profile.functional_programs:
            self._program_index.setdefault(p, []).append(profile.cell_id)
        return profile

    def get(self, cell_id: str) -> ImmuneCellProfile:
        try:
            return self._profiles[cell_id]
        except KeyError as exc:
            raise ImmuneCellError(f"unknown cell_id: {cell_id}") from exc

    def by_lineage(self, lineage: str) -> List[ImmuneCellProfile]:
        if lineage not in LINEAGES:
            raise ImmuneCellError(f"invalid lineage: {lineage!r}")
        return [p for p in self._profiles.values() if p.lineage == lineage]

    def by_marker(self, marker: str) -> List[ImmuneCellProfile]:
        return [self.get(cid) for cid in self._marker_index.get(marker, [])]

    def by_cytokine(self, cytokine: str) -> List[ImmuneCellProfile]:
        return [self.get(cid) for cid in self._cytokine_index.get(cytokine, [])]

    def by_program(self, program: str) -> List[ImmuneCellProfile]:
        if program not in FUNCTIONAL_PROGRAMS:
            raise ImmuneCellError(f"invalid functional_program: {program!r}")
        return [self.get(cid) for cid in self._program_index.get(program, [])]

    def tissue_resident_cells(self) -> List[ImmuneCellProfile]:
        return [p for p in self._profiles.values() if p.tissue_resident]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "myeloid": len(self.by_lineage("myeloid")),
            "lymphoid": len(self.by_lineage("lymphoid")),
        }


def self_test() -> bool:
    intel = ImmuneCellIntelligence()
    intel.add(ImmuneCellProfile(
        "CD8_T", "Cytotoxic T cell", "lymphoid",
        surface_markers=["CD3", "CD8"],
        secreted_cytokines=["IFN-gamma", "TNF-alpha"],
        functional_programs=["cytotoxicity", "cytokine_secretion"]))
    intel.add(ImmuneCellProfile(
        "MAC_M1", "M1 macrophage", "myeloid",
        surface_markers=["CD68", "CD80"],
        secreted_cytokines=["IL-1beta", "TNF-alpha"],
        functional_programs=["phagocytosis", "antigen_presentation"],
        tissue_resident=True))
    intel.add(ImmuneCellProfile(
        "TREG", "Regulatory T cell", "lymphoid",
        surface_markers=["CD4", "CD25", "FOXP3"],
        secreted_cytokines=["IL-10", "TGF-beta"],
        functional_programs=["immune_suppression"]))
    assert len(intel.by_lineage("lymphoid")) == 2
    assert intel.by_marker("CD8")[0].cell_id == "CD8_T"
    assert len(intel.by_cytokine("TNF-alpha")) == 2
    assert intel.by_program("immune_suppression")[0].cell_id == "TREG"
    assert len(intel.tissue_resident_cells()) == 1
    print("immune_cell_intelligence: OK")
    return True


if __name__ == "__main__":
    self_test()
