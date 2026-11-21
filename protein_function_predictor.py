"""DESI Infinity System - Protein Function Predictor (v6.2.0).

Rule-based prediction of protein functional class from structured
features (domains, motifs, localization signals, interaction partners).
Every prediction is labelled. Research predictions only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FUNCTION_CLASSES = ("enzyme", "receptor", "transporter", "channel",
                    "transcription_factor", "signaling", "structural",
                    "chaperone", "unknown")
LOCALIZATIONS = ("nucleus", "cytoplasm", "membrane", "secreted",
                 "mitochondria", "er", "golgi", "unknown")


class ProteinFunctionError(Exception):
    """Base protein function error."""


@dataclass
class ProteinFunctionInput:
    protein_id: str
    domains: List[str] = field(default_factory=list)
    motifs: List[str] = field(default_factory=list)
    localization_signal: str = "unknown"
    membrane_segments: int = 0
    interacts_with_dna: bool = False
    has_atp_binding: bool = False
    has_kinase_motif: bool = False

    def __post_init__(self) -> None:
        if not self.protein_id or not isinstance(self.protein_id, str):
            raise ProteinFunctionError("protein_id required")
        if self.localization_signal not in LOCALIZATIONS:
            raise ProteinFunctionError(
                f"invalid localization_signal: {self.localization_signal!r}")
        if not isinstance(self.membrane_segments, int) or self.membrane_segments < 0:
            raise ProteinFunctionError("membrane_segments must be non-negative int")


@dataclass
class ProteinFunctionPrediction:
    protein_id: str
    function_class: str
    localization: str
    confidence: float
    rationale: List[str] = field(default_factory=list)
    is_prediction: bool = True

    def __post_init__(self) -> None:
        if self.function_class not in FUNCTION_CLASSES:
            raise ProteinFunctionError(
                f"invalid function_class: {self.function_class!r}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ProteinFunctionError("confidence must be in [0, 1]")
        if not self.is_prediction:
            raise ProteinFunctionError("must be marked as prediction")


class ProteinFunctionPredictor:
    """Deterministic feature-to-function predictor."""

    def __init__(self) -> None:
        self._predictions: Dict[str, ProteinFunctionPrediction] = {}

    def predict(self, inp: ProteinFunctionInput) -> ProteinFunctionPrediction:
        rationale: List[str] = []
        score = 0.3
        function_class = "unknown"
        localization = inp.localization_signal

        if inp.interacts_with_dna:
            function_class = "transcription_factor"
            score += 0.5
            rationale.append("DNA-binding feature")
            if localization == "unknown":
                localization = "nucleus"
        elif inp.has_kinase_motif:
            function_class = "enzyme"
            score += 0.4
            rationale.append("kinase motif present")
        elif inp.membrane_segments >= 7:
            function_class = "channel"
            score += 0.5
            rationale.append(f"{inp.membrane_segments} transmembrane segments")
            if localization == "unknown":
                localization = "membrane"
        elif inp.membrane_segments in (1, 2):
            function_class = "receptor"
            score += 0.4
            rationale.append("single-pass transmembrane domain")
            if localization == "unknown":
                localization = "membrane"
        elif inp.has_atp_binding:
            function_class = "enzyme"
            score += 0.25
            rationale.append("ATP-binding motif")
        elif "chaperone" in inp.domains:
            function_class = "chaperone"
            score += 0.4
            rationale.append("chaperone domain")

        prediction = ProteinFunctionPrediction(
            protein_id=inp.protein_id,
            function_class=function_class,
            localization=localization,
            confidence=round(min(1.0, score), 4),
            rationale=rationale,
        )
        self._predictions[inp.protein_id] = prediction
        return prediction

    def get(self, protein_id: str) -> ProteinFunctionPrediction:
        try:
            return self._predictions[protein_id]
        except KeyError as exc:
            raise ProteinFunctionError(f"unknown protein_id: {protein_id}") from exc

    def by_class(self, function_class: str) -> List[ProteinFunctionPrediction]:
        if function_class not in FUNCTION_CLASSES:
            raise ProteinFunctionError(f"invalid function_class: {function_class!r}")
        return [p for p in self._predictions.values()
                if p.function_class == function_class]

    def high_confidence(self, threshold: float = 0.7) -> List[ProteinFunctionPrediction]:
        return [p for p in self._predictions.values() if p.confidence >= threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "predictions": len(self._predictions),
            "enzymes": len(self.by_class("enzyme")),
            "tf": len(self.by_class("transcription_factor")),
        }


def self_test() -> bool:
    predictor = ProteinFunctionPredictor()
    p1 = predictor.predict(ProteinFunctionInput(
        "P1", interacts_with_dna=True))
    assert p1.function_class == "transcription_factor"
    assert p1.localization == "nucleus"
    p2 = predictor.predict(ProteinFunctionInput(
        "P2", membrane_segments=7))
    assert p2.function_class == "channel"
    p3 = predictor.predict(ProteinFunctionInput(
        "P3", has_kinase_motif=True, has_atp_binding=True))
    assert p3.function_class == "enzyme"
    p4 = predictor.predict(ProteinFunctionInput(
        "P4", domains=["chaperone"]))
    assert p4.function_class == "chaperone"
    assert len(predictor.by_class("enzyme")) == 1
    assert predictor.stats()["predictions"] == 4
    print("protein_function_predictor: OK")
    return True


if __name__ == "__main__":
    self_test()
