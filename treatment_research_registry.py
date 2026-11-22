"""DESI Infinity System - Treatment Research Registry (v6.2.0).

Registry of research-scoped treatment approaches with mechanism summary,
evidence class, and status. NO prescribing, NO dosing, NO patient-specific
recommendations. Research catalogue only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

TREATMENT_CATEGORIES = ("small_molecule", "biologic", "gene_therapy",
                        "cell_therapy", "vaccine", "surgery", "radiation",
                        "behavioral", "dietary", "device", "other")
EVIDENCE_LEVELS = ("established", "emerging", "experimental", "hypothetical")
RESEARCH_STATUS = ("approved", "in_trials", "preclinical", "discontinued",
                   "withdrawn", "unknown")
SOURCES = ("curated", "literature", "predicted")


class TreatmentRegistryError(Exception):
    """Base treatment registry error."""


@dataclass
class TreatmentRecord:
    treatment_id: str
    name: str
    category: str
    disease_ids: List[str] = field(default_factory=list)
    mechanism_summary: str = ""
    evidence_level: str = "emerging"
    research_status: str = "unknown"
    biomarker_requirements: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.treatment_id or not isinstance(self.treatment_id, str):
            raise TreatmentRegistryError("treatment_id required")
        if not self.name or not isinstance(self.name, str):
            raise TreatmentRegistryError("name required")
        if self.category not in TREATMENT_CATEGORIES:
            raise TreatmentRegistryError(f"invalid category: {self.category!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise TreatmentRegistryError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.research_status not in RESEARCH_STATUS:
            raise TreatmentRegistryError(
                f"invalid research_status: {self.research_status!r}")
        if self.source not in SOURCES:
            raise TreatmentRegistryError(f"invalid source: {self.source!r}")


class TreatmentResearchRegistry:
    """Treatment catalogue with category / disease / status queries."""

    def __init__(self) -> None:
        self._treatments: Dict[str, TreatmentRecord] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._category_index: Dict[str, List[str]] = {}

    def add(self, treatment: TreatmentRecord) -> TreatmentRecord:
        if treatment.treatment_id in self._treatments:
            raise TreatmentRegistryError(
                f"duplicate treatment_id: {treatment.treatment_id}")
        self._treatments[treatment.treatment_id] = treatment
        self._category_index.setdefault(treatment.category, []).append(
            treatment.treatment_id)
        for did in treatment.disease_ids:
            self._disease_index.setdefault(did, []).append(treatment.treatment_id)
        return treatment

    def get(self, treatment_id: str) -> TreatmentRecord:
        try:
            return self._treatments[treatment_id]
        except KeyError as exc:
            raise TreatmentRegistryError(
                f"unknown treatment_id: {treatment_id}") from exc

    def for_disease(self, disease_id: str) -> List[TreatmentRecord]:
        return [self.get(t) for t in self._disease_index.get(disease_id, [])]

    def by_category(self, category: str) -> List[TreatmentRecord]:
        if category not in TREATMENT_CATEGORIES:
            raise TreatmentRegistryError(f"invalid category: {category!r}")
        return [self.get(t) for t in self._category_index.get(category, [])]

    def by_evidence(self, level: str) -> List[TreatmentRecord]:
        if level not in EVIDENCE_LEVELS:
            raise TreatmentRegistryError(f"invalid evidence_level: {level!r}")
        return [t for t in self._treatments.values() if t.evidence_level == level]

    def by_status(self, status: str) -> List[TreatmentRecord]:
        if status not in RESEARCH_STATUS:
            raise TreatmentRegistryError(f"invalid research_status: {status!r}")
        return [t for t in self._treatments.values() if t.research_status == status]

    def experimental(self) -> List[TreatmentRecord]:
        return self.by_evidence("experimental") + self.by_evidence("hypothetical")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "treatments": len(self._treatments),
            "diseases": len(self._disease_index),
            "categories": len(self._category_index),
            "experimental": len(self.experimental()),
        }


def self_test() -> bool:
    registry = TreatmentResearchRegistry()
    registry.add(TreatmentRecord(
        "T1", "Imatinib", "small_molecule",
        disease_ids=["D_cml"], mechanism_summary="BCR-ABL1 inhibitor",
        evidence_level="established", research_status="approved"))
    registry.add(TreatmentRecord(
        "T2", "CAR-T CD19", "cell_therapy",
        disease_ids=["D_dlbcl"], mechanism_summary="engineered T cells",
        evidence_level="established", research_status="approved"))
    registry.add(TreatmentRecord(
        "T3", "Investigational CRISPR", "gene_therapy",
        disease_ids=["D_scd"], mechanism_summary="HBB editing",
        evidence_level="experimental", research_status="in_trials"))
    assert len(registry.for_disease("D_cml")) == 1
    assert len(registry.by_category("cell_therapy")) == 1
    assert len(registry.by_evidence("established")) == 2
    assert len(registry.by_status("in_trials")) == 1
    assert len(registry.experimental()) == 1
    print("treatment_research_registry: OK")
    return True


if __name__ == "__main__":
    self_test()
