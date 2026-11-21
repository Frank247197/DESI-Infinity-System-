"""DESI Infinity System - Stem Cell Research Engine (v6.2.0).

Registry of stem cell types, differentiation potential, markers, and
disease links. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STEM_TYPES = ("embryonic", "induced_pluripotent", "hematopoietic",
              "mesenchymal", "neural", "epithelial", "muscle",
              "cancer_stem", "other")
POTENCY = ("totipotent", "pluripotent", "multipotent", "oligopotent",
           "unipotent", "unknown")
SOURCES = ("curated", "literature", "predicted")


class StemCellError(Exception):
    """Base stem cell error."""


@dataclass
class StemCellProfile:
    stem_id: str
    name: str
    stem_type: str
    potency: str = "unknown"
    surface_markers: List[str] = field(default_factory=list)
    differentiation_potential: List[str] = field(default_factory=list)
    tissue_origin: str = ""
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.stem_id or not isinstance(self.stem_id, str):
            raise StemCellError("stem_id required")
        if not self.name or not isinstance(self.name, str):
            raise StemCellError("name required")
        if self.stem_type not in STEM_TYPES:
            raise StemCellError(f"invalid stem_type: {self.stem_type!r}")
        if self.potency not in POTENCY:
            raise StemCellError(f"invalid potency: {self.potency!r}")
        if self.source not in SOURCES:
            raise StemCellError(f"invalid source: {self.source!r}")


class StemCellResearchEngine:
    """Registry with type / potency / marker / disease queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, StemCellProfile] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._marker_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, profile: StemCellProfile) -> StemCellProfile:
        if profile.stem_id in self._profiles:
            raise StemCellError(f"duplicate stem_id: {profile.stem_id}")
        self._profiles[profile.stem_id] = profile
        self._type_index.setdefault(profile.stem_type, []).append(profile.stem_id)
        for m in profile.surface_markers:
            self._marker_index.setdefault(m, []).append(profile.stem_id)
        for did in profile.disease_ids:
            self._disease_index.setdefault(did, []).append(profile.stem_id)
        return profile

    def get(self, stem_id: str) -> StemCellProfile:
        try:
            return self._profiles[stem_id]
        except KeyError as exc:
            raise StemCellError(f"unknown stem_id: {stem_id}") from exc

    def by_type(self, stem_type: str) -> List[StemCellProfile]:
        if stem_type not in STEM_TYPES:
            raise StemCellError(f"invalid stem_type: {stem_type!r}")
        return [self.get(s) for s in self._type_index.get(stem_type, [])]

    def by_potency(self, potency: str) -> List[StemCellProfile]:
        if potency not in POTENCY:
            raise StemCellError(f"invalid potency: {potency!r}")
        return [p for p in self._profiles.values() if p.potency == potency]

    def by_marker(self, marker: str) -> List[StemCellProfile]:
        return [self.get(s) for s in self._marker_index.get(marker, [])]

    def for_disease(self, disease_id: str) -> List[StemCellProfile]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def cancer_stem_cells(self) -> List[StemCellProfile]:
        return self.by_type("cancer_stem")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "types": len(self._type_index),
            "markers": len(self._marker_index),
        }


def self_test() -> bool:
    engine = StemCellResearchEngine()
    engine.add(StemCellProfile(
        "SC1", "Hematopoietic stem cell", "hematopoietic", "multipotent",
        surface_markers=["CD34", "CD133"],
        differentiation_potential=["myeloid", "lymphoid"],
        tissue_origin="bone_marrow"))
    engine.add(StemCellProfile(
        "SC2", "Induced pluripotent stem cell", "induced_pluripotent",
        "pluripotent", surface_markers=["OCT4", "SOX2", "NANOG"],
        differentiation_potential=["any"]))
    engine.add(StemCellProfile(
        "SC3", "Leukemia stem cell", "cancer_stem", "multipotent",
        surface_markers=["CD34", "CD38_neg"],
        disease_ids=["D_aml"]))
    assert len(engine.by_type("hematopoietic")) == 1
    assert len(engine.by_potency("pluripotent")) == 1
    assert len(engine.by_marker("CD34")) == 2
    assert engine.for_disease("D_aml")[0].stem_id == "SC3"
    assert len(engine.cancer_stem_cells()) == 1
    print("stem_cell_research_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
