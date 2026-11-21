"""DESI Infinity System - Protein Pathogenicity Engine (v6.2.0).

Stores curated pathogenicity assertions at protein level (domain
disruption, stability, interaction loss) with explicit evidence strength.
Research annotations only; not clinical interpretation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

EFFECT_CATEGORIES = ("destabilizing", "stabilizing", "interaction_loss",
                     "interaction_gain", "mislocalization", "aggregation",
                     "loss_of_function", "gain_of_function", "neutral",
                     "unknown")
EVIDENCE_CLASSES = ("experimental", "computational", "curated", "predicted")
SOURCES = ("curated", "literature", "predicted")


class ProteinPathogenicityError(Exception):
    """Base protein pathogenicity error."""


@dataclass
class ProteinPathogenicityAssertion:
    assertion_id: str
    protein_id: str
    variant_id: str
    effect_category: str = "unknown"
    delta_ddg_kcal: float = 0.0
    evidence_class: str = "predicted"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.assertion_id or not isinstance(self.assertion_id, str):
            raise ProteinPathogenicityError("assertion_id required")
        if not self.protein_id or not isinstance(self.protein_id, str):
            raise ProteinPathogenicityError("protein_id required")
        if not self.variant_id or not isinstance(self.variant_id, str):
            raise ProteinPathogenicityError("variant_id required")
        if self.effect_category not in EFFECT_CATEGORIES:
            raise ProteinPathogenicityError(
                f"invalid effect_category: {self.effect_category!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise ProteinPathogenicityError(
                f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise ProteinPathogenicityError(f"invalid source: {self.source!r}")

    def is_destabilizing(self, threshold: float = 1.0) -> bool:
        return (self.effect_category == "destabilizing"
                or self.delta_ddg_kcal >= threshold)

    def is_prediction(self) -> bool:
        return self.source == "predicted" or self.evidence_class == "predicted"


class ProteinPathogenicityEngine:
    """Assertion registry with protein / variant / effect queries."""

    def __init__(self) -> None:
        self._assertions: Dict[str, ProteinPathogenicityAssertion] = {}
        self._protein_index: Dict[str, List[str]] = {}
        self._variant_index: Dict[str, List[str]] = {}

    def add(self, assertion: ProteinPathogenicityAssertion
            ) -> ProteinPathogenicityAssertion:
        if assertion.assertion_id in self._assertions:
            raise ProteinPathogenicityError(
                f"duplicate assertion_id: {assertion.assertion_id}")
        self._assertions[assertion.assertion_id] = assertion
        self._protein_index.setdefault(assertion.protein_id, []).append(
            assertion.assertion_id)
        self._variant_index.setdefault(assertion.variant_id, []).append(
            assertion.assertion_id)
        return assertion

    def get(self, assertion_id: str) -> ProteinPathogenicityAssertion:
        try:
            return self._assertions[assertion_id]
        except KeyError as exc:
            raise ProteinPathogenicityError(
                f"unknown assertion_id: {assertion_id}") from exc

    def for_protein(self, protein_id: str) -> List[ProteinPathogenicityAssertion]:
        return [self.get(a) for a in self._protein_index.get(protein_id, [])]

    def for_variant(self, variant_id: str) -> List[ProteinPathogenicityAssertion]:
        return [self.get(a) for a in self._variant_index.get(variant_id, [])]

    def by_effect(self, effect: str) -> List[ProteinPathogenicityAssertion]:
        if effect not in EFFECT_CATEGORIES:
            raise ProteinPathogenicityError(f"invalid effect: {effect!r}")
        return [a for a in self._assertions.values() if a.effect_category == effect]

    def destabilizing(self, threshold: float = 1.0) -> List[ProteinPathogenicityAssertion]:
        return [a for a in self._assertions.values()
                if a.is_destabilizing(threshold)]

    def experimental(self) -> List[ProteinPathogenicityAssertion]:
        return [a for a in self._assertions.values()
                if a.evidence_class == "experimental"]

    def predictions(self) -> List[ProteinPathogenicityAssertion]:
        return [a for a in self._assertions.values() if a.is_prediction()]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "assertions": len(self._assertions),
            "proteins": len(self._protein_index),
            "experimental": len(self.experimental()),
            "predictions": len(self.predictions()),
        }


def self_test() -> bool:
    engine = ProteinPathogenicityEngine()
    engine.add(ProteinPathogenicityAssertion(
        "A1", "P04637", "V1", "destabilizing",
        delta_ddg_kcal=2.5, evidence_class="experimental"))
    engine.add(ProteinPathogenicityAssertion(
        "A2", "P04637", "V2", "loss_of_function",
        evidence_class="predicted", source="predicted"))
    engine.add(ProteinPathogenicityAssertion(
        "A3", "P00533", "V3", "interaction_loss",
        evidence_class="computational", source="literature"))
    assert len(engine.for_protein("P04637")) == 2
    assert engine.for_variant("V1")[0].assertion_id == "A1"
    assert len(engine.by_effect("loss_of_function")) == 1
    assert len(engine.destabilizing()) == 1
    assert len(engine.experimental()) == 1
    assert len(engine.predictions()) == 1
    print("protein_pathogenicity_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
