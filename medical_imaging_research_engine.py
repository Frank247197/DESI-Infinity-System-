"""DESI Infinity System - Medical Imaging Research Engine (v6.2.0).

Structured imaging research metadata: modality, body region, acquisition
protocol, findings, and radiological annotations. NO diagnostic image
interpretation — research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MODALITIES = ("ct", "mri", "pet", "spect", "xray", "ultrasound",
              "mammography", "oct", "other")
BODY_REGIONS = ("brain", "chest", "abdomen", "pelvis", "spine",
                "extremity", "neck", "whole_body", "other")
FINDING_TYPES = ("mass", "opacity", "fracture", "edema", "hemorrhage",
                 "atrophy", "calcification", "normal", "other")
SOURCES = ("curated", "literature", "predicted")


class ImagingResearchError(Exception):
    """Base imaging research error."""


@dataclass
class ImagingStudy:
    study_id: str
    modality: str
    body_region: str
    findings: List[str] = field(default_factory=list)
    finding_type: str = "other"
    disease_id: str = ""
    age_group: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.study_id or not isinstance(self.study_id, str):
            raise ImagingResearchError("study_id required")
        if self.modality not in MODALITIES:
            raise ImagingResearchError(f"invalid modality: {self.modality!r}")
        if self.body_region not in BODY_REGIONS:
            raise ImagingResearchError(
                f"invalid body_region: {self.body_region!r}")
        if self.finding_type not in FINDING_TYPES:
            raise ImagingResearchError(
                f"invalid finding_type: {self.finding_type!r}")
        if self.source not in SOURCES:
            raise ImagingResearchError(f"invalid source: {self.source!r}")


class MedicalImagingResearchEngine:
    """Imaging study registry with modality / region / finding queries."""

    def __init__(self) -> None:
        self._studies: Dict[str, ImagingStudy] = {}
        self._modality_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, study: ImagingStudy) -> ImagingStudy:
        if study.study_id in self._studies:
            raise ImagingResearchError(f"duplicate study_id: {study.study_id}")
        self._studies[study.study_id] = study
        self._modality_index.setdefault(study.modality, []).append(study.study_id)
        if study.disease_id:
            self._disease_index.setdefault(study.disease_id, []).append(study.study_id)
        return study

    def get(self, study_id: str) -> ImagingStudy:
        try:
            return self._studies[study_id]
        except KeyError as exc:
            raise ImagingResearchError(f"unknown study_id: {study_id}") from exc

    def by_modality(self, modality: str) -> List[ImagingStudy]:
        if modality not in MODALITIES:
            raise ImagingResearchError(f"invalid modality: {modality!r}")
        return [self.get(s) for s in self._modality_index.get(modality, [])]

    def by_region(self, region: str) -> List[ImagingStudy]:
        if region not in BODY_REGIONS:
            raise ImagingResearchError(f"invalid body_region: {region!r}")
        return [s for s in self._studies.values() if s.body_region == region]

    def for_disease(self, disease_id: str) -> List[ImagingStudy]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def with_finding_type(self, finding_type: str) -> List[ImagingStudy]:
        if finding_type not in FINDING_TYPES:
            raise ImagingResearchError(
                f"invalid finding_type: {finding_type!r}")
        return [s for s in self._studies.values()
                if s.finding_type == finding_type]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "studies": len(self._studies),
            "modalities": len(self._modality_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    engine = MedicalImagingResearchEngine()
    engine.add(ImagingStudy(
        "IS1", "ct", "chest", ["ground_glass_opacity"],
        "opacity", disease_id="D_covid19"))
    engine.add(ImagingStudy(
        "IS2", "mri", "brain", ["hippocampal_atrophy"],
        "atrophy", disease_id="D_alz"))
    engine.add(ImagingStudy(
        "IS3", "mri", "brain", ["white_matter_hyperintensity"],
        "edema", disease_id="D_ms"))
    engine.add(ImagingStudy(
        "IS4", "ct", "chest", ["consolidation"],
        "opacity", disease_id="D_pneumonia"))
    assert len(engine.by_modality("mri")) == 2
    assert len(engine.by_region("chest")) == 2
    assert len(engine.for_disease("D_alz")) == 1
    assert len(engine.with_finding_type("opacity")) == 2
    assert engine.stats()["studies"] == 4
    print("medical_imaging_research_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
