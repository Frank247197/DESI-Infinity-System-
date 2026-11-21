"""DESI Infinity System - Disease Symptom Analyzer (v6.2.0).

Analyzes symptom-disease associations: co-occurrence, frequency-weighted
ranking, and differential-symptom overlap across candidate diseases.
AI-derived associations carry source="predicted" and are NEVER presented
as clinical facts. This module supports research, not diagnosis.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

SEVERITIES = ("mild", "moderate", "severe", "critical", "unknown")
ONSETS = ("acute", "subacute", "chronic", "insidious", "unknown")
SOURCES = ("curated", "literature", "predicted")


class SymptomAnalysisError(Exception):
    """Base symptom analyzer error."""


@dataclass
class SymptomAssociation:
    disease_id: str
    symptom_id: str
    symptom_name: str
    frequency: float = 0.0
    severity: str = "unknown"
    onset: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise SymptomAnalysisError("disease_id required")
        if not self.symptom_id or not isinstance(self.symptom_id, str):
            raise SymptomAnalysisError("symptom_id required")
        if not 0.0 <= float(self.frequency) <= 1.0:
            raise SymptomAnalysisError("frequency must be in [0, 1]")
        if self.severity not in SEVERITIES:
            raise SymptomAnalysisError(f"invalid severity: {self.severity!r}")
        if self.onset not in ONSETS:
            raise SymptomAnalysisError(f"invalid onset: {self.onset!r}")
        if self.source not in SOURCES:
            raise SymptomAnalysisError(f"invalid source: {self.source!r}")

    def is_prediction(self) -> bool:
        return self.source == "predicted"


class DiseaseSymptomAnalyzer:
    """Symptom-disease association store with ranking and overlap analysis."""

    def __init__(self) -> None:
        self._associations: List[SymptomAssociation] = []
        self._by_disease: Dict[str, List[int]] = {}
        self._by_symptom: Dict[str, List[int]] = {}

    def add(self, assoc: SymptomAssociation) -> None:
        idx = len(self._associations)
        self._associations.append(assoc)
        self._by_disease.setdefault(assoc.disease_id, []).append(idx)
        self._by_symptom.setdefault(assoc.symptom_id, []).append(idx)

    def symptoms_for_disease(self, disease_id: str) -> List[SymptomAssociation]:
        return [self._associations[i] for i in self._by_disease.get(disease_id, [])]

    def diseases_for_symptom(self, symptom_id: str) -> List[SymptomAssociation]:
        return [self._associations[i] for i in self._by_symptom.get(symptom_id, [])]

    def rank_diseases_for_symptoms(
        self, symptom_ids: List[str], min_coverage: float = 0.0
    ) -> List[Tuple[str, float, int]]:
        """Rank diseases by weighted match score against a symptom set.

        Returns list of (disease_id, score, matched_count) sorted desc.
        Scores are research hints, NOT diagnostic conclusions.
        """
        if not symptom_ids:
            return []
        wanted = set(symptom_ids)
        scores: Dict[str, float] = {}
        matched: Dict[str, int] = {}
        for idx, assoc in enumerate(self._associations):
            if assoc.symptom_id in wanted:
                scores[assoc.disease_id] = scores.get(assoc.disease_id, 0.0) + assoc.frequency
                matched[assoc.disease_id] = matched.get(assoc.disease_id, 0) + 1
        coverage = {d: matched[d] / len(wanted) for d in scores}
        out = [(d, scores[d], matched[d]) for d in scores
               if coverage[d] >= min_coverage]
        out.sort(key=lambda x: x[1], reverse=True)
        return out

    def overlap(self, disease_a: str, disease_b: str) -> Dict[str, object]:
        a = {x.symptom_id for x in self.symptoms_for_disease(disease_a)}
        b = {x.symptom_id for x in self.symptoms_for_disease(disease_b)}
        union = a | b
        inter = a & b
        jaccard = (len(inter) / len(union)) if union else 0.0
        return {
            "disease_a": disease_a,
            "disease_b": disease_b,
            "shared": sorted(inter),
            "unique_a": sorted(a - b),
            "unique_b": sorted(b - a),
            "jaccard": round(jaccard, 4),
        }

    def frequent(self, disease_id: str, threshold: float = 0.5) -> List[SymptomAssociation]:
        return [s for s in self.symptoms_for_disease(disease_id)
                if s.frequency >= threshold]

    def predictions(self) -> List[SymptomAssociation]:
        return [a for a in self._associations if a.is_prediction()]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "associations": len(self._associations),
            "diseases": len(self._by_disease),
            "symptoms": len(self._by_symptom),
            "predictions": len(self.predictions()),
        }


def self_test() -> bool:
    analyzer = DiseaseSymptomAnalyzer()
    analyzer.add(SymptomAssociation("D1", "S_fever", "Fever", 0.9, "moderate", "acute"))
    analyzer.add(SymptomAssociation("D1", "S_fatigue", "Fatigue", 0.7, "mild", "subacute"))
    analyzer.add(SymptomAssociation("D2", "S_fever", "Fever", 0.5, "moderate", "acute"))
    analyzer.add(SymptomAssociation("D2", "S_cough", "Cough", 0.8, "mild", "acute"))
    ranked = analyzer.rank_diseases_for_symptoms(["S_fever"])
    assert ranked[0][0] == "D1"
    ov = analyzer.overlap("D1", "D2")
    assert ov["shared"] == ["S_fever"]
    assert len(analyzer.frequent("D1", 0.8)) == 1
    assert analyzer.stats()["associations"] == 4
    print("009 disease_symptom_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
