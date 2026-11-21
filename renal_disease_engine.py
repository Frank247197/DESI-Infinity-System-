"""DESI Infinity System - Renal Disease Engine (v6.2.0).

Stores kidney diseases across glomerular, tubular, vascular, cystic,
obstructive, and neoplastic categories with affected kidney structures,
renal biomarkers, and gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

RENAL_CATEGORIES = ("glomerular", "tubular", "vascular", "cystic",
                    "obstructive", "neoplastic", "infectious", "other")
RENAL_STRUCTURES = ("glomerulus", "proximal_tubule", "loop_of_henle",
                    "distal_tubule", "collecting_duct", "renal_artery",
                    "renal_vein", "interstitium", "renal_pelvis")
SOURCES = ("curated", "literature", "predicted")


class RenalError(Exception):
    """Base renal error."""


@dataclass
class RenalDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_structures: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise RenalError("disease_id required")
        if self.category not in RENAL_CATEGORIES:
            raise RenalError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise RenalError(f"invalid source: {self.source!r}")
        for s in self.affected_structures:
            if s not in RENAL_STRUCTURES:
                raise RenalError(f"invalid affected_structure: {s!r}")


class RenalDiseaseEngine:
    """Registry with structure / biomarker / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, RenalDisease] = {}
        self._structure_index: Dict[str, List[str]] = {}
        self._biomarker_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: RenalDisease) -> RenalDisease:
        if disease.disease_id in self._diseases:
            raise RenalError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for s in disease.affected_structures:
            self._structure_index.setdefault(s, []).append(disease.disease_id)
        for b in disease.biomarkers:
            self._biomarker_index.setdefault(b, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> RenalDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise RenalError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[RenalDisease]:
        if category not in RENAL_CATEGORIES:
            raise RenalError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_structure(self, structure: str) -> List[RenalDisease]:
        if structure not in RENAL_STRUCTURES:
            raise RenalError(f"invalid structure: {structure!r}")
        return [self.get(did) for did in self._structure_index.get(structure, [])]

    def by_biomarker(self, biomarker: str) -> List[RenalDisease]:
        return [self.get(did) for did in self._biomarker_index.get(biomarker, [])]

    def by_gene(self, gene_symbol: str) -> List[RenalDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "structures": len(self._structure_index),
            "biomarkers": len(self._biomarker_index),
        }


def self_test() -> bool:
    engine = RenalDiseaseEngine()
    engine.add(RenalDisease(
        "D_iga", "IgA nephropathy", "glomerular",
        affected_structures=["glomerulus"],
        biomarkers=["IgA", "creatinine"],
        gene_associations=["CFHR1"]))
    engine.add(RenalDisease(
        "D_adpkd", "ADPKD", "cystic",
        affected_structures=["collecting_duct"],
        biomarkers=["eGFR"],
        gene_associations=["PKD1", "PKD2"]))
    assert engine.by_category("glomerular")[0].disease_id == "D_iga"
    assert engine.by_structure("glomerulus")[0].disease_id == "D_iga"
    assert engine.by_biomarker("eGFR")[0].disease_id == "D_adpkd"
    assert len(engine.by_gene("PKD1")) == 1
    print("renal_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
