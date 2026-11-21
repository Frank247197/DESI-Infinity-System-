"""DESI Infinity System - Respiratory Disease Engine (v6.2.0).

Stores respiratory diseases across obstructive, restrictive, infectious,
vascular, and neoplastic categories, with affected lung structures,
exposure risk factors, and biomarkers.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

RESP_CATEGORIES = ("obstructive", "restrictive", "infectious", "vascular",
                   "neoplastic", "interstitial", "pleural", "other")
SOURCES = ("curated", "literature", "predicted")


class RespiratoryError(Exception):
    """Base respiratory error."""


@dataclass
class RespiratoryDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_structures: List[str] = field(default_factory=list)
    exposures: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise RespiratoryError("disease_id required")
        if self.category not in RESP_CATEGORIES:
            raise RespiratoryError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise RespiratoryError(f"invalid source: {self.source!r}")


class RespiratoryDiseaseEngine:
    """Registry with structure / exposure / biomarker / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, RespiratoryDisease] = {}
        self._structure_index: Dict[str, List[str]] = {}
        self._exposure_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: RespiratoryDisease) -> RespiratoryDisease:
        if disease.disease_id in self._diseases:
            raise RespiratoryError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for s in disease.affected_structures:
            self._structure_index.setdefault(s, []).append(disease.disease_id)
        for e in disease.exposures:
            self._exposure_index.setdefault(e, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> RespiratoryDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise RespiratoryError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[RespiratoryDisease]:
        if category not in RESP_CATEGORIES:
            raise RespiratoryError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_structure(self, structure: str) -> List[RespiratoryDisease]:
        return [self.get(did) for did in self._structure_index.get(structure, [])]

    def by_exposure(self, exposure: str) -> List[RespiratoryDisease]:
        return [self.get(did) for did in self._exposure_index.get(exposure, [])]

    def by_gene(self, gene_symbol: str) -> List[RespiratoryDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "structures": len(self._structure_index),
            "exposures": len(self._exposure_index),
            "genes": len(self._gene_index),
        }


def self_test() -> bool:
    engine = RespiratoryDiseaseEngine()
    engine.add(RespiratoryDisease(
        "D_copd", "COPD", "obstructive",
        affected_structures=["alveoli", "bronchioles"],
        exposures=["smoking", "biomass_fuel"],
        biomarkers=["FEV1"],
        gene_associations=["CHRNA3"]))
    engine.add(RespiratoryDisease(
        "D_asthma", "Asthma", "obstructive",
        affected_structures=["bronchi"],
        exposures=["allergens"],
        biomarkers=["IgE", "FeNO"]))
    assert len(engine.by_category("obstructive")) == 2
    assert engine.by_structure("alveoli")[0].disease_id == "D_copd"
    assert engine.by_exposure("smoking")[0].disease_id == "D_copd"
    assert engine.by_gene("CHRNA3")[0].disease_id == "D_copd"
    print("respiratory_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
