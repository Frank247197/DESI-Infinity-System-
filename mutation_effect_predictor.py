"""DESI Infinity System - Mutation Effect Predictor (v6.2.0).

Rule-based prediction of molecular effect class for mutations using
structured features (region, amino-acid change, conservation, domain
disruption). Every prediction is labelled `is_prediction = True`.
Research predictions only — NOT clinical interpretation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

GENOMIC_REGIONS = ("coding", "splice_site", "promoter", "utr_5", "utr_3",
                   "intronic", "intergenic", "unknown")
EFFECT_CLASSES = ("loss_of_function", "gain_of_function",
                  "dominant_negative", "splice_altering",
                  "regulatory", "neutral", "unknown")
CONSERVATION = ("low", "moderate", "high", "unknown")


class MutationEffectError(Exception):
    """Base mutation effect error."""


@dataclass
class MutationEffectInput:
    mutation_id: str
    gene_symbol: str
    genomic_region: str
    amino_acid_change: str = ""
    conservation: str = "unknown"
    in_critical_domain: bool = False
    affects_start_codon: bool = False
    affects_stop_codon: bool = False
    predicted_splice_effect: bool = False

    def __post_init__(self) -> None:
        if not self.mutation_id or not isinstance(self.mutation_id, str):
            raise MutationEffectError("mutation_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise MutationEffectError("gene_symbol required")
        if self.genomic_region not in GENOMIC_REGIONS:
            raise MutationEffectError(f"invalid genomic_region: {self.genomic_region!r}")
        if self.conservation not in CONSERVATION:
            raise MutationEffectError(f"invalid conservation: {self.conservation!r}")


@dataclass
class MutationEffectPrediction:
    mutation_id: str
    effect_class: str
    confidence: float
    rationale: List[str] = field(default_factory=list)
    is_prediction: bool = True

    def __post_init__(self) -> None:
        if self.effect_class not in EFFECT_CLASSES:
            raise MutationEffectError(f"invalid effect_class: {self.effect_class!r}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise MutationEffectError("confidence must be in [0, 1]")
        if not self.is_prediction:
            raise MutationEffectError("MutationEffectPrediction must be marked as prediction")


class MutationEffectPredictor:
    """Deterministic rule-based predictor with confidence scoring."""

    def __init__(self) -> None:
        self._predictions: Dict[str, MutationEffectPrediction] = {}

    def predict(self, inp: MutationEffectInput) -> MutationEffectPrediction:
        rationale: List[str] = []
        score = 0.0
        effect = "unknown"

        if inp.genomic_region == "splice_site" or inp.predicted_splice_effect:
            effect = "splice_altering"
            score += 0.7
            rationale.append("splice site disruption")
        elif inp.affects_start_codon:
            effect = "loss_of_function"
            score += 0.85
            rationale.append("start codon disrupted")
        elif inp.affects_stop_codon:
            effect = "loss_of_function"
            score += 0.6
            rationale.append("premature stop or stop loss")
        elif inp.genomic_region == "coding":
            if inp.in_critical_domain:
                score += 0.5
                rationale.append("in critical domain")
            if inp.conservation == "high":
                score += 0.3
                rationale.append("highly conserved position")
            elif inp.conservation == "moderate":
                score += 0.15
                rationale.append("moderately conserved")
            effect = "loss_of_function" if score >= 0.5 else "neutral"
        elif inp.genomic_region in ("promoter", "utr_5", "utr_3"):
            effect = "regulatory"
            score += 0.35
            rationale.append("regulatory region")
        elif inp.genomic_region == "intronic":
            effect = "neutral"
            score += 0.15
            rationale.append("intronic, no splice signal")
        else:
            effect = "unknown"
            rationale.append("insufficient evidence")

        prediction = MutationEffectPrediction(
            mutation_id=inp.mutation_id,
            effect_class=effect,
            confidence=round(min(1.0, score), 4),
            rationale=rationale,
        )
        self._predictions[inp.mutation_id] = prediction
        return prediction

    def get(self, mutation_id: str) -> MutationEffectPrediction:
        try:
            return self._predictions[mutation_id]
        except KeyError as exc:
            raise MutationEffectError(f"unknown mutation_id: {mutation_id}") from exc

    def by_effect(self, effect_class: str) -> List[MutationEffectPrediction]:
        if effect_class not in EFFECT_CLASSES:
            raise MutationEffectError(f"invalid effect_class: {effect_class!r}")
        return [p for p in self._predictions.values() if p.effect_class == effect_class]

    def high_confidence(self, threshold: float = 0.7) -> List[MutationEffectPrediction]:
        return [p for p in self._predictions.values() if p.confidence >= threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "predictions": len(self._predictions),
            "lof": len(self.by_effect("loss_of_function")),
            "splice": len(self.by_effect("splice_altering")),
        }


def self_test() -> bool:
    predictor = MutationEffectPredictor()
    p1 = predictor.predict(MutationEffectInput(
        "M1", "BRCA1", "coding", "p.Cys61Gly",
        conservation="high", in_critical_domain=True))
    assert p1.effect_class == "loss_of_function"
    assert p1.is_prediction is True
    p2 = predictor.predict(MutationEffectInput(
        "M2", "GENE", "splice_site"))
    assert p2.effect_class == "splice_altering"
    p3 = predictor.predict(MutationEffectInput(
        "M3", "GENE", "intronic"))
    assert p3.effect_class == "neutral"
    p4 = predictor.predict(MutationEffectInput(
        "M4", "GENE", "coding", affects_start_codon=True))
    assert p4.effect_class == "loss_of_function"
    assert len(predictor.high_confidence(0.6)) >= 2
    assert predictor.stats()["predictions"] == 4
    print("mutation_effect_predictor: OK")
    return True


if __name__ == "__main__":
    self_test()
