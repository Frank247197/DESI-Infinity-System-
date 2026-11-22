"""DESI Infinity System - Precision Medicine Analyzer (v6.2.0).

Research-level precision medicine analysis: molecular stratification,
cohort definitions, predictive biomarker readiness. NO clinical
recommendation, NO patient-specific guidance.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STRATIFICATION_TYPES = ("molecular_subtype", "genomic_signature",
                        "expression_cluster", "immune_phenotype",
                        "pharmacogenomic", "other")
READINESS_LEVELS = ("research_only", "translational", "clinical_trial_ready",
                    "clinically_validated", "unknown")
SOURCES = ("curated", "literature", "predicted")


class PrecisionMedicineError(Exception):
    """Base precision medicine error."""


@dataclass
class StratificationScheme:
    scheme_id: str
    disease_id: str
    name: str
    stratification_type: str
    defining_features: List[str] = field(default_factory=list)
    readiness: str = "research_only"
    cohort_size: int = 0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.scheme_id or not isinstance(self.scheme_id, str):
            raise PrecisionMedicineError("scheme_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise PrecisionMedicineError("disease_id required")
        if not self.name or not isinstance(self.name, str):
            raise PrecisionMedicineError("name required")
        if self.stratification_type not in STRATIFICATION_TYPES:
            raise PrecisionMedicineError(
                f"invalid stratification_type: {self.stratification_type!r}")
        if self.readiness not in READINESS_LEVELS:
            raise PrecisionMedicineError(f"invalid readiness: {self.readiness!r}")
        if self.source not in SOURCES:
            raise PrecisionMedicineError(f"invalid source: {self.source!r}")
        if not isinstance(self.cohort_size, int) or self.cohort_size < 0:
            raise PrecisionMedicineError("cohort_size must be non-negative int")


class PrecisionMedicineAnalyzer:
    """Scheme registry with type / readiness / feature queries."""

    def __init__(self) -> None:
        self._schemes: Dict[str, StratificationScheme] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}

    def add(self, scheme: StratificationScheme) -> StratificationScheme:
        if scheme.scheme_id in self._schemes:
            raise PrecisionMedicineError(f"duplicate scheme_id: {scheme.scheme_id}")
        self._schemes[scheme.scheme_id] = scheme
        self._disease_index.setdefault(scheme.disease_id, []).append(scheme.scheme_id)
        self._type_index.setdefault(scheme.stratification_type, []).append(
            scheme.scheme_id)
        return scheme

    def get(self, scheme_id: str) -> StratificationScheme:
        try:
            return self._schemes[scheme_id]
        except KeyError as exc:
            raise PrecisionMedicineError(f"unknown scheme_id: {scheme_id}") from exc

    def for_disease(self, disease_id: str) -> List[StratificationScheme]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def by_type(self, stratification_type: str) -> List[StratificationScheme]:
        if stratification_type not in STRATIFICATION_TYPES:
            raise PrecisionMedicineError(
                f"invalid stratification_type: {stratification_type!r}")
        return [self.get(s) for s in self._type_index.get(stratification_type, [])]

    def by_readiness(self, readiness: str) -> List[StratificationScheme]:
        if readiness not in READINESS_LEVELS:
            raise PrecisionMedicineError(f"invalid readiness: {readiness!r}")
        return [s for s in self._schemes.values() if s.readiness == readiness]

    def clinically_validated(self) -> List[StratificationScheme]:
        return self.by_readiness("clinically_validated")

    def large_cohort(self, min_cohort: int = 500) -> List[StratificationScheme]:
        return [s for s in self._schemes.values() if s.cohort_size >= min_cohort]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "schemes": len(self._schemes),
            "diseases": len(self._disease_index),
            "clinically_validated": len(self.clinically_validated()),
        }


def self_test() -> bool:
    analyzer = PrecisionMedicineAnalyzer()
    analyzer.add(StratificationScheme(
        "PAM50", "D_breast_cancer", "PAM50 intrinsic subtypes",
        "expression_cluster", ["Luminal_A", "Luminal_B", "HER2", "Basal"],
        readiness="clinically_validated", cohort_size=5000))
    analyzer.add(StratificationScheme(
        "MSI", "D_colorectal", "MSI-H status",
        "genomic_signature", ["MSI_H", "MSS"],
        readiness="clinically_validated", cohort_size=3000))
    analyzer.add(StratificationScheme(
        "SC_melanoma", "D_melanoma", "Melanoma immune subtype",
        "immune_phenotype", ["hot", "cold"],
        readiness="translational", cohort_size=200))
    assert len(analyzer.for_disease("D_breast_cancer")) == 1
    assert len(analyzer.by_type("genomic_signature")) == 1
    assert len(analyzer.clinically_validated()) == 2
    assert len(analyzer.large_cohort(1000)) == 2
    print("precision_medicine_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
