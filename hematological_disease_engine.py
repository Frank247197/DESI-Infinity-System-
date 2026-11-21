"""DESI Infinity System - Hematological Disease Engine (v6.2.0).

Stores hematological diseases across anemia, coagulopathy, leukemia,
lymphoma, myeloproliferative, and bone-marrow-failure categories with
affected blood lineages, CBC markers, and gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

HEME_CATEGORIES = ("anemia", "coagulopathy", "leukemia", "lymphoma",
                   "myeloproliferative", "myelodysplastic",
                   "bone_marrow_failure", "other")
BLOOD_LINEAGES = ("erythroid", "myeloid", "lymphoid", "megakaryocyte",
                  "plasma_cell", "coagulation_cascade")
SOURCES = ("curated", "literature", "predicted")


class HematologicalError(Exception):
    """Base hematological error."""


@dataclass
class HematologicalDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_lineages: List[str] = field(default_factory=list)
    cbc_markers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise HematologicalError("disease_id required")
        if self.category not in HEME_CATEGORIES:
            raise HematologicalError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise HematologicalError(f"invalid source: {self.source!r}")
        for l in self.affected_lineages:
            if l not in BLOOD_LINEAGES:
                raise HematologicalError(f"invalid affected_lineage: {l!r}")


class HematologicalDiseaseEngine:
    """Registry with lineage / marker / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, HematologicalDisease] = {}
        self._lineage_index: Dict[str, List[str]] = {}
        self._marker_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: HematologicalDisease) -> HematologicalDisease:
        if disease.disease_id in self._diseases:
            raise HematologicalError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for l in disease.affected_lineages:
            self._lineage_index.setdefault(l, []).append(disease.disease_id)
        for m in disease.cbc_markers:
            self._marker_index.setdefault(m, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> HematologicalDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise HematologicalError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[HematologicalDisease]:
        if category not in HEME_CATEGORIES:
            raise HematologicalError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_lineage(self, lineage: str) -> List[HematologicalDisease]:
        if lineage not in BLOOD_LINEAGES:
            raise HematologicalError(f"invalid lineage: {lineage!r}")
        return [self.get(did) for did in self._lineage_index.get(lineage, [])]

    def by_marker(self, marker: str) -> List[HematologicalDisease]:
        return [self.get(did) for did in self._marker_index.get(marker, [])]

    def by_gene(self, gene_symbol: str) -> List[HematologicalDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "lineages": len(self._lineage_index),
            "markers": len(self._marker_index),
        }


def self_test() -> bool:
    engine = HematologicalDiseaseEngine()
    engine.add(HematologicalDisease(
        "D_scd", "Sickle cell disease", "anemia",
        affected_lineages=["erythroid"],
        cbc_markers=["hemoglobin", "MCV"],
        gene_associations=["HBB"]))
    engine.add(HematologicalDisease(
        "D_cml", "Chronic myeloid leukemia", "leukemia",
        affected_lineages=["myeloid"],
        cbc_markers=["WBC", "basophils"],
        gene_associations=["BCR-ABL1"]))
    assert engine.by_category("anemia")[0].disease_id == "D_scd"
    assert engine.by_lineage("erythroid")[0].disease_id == "D_scd"
    assert engine.by_marker("WBC")[0].disease_id == "D_cml"
    assert engine.by_gene("BCR-ABL1")[0].disease_id == "D_cml"
    print("hematological_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
