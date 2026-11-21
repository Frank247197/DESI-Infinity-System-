"""DESI Infinity System - Reproductive Disease Engine (v6.2.0).

Stores reproductive system disorders across male, female, pregnancy-related,
and fertility categories with affected organs, hormones, biomarkers, and
gene associations. Research data only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

REPRO_CATEGORIES = ("male_reproductive", "female_reproductive", "pregnancy",
                    "fertility", "infectious", "neoplastic", "endocrine",
                    "genetic", "other")
REPRO_ORGANS = ("ovary", "uterus", "cervix", "vagina", "fallopian_tube",
                "testis", "epididymis", "prostate", "penis", "placenta",
                "breast")
SOURCES = ("curated", "literature", "predicted")


class ReproductiveError(Exception):
    """Base reproductive error."""


@dataclass
class ReproductiveDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_organs: List[str] = field(default_factory=list)
    hormones: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise ReproductiveError("disease_id required")
        if self.category not in REPRO_CATEGORIES:
            raise ReproductiveError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise ReproductiveError(f"invalid source: {self.source!r}")
        for o in self.affected_organs:
            if o not in REPRO_ORGANS:
                raise ReproductiveError(f"invalid affected_organ: {o!r}")


class ReproductiveDiseaseEngine:
    """Registry with organ / hormone / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, ReproductiveDisease] = {}
        self._organ_index: Dict[str, List[str]] = {}
        self._hormone_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: ReproductiveDisease) -> ReproductiveDisease:
        if disease.disease_id in self._diseases:
            raise ReproductiveError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for o in disease.affected_organs:
            self._organ_index.setdefault(o, []).append(disease.disease_id)
        for h in disease.hormones:
            self._hormone_index.setdefault(h, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> ReproductiveDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise ReproductiveError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[ReproductiveDisease]:
        if category not in REPRO_CATEGORIES:
            raise ReproductiveError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_organ(self, organ: str) -> List[ReproductiveDisease]:
        if organ not in REPRO_ORGANS:
            raise ReproductiveError(f"invalid organ: {organ!r}")
        return [self.get(did) for did in self._organ_index.get(organ, [])]

    def by_hormone(self, hormone: str) -> List[ReproductiveDisease]:
        return [self.get(did) for did in self._hormone_index.get(hormone, [])]

    def by_gene(self, gene_symbol: str) -> List[ReproductiveDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "organs": len(self._organ_index),
            "hormones": len(self._hormone_index),
            "genes": len(self._gene_index),
        }


def self_test() -> bool:
    engine = ReproductiveDiseaseEngine()
    engine.add(ReproductiveDisease(
        "D_pcos", "Polycystic ovary syndrome", "female_reproductive",
        affected_organs=["ovary"],
        hormones=["LH", "FSH", "testosterone"],
        biomarkers=["AMH"],
        gene_associations=["DENND1A"]))
    engine.add(ReproductiveDisease(
        "D_endo", "Endometriosis", "female_reproductive",
        affected_organs=["uterus", "ovary"],
        biomarkers=["CA-125"],
        gene_associations=["GREB1"]))
    engine.add(ReproductiveDisease(
        "D_bph", "Benign prostatic hyperplasia", "male_reproductive",
        affected_organs=["prostate"],
        hormones=["DHT"],
        biomarkers=["PSA"]))
    assert len(engine.by_category("female_reproductive")) == 2
    assert engine.by_organ("prostate")[0].disease_id == "D_bph"
    assert engine.by_hormone("LH")[0].disease_id == "D_pcos"
    assert engine.by_gene("GREB1")[0].disease_id == "D_endo"
    assert engine.stats()["diseases"] == 3
    print("reproductive_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
