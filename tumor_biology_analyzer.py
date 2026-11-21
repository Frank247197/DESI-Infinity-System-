"""DESI Infinity System - Tumor Biology Analyzer (v6.2.0).

Analyzes tumor biological hallmarks (proliferation, angiogenesis,
immune evasion, genomic instability) using structured research scores.
Hallmark scores are research annotations, not prognostic outputs.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

HALLMARKS = ("proliferative_signaling", "growth_suppression_evasion",
             "resistance_to_apoptosis", "replicative_immortality",
             "angiogenesis", "invasion_metastasis", "genomic_instability",
             "immune_evasion", "inflammation", "metabolic_reprogramming")
SOURCES = ("curated", "literature", "predicted")


class TumorBiologyError(Exception):
    """Base tumor biology error."""


@dataclass
class TumorProfile:
    tumor_id: str
    cancer_id: str
    hallmark_scores: Dict[str, float]
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tumor_id or not isinstance(self.tumor_id, str):
            raise TumorBiologyError("tumor_id required")
        if not self.cancer_id or not isinstance(self.cancer_id, str):
            raise TumorBiologyError("cancer_id required")
        if self.source not in SOURCES:
            raise TumorBiologyError(f"invalid source: {self.source!r}")
        for k, v in self.hallmark_scores.items():
            if k not in HALLMARKS:
                raise TumorBiologyError(f"unknown hallmark: {k!r}")
            if not isinstance(v, (int, float)) or not 0.0 <= float(v) <= 1.0:
                raise TumorBiologyError(f"hallmark score for {k!r} must be in [0, 1]")

    def composite(self) -> float:
        if not self.hallmark_scores:
            return 0.0
        return round(sum(self.hallmark_scores.values()) / len(self.hallmark_scores), 4)


class TumorBiologyAnalyzer:
    """Hallmark profiles with comparative and dominant-hallmark queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, TumorProfile] = {}

    def add(self, profile: TumorProfile) -> TumorProfile:
        if profile.tumor_id in self._profiles:
            raise TumorBiologyError(f"duplicate tumor_id: {profile.tumor_id}")
        self._profiles[profile.tumor_id] = profile
        return profile

    def get(self, tumor_id: str) -> TumorProfile:
        try:
            return self._profiles[tumor_id]
        except KeyError as exc:
            raise TumorBiologyError(f"unknown tumor_id: {tumor_id}") from exc

    def for_cancer(self, cancer_id: str) -> List[TumorProfile]:
        return [p for p in self._profiles.values() if p.cancer_id == cancer_id]

    def dominant_hallmark(self, tumor_id: str) -> str:
        p = self.get(tumor_id)
        if not p.hallmark_scores:
            return "unknown"
        return max(p.hallmark_scores, key=lambda k: p.hallmark_scores[k])

    def rank_tumors(self) -> List[Dict[str, object]]:
        rows = [{"tumor_id": p.tumor_id, "cancer_id": p.cancer_id,
                 "composite": p.composite()} for p in self._profiles.values()]
        rows.sort(key=lambda r: r["composite"], reverse=True)  # type: ignore
        return rows

    def hallmark_ranking(self, hallmark: str) -> List[Dict[str, object]]:
        if hallmark not in HALLMARKS:
            raise TumorBiologyError(f"unknown hallmark: {hallmark!r}")
        rows = []
        for p in self._profiles.values():
            if hallmark in p.hallmark_scores:
                rows.append({"tumor_id": p.tumor_id,
                             "score": p.hallmark_scores[hallmark]})
        rows.sort(key=lambda r: r["score"], reverse=True)  # type: ignore
        return rows

    def compare(self, tumor_a: str, tumor_b: str) -> Dict[str, Dict[str, float]]:
        a = self.get(tumor_a).hallmark_scores
        b = self.get(tumor_b).hallmark_scores
        keys = set(a) | set(b)
        return {k: {"a": a.get(k, 0.0), "b": b.get(k, 0.0)} for k in sorted(keys)}

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "tumors": len(self._profiles),
                "cancers": len({p.cancer_id for p in self._profiles.values()})}


def self_test() -> bool:
    analyzer = TumorBiologyAnalyzer()
    analyzer.add(TumorProfile("T1", "C_luad",
                              {"proliferative_signaling": 0.9,
                               "angiogenesis": 0.8,
                               "immune_evasion": 0.6}))
    analyzer.add(TumorProfile("T2", "C_luad",
                              {"proliferative_signaling": 0.5,
                               "angiogenesis": 0.3,
                               "genomic_instability": 0.4}))
    assert analyzer.dominant_hallmark("T1") == "proliferative_signaling"
    assert analyzer.rank_tumors()[0]["tumor_id"] == "T1"
    assert analyzer.hallmark_ranking("angiogenesis")[0]["tumor_id"] == "T1"
    cmp = analyzer.compare("T1", "T2")
    assert cmp["proliferative_signaling"]["a"] == 0.9
    print("tumor_biology_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
