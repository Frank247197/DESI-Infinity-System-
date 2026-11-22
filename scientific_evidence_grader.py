"""DESI Infinity System - Scientific Evidence Grader (v6.2.0).

Grades structured evidence using a rubric over study design, replication,
sample size, and bias controls. Output is a RESEARCH grade, not a
regulatory determination.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STUDY_DESIGNS = ("meta_analysis", "rct", "cohort", "case_control",
                 "cross_sectional", "case_series", "expert_opinion")
GRADE_LEVELS = ("A", "B", "C", "D")
SOURCES = ("curated", "literature", "predicted")


class EvidenceGradingError(Exception):
    """Base evidence grading error."""


@dataclass
class EvidenceItem:
    item_id: str
    source_type: str
    study_design: str
    sample_size: int
    replicated: bool = False
    bias_controlled: bool = False
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.item_id or not isinstance(self.item_id, str):
            raise EvidenceGradingError("item_id required")
        if self.study_design not in STUDY_DESIGNS:
            raise EvidenceGradingError(
                f"invalid study_design: {self.study_design!r}")
        if self.source not in SOURCES:
            raise EvidenceGradingError(f"invalid source: {self.source!r}")
        if not isinstance(self.sample_size, int) or self.sample_size < 0:
            raise EvidenceGradingError("sample_size must be non-negative int")

    def grade(self) -> str:
        score = 0
        design_weight = {
            "meta_analysis": 4, "rct": 4, "cohort": 3,
            "case_control": 2, "cross_sectional": 2,
            "case_series": 1, "expert_opinion": 0,
        }
        score += design_weight[self.study_design]
        if self.sample_size >= 1000:
            score += 2
        elif self.sample_size >= 100:
            score += 1
        if self.replicated:
            score += 2
        if self.bias_controlled:
            score += 1
        if score >= 8:
            return "A"
        if score >= 5:
            return "B"
        if score >= 3:
            return "C"
        return "D"


class ScientificEvidenceGrader:
    """Rubric store with grade / design / replication queries."""

    def __init__(self) -> None:
        self._items: Dict[str, EvidenceItem] = {}

    def add(self, item: EvidenceItem) -> EvidenceItem:
        if item.item_id in self._items:
            raise EvidenceGradingError(f"duplicate item_id: {item.item_id}")
        self._items[item.item_id] = item
        return item

    def get(self, item_id: str) -> EvidenceItem:
        try:
            return self._items[item_id]
        except KeyError as exc:
            raise EvidenceGradingError(f"unknown item_id: {item_id}") from exc

    def by_grade(self, grade: str) -> List[EvidenceItem]:
        if grade not in GRADE_LEVELS:
            raise EvidenceGradingError(f"invalid grade: {grade!r}")
        return [i for i in self._items.values() if i.grade() == grade]

    def by_design(self, design: str) -> List[EvidenceItem]:
        if design not in STUDY_DESIGNS:
            raise EvidenceGradingError(f"invalid study_design: {design!r}")
        return [i for i in self._items.values() if i.study_design == design]

    def high_quality(self) -> List[EvidenceItem]:
        return self.by_grade("A") + self.by_grade("B")

    def replicated(self) -> List[EvidenceItem]:
        return [i for i in self._items.values() if i.replicated]

    def stats(self) -> Dict[str, int]:
        grades: Dict[str, int] = {g: 0 for g in GRADE_LEVELS}
        for i in self._items.values():
            grades[i.grade()] += 1
        return {
            "version": VERSION,
            "items": len(self._items),
            "grade_A": grades["A"],
            "grade_B": grades["B"],
            "grade_C": grades["C"],
            "grade_D": grades["D"],
        }


def self_test() -> bool:
    grader = ScientificEvidenceGrader()
    grader.add(EvidenceItem(
        "E1", "meta_analysis", "meta_analysis", 5000,
        replicated=True, bias_controlled=True))
    grader.add(EvidenceItem(
        "E2", "journal", "rct", 800, replicated=False, bias_controlled=True))
    grader.add(EvidenceItem(
        "E3", "journal", "cohort", 5000, replicated=True))
    grader.add(EvidenceItem(
        "E4", "review", "case_series", 20))
    assert grader.get("E1").grade() == "A"
    assert grader.get("E2").grade() in ("A", "B")
    assert grader.get("E4").grade() == "D"
    assert len(grader.by_grade("A")) >= 1
    assert len(grader.by_design("rct")) == 1
    assert len(grader.replicated()) == 2
    print("scientific_evidence_grader: OK")
    return True


if __name__ == "__main__":
    self_test()
