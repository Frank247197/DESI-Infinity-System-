"""DESI Infinity System - Diagnostic Biomarker Validator (v6.2.0).

Structured evaluation of diagnostic biomarker performance against
validation criteria (sensitivity, specificity, AUC, cohort size,
replication). Research evaluation only — no clinical clearance claims.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

VALIDATION_TIERS = ("discovery", "internal_validation", "external_validation",
                    "prospective", "regulatory_grade")
SOURCES = ("curated", "literature", "predicted")


class BiomarkerValidationError(Exception):
    """Base biomarker validation error."""


@dataclass
class ValidationEvidence:
    evidence_id: str
    biomarker_id: str
    disease_id: str
    tier: str
    sensitivity: float
    specificity: float
    auc: float
    cohort_size: int
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id or not isinstance(self.evidence_id, str):
            raise BiomarkerValidationError("evidence_id required")
        if not self.biomarker_id or not isinstance(self.biomarker_id, str):
            raise BiomarkerValidationError("biomarker_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise BiomarkerValidationError("disease_id required")
        if self.tier not in VALIDATION_TIERS:
            raise BiomarkerValidationError(f"invalid tier: {self.tier!r}")
        if self.source not in SOURCES:
            raise BiomarkerValidationError(f"invalid source: {self.source!r}")
        for label, val in (("sensitivity", self.sensitivity),
                           ("specificity", self.specificity),
                           ("auc", self.auc)):
            if not isinstance(val, (int, float)) or not 0.0 <= float(val) <= 1.0:
                raise BiomarkerValidationError(f"{label} must be in [0, 1]")
        if not isinstance(self.cohort_size, int) or self.cohort_size <= 0:
            raise BiomarkerValidationError("cohort_size must be positive int")

    def tier_rank(self) -> int:
        return VALIDATION_TIERS.index(self.tier)

    def passes(self, min_auc: float = 0.8, min_cohort: int = 100) -> bool:
        return self.auc >= min_auc and self.cohort_size >= min_cohort


class DiagnosticBiomarkerValidator:
    """Validation evidence store with tier and performance queries."""

    def __init__(self) -> None:
        self._evidence: Dict[str, ValidationEvidence] = {}
        self._biomarker_index: Dict[str, List[str]] = {}

    def add(self, evidence: ValidationEvidence) -> ValidationEvidence:
        if evidence.evidence_id in self._evidence:
            raise BiomarkerValidationError(
                f"duplicate evidence_id: {evidence.evidence_id}")
        self._evidence[evidence.evidence_id] = evidence
        self._biomarker_index.setdefault(evidence.biomarker_id, []).append(
            evidence.evidence_id)
        return evidence

    def get(self, evidence_id: str) -> ValidationEvidence:
        try:
            return self._evidence[evidence_id]
        except KeyError as exc:
            raise BiomarkerValidationError(
                f"unknown evidence_id: {evidence_id}") from exc

    def for_biomarker(self, biomarker_id: str) -> List[ValidationEvidence]:
        return [self.get(e) for e in self._biomarker_index.get(biomarker_id, [])]

    def strongest_tier(self, biomarker_id: str) -> str:
        recs = self.for_biomarker(biomarker_id)
        if not recs:
            return "none"
        return max(recs, key=lambda e: e.tier_rank()).tier

    def passing(self, min_auc: float = 0.8, min_cohort: int = 100
                ) -> List[ValidationEvidence]:
        return [e for e in self._evidence.values() if e.passes(min_auc, min_cohort)]

    def by_tier(self, tier: str) -> List[ValidationEvidence]:
        if tier not in VALIDATION_TIERS:
            raise BiomarkerValidationError(f"invalid tier: {tier!r}")
        return [e for e in self._evidence.values() if e.tier == tier]

    def regulatory_grade(self) -> List[ValidationEvidence]:
        return self.by_tier("regulatory_grade")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "evidence": len(self._evidence),
            "biomarkers": len(self._biomarker_index),
            "regulatory_grade": len(self.regulatory_grade()),
        }


def self_test() -> bool:
    validator = DiagnosticBiomarkerValidator()
    validator.add(ValidationEvidence(
        "VE1", "B1", "D_t2d", "external_validation",
        sensitivity=0.85, specificity=0.88, auc=0.89, cohort_size=1200))
    validator.add(ValidationEvidence(
        "VE2", "B1", "D_t2d", "discovery",
        sensitivity=0.7, specificity=0.75, auc=0.72, cohort_size=80))
    validator.add(ValidationEvidence(
        "VE3", "B2", "D_mi", "regulatory_grade",
        sensitivity=0.95, specificity=0.96, auc=0.97, cohort_size=5000))
    assert len(validator.for_biomarker("B1")) == 2
    assert validator.strongest_tier("B1") == "external_validation"
    assert len(validator.passing()) == 2
    assert len(validator.by_tier("discovery")) == 1
    assert len(validator.regulatory_grade()) == 1
    print("diagnostic_biomarker_validator: OK")
    return True


if __name__ == "__main__":
    self_test()
