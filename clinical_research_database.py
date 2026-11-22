"""DESI Infinity System - Clinical Research Database (v6.2.0).

Registry of de-identified, research-scoped study records (cohorts,
endpoints, measurements). NO patient-identifying data. NO clinical
decision support.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STUDY_DESIGNS = ("observational", "cohort", "case_control", "cross_sectional",
                 "rct", "pragmatic_trial", "other")
ENDPOINT_TYPES = ("primary", "secondary", "exploratory", "safety")
SOURCES = ("curated", "literature", "predicted")


class ClinicalResearchError(Exception):
    """Base clinical research error."""


@dataclass
class StudyEndpoint:
    endpoint_id: str
    name: str
    endpoint_type: str = "primary"
    measurement_unit: str = ""
    description: str = ""

    def __post_init__(self) -> None:
        if not self.endpoint_id or not isinstance(self.endpoint_id, str):
            raise ClinicalResearchError("endpoint_id required")
        if not self.name or not isinstance(self.name, str):
            raise ClinicalResearchError("name required")
        if self.endpoint_type not in ENDPOINT_TYPES:
            raise ClinicalResearchError(
                f"invalid endpoint_type: {self.endpoint_type!r}")


@dataclass
class ClinicalStudy:
    study_id: str
    title: str
    disease_id: str
    design: str = "observational"
    population_size: int = 0
    follow_up_months: float = 0.0
    endpoints: List[StudyEndpoint] = field(default_factory=list)
    publication_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.study_id or not isinstance(self.study_id, str):
            raise ClinicalResearchError("study_id required")
        if not self.title or not isinstance(self.title, str):
            raise ClinicalResearchError("title required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise ClinicalResearchError("disease_id required")
        if self.design not in STUDY_DESIGNS:
            raise ClinicalResearchError(f"invalid design: {self.design!r}")
        if self.source not in SOURCES:
            raise ClinicalResearchError(f"invalid source: {self.source!r}")
        if not isinstance(self.population_size, int) or self.population_size < 0:
            raise ClinicalResearchError("population_size must be non-negative int")
        if self.follow_up_months < 0:
            raise ClinicalResearchError("follow_up_months must be non-negative")


class ClinicalResearchDatabase:
    """Study registry with design / disease / endpoint queries."""

    def __init__(self) -> None:
        self._studies: Dict[str, ClinicalStudy] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._design_index: Dict[str, List[str]] = {}

    def add(self, study: ClinicalStudy) -> ClinicalStudy:
        if study.study_id in self._studies:
            raise ClinicalResearchError(f"duplicate study_id: {study.study_id}")
        self._studies[study.study_id] = study
        self._disease_index.setdefault(study.disease_id, []).append(study.study_id)
        self._design_index.setdefault(study.design, []).append(study.study_id)
        return study

    def get(self, study_id: str) -> ClinicalStudy:
        try:
            return self._studies[study_id]
        except KeyError as exc:
            raise ClinicalResearchError(f"unknown study_id: {study_id}") from exc

    def for_disease(self, disease_id: str) -> List[ClinicalStudy]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def by_design(self, design: str) -> List[ClinicalStudy]:
        if design not in STUDY_DESIGNS:
            raise ClinicalResearchError(f"invalid design: {design!r}")
        return [self.get(s) for s in self._design_index.get(design, [])]

    def large_studies(self, min_population: int = 1000) -> List[ClinicalStudy]:
        return [s for s in self._studies.values()
                if s.population_size >= min_population]

    def with_primary_endpoint(self, endpoint_name: str) -> List[ClinicalStudy]:
        return [s for s in self._studies.values()
                if any(e.name == endpoint_name and e.endpoint_type == "primary"
                       for e in s.endpoints)]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "studies": len(self._studies),
            "diseases": len(self._disease_index),
            "designs": len(self._design_index),
        }


def self_test() -> bool:
    db = ClinicalResearchDatabase()
    db.add(ClinicalStudy(
        "S1", "Metformin CV outcomes", "D_t2d", "rct",
        population_size=10000, follow_up_months=60,
        endpoints=[
            StudyEndpoint("E1", "MACE", "primary", "events"),
            StudyEndpoint("E2", "HbA1c change", "secondary", "%"),
        ]))
    db.add(ClinicalStudy(
        "S2", "T2D cohort study", "D_t2d", "cohort",
        population_size=2500, follow_up_months=36,
        endpoints=[StudyEndpoint("E3", "Incident CVD", "primary", "events")]))
    assert len(db.for_disease("D_t2d")) == 2
    assert len(db.by_design("rct")) == 1
    assert len(db.large_studies()) == 2
    assert len(db.with_primary_endpoint("MACE")) == 1
    print("clinical_research_database: OK")
    return True


if __name__ == "__main__":
    self_test()
