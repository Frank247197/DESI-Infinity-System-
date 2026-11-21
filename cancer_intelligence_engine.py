"""DESI Infinity System - Cancer Intelligence Engine (v6.2.0).

Stores cancer entities with tissue of origin, histologic classification,
stage systems, driver genes, and therapeutic categories. Research-only;
no treatment recommendation, dosing, or diagnosis.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

TISSUES = ("lung", "breast", "colon", "prostate", "pancreas", "liver",
           "kidney", "bladder", "ovary", "uterus", "cervix", "stomach",
           "esophagus", "thyroid", "skin", "brain", "blood", "lymph_node",
           "bone", "soft_tissue", "other")
HISTOLOGY = ("adenocarcinoma", "squamous_cell", "small_cell", "large_cell",
             "ductal", "lobular", "lymphoma", "leukemia", "sarcoma",
             "melanoma", "glioma", "other")
STAGE_SYSTEMS = ("TNM", "FIGO", "Ann_Arbor", "ISS", "other", "unknown")
SOURCES = ("curated", "literature", "predicted")


class CancerError(Exception):
    """Base cancer intelligence error."""


@dataclass
class CancerEntity:
    cancer_id: str
    name: str
    tissue_of_origin: str
    histology: str = "other"
    stage_system: str = "unknown"
    driver_genes: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    therapeutic_categories: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.cancer_id or not isinstance(self.cancer_id, str):
            raise CancerError("cancer_id required")
        if self.tissue_of_origin not in TISSUES:
            raise CancerError(f"invalid tissue_of_origin: {self.tissue_of_origin!r}")
        if self.histology not in HISTOLOGY:
            raise CancerError(f"invalid histology: {self.histology!r}")
        if self.stage_system not in STAGE_SYSTEMS:
            raise CancerError(f"invalid stage_system: {self.stage_system!r}")
        if self.source not in SOURCES:
            raise CancerError(f"invalid source: {self.source!r}")


class CancerIntelligenceEngine:
    """Registry with tissue / histology / driver-gene queries."""

    def __init__(self) -> None:
        self._cancers: Dict[str, CancerEntity] = {}
        self._tissue_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}
        self._histology_index: Dict[str, List[str]] = {}

    def add(self, cancer: CancerEntity) -> CancerEntity:
        if cancer.cancer_id in self._cancers:
            raise CancerError(f"duplicate cancer_id: {cancer.cancer_id}")
        self._cancers[cancer.cancer_id] = cancer
        self._tissue_index.setdefault(cancer.tissue_of_origin, []).append(cancer.cancer_id)
        self._histology_index.setdefault(cancer.histology, []).append(cancer.cancer_id)
        for g in cancer.driver_genes:
            self._gene_index.setdefault(g, []).append(cancer.cancer_id)
        return cancer

    def get(self, cancer_id: str) -> CancerEntity:
        try:
            return self._cancers[cancer_id]
        except KeyError as exc:
            raise CancerError(f"unknown cancer_id: {cancer_id}") from exc

    def by_tissue(self, tissue: str) -> List[CancerEntity]:
        if tissue not in TISSUES:
            raise CancerError(f"invalid tissue: {tissue!r}")
        return [self.get(cid) for cid in self._tissue_index.get(tissue, [])]

    def by_histology(self, histology: str) -> List[CancerEntity]:
        if histology not in HISTOLOGY:
            raise CancerError(f"invalid histology: {histology!r}")
        return [self.get(cid) for cid in self._histology_index.get(histology, [])]

    def by_driver_gene(self, gene_symbol: str) -> List[CancerEntity]:
        return [self.get(cid) for cid in self._gene_index.get(gene_symbol, [])]

    def shared_drivers(self, cancer_a: str, cancer_b: str) -> List[str]:
        a = set(self.get(cancer_a).driver_genes)
        b = set(self.get(cancer_b).driver_genes)
        return sorted(a & b)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "cancers": len(self._cancers),
            "tissues": len(self._tissue_index),
            "driver_genes": len(self._gene_index),
        }


def self_test() -> bool:
    engine = CancerIntelligenceEngine()
    engine.add(CancerEntity(
        "C_luad", "Lung adenocarcinoma", "lung", "adenocarcinoma", "TNM",
        driver_genes=["EGFR", "KRAS", "ALK"],
        biomarkers=["PD-L1"],
        therapeutic_categories=["targeted", "immunotherapy"]))
    engine.add(CancerEntity(
        "C_brca", "Breast invasive carcinoma", "breast", "ductal", "TNM",
        driver_genes=["BRCA1", "BRCA2", "HER2"],
        biomarkers=["ER", "PR", "HER2"]))
    assert engine.by_tissue("lung")[0].cancer_id == "C_luad"
    assert engine.by_histology("ductal")[0].cancer_id == "C_brca"
    assert engine.by_driver_gene("EGFR")[0].cancer_id == "C_luad"
    assert engine.shared_drivers("C_luad", "C_brca") == []
    assert engine.stats()["cancers"] == 2
    print("cancer_intelligence_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
