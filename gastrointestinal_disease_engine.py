"""DESI Infinity System - Gastrointestinal Disease Engine (v6.2.0).

Stores GI, hepatobiliary, and pancreatic diseases across inflammatory,
infectious, neoplastic, functional, and autoimmune categories with
affected organs, biomarkers, and gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

GI_CATEGORIES = ("inflammatory", "infectious", "neoplastic", "functional",
                 "autoimmune", "metabolic", "vascular", "other")
GI_ORGANS = ("esophagus", "stomach", "duodenum", "jejunum", "ileum", "colon",
             "rectum", "liver", "gallbladder", "pancreas", "peritoneum")
SOURCES = ("curated", "literature", "predicted")


class GastrointestinalError(Exception):
    """Base GI error."""


@dataclass
class GastrointestinalDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_organs: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise GastrointestinalError("disease_id required")
        if self.category not in GI_CATEGORIES:
            raise GastrointestinalError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise GastrointestinalError(f"invalid source: {self.source!r}")
        for o in self.affected_organs:
            if o not in GI_ORGANS:
                raise GastrointestinalError(f"invalid affected_organ: {o!r}")


class GastrointestinalDiseaseEngine:
    """Registry with organ / biomarker / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, GastrointestinalDisease] = {}
        self._organ_index: Dict[str, List[str]] = {}
        self._biomarker_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: GastrointestinalDisease) -> GastrointestinalDisease:
        if disease.disease_id in self._diseases:
            raise GastrointestinalError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for o in disease.affected_organs:
            self._organ_index.setdefault(o, []).append(disease.disease_id)
        for b in disease.biomarkers:
            self._biomarker_index.setdefault(b, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> GastrointestinalDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise GastrointestinalError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[GastrointestinalDisease]:
        if category not in GI_CATEGORIES:
            raise GastrointestinalError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_organ(self, organ: str) -> List[GastrointestinalDisease]:
        if organ not in GI_ORGANS:
            raise GastrointestinalError(f"invalid organ: {organ!r}")
        return [self.get(did) for did in self._organ_index.get(organ, [])]

    def by_biomarker(self, biomarker: str) -> List[GastrointestinalDisease]:
        return [self.get(did) for did in self._biomarker_index.get(biomarker, [])]

    def by_gene(self, gene_symbol: str) -> List[GastrointestinalDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "organs": len(self._organ_index),
            "biomarkers": len(self._biomarker_index),
        }


def self_test() -> bool:
    engine = GastrointestinalDiseaseEngine()
    engine.add(GastrointestinalDisease(
        "D_ibd", "Inflammatory bowel disease", "inflammatory",
        affected_organs=["ileum", "colon"],
        biomarkers=["CRP", "calprotectin"],
        gene_associations=["NOD2", "IL23R"]))
    engine.add(GastrointestinalDisease(
        "D_nafld", "NAFLD", "metabolic",
        affected_organs=["liver"],
        biomarkers=["ALT", "AST"]))
    assert engine.by_category("inflammatory")[0].disease_id == "D_ibd"
    assert engine.by_organ("colon")[0].disease_id == "D_ibd"
    assert engine.by_biomarker("ALT")[0].disease_id == "D_nafld"
    assert engine.by_gene("NOD2")[0].disease_id == "D_ibd"
    print("gastrointestinal_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
