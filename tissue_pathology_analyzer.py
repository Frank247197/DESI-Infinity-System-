"""DESI Infinity System - Tissue Pathology Analyzer (v6.2.0).

Stores structured pathology features (inflammation, necrosis, hyperplasia,
metaplasia, dysplasia, neoplastic) with severity grading and tissue
location. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FEATURE_TYPES = ("inflammation", "necrosis", "hyperplasia", "metaplasia",
                 "dysplasia", "neoplastic", "fibrosis", "edema",
                 "hemorrhage", "other")
GRADES = ("none", "mild", "moderate", "severe", "unknown")
SOURCES = ("curated", "literature", "predicted")


class TissuePathologyError(Exception):
    """Base tissue pathology error."""


@dataclass
class PathologyFeature:
    feature_id: str
    tissue: str
    feature_type: str
    grade: str = "unknown"
    description: str = ""
    disease_id: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.feature_id or not isinstance(self.feature_id, str):
            raise TissuePathologyError("feature_id required")
        if not self.tissue or not isinstance(self.tissue, str):
            raise TissuePathologyError("tissue required")
        if self.feature_type not in FEATURE_TYPES:
            raise TissuePathologyError(f"invalid feature_type: {self.feature_type!r}")
        if self.grade not in GRADES:
            raise TissuePathologyError(f"invalid grade: {self.grade!r}")
        if self.source not in SOURCES:
            raise TissuePathologyError(f"invalid source: {self.source!r}")


class TissuePathologyAnalyzer:
    """Registry with tissue / feature / grade queries."""

    def __init__(self) -> None:
        self._features: Dict[str, PathologyFeature] = {}
        self._tissue_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, feature: PathologyFeature) -> PathologyFeature:
        if feature.feature_id in self._features:
            raise TissuePathologyError(f"duplicate feature_id: {feature.feature_id}")
        self._features[feature.feature_id] = feature
        self._tissue_index.setdefault(feature.tissue, []).append(feature.feature_id)
        if feature.disease_id:
            self._disease_index.setdefault(feature.disease_id, []).append(
                feature.feature_id)
        return feature

    def get(self, feature_id: str) -> PathologyFeature:
        try:
            return self._features[feature_id]
        except KeyError as exc:
            raise TissuePathologyError(f"unknown feature_id: {feature_id}") from exc

    def by_tissue(self, tissue: str) -> List[PathologyFeature]:
        return [self.get(f) for f in self._tissue_index.get(tissue, [])]

    def by_type(self, feature_type: str) -> List[PathologyFeature]:
        if feature_type not in FEATURE_TYPES:
            raise TissuePathologyError(f"invalid feature_type: {feature_type!r}")
        return [f for f in self._features.values() if f.feature_type == feature_type]

    def by_grade(self, grade: str) -> List[PathologyFeature]:
        if grade not in GRADES:
            raise TissuePathologyError(f"invalid grade: {grade!r}")
        return [f for f in self._features.values() if f.grade == grade]

    def for_disease(self, disease_id: str) -> List[PathologyFeature]:
        return [self._features[f] for f in self._disease_index.get(disease_id, [])]

    def severe_features(self) -> List[PathologyFeature]:
        return self.by_grade("severe")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "features": len(self._features),
            "tissues": len(self._tissue_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    analyzer = TissuePathologyAnalyzer()
    analyzer.add(PathologyFeature(
        "PF1", "liver", "inflammation", "moderate",
        "portal inflammation", "D_hepatitis"))
    analyzer.add(PathologyFeature(
        "PF2", "liver", "fibrosis", "severe",
        "bridging fibrosis", "D_hepatitis"))
    analyzer.add(PathologyFeature(
        "PF3", "colon", "dysplasia", "moderate",
        "low-grade dysplasia", "D_ibd"))
    analyzer.add(PathologyFeature(
        "PF4", "colon", "neoplastic", "severe",
        "adenocarcinoma", "D_crc"))
    assert len(analyzer.by_tissue("liver")) == 2
    assert len(analyzer.by_type("inflammation")) == 1
    assert len(analyzer.by_grade("severe")) == 2
    assert len(analyzer.for_disease("D_hepatitis")) == 2
    assert len(analyzer.severe_features()) == 2
    print("tissue_pathology_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
