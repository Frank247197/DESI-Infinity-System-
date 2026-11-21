"""DESI Infinity System - Biomarker Discovery Analyzer (v6.2.0).

Candidate biomarker discovery from structured research evidence
(differential expression, cohort effect sizes, replication status).
Ranked candidates are labelled as research predictions only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CANDIDATE_TYPES = ("rna", "protein", "metabolite", "mirna", "cell_free_dna",
                   "imaging", "clinical_score", "other")
REPLICATION_STATUS = ("replicated", "single_cohort", "not_replicated",
                      "preliminary", "unknown")


class BiomarkerDiscoveryError(Exception):
    """Base biomarker discovery error."""


@dataclass
class CandidateBiomarker:
    candidate_id: str
    disease_id: str
    candidate_type: str
    name: str
    effect_size: float = 0.0
    p_value: Optional[float] = None
    cohort_size: int = 0
    replication: str = "unknown"
    is_prediction: bool = True
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.candidate_id or not isinstance(self.candidate_id, str):
            raise BiomarkerDiscoveryError("candidate_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise BiomarkerDiscoveryError("disease_id required")
        if self.candidate_type not in CANDIDATE_TYPES:
            raise BiomarkerDiscoveryError(
                f"invalid candidate_type: {self.candidate_type!r}")
        if self.replication not in REPLICATION_STATUS:
            raise BiomarkerDiscoveryError(
                f"invalid replication: {self.replication!r}")
        if not isinstance(self.effect_size, (int, float)):
            raise BiomarkerDiscoveryError("effect_size must be numeric")
        if self.p_value is not None:
            if not isinstance(self.p_value, (int, float)):
                raise BiomarkerDiscoveryError("p_value must be numeric or None")
            if not 0.0 <= float(self.p_value) <= 1.0:
                raise BiomarkerDiscoveryError("p_value must be in [0, 1]")
        if not isinstance(self.cohort_size, int) or self.cohort_size < 0:
            raise BiomarkerDiscoveryError("cohort_size must be non-negative int")

    def priority_score(self) -> float:
        score = 0.0
        if self.replication == "replicated":
            score += 0.4
        elif self.replication == "single_cohort":
            score += 0.2
        if self.p_value is not None and self.p_value < 0.001:
            score += 0.3
        elif self.p_value is not None and self.p_value < 0.05:
            score += 0.15
        if abs(self.effect_size) >= 1.0:
            score += 0.2
        if self.cohort_size >= 500:
            score += 0.1
        return round(min(1.0, score), 4)


class BiomarkerDiscoveryAnalyzer:
    """Ranking and filtering over structured discovery candidates."""

    def __init__(self) -> None:
        self._candidates: Dict[str, CandidateBiomarker] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, candidate: CandidateBiomarker) -> CandidateBiomarker:
        if candidate.candidate_id in self._candidates:
            raise BiomarkerDiscoveryError(
                f"duplicate candidate_id: {candidate.candidate_id}")
        self._candidates[candidate.candidate_id] = candidate
        self._disease_index.setdefault(candidate.disease_id, []).append(
            candidate.candidate_id)
        return candidate

    def get(self, candidate_id: str) -> CandidateBiomarker:
        try:
            return self._candidates[candidate_id]
        except KeyError as exc:
            raise BiomarkerDiscoveryError(
                f"unknown candidate_id: {candidate_id}") from exc

    def for_disease(self, disease_id: str) -> List[CandidateBiomarker]:
        return [self.get(c) for c in self._disease_index.get(disease_id, [])]

    def ranked_for_disease(self, disease_id: str, top_n: int = 10
                           ) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise BiomarkerDiscoveryError("top_n must be positive")
        rows = [{"candidate_id": c.candidate_id, "name": c.name,
                 "type": c.candidate_type, "priority": c.priority_score(),
                 "replication": c.replication}
                for c in self.for_disease(disease_id)]
        rows.sort(key=lambda r: r["priority"], reverse=True)  # type: ignore
        return rows[:top_n]

    def replicated(self, disease_id: Optional[str] = None) -> List[CandidateBiomarker]:
        pool = ([c for c in self._candidates.values() if c.disease_id == disease_id]
                if disease_id else self._candidates.values())
        return [c for c in pool if c.replication == "replicated"]

    def by_type(self, candidate_type: str) -> List[CandidateBiomarker]:
        if candidate_type not in CANDIDATE_TYPES:
            raise BiomarkerDiscoveryError(
                f"invalid candidate_type: {candidate_type!r}")
        return [c for c in self._candidates.values()
                if c.candidate_type == candidate_type]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "candidates": len(self._candidates),
            "diseases": len(self._disease_index),
            "replicated": len(self.replicated()),
        }


def self_test() -> bool:
    analyzer = BiomarkerDiscoveryAnalyzer()
    analyzer.add(CandidateBiomarker(
        "CB1", "D_pd", "mirna", "miR-1234",
        effect_size=1.8, p_value=0.0005, cohort_size=800, replication="replicated"))
    analyzer.add(CandidateBiomarker(
        "CB2", "D_pd", "protein", "ProteinX",
        effect_size=0.6, p_value=0.04, cohort_size=120, replication="single_cohort"))
    analyzer.add(CandidateBiomarker(
        "CB3", "D_ad", "metabolite", "MetabY",
        effect_size=1.2, p_value=0.001, cohort_size=600, replication="replicated"))
    ranked = analyzer.ranked_for_disease("D_pd")
    assert ranked[0]["candidate_id"] == "CB1"
    assert len(analyzer.for_disease("D_pd")) == 2
    assert len(analyzer.replicated()) == 2
    assert len(analyzer.replicated("D_pd")) == 1
    assert len(analyzer.by_type("protein")) == 1
    print("biomarker_discovery_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
