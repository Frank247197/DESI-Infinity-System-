"""DESI Infinity System - Tumor Microenvironment Engine (v6.2.0).

Models tumor microenvironment (TME) composition using structured cell-type
abundance profiles, immune phenotypes, and stromal signatures. Research
annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CELL_TYPES = ("tumor_cell", "cd8_t_cell", "cd4_t_cell", "treg",
              "nk_cell", "b_cell", "macrophage_m1", "macrophage_m2",
              "dendritic_cell", "neutrophil", "caf", "endothelial",
              "pericyte", "other")
IMMUNE_PHENOTYPES = ("hot", "cold", "excluded", "immunosuppressed", "unknown")
SOURCES = ("curated", "literature", "predicted")


class TMEError(Exception):
    """Base TME error."""


@dataclass
class TMEProfile:
    profile_id: str
    tumor_id: str
    cell_abundance: Dict[str, float]
    immune_phenotype: str = "unknown"
    stromal_score: float = 0.0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise TMEError("profile_id required")
        if not self.tumor_id or not isinstance(self.tumor_id, str):
            raise TMEError("tumor_id required")
        if self.immune_phenotype not in IMMUNE_PHENOTYPES:
            raise TMEError(f"invalid immune_phenotype: {self.immune_phenotype!r}")
        if self.source not in SOURCES:
            raise TMEError(f"invalid source: {self.source!r}")
        if not 0.0 <= float(self.stromal_score) <= 1.0:
            raise TMEError("stromal_score must be in [0, 1]")
        for ct, v in self.cell_abundance.items():
            if ct not in CELL_TYPES:
                raise TMEError(f"unknown cell_type: {ct!r}")
            if not isinstance(v, (int, float)) or v < 0:
                raise TMEError(f"abundance for {ct!r} must be non-negative")

    def immune_infiltration(self) -> float:
        immune = {"cd8_t_cell", "cd4_t_cell", "treg", "nk_cell", "b_cell",
                  "macrophage_m1", "macrophage_m2", "dendritic_cell",
                  "neutrophil"}
        return round(sum(v for k, v in self.cell_abundance.items() if k in immune), 4)

    def immune_suppression_index(self) -> float:
        sup = {"treg", "macrophage_m2"}
        eff = {"cd8_t_cell", "nk_cell", "macrophage_m1"}
        s = sum(self.cell_abundance.get(k, 0.0) for k in sup)
        e = sum(self.cell_abundance.get(k, 0.0) for k in eff)
        if s + e == 0:
            return 0.0
        return round(s / (s + e), 4)


class TumorMicroenvironmentEngine:
    """TME profile registry with immune and stromal analyses."""

    def __init__(self) -> None:
        self._profiles: Dict[str, TMEProfile] = {}

    def add(self, profile: TMEProfile) -> TMEProfile:
        if profile.profile_id in self._profiles:
            raise TMEError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        return profile

    def get(self, profile_id: str) -> TMEProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise TMEError(f"unknown profile_id: {profile_id}") from exc

    def for_tumor(self, tumor_id: str) -> List[TMEProfile]:
        return [p for p in self._profiles.values() if p.tumor_id == tumor_id]

    def by_phenotype(self, phenotype: str) -> List[TMEProfile]:
        if phenotype not in IMMUNE_PHENOTYPES:
            raise TMEError(f"invalid immune_phenotype: {phenotype!r}")
        return [p for p in self._profiles.values() if p.immune_phenotype == phenotype]

    def most_infiltrated(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise TMEError("top_n must be positive")
        rows = [{"profile_id": p.profile_id,
                 "immune_infiltration": p.immune_infiltration()}
                for p in self._profiles.values()]
        rows.sort(key=lambda r: r["immune_infiltration"], reverse=True)  # type: ignore
        return rows[:top_n]

    def most_suppressed(self) -> List[Dict[str, object]]:
        rows = [{"profile_id": p.profile_id,
                 "suppression_index": p.immune_suppression_index()}
                for p in self._profiles.values()]
        rows.sort(key=lambda r: r["suppression_index"], reverse=True)  # type: ignore
        return rows

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "profiles": len(self._profiles),
                "tumors": len({p.tumor_id for p in self._profiles.values()})}


def self_test() -> bool:
    engine = TumorMicroenvironmentEngine()
    engine.add(TMEProfile("TME1", "T1",
                          {"cd8_t_cell": 0.3, "cd4_t_cell": 0.1,
                           "treg": 0.05, "macrophage_m1": 0.1,
                           "tumor_cell": 0.45},
                          immune_phenotype="hot", stromal_score=0.2))
    engine.add(TMEProfile("TME2", "T2",
                          {"treg": 0.3, "macrophage_m2": 0.25,
                           "cd8_t_cell": 0.05, "tumor_cell": 0.4},
                          immune_phenotype="immunosuppressed", stromal_score=0.6))
    assert len(engine.by_phenotype("hot")) == 1
    assert engine.most_infiltrated(1)[0]["profile_id"] == "TME1"
    assert engine.most_suppressed()[0]["profile_id"] == "TME2"
    assert engine.get("TME2").immune_suppression_index() > 0.5
    print("tumor_microenvironment_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
