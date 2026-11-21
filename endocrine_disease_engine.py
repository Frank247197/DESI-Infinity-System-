"""DESI Infinity System - Endocrine Disease Engine (v6.2.0).

Stores endocrine and hormonal diseases across thyroid, adrenal, pituitary,
gonadal, pancreatic, and parathyroid categories with affected glands,
hormones, biomarkers, and gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ENDOCRINE_CATEGORIES = ("thyroid", "adrenal", "pituitary", "gonadal",
                        "pancreatic", "parathyroid", "polyglandular", "other")
GLANDS = ("thyroid", "adrenal_cortex", "adrenal_medulla", "anterior_pituitary",
          "posterior_pituitary", "ovary", "testis", "pancreatic_islets",
          "parathyroid")
SOURCES = ("curated", "literature", "predicted")


class EndocrineError(Exception):
    """Base endocrine error."""


@dataclass
class EndocrineDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_glands: List[str] = field(default_factory=list)
    hormones: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise EndocrineError("disease_id required")
        if self.category not in ENDOCRINE_CATEGORIES:
            raise EndocrineError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise EndocrineError(f"invalid source: {self.source!r}")
        for g in self.affected_glands:
            if g not in GLANDS:
                raise EndocrineError(f"invalid affected_gland: {g!r}")


class EndocrineDiseaseEngine:
    """Registry with gland / hormone / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, EndocrineDisease] = {}
        self._gland_index: Dict[str, List[str]] = {}
        self._hormone_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: EndocrineDisease) -> EndocrineDisease:
        if disease.disease_id in self._diseases:
            raise EndocrineError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for g in disease.affected_glands:
            self._gland_index.setdefault(g, []).append(disease.disease_id)
        for h in disease.hormones:
            self._hormone_index.setdefault(h, []).append(disease.disease_id)
        for gene in disease.gene_associations:
            self._gene_index.setdefault(gene, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> EndocrineDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise EndocrineError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[EndocrineDisease]:
        if category not in ENDOCRINE_CATEGORIES:
            raise EndocrineError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_gland(self, gland: str) -> List[EndocrineDisease]:
        if gland not in GLANDS:
            raise EndocrineError(f"invalid gland: {gland!r}")
        return [self.get(did) for did in self._gland_index.get(gland, [])]

    def by_hormone(self, hormone: str) -> List[EndocrineDisease]:
        return [self.get(did) for did in self._hormone_index.get(hormone, [])]

    def by_gene(self, gene_symbol: str) -> List[EndocrineDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "glands": len(self._gland_index),
            "hormones": len(self._hormone_index),
        }


def self_test() -> bool:
    engine = EndocrineDiseaseEngine()
    engine.add(EndocrineDisease(
        "D_hashimoto", "Hashimoto thyroiditis", "thyroid",
        affected_glands=["thyroid"],
        hormones=["TSH", "T4"],
        biomarkers=["anti-TPO"],
        gene_associations=["HLA-DR5"]))
    engine.add(EndocrineDisease(
        "D_t2d", "Type 2 diabetes", "pancreatic",
        affected_glands=["pancreatic_islets"],
        hormones=["insulin"],
        biomarkers=["HbA1c"],
        gene_associations=["TCF7L2"]))
    assert engine.by_category("thyroid")[0].disease_id == "D_hashimoto"
    assert engine.by_gland("pancreatic_islets")[0].disease_id == "D_t2d"
    assert engine.by_hormone("insulin")[0].disease_id == "D_t2d"
    assert engine.by_gene("TCF7L2")[0].disease_id == "D_t2d"
    print("endocrine_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
