"""DESI Infinity System - Variant Pathogenicity Engine (v6.2.0).

Stores curated pathogenicity assertions using ACMG-style categories and
computational evidence. This is a RESEARCH annotation store — not a
clinical variant interpretation service. Predictions are labelled.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ACMG_CLASSES = ("pathogenic", "likely_pathogenic", "uncertain_significance",
                "likely_benign", "benign")
EVIDENCE_STRENGTHS = ("very_strong", "strong", "moderate", "supporting",
                      "predicted")
SOURCES = ("curated", "literature", "predicted")


class VariantPathogenicityError(Exception):
    """Base pathogenicity error."""


@dataclass
class PathogenicityAssertion:
    assertion_id: str
    variant_id: str
    acmg_class: str
    evidence_strength: str = "supporting"
    criteria: List[str] = field(default_factory=list)
    rationale: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.assertion_id or not isinstance(self.assertion_id, str):
            raise VariantPathogenicityError("assertion_id required")
        if not self.variant_id or not isinstance(self.variant_id, str):
            raise VariantPathogenicityError("variant_id required")
        if self.acmg_class not in ACMG_CLASSES:
            raise VariantPathogenicityError(f"invalid acmg_class: {self.acmg_class!r}")
        if self.evidence_strength not in EVIDENCE_STRENGTHS:
            raise VariantPathogenicityError(
                f"invalid evidence_strength: {self.evidence_strength!r}")
        if self.source not in SOURCES:
            raise VariantPathogenicityError(f"invalid source: {self.source!r}")

    def is_prediction(self) -> bool:
        return self.source == "predicted"

    def is_clinically_actionable_research(self) -> bool:
        return (self.source == "curated"
                and self.acmg_class in ("pathogenic", "likely_pathogenic"))


class VariantPathogenicityEngine:
    """Assertion registry with ACMG-class and evidence-strength queries."""

    def __init__(self) -> None:
        self._assertions: Dict[str, PathogenicityAssertion] = {}
        self._variant_index: Dict[str, List[str]] = {}

    def add(self, assertion: PathogenicityAssertion) -> PathogenicityAssertion:
        if assertion.assertion_id in self._assertions:
            raise VariantPathogenicityError(
                f"duplicate assertion_id: {assertion.assertion_id}")
        self._assertions[assertion.assertion_id] = assertion
        self._variant_index.setdefault(assertion.variant_id, []).append(
            assertion.assertion_id)
        return assertion

    def get(self, assertion_id: str) -> PathogenicityAssertion:
        try:
            return self._assertions[assertion_id]
        except KeyError as exc:
            raise VariantPathogenicityError(
                f"unknown assertion_id: {assertion_id}") from exc

    def for_variant(self, variant_id: str) -> List[PathogenicityAssertion]:
        return [self.get(aid) for aid in self._variant_index.get(variant_id, [])]

    def by_class(self, acmg_class: str) -> List[PathogenicityAssertion]:
        if acmg_class not in ACMG_CLASSES:
            raise VariantPathogenicityError(f"invalid acmg_class: {acmg_class!r}")
        return [a for a in self._assertions.values() if a.acmg_class == acmg_class]

    def by_strength(self, strength: str) -> List[PathogenicityAssertion]:
        if strength not in EVIDENCE_STRENGTHS:
            raise VariantPathogenicityError(
                f"invalid evidence_strength: {strength!r}")
        return [a for a in self._assertions.values() if a.evidence_strength == strength]

    def actionable_research(self) -> List[PathogenicityAssertion]:
        return [a for a in self._assertions.values()
                if a.is_clinically_actionable_research()]

    def predictions(self) -> List[PathogenicityAssertion]:
        return [a for a in self._assertions.values() if a.is_prediction()]

    def strongest_assertion(self, variant_id: str) -> PathogenicityAssertion:
        recs = self.for_variant(variant_id)
        if not recs:
            raise VariantPathogenicityError(f"no assertions for variant_id: {variant_id}")
        order = {"very_strong": 0, "strong": 1, "moderate": 2,
                 "supporting": 3, "predicted": 4}
        return sorted(recs, key=lambda a: order[a.evidence_strength])[0]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "assertions": len(self._assertions),
            "variants": len(self._variant_index),
            "pathogenic": len(self.by_class("pathogenic")),
            "predictions": len(self.predictions()),
        }


def self_test() -> bool:
    engine = VariantPathogenicityEngine()
    engine.add(PathogenicityAssertion(
        "PA1", "V1", "pathogenic", "very_strong",
        ["PVS1", "PS3", "PM2"], "loss-of-function in disease gene"))
    engine.add(PathogenicityAssertion(
        "PA2", "V1", "uncertain_significance", "supporting",
        ["PP3"], "computational support only", source="predicted"))
    engine.add(PathogenicityAssertion(
        "PA3", "V2", "benign", "strong", ["BA1"], "high population frequency"))
    assert len(engine.for_variant("V1")) == 2
    assert engine.by_class("pathogenic")[0].assertion_id == "PA1"
    assert len(engine.by_strength("very_strong")) == 1
    assert len(engine.actionable_research()) == 1
    assert len(engine.predictions()) == 1
    assert engine.strongest_assertion("V1").assertion_id == "PA1"
    print("variant_pathogenicity_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
