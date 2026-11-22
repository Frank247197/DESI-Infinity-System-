"""DESI Infinity System - Histopathology Image Analyzer (v6.2.0).

Structured histopathology image annotations: stain, tissue, Gleason
grade style inputs, cellular density, and AI annotation provenance.
Research record-keeping only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STAINS = ("h_and_e", "ihc", "special_stain", "fluorescence", "other")
ANNOTATION_SOURCES = ("pathologist", "ai_model", "consensus", "unknown")
TUMOR_GRADES = ("grade_1", "grade_2", "grade_3", "grade_4", "not_applicable")
SOURCES = ("curated", "literature", "predicted")


class HistopathImageError(Exception):
    """Base histopath image error."""


@dataclass
class HistopathAnnotation:
    annotation_id: str
    slide_id: str
    tissue: str
    stain: str
    tumor_grade: str = "not_applicable"
    cellular_density: Optional[float] = None
    mitotic_count: Optional[int] = None
    annotation_source: str = "unknown"
    disease_id: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.annotation_id or not isinstance(self.annotation_id, str):
            raise HistopathImageError("annotation_id required")
        if not self.slide_id or not isinstance(self.slide_id, str):
            raise HistopathImageError("slide_id required")
        if self.stain not in STAINS:
            raise HistopathImageError(f"invalid stain: {self.stain!r}")
        if self.tumor_grade not in TUMOR_GRADES:
            raise HistopathImageError(f"invalid tumor_grade: {self.tumor_grade!r}")
        if self.annotation_source not in ANNOTATION_SOURCES:
            raise HistopathImageError(
                f"invalid annotation_source: {self.annotation_source!r}")
        if self.source not in SOURCES:
            raise HistopathImageError(f"invalid source: {self.source!r}")
        if self.cellular_density is not None:
            if not isinstance(self.cellular_density, (int, float)):
                raise HistopathImageError("cellular_density must be numeric or None")
            if not 0.0 <= float(self.cellular_density) <= 1.0:
                raise HistopathImageError("cellular_density must be in [0, 1]")
        if self.mitotic_count is not None:
            if not isinstance(self.mitotic_count, int) or self.mitotic_count < 0:
                raise HistopathImageError(
                    "mitotic_count must be non-negative int or None")


class HistopathologyImageAnalyzer:
    """Annotation store with stain / grade / provenance queries."""

    def __init__(self) -> None:
        self._annotations: Dict[str, HistopathAnnotation] = {}
        self._stain_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, annotation: HistopathAnnotation) -> HistopathAnnotation:
        if annotation.annotation_id in self._annotations:
            raise HistopathImageError(
                f"duplicate annotation_id: {annotation.annotation_id}")
        self._annotations[annotation.annotation_id] = annotation
        self._stain_index.setdefault(annotation.stain, []).append(
            annotation.annotation_id)
        if annotation.disease_id:
            self._disease_index.setdefault(annotation.disease_id, []).append(
                annotation.annotation_id)
        return annotation

    def get(self, annotation_id: str) -> HistopathAnnotation:
        try:
            return self._annotations[annotation_id]
        except KeyError as exc:
            raise HistopathImageError(
                f"unknown annotation_id: {annotation_id}") from exc

    def by_stain(self, stain: str) -> List[HistopathAnnotation]:
        if stain not in STAINS:
            raise HistopathImageError(f"invalid stain: {stain!r}")
        return [self.get(a) for a in self._stain_index.get(stain, [])]

    def for_disease(self, disease_id: str) -> List[HistopathAnnotation]:
        return [self.get(a) for a in self._disease_index.get(disease_id, [])]

    def by_grade(self, tumor_grade: str) -> List[HistopathAnnotation]:
        if tumor_grade not in TUMOR_GRADES:
            raise HistopathImageError(f"invalid tumor_grade: {tumor_grade!r}")
        return [a for a in self._annotations.values()
                if a.tumor_grade == tumor_grade]

    def human_annotated(self) -> List[HistopathAnnotation]:
        return [a for a in self._annotations.values()
                if a.annotation_source == "pathologist"]

    def ai_annotated(self) -> List[HistopathAnnotation]:
        return [a for a in self._annotations.values()
                if a.annotation_source == "ai_model"]

    def high_proliferation(self, min_mitotic: int = 10) -> List[HistopathAnnotation]:
        return [a for a in self._annotations.values()
                if a.mitotic_count is not None and a.mitotic_count >= min_mitotic]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "annotations": len(self._annotations),
            "stains": len(self._stain_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    analyzer = HistopathologyImageAnalyzer()
    analyzer.add(HistopathAnnotation(
        "A1", "SL1", "breast", "h_and_e", "grade_2",
        cellular_density=0.65, mitotic_count=12,
        annotation_source="pathologist", disease_id="D_breast_cancer"))
    analyzer.add(HistopathAnnotation(
        "A2", "SL2", "breast", "ihc", "not_applicable",
        cellular_density=0.45, annotation_source="ai_model",
        disease_id="D_breast_cancer"))
    analyzer.add(HistopathAnnotation(
        "A3", "SL3", "prostate", "h_and_e", "grade_3",
        mitotic_count=15, annotation_source="pathologist",
        disease_id="D_prostate_cancer"))
    assert len(analyzer.by_stain("h_and_e")) == 2
    assert len(analyzer.for_disease("D_breast_cancer")) == 2
    assert len(analyzer.by_grade("grade_2")) == 1
    assert len(analyzer.human_annotated()) == 2
    assert len(analyzer.ai_annotated()) == 1
    assert len(analyzer.high_proliferation()) == 2
    print("histopathology_image_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
