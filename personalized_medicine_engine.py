"""DESI Infinity System - Personalized Medicine Engine (v6.2.0).

Research store for personalized-medicine strategy categories (biomarker-
guided, pharmacogenomic, tumor-genomic, immune-profiling). NO patient-
specific recommendations, NO clinical decision support.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PERSONALIZATION_TYPES = ("biomarker_guided", "pharmacogenomic",
                         "tumor_genomic", "immune_profiling",
                         "rare_disease_genomic", "other")
EVIDENCE_LEVELS = ("established", "emerging", "experimental", "hypothetical")
SOURCES = ("curated", "literature", "predicted")


class PersonalizedMedicineError(Exception):
    """Base personalized medicine error."""


@dataclass
class PersonalizedStrategy:
    strategy_id: str
    disease_id: str
    name: str
    personalization_type: str
    required_markers: List[str] = field(default_factory=list)
    evidence_level: str = "emerging"
    research_notes: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.strategy_id or not isinstance(self.strategy_id, str):
            raise PersonalizedMedicineError("strategy_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise PersonalizedMedicineError("disease_id required")
        if not self.name or not isinstance(self.name, str):
            raise PersonalizedMedicineError("name required")
        if self.personalization_type not in PERSONALIZATION_TYPES:
            raise PersonalizedMedicineError(
                f"invalid personalization_type: {self.personalization_type!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise PersonalizedMedicineError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise PersonalizedMedicineError(f"invalid source: {self.source!r}")


class PersonalizedMedicineEngine:
    """Strategy registry with type / disease / marker / evidence queries."""

    def __init__(self) -> None:
        self._strategies: Dict[str, PersonalizedStrategy] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._marker_index: Dict[str, List[str]] = {}

    def add(self, strategy: PersonalizedStrategy) -> PersonalizedStrategy:
        if strategy.strategy_id in self._strategies:
            raise PersonalizedMedicineError(
                f"duplicate strategy_id: {strategy.strategy_id}")
        self._strategies[strategy.strategy_id] = strategy
        self._disease_index.setdefault(strategy.disease_id, []).append(
            strategy.strategy_id)
        for m in strategy.required_markers:
            self._marker_index.setdefault(m, []).append(strategy.strategy_id)
        return strategy

    def get(self, strategy_id: str) -> PersonalizedStrategy:
        try:
            return self._strategies[strategy_id]
        except KeyError as exc:
            raise PersonalizedMedicineError(
                f"unknown strategy_id: {strategy_id}") from exc

    def for_disease(self, disease_id: str) -> List[PersonalizedStrategy]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def by_type(self, personalization_type: str) -> List[PersonalizedStrategy]:
        if personalization_type not in PERSONALIZATION_TYPES:
            raise PersonalizedMedicineError(
                f"invalid personalization_type: {personalization_type!r}")
        return [s for s in self._strategies.values()
                if s.personalization_type == personalization_type]

    def by_marker(self, marker: str) -> List[PersonalizedStrategy]:
        return [self.get(s) for s in self._marker_index.get(marker, [])]

    def by_evidence(self, level: str) -> List[PersonalizedStrategy]:
        if level not in EVIDENCE_LEVELS:
            raise PersonalizedMedicineError(f"invalid evidence_level: {level!r}")
        return [s for s in self._strategies.values() if s.evidence_level == level]

    def established(self) -> List[PersonalizedStrategy]:
        return self.by_evidence("established")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "strategies": len(self._strategies),
            "diseases": len(self._disease_index),
            "markers": len(self._marker_index),
            "established": len(self.established()),
        }


def self_test() -> bool:
    engine = PersonalizedMedicineEngine()
    engine.add(PersonalizedStrategy(
        "PS1", "D_breast_cancer", "HER2-targeted therapy",
        "biomarker_guided",
        required_markers=["HER2"], evidence_level="established"))
    engine.add(PersonalizedStrategy(
        "PS2", "D_breast_cancer", "BRCA1/2 PARP inhibitor",
        "tumor_genomic",
        required_markers=["BRCA1", "BRCA2"], evidence_level="established"))
    engine.add(PersonalizedStrategy(
        "PS3", "D_melanoma", "PD-L1 guided checkpoint",
        "immune_profiling",
        required_markers=["PD-L1"], evidence_level="established"))
    engine.add(PersonalizedStrategy(
        "PS4", "D_aml", "FLT3-inhibitor guided",
        "tumor_genomic",
        required_markers=["FLT3_ITD"], evidence_level="emerging"))
    assert len(engine.for_disease("D_breast_cancer")) == 2
    assert len(engine.by_type("tumor_genomic")) == 2
    assert len(engine.by_marker("HER2")) == 1
    assert len(engine.by_evidence("established")) == 3
    assert len(engine.established()) == 3
    print("personalized_medicine_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
