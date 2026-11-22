"""DESI Infinity System - Drug Target Discovery Engine (v6.2.0).

Ranks candidate drug targets from structured evidence signals: genetic
association, expression alteration, pathway centrality, tractability.
All ranking outputs are LABELLED as predictions for research
prioritisation. NO target validation claims.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

TRACTABILITY = ("high", "medium", "low", "unknown")
TARGET_CLASSES = ("kinase", "gpcr", "ion_channel", "protease",
                  "transporter", "transcription_factor", "other")
SOURCES = ("curated", "literature", "predicted")


class DrugTargetError(Exception):
    """Base drug target error."""


@dataclass
class CandidateTarget:
    candidate_id: str
    gene_symbol: str
    disease_id: str
    target_class: str = "other"
    genetic_evidence: float = 0.0
    expression_evidence: float = 0.0
    pathway_evidence: float = 0.0
    tractability: str = "unknown"
    is_prediction: bool = True
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.candidate_id or not isinstance(self.candidate_id, str):
            raise DrugTargetError("candidate_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise DrugTargetError("gene_symbol required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise DrugTargetError("disease_id required")
        if self.target_class not in TARGET_CLASSES:
            raise DrugTargetError(f"invalid target_class: {self.target_class!r}")
        if self.tractability not in TRACTABILITY:
            raise DrugTargetError(f"invalid tractability: {self.tractability!r}")
        if self.source not in SOURCES:
            raise DrugTargetError(f"invalid source: {self.source!r}")
        for label, val in (("genetic_evidence", self.genetic_evidence),
                           ("expression_evidence", self.expression_evidence),
                           ("pathway_evidence", self.pathway_evidence)):
            if not isinstance(val, (int, float)) or not 0.0 <= float(val) <= 1.0:
                raise DrugTargetError(f"{label} must be in [0, 1]")

    def priority(self) -> float:
        tract_bonus = {"high": 0.15, "medium": 0.08, "low": 0.0,
                       "unknown": 0.0}[self.tractability]
        score = (0.45 * self.genetic_evidence
                 + 0.30 * self.expression_evidence
                 + 0.25 * self.pathway_evidence) + tract_bonus
        return round(min(1.0, score), 4)


class DrugTargetDiscoveryEngine:
    """Registry + ranked candidate predictions per disease."""

    def __init__(self) -> None:
        self._candidates: Dict[str, CandidateTarget] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, candidate: CandidateTarget) -> CandidateTarget:
        if candidate.candidate_id in self._candidates:
            raise DrugTargetError(f"duplicate candidate_id: {candidate.candidate_id}")
        self._candidates[candidate.candidate_id] = candidate
        self._disease_index.setdefault(candidate.disease_id, []).append(
            candidate.candidate_id)
        return candidate

    def get(self, candidate_id: str) -> CandidateTarget:
        try:
            return self._candidates[candidate_id]
        except KeyError as exc:
            raise DrugTargetError(f"unknown candidate_id: {candidate_id}") from exc

    def for_disease(self, disease_id: str) -> List[CandidateTarget]:
        return [self.get(c) for c in self._disease_index.get(disease_id, [])]

    def ranked(self, disease_id: str, top_n: int = 10) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise DrugTargetError("top_n must be positive")
        rows = [{"candidate_id": c.candidate_id,
                 "gene_symbol": c.gene_symbol,
                 "priority": c.priority(),
                 "target_class": c.target_class,
                 "tractability": c.tractability,
                 "is_prediction": c.is_prediction}
                for c in self.for_disease(disease_id)]
        rows.sort(key=lambda r: r["priority"], reverse=True)  # type: ignore
        return rows[:top_n]

    def by_class(self, target_class: str) -> List[CandidateTarget]:
        if target_class not in TARGET_CLASSES:
            raise DrugTargetError(f"invalid target_class: {target_class!r}")
        return [c for c in self._candidates.values()
                if c.target_class == target_class]

    def high_tractability(self) -> List[CandidateTarget]:
        return [c for c in self._candidates.values() if c.tractability == "high"]

    def predictions(self) -> List[CandidateTarget]:
        return [c for c in self._candidates.values() if c.is_prediction]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "candidates": len(self._candidates),
            "diseases": len(self._disease_index),
            "high_tractability": len(self.high_tractability()),
            "predictions": len(self.predictions()),
        }


def self_test() -> bool:
    engine = DrugTargetDiscoveryEngine()
    engine.add(CandidateTarget(
        "CT1", "PCSK9", "D_hyperlipidemia", "protease",
        genetic_evidence=0.9, expression_evidence=0.4, pathway_evidence=0.6,
        tractability="high"))
    engine.add(CandidateTarget(
        "CT2", "LDLR", "D_hyperlipidemia", "transporter",
        genetic_evidence=0.85, expression_evidence=0.7, pathway_evidence=0.6,
        tractability="medium"))
    engine.add(CandidateTarget(
        "CT3", "APOB", "D_hyperlipidemia", "other",
        genetic_evidence=0.6, expression_evidence=0.3, pathway_evidence=0.4,
        tractability="low"))
    ranked = engine.ranked("D_hyperlipidemia")
    assert ranked[0]["gene_symbol"] == "PCSK9"
    assert len(engine.for_disease("D_hyperlipidemia")) == 3
    assert len(engine.by_class("protease")) == 1
    assert len(engine.high_tractability()) == 1
    assert len(engine.predictions()) == 3
    print("drug_target_discovery_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
