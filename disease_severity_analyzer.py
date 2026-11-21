"""DESI Infinity System - Disease Severity Analyzer (v6.2.0).

Stores severity grading scales per disease and computes aggregate
severity distribution across documented cases. Does NOT grade any
individual patient; treats severity as population research metadata.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

GRADES = ("mild", "moderate", "severe", "critical", "fatal", "unknown")
SOURCES = ("curated", "literature", "predicted")


class SeverityError(Exception):
    """Base severity error."""


@dataclass
class SeverityScale:
    disease_id: str
    scale_id: str
    name: str
    grades: List[str]
    description: str = ""
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.disease_id or not self.scale_id:
            raise SeverityError("disease_id and scale_id required")
        if not self.name:
            raise SeverityError("name required")
        if not self.grades:
            raise SeverityError("grades list required")
        for g in self.grades:
            if g not in GRADES:
                raise SeverityError(f"invalid grade: {g!r}")


@dataclass
class SeverityObservation:
    disease_id: str
    grade: str
    count: int
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.grade not in GRADES:
            raise SeverityError(f"invalid grade: {self.grade!r}")
        if not isinstance(self.count, int) or self.count < 0:
            raise SeverityError("count must be non-negative int")
        if self.source not in SOURCES:
            raise SeverityError(f"invalid source: {self.source!r}")


class DiseaseSeverityAnalyzer:
    """Severity scale registry and observation aggregator."""

    def __init__(self) -> None:
        self._scales: Dict[str, List[SeverityScale]] = {}
        self._observations: List[SeverityObservation] = []

    def add_scale(self, scale: SeverityScale) -> None:
        scales = self._scales.setdefault(scale.disease_id, [])
        if any(s.scale_id == scale.scale_id for s in scales):
            raise SeverityError(f"duplicate scale for {scale.disease_id}: {scale.scale_id}")
        scales.append(scale)

    def add_observation(self, obs: SeverityObservation) -> None:
        self._observations.append(obs)

    def scales_for_disease(self, disease_id: str) -> List[SeverityScale]:
        return list(self._scales.get(disease_id, []))

    def distribution(self, disease_id: str) -> Dict[str, int]:
        out: Dict[str, int] = {g: 0 for g in GRADES}
        for o in self._observations:
            if o.disease_id == disease_id:
                out[o.grade] += o.count
        return out

    def proportions(self, disease_id: str) -> Dict[str, float]:
        dist = self.distribution(disease_id)
        total = sum(dist.values())
        if total == 0:
            return {g: 0.0 for g in GRADES}
        return {g: round(v / total, 4) for g, v in dist.items()}

    def severe_fraction(self, disease_id: str) -> float:
        prop = self.proportions(disease_id)
        return round(prop.get("severe", 0.0) + prop.get("critical", 0.0) + prop.get("fatal", 0.0), 4)

    def highest_grade_documented(self, disease_id: str) -> Optional[str]:
        dist = self.distribution(disease_id)
        for grade in ("fatal", "critical", "severe", "moderate", "mild"):
            if dist.get(grade, 0) > 0:
                return grade
        return None

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION,
                "scales": sum(len(v) for v in self._scales.values()),
                "observations": len(self._observations)}


def self_test() -> bool:
    a = DiseaseSeverityAnalyzer()
    a.add_scale(SeverityScale("D1", "SC1", "Severity Scale 1",
                              ["mild", "moderate", "severe", "critical"]))
    a.add_observation(SeverityObservation("D1", "mild", 100))
    a.add_observation(SeverityObservation("D1", "moderate", 60))
    a.add_observation(SeverityObservation("D1", "severe", 30))
    a.add_observation(SeverityObservation("D1", "critical", 10))
    dist = a.distribution("D1")
    assert dist["mild"] == 100
    assert a.severe_fraction("D1") == 0.2
    assert a.highest_grade_documented("D1") == "critical"
    assert len(a.scales_for_disease("D1")) == 1
    print("015 disease_severity_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
