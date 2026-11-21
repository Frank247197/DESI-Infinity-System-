"""DESI Infinity System - Disease Risk Factor Engine (v6.2.0).

Stores and ranks documented risk factors (genetic, environmental,
behavioral, demographic, clinical) for diseases. Risk estimates are
research associations only; this module does not compute individual
patient risk scores or provide clinical advice.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FACTOR_CATEGORIES = ("genetic", "environmental", "behavioral",
                     "demographic", "clinical", "unknown")
EVIDENCE_LEVELS = ("established", "emerging", "experimental", "hypothetical")
SOURCES = ("curated", "literature", "predicted")


class RiskFactorError(Exception):
    """Base risk factor error."""


@dataclass
class RiskFactor:
    factor_id: str
    name: str
    category: str
    description: str = ""
    evidence_level: str = "emerging"
    source: str = "curated"
    effect_size: Optional[float] = None
    population_note: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.factor_id or not isinstance(self.factor_id, str):
            raise RiskFactorError("factor_id required")
        if not self.name or not isinstance(self.name, str):
            raise RiskFactorError("name required")
        if self.category not in FACTOR_CATEGORIES:
            raise RiskFactorError(f"invalid category: {self.category!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise RiskFactorError(f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise RiskFactorError(f"invalid source: {self.source!r}")
        if self.effect_size is not None and not isinstance(self.effect_size, (int, float)):
            raise RiskFactorError("effect_size must be numeric or None")

    def is_prediction(self) -> bool:
        return self.source == "predicted"


class DiseaseRiskFactorEngine:
    """Risk factor registry with disease linkage and category queries."""

    def __init__(self) -> None:
        self._factors: Dict[str, RiskFactor] = {}
        self._disease_map: Dict[str, List[str]] = {}

    def add(self, factor: RiskFactor) -> RiskFactor:
        if factor.factor_id in self._factors:
            raise RiskFactorError(f"duplicate factor_id: {factor.factor_id}")
        self._factors[factor.factor_id] = factor
        return factor

    def get(self, factor_id: str) -> RiskFactor:
        try:
            return self._factors[factor_id]
        except KeyError as exc:
            raise RiskFactorError(f"unknown factor_id: {factor_id}") from exc

    def link_disease(self, disease_id: str, factor_id: str) -> None:
        self.get(factor_id)
        self._disease_map.setdefault(disease_id, [])
        if factor_id not in self._disease_map[disease_id]:
            self._disease_map[disease_id].append(factor_id)

    def factors_for_disease(self, disease_id: str) -> List[RiskFactor]:
        return [self.get(fid) for fid in self._disease_map.get(disease_id, [])]

    def by_category(self, category: str) -> List[RiskFactor]:
        if category not in FACTOR_CATEGORIES:
            raise RiskFactorError(f"invalid category: {category!r}")
        return [f for f in self._factors.values() if f.category == category]

    def by_evidence(self, level: str) -> List[RiskFactor]:
        if level not in EVIDENCE_LEVELS:
            raise RiskFactorError(f"invalid evidence_level: {level!r}")
        return [f for f in self._factors.values() if f.evidence_level == level]

    def ranked_for_disease(self, disease_id: str) -> List[RiskFactor]:
        factors = self.factors_for_disease(disease_id)
        return sorted(factors, key=lambda f: abs(f.effect_size or 0.0), reverse=True)

    def predictions(self) -> List[RiskFactor]:
        return [f for f in self._factors.values() if f.is_prediction()]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "factors": len(self._factors),
            "diseases": len(self._disease_map),
            "predictions": len(self.predictions()),
        }


def self_test() -> bool:
    engine = DiseaseRiskFactorEngine()
    f1 = RiskFactor("RF_smoking", "Smoking", "behavioral", evidence_level="established",
                    effect_size=2.5)
    f2 = RiskFactor("RF_age", "Age > 60", "demographic", evidence_level="established",
                    effect_size=1.8)
    engine.add(f1)
    engine.add(f2)
    engine.link_disease("D_heart", f1.factor_id)
    engine.link_disease("D_heart", f2.factor_id)
    ranked = engine.ranked_for_disease("D_heart")
    assert ranked[0].factor_id == "RF_smoking"
    assert len(engine.by_category("behavioral")) == 1
    assert len(engine.by_evidence("established")) == 2
    assert engine.stats()["factors"] == 2
    print("010 disease_risk_factor_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
