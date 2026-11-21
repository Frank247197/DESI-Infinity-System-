"""DESI Infinity System - Cardiovascular Disease Engine (v6.2.0).

Stores cardiovascular diseases with risk markers, affected structures,
biomarkers, and gene associations. Research data only — no clinical guidance.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CVD_SUBTYPES = ("coronary_artery", "cerebrovascular", "peripheral_artery",
                "cardiomyopathy", "arrhythmia", "valvular", "congenital",
                "venous_thromboembolism", "other")
SOURCES = ("curated", "literature", "predicted")


class CardiovascularError(Exception):
    """Base cardiovascular error."""


@dataclass
class CardiovascularDisease:
    disease_id: str
    name: str
    subtype: str = "other"
    affected_structures: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise CardiovascularError("disease_id required")
        if self.subtype not in CVD_SUBTYPES:
            raise CardiovascularError(f"invalid subtype: {self.subtype!r}")
        if self.source not in SOURCES:
            raise CardiovascularError(f"invalid source: {self.source!r}")


class CardiovascularDiseaseEngine:
    """Registry with subtype / biomarker / risk factor / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, CardiovascularDisease] = {}
        self._biomarker_index: Dict[str, List[str]] = {}
        self._risk_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: CardiovascularDisease) -> CardiovascularDisease:
        if disease.disease_id in self._diseases:
            raise CardiovascularError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for b in disease.biomarkers:
            self._biomarker_index.setdefault(b, []).append(disease.disease_id)
        for r in disease.risk_factors:
            self._risk_index.setdefault(r, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> CardiovascularDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise CardiovascularError(f"unknown disease_id: {disease_id}") from exc

    def by_subtype(self, subtype: str) -> List[CardiovascularDisease]:
        if subtype not in CVD_SUBTYPES:
            raise CardiovascularError(f"invalid subtype: {subtype!r}")
        return [d for d in self._diseases.values() if d.subtype == subtype]

    def by_biomarker(self, biomarker: str) -> List[CardiovascularDisease]:
        return [self.get(did) for did in self._biomarker_index.get(biomarker, [])]

    def by_risk_factor(self, risk_factor: str) -> List[CardiovascularDisease]:
        return [self.get(did) for did in self._risk_index.get(risk_factor, [])]

    def by_gene(self, gene_symbol: str) -> List[CardiovascularDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def shared_risk_factors(self, disease_a: str, disease_b: str) -> List[str]:
        a = set(self.get(disease_a).risk_factors)
        b = set(self.get(disease_b).risk_factors)
        return sorted(a & b)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "biomarkers": len(self._biomarker_index),
            "risk_factors": len(self._risk_index),
            "genes": len(self._gene_index),
        }


def self_test() -> bool:
    engine = CardiovascularDiseaseEngine()
    engine.add(CardiovascularDisease(
        "D_mi", "Myocardial infarction", "coronary_artery",
        affected_structures=["coronary_arteries", "myocardium"],
        biomarkers=["troponin", "CK-MB"],
        risk_factors=["hypertension", "smoking", "diabetes"],
        gene_associations=["LDLR", "PCSK9"]))
    engine.add(CardiovascularDisease(
        "D_stroke", "Ischemic stroke", "cerebrovascular",
        affected_structures=["cerebral_arteries"],
        biomarkers=["D-dimer"],
        risk_factors=["hypertension", "smoking"]))
    assert engine.by_subtype("coronary_artery")[0].disease_id == "D_mi"
    assert engine.by_biomarker("troponin")[0].disease_id == "D_mi"
    assert engine.by_gene("LDLR")[0].disease_id == "D_mi"
    assert set(engine.shared_risk_factors("D_mi", "D_stroke")) == {"hypertension", "smoking"}
    assert engine.stats()["diseases"] == 2
    print("022 cardiovascular_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
