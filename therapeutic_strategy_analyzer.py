"""DESI Infinity System - Therapeutic Strategy Analyzer (v6.2.0).

Compares documented therapeutic strategy categories (monotherapy,
combination, targeted, immunomodulation, gene/cell-based) across
research dimensions. NO clinical recommendation, NO ranking of
treatment options for a specific patient.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STRATEGY_TYPES = ("monotherapy", "combination", "targeted", "immunomodulation",
                  "gene_therapy", "cell_therapy", "preventive", "other")
MATURITY = ("routine", "emerging", "experimental", "hypothetical")
SOURCES = ("curated", "literature", "predicted")


class TherapeuticStrategyError(Exception):
    """Base therapeutic strategy error."""


@dataclass
class TherapeuticStrategy:
    strategy_id: str
    disease_id: str
    name: str
    strategy_type: str
    maturity: str = "emerging"
    mechanism_class: str = ""
    known_limitations: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.strategy_id or not isinstance(self.strategy_id, str):
            raise TherapeuticStrategyError("strategy_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise TherapeuticStrategyError("disease_id required")
        if not self.name or not isinstance(self.name, str):
            raise TherapeuticStrategyError("name required")
        if self.strategy_type not in STRATEGY_TYPES:
            raise TherapeuticStrategyError(
                f"invalid strategy_type: {self.strategy_type!r}")
        if self.maturity not in MATURITY:
            raise TherapeuticStrategyError(f"invalid maturity: {self.maturity!r}")
        if self.source not in SOURCES:
            raise TherapeuticStrategyError(f"invalid source: {self.source!r}")


class TherapeuticStrategyAnalyzer:
    """Strategy comparison store with type / maturity / disease queries."""

    def __init__(self) -> None:
        self._strategies: Dict[str, TherapeuticStrategy] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}

    def add(self, strategy: TherapeuticStrategy) -> TherapeuticStrategy:
        if strategy.strategy_id in self._strategies:
            raise TherapeuticStrategyError(
                f"duplicate strategy_id: {strategy.strategy_id}")
        self._strategies[strategy.strategy_id] = strategy
        self._disease_index.setdefault(strategy.disease_id, []).append(
            strategy.strategy_id)
        self._type_index.setdefault(strategy.strategy_type, []).append(
            strategy.strategy_id)
        return strategy

    def get(self, strategy_id: str) -> TherapeuticStrategy:
        try:
            return self._strategies[strategy_id]
        except KeyError as exc:
            raise TherapeuticStrategyError(
                f"unknown strategy_id: {strategy_id}") from exc

    def for_disease(self, disease_id: str) -> List[TherapeuticStrategy]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def by_type(self, strategy_type: str) -> List[TherapeuticStrategy]:
        if strategy_type not in STRATEGY_TYPES:
            raise TherapeuticStrategyError(
                f"invalid strategy_type: {strategy_type!r}")
        return [self.get(s) for s in self._type_index.get(strategy_type, [])]

    def by_maturity(self, maturity: str) -> List[TherapeuticStrategy]:
        if maturity not in MATURITY:
            raise TherapeuticStrategyError(f"invalid maturity: {maturity!r}")
        return [s for s in self._strategies.values() if s.maturity == maturity]

    def compare(self, disease_id: str) -> List[Dict[str, object]]:
        rows = []
        for s in self.for_disease(disease_id):
            rows.append({
                "strategy_id": s.strategy_id,
                "name": s.name,
                "type": s.strategy_type,
                "maturity": s.maturity,
                "mechanism": s.mechanism_class,
                "limitations": list(s.known_limitations),
            })
        return rows

    def strategies_with_limitations(self) -> List[TherapeuticStrategy]:
        return [s for s in self._strategies.values() if s.known_limitations]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "strategies": len(self._strategies),
            "diseases": len(self._disease_index),
            "types": len(self._type_index),
        }


def self_test() -> bool:
    analyzer = TherapeuticStrategyAnalyzer()
    analyzer.add(TherapeuticStrategy(
        "S1", "D_t2d", "Metformin monotherapy", "monotherapy",
        maturity="routine", mechanism_class="biguanide",
        known_limitations=["GI intolerance", "B12 deficiency"]))
    analyzer.add(TherapeuticStrategy(
        "S2", "D_t2d", "GLP-1 + SGLT2 combination", "combination",
        maturity="emerging", mechanism_class="incretin + SGLT2i",
        known_limitations=["cost", "GI effects"]))
    analyzer.add(TherapeuticStrategy(
        "S3", "D_t2d", "Islet cell replacement", "cell_therapy",
        maturity="experimental", mechanism_class="beta cell replacement",
        known_limitations=["immunosuppression", "limited supply"]))
    assert len(analyzer.for_disease("D_t2d")) == 3
    assert len(analyzer.by_type("combination")) == 1
    assert len(analyzer.by_maturity("experimental")) == 1
    assert len(analyzer.compare("D_t2d")) == 3
    assert len(analyzer.strategies_with_limitations()) == 3
    print("therapeutic_strategy_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
