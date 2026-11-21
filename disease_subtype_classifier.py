"""DESI Infinity System - Disease Subtype Classifier (v6.2.0).

Stores documented disease subtype definitions (e.g. molecular, clinical,
histologic) and rule-based assignments against structured feature sets.
Classification is deterministic against curator-supplied rules — not an
AI guess and not a clinical diagnosis. Unmatched cases are explicitly
reported, never force-classified.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)


class SubtypeError(Exception):
    """Base subtype error."""


@dataclass
class SubtypeRule:
    subtype_id: str
    disease_id: str
    name: str
    description: str = ""
    required_features: Dict[str, Any] = field(default_factory=dict)
    excluded_features: Dict[str, Any] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.subtype_id or not self.disease_id or not self.name:
            raise SubtypeError("subtype_id, disease_id, name required")

    def matches(self, features: Dict[str, Any]) -> bool:
        for k, v in self.required_features.items():
            if features.get(k) != v:
                return False
        for k, v in self.excluded_features.items():
            if features.get(k) == v:
                return False
        return True


@dataclass
class SubtypeAssignment:
    disease_id: str
    subtype_id: str
    matched_rules: List[str]
    unmatched: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)


class DiseaseSubtypeClassifier:
    """Rule-based deterministic subtype classifier."""

    def __init__(self) -> None:
        self._rules: Dict[str, List[SubtypeRule]] = {}

    def add_rule(self, rule: SubtypeRule) -> None:
        existing = self._rules.setdefault(rule.disease_id, [])
        if any(r.subtype_id == rule.subtype_id for r in existing):
            raise SubtypeError(f"duplicate subtype rule: {rule.subtype_id}")
        existing.append(rule)

    def rules_for_disease(self, disease_id: str) -> List[SubtypeRule]:
        return list(self._rules.get(disease_id, []))

    def classify(self, disease_id: str, features: Dict[str, Any]) -> SubtypeAssignment:
        if not isinstance(features, dict):
            raise SubtypeError("features must be a dict")
        matches: List[str] = []
        for rule in self.rules_for_disease(disease_id):
            if rule.matches(features):
                matches.append(rule.subtype_id)
        if not matches:
            return SubtypeAssignment(disease_id=disease_id, subtype_id="",
                                     matched_rules=[], unmatched=True,
                                     metadata={"reason": "no_rule_matched"})
        if len(matches) > 1:
            return SubtypeAssignment(disease_id=disease_id, subtype_id=matches[0],
                                     matched_rules=matches,
                                     metadata={"warning": "multiple_subtypes",
                                               "count": str(len(matches))})
        return SubtypeAssignment(disease_id=disease_id, subtype_id=matches[0],
                                 matched_rules=matches)

    def subtype_catalog(self, disease_id: str) -> List[Dict[str, str]]:
        return [{"subtype_id": r.subtype_id, "name": r.name,
                 "description": r.description} for r in self.rules_for_disease(disease_id)]

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION,
                "diseases": len(self._rules),
                "rules": sum(len(v) for v in self._rules.values())}


def self_test() -> bool:
    c = DiseaseSubtypeClassifier()
    c.add_rule(SubtypeRule("SUB_A", "D1", "Subtype A", required_features={"er": "positive"}))
    c.add_rule(SubtypeRule("SUB_B", "D1", "Subtype B", required_features={"er": "negative",
                                                                          "pr": "negative"}))
    a = c.classify("D1", {"er": "positive"})
    assert a.subtype_id == "SUB_A" and not a.unmatched
    b = c.classify("D1", {"er": "negative", "pr": "negative"})
    assert b.subtype_id == "SUB_B"
    u = c.classify("D1", {"er": "unknown"})
    assert u.unmatched
    assert len(c.subtype_catalog("D1")) == 2
    print("016 disease_subtype_classifier: OK")
    return True


if __name__ == "__main__":
    self_test()
