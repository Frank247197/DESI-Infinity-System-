"""DESI Infinity System - Disease Biomarker Engine (v6.2.0).

Biomarker-disease associations across molecular, genetic, imaging,
clinical, cellular, and proteomic categories. Unvalidated AI hypotheses
carry source="predicted"; they are never promoted to clinical truth.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

BIOMARKER_TYPES = ("molecular", "genetic", "imaging", "clinical",
                   "cellular", "proteomic")
EVIDENCE_LEVELS = ("established", "emerging", "experimental", "hypothetical")
SOURCES = ("curated", "literature", "predicted")


class BiomarkerError(Exception):
    """Base biomarker error."""


@dataclass
class Biomarker:
    biomarker_id: str
    name: str
    biomarker_type: str
    description: str = ""
    evidence_level: str = "emerging"
    source: str = "curated"
    specificity: Optional[float] = None
    sensitivity: Optional[float] = None
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.biomarker_id or not isinstance(self.biomarker_id, str):
            raise BiomarkerError("biomarker_id required")
        if not self.name or not isinstance(self.name, str):
            raise BiomarkerError("name required")
        if self.biomarker_type not in BIOMARKER_TYPES:
            raise BiomarkerError(f"invalid biomarker_type: {self.biomarker_type!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise BiomarkerError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise BiomarkerError(f"invalid source: {self.source!r}")
        for label, val in (("specificity", self.specificity),
                           ("sensitivity", self.sensitivity)):
            if val is not None:
                if not isinstance(val, (int, float)):
                    raise BiomarkerError(f"{label} must be numeric or None")
                if not 0.0 <= float(val) <= 1.0:
                    raise BiomarkerError(f"{label} must be in [0, 1]")

    def is_prediction(self) -> bool:
        return self.source == "predicted"

    def to_dict(self) -> Dict[str, object]:
        return {
            "biomarker_id": self.biomarker_id, "name": self.name,
            "biomarker_type": self.biomarker_type,
            "evidence_level": self.evidence_level,
            "specificity": self.specificity, "sensitivity": self.sensitivity,
            "source": self.source,
        }


class DiseaseBiomarkerEngine:
    """Biomarker registry with disease linkage and evidence querying."""

    def __init__(self) -> None:
        self._biomarkers: Dict[str, Biomarker] = {}
        self._disease_map: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}

    def add(self, biomarker: Biomarker) -> Biomarker:
        if biomarker.biomarker_id in self._biomarkers:
            raise BiomarkerError(
                f"duplicate biomarker_id: {biomarker.biomarker_id}")
        self._biomarkers[biomarker.biomarker_id] = biomarker
        self._type_index.setdefault(biomarker.biomarker_type, []).append(
            biomarker.biomarker_id)
        return biomarker

    def get(self, biomarker_id: str) -> Biomarker:
        try:
            return self._biomarkers[biomarker_id]
        except KeyError as exc:
            raise BiomarkerError(f"unknown biomarker_id: {biomarker_id}") from exc

    def link_disease(self, disease_id: str, biomarker_id: str) -> None:
        self.get(biomarker_id)
        self._disease_map.setdefault(disease_id, [])
        if biomarker_id not in self._disease_map[disease_id]:
            self._disease_map[disease_id].append(biomarker_id)

    def biomarkers_for_disease(self, disease_id: str) -> List[Biomarker]:
        return [self.get(b) for b in self._disease_map.get(disease_id, [])]

    def by_type(self, biomarker_type: str) -> List[Biomarker]:
        if biomarker_type not in BIOMARKER_TYPES:
            raise BiomarkerError(f"invalid biomarker_type: {biomarker_type!r}")
        return [self.get(b) for b in self._type_index.get(biomarker_type, [])]

    def established(self) -> List[Biomarker]:
        return [b for b in self._biomarkers.values()
                if b.evidence_level == "established"]

    def predictions(self) -> List[Biomarker]:
        return [b for b in self._biomarkers.values() if b.is_prediction()]

    def high_performance(self, threshold: float = 0.85) -> List[Biomarker]:
        return [b for b in self._biomarkers.values()
                if b.specificity is not None and b.sensitivity is not None
                and b.specificity >= threshold and b.sensitivity >= threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "biomarkers": len(self._biomarkers),
            "diseases": len(self._disease_map),
            "established": len(self.established()),
            "predictions": len(self.predictions()),
        }


def self_test() -> bool:
    engine = DiseaseBiomarkerEngine()
    engine.add(Biomarker(
        "B1", "HbA1c", "molecular", evidence_level="established",
        specificity=0.92, sensitivity=0.78))
    engine.add(Biomarker(
        "B2", "Troponin I", "molecular", evidence_level="established",
        specificity=0.95, sensitivity=0.90))
    engine.add(Biomarker(
        "B3", "AI-predicted microRNA panel", "molecular",
        evidence_level="hypothetical", source="predicted"))
    engine.link_disease("D_t2d", "B1")
    engine.link_disease("D_mi", "B2")
    engine.link_disease("D_mi", "B3")
    assert len(engine.biomarkers_for_disease("D_mi")) == 2
    assert len(engine.by_type("molecular")) == 3
    assert len(engine.established()) == 2
    assert len(engine.predictions()) == 1
    assert len(engine.high_performance(0.85)) == 1
    assert engine.stats()["diseases"] == 2
    print("disease_biomarker_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
