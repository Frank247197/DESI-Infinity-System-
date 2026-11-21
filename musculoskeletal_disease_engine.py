"""DESI Infinity System - Musculoskeletal Disease Engine (v6.2.0).

Stores musculoskeletal disorders across bone, joint, muscle, tendon, and
connective-tissue categories with affected structures, biomarkers, and
gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MSK_CATEGORIES = ("bone", "joint", "muscle", "tendon", "connective_tissue",
                  "autoimmune", "metabolic", "neoplastic", "other")
MSK_STRUCTURES = ("cortical_bone", "trabecular_bone", "cartilage", "synovium",
                  "skeletal_muscle", "tendon", "ligament", "fascia", "spine")
SOURCES = ("curated", "literature", "predicted")


class MusculoskeletalError(Exception):
    """Base musculoskeletal error."""


@dataclass
class MusculoskeletalDisease:
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
            raise MusculoskeletalError("disease_id required")
        if self.category not in MSK_CATEGORIES:
            raise MusculoskeletalError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise MusculoskeletalError(f"invalid source: {self.source!r}")
        for s in self.affected_structures:
            if s not in MSK_STRUCTURES:
                raise MusculoskeletalError(f"invalid affected_structure: {s!r}")


class MusculoskeletalDiseaseEngine:
    """Registry with structure / biomarker / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, MusculoskeletalDisease] = {}
        self._structure_index: Dict[str, List[str]] = {}
        self._biomarker_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: MusculoskeletalDisease) -> MusculoskeletalDisease:
        if disease.disease_id in self._diseases:
            raise MusculoskeletalError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for s in disease.affected_structures:
            self._structure_index.setdefault(s, []).append(disease.disease_id)
        for b in disease.biomarkers:
            self._biomarker_index.setdefault(b, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> MusculoskeletalDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise MusculoskeletalError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[MusculoskeletalDisease]:
        if category not in MSK_CATEGORIES:
            raise MusculoskeletalError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_structure(self, structure: str) -> List[MusculoskeletalDisease]:
        if structure not in MSK_STRUCTURES:
            raise MusculoskeletalError(f"invalid structure: {structure!r}")
        return [self.get(did) for did in self._structure_index.get(structure, [])]

    def by_biomarker(self, biomarker: str) -> List[MusculoskeletalDisease]:
        return [self.get(did) for did in self._biomarker_index.get(biomarker, [])]

    def by_gene(self, gene_symbol: str) -> List[MusculoskeletalDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "structures": len(self._structure_index),
            "biomarkers": len(self._biomarker_index),
        }


def self_test() -> bool:
    engine = MusculoskeletalDiseaseEngine()
    engine.add(MusculoskeletalDisease(
        "D_oa", "Osteoarthritis", "joint",
        affected_structures=["cartilage", "synovium"],
        biomarkers=["COMP"],
        gene_associations=["GDF5"]))
    engine.add(MusculoskeletalDisease(
        "D_ra", "Rheumatoid arthritis", "autoimmune",
        affected_structures=["synovium"],
        biomarkers=["RF", "anti-CCP"],
        gene_associations=["HLA-DRB1"]))
    assert engine.by_category("joint")[0].disease_id == "D_oa"
    assert engine.by_structure("synovium")[0].disease_id == "D_oa"
    assert engine.by_biomarker("RF")[0].disease_id == "D_ra"
    assert engine.by_gene("HLA-DRB1")[0].disease_id == "D_ra"
    print("musculoskeletal_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
