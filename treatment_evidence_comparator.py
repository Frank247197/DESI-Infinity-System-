"""DESI Infinity System - Treatment Evidence Comparator (v6.2.0).

Side-by-side comparison of documented evidence for multiple treatment
approaches across a disease. Presents documented evidence, limitations,
and research status — NOT clinical ranking for a specific patient.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

EVIDENCE_LEVELS = ("high", "moderate", "low", "very_low", "unknown")
RESEARCH_STATUS = ("approved", "in_trials", "preclinical", "discontinued",
                   "unknown")
SOURCES = ("curated", "literature", "predicted")


class TreatmentEvidenceError(Exception):
    """Base treatment evidence error."""


@dataclass
class TreatmentEvidence:
    evidence_id: str
    treatment_id: str
    disease_id: str
    evidence_level: str = "unknown"
    research_status: str = "unknown"
    population_studied: str = ""
    documented_limitations: List[str] = field(default_factory=list)
    outcome_notes: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.evidence_id or not isinstance(self.evidence_id, str):
            raise TreatmentEvidenceError("evidence_id required")
        if not self.treatment_id or not isinstance(self.treatment_id, str):
            raise TreatmentEvidenceError("treatment_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise TreatmentEvidenceError("disease_id required")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise TreatmentEvidenceError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.research_status not in RESEARCH_STATUS:
            raise TreatmentEvidenceError(
                f"invalid research_status: {self.research_status!r}")
        if self.source not in SOURCES:
            raise TreatmentEvidenceError(f"invalid source: {self.source!r}")


class TreatmentEvidenceComparator:
    """Comparison engine across treatment approaches per disease."""

    def __init__(self) -> None:
        self._evidence: Dict[str, TreatmentEvidence] = {}
        self._treatment_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, evidence: TreatmentEvidence) -> TreatmentEvidence:
        if evidence.evidence_id in self._evidence:
            raise TreatmentEvidenceError(
                f"duplicate evidence_id: {evidence.evidence_id}")
        self._evidence[evidence.evidence_id] = evidence
        self._treatment_index.setdefault(evidence.treatment_id, []).append(
            evidence.evidence_id)
        self._disease_index.setdefault(evidence.disease_id, []).append(
            evidence.evidence_id)
        return evidence

    def get(self, evidence_id: str) -> TreatmentEvidence:
        try:
            return self._evidence[evidence_id]
        except KeyError as exc:
            raise TreatmentEvidenceError(
                f"unknown evidence_id: {evidence_id}") from exc

    def for_treatment(self, treatment_id: str) -> List[TreatmentEvidence]:
        return [self.get(e) for e in self._treatment_index.get(treatment_id, [])]

    def for_disease(self, disease_id: str) -> List[TreatmentEvidence]:
        return [self.get(e) for e in self._disease_index.get(disease_id, [])]

    def compare(self, disease_id: str) -> List[Dict[str, object]]:
        rows = []
        for e in self.for_disease(disease_id):
            rows.append({
                "treatment_id": e.treatment_id,
                "evidence_level": e.evidence_level,
                "research_status": e.research_status,
                "population_studied": e.population_studied,
                "documented_limitations": list(e.documented_limitations),
                "outcome_notes": e.outcome_notes,
            })
        return rows

    def by_evidence_level(self, level: str) -> List[TreatmentEvidence]:
        if level not in EVIDENCE_LEVELS:
            raise TreatmentEvidenceError(f"invalid evidence_level: {level!r}")
        return [e for e in self._evidence.values() if e.evidence_level == level]

    def approved(self) -> List[TreatmentEvidence]:
        return [e for e in self._evidence.values()
                if e.research_status == "approved"]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "evidence": len(self._evidence),
            "treatments": len(self._treatment_index),
            "diseases": len(self._disease_index),
            "approved": len(self.approved()),
        }


def self_test() -> bool:
    comp = TreatmentEvidenceComparator()
    comp.add(TreatmentEvidence(
        "TE1", "T_metformin", "D_t2d", "high", "approved",
        population_studied="adults, overweight",
        documented_limitations=["GI intolerance", "B12 deficiency"],
        outcome_notes="HbA1c reduction"))
    comp.add(TreatmentEvidence(
        "TE2", "T_glp1", "D_t2d", "high", "approved",
        population_studied="adults with CV disease",
        documented_limitations=["cost", "GI effects"],
        outcome_notes="HbA1c and CV risk reduction"))
    comp.add(TreatmentEvidence(
        "TE3", "T_islet", "D_t2d", "low", "in_trials",
        documented_limitations=["immunosuppression"]))
    assert len(comp.for_treatment("T_metformin")) == 1
    assert len(comp.for_disease("D_t2d")) == 3
    rows = comp.compare("D_t2d")
    assert len(rows) == 3
    assert len(comp.by_evidence_level("high")) == 2
    assert len(comp.approved()) == 2
    print("treatment_evidence_comparator: OK")
    return True


if __name__ == "__main__":
    self_test()
