"""DESI Infinity System - Pediatric Disease Engine (v6.2.0).

Stores pediatric-specific diseases, congenital conditions, and
age-of-onset-restricted disorders with structured age ranges, affected
systems, and gene associations. Research only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PEDIATRIC_CATEGORIES = ("congenital", "neonatal", "developmental",
                        "genetic", "infectious", "neoplastic", "metabolic",
                        "autoimmune", "other")
SYSTEMS = ("nervous", "cardiovascular", "respiratory", "gastrointestinal",
           "renal", "musculoskeletal", "endocrine", "immune", "hematologic",
           "integumentary", "reproductive")
SOURCES = ("curated", "literature", "predicted")


class PediatricError(Exception):
    """Base pediatric error."""


@dataclass
class PediatricDisease:
    disease_id: str
    name: str
    category: str = "other"
    onset_age_months_min: Optional[int] = None
    onset_age_months_max: Optional[int] = None
    affected_systems: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise PediatricError("disease_id required")
        if self.category not in PEDIATRIC_CATEGORIES:
            raise PediatricError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise PediatricError(f"invalid source: {self.source!r}")
        for s in self.affected_systems:
            if s not in SYSTEMS:
                raise PediatricError(f"invalid affected_system: {s!r}")
        for name, val in (("onset_age_months_min", self.onset_age_months_min),
                          ("onset_age_months_max", self.onset_age_months_max)):
            if val is not None and (not isinstance(val, int) or val < 0):
                raise PediatricError(f"{name} must be non-negative int or None")
        if (self.onset_age_months_min is not None
                and self.onset_age_months_max is not None
                and self.onset_age_months_min > self.onset_age_months_max):
            raise PediatricError("onset min cannot exceed onset max")


class PediatricDiseaseEngine:
    """Registry with system / category / age-of-onset queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, PediatricDisease] = {}
        self._system_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: PediatricDisease) -> PediatricDisease:
        if disease.disease_id in self._diseases:
            raise PediatricError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for s in disease.affected_systems:
            self._system_index.setdefault(s, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> PediatricDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise PediatricError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[PediatricDisease]:
        if category not in PEDIATRIC_CATEGORIES:
            raise PediatricError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_system(self, system: str) -> List[PediatricDisease]:
        if system not in SYSTEMS:
            raise PediatricError(f"invalid system: {system!r}")
        return [self.get(did) for did in self._system_index.get(system, [])]

    def by_gene(self, gene_symbol: str) -> List[PediatricDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def onset_within(self, age_months: int) -> List[PediatricDisease]:
        if not isinstance(age_months, int) or age_months < 0:
            raise PediatricError("age_months must be non-negative int")
        out = []
        for d in self._diseases.values():
            lo = d.onset_age_months_min if d.onset_age_months_min is not None else 0
            hi = d.onset_age_months_max if d.onset_age_months_max is not None else 10**6
            if lo <= age_months <= hi:
                out.append(d)
        return out

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "systems": len(self._system_index),
            "genes": len(self._gene_index),
        }


def self_test() -> bool:
    engine = PediatricDiseaseEngine()
    engine.add(PediatricDisease(
        "D_kd", "Kawasaki disease", "autoimmune",
        onset_age_months_min=6, onset_age_months_max=60,
        affected_systems=["cardiovascular", "immune"],
        biomarkers=["CRP", "ESR"]))
    engine.add(PediatricDisease(
        "D_nicu", "Neonatal jaundice", "neonatal",
        onset_age_months_min=0, onset_age_months_max=1,
        affected_systems=["hematologic"]))
    assert engine.by_category("neonatal")[0].disease_id == "D_nicu"
    assert engine.by_system("cardiovascular")[0].disease_id == "D_kd"
    assert len(engine.onset_within(12)) == 2
    assert len(engine.onset_within(120)) == 1
    print("pediatric_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
