"""DESI Infinity System - Combination Therapy Research (v6.2.0).

Research store for combination therapeutic approaches: components,
rationale, documented synergy/antagonism, and research status.
NO clinical recommendation or dosing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INTERACTION_OUTCOMES = ("synergistic", "additive", "antagonistic",
                        "independent", "unknown")
RESEARCH_STATUS = ("approved", "in_trials", "preclinical", "discontinued",
                   "unknown")
SOURCES = ("curated", "literature", "predicted")


class CombinationTherapyError(Exception):
    """Base combination therapy error."""


@dataclass
class CombinationTherapy:
    combination_id: str
    disease_id: str
    component_treatment_ids: List[str]
    rationale: str = ""
    interaction_outcome: str = "unknown"
    research_status: str = "unknown"
    documented_limitations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.combination_id or not isinstance(self.combination_id, str):
            raise CombinationTherapyError("combination_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise CombinationTherapyError("disease_id required")
        if not self.component_treatment_ids or len(self.component_treatment_ids) < 2:
            raise CombinationTherapyError(
                "at least two component_treatment_ids required")
        if self.interaction_outcome not in INTERACTION_OUTCOMES:
            raise CombinationTherapyError(
                f"invalid interaction_outcome: {self.interaction_outcome!r}")
        if self.research_status not in RESEARCH_STATUS:
            raise CombinationTherapyError(
                f"invalid research_status: {self.research_status!r}")
        if self.source not in SOURCES:
            raise CombinationTherapyError(f"invalid source: {self.source!r}")


class CombinationTherapyResearch:
    """Combination store with disease / component / outcome queries."""

    def __init__(self) -> None:
        self._combinations: Dict[str, CombinationTherapy] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._component_index: Dict[str, List[str]] = {}

    def add(self, combo: CombinationTherapy) -> CombinationTherapy:
        if combo.combination_id in self._combinations:
            raise CombinationTherapyError(
                f"duplicate combination_id: {combo.combination_id}")
        self._combinations[combo.combination_id] = combo
        self._disease_index.setdefault(combo.disease_id, []).append(
            combo.combination_id)
        for c in combo.component_treatment_ids:
            self._component_index.setdefault(c, []).append(combo.combination_id)
        return combo

    def get(self, combination_id: str) -> CombinationTherapy:
        try:
            return self._combinations[combination_id]
        except KeyError as exc:
            raise CombinationTherapyError(
                f"unknown combination_id: {combination_id}") from exc

    def for_disease(self, disease_id: str) -> List[CombinationTherapy]:
        return [self.get(c) for c in self._disease_index.get(disease_id, [])]

    def with_component(self, treatment_id: str) -> List[CombinationTherapy]:
        return [self.get(c) for c in self._component_index.get(treatment_id, [])]

    def by_outcome(self, outcome: str) -> List[CombinationTherapy]:
        if outcome not in INTERACTION_OUTCOMES:
            raise CombinationTherapyError(
                f"invalid interaction_outcome: {outcome!r}")
        return [c for c in self._combinations.values()
                if c.interaction_outcome == outcome]

    def approved(self) -> List[CombinationTherapy]:
        return [c for c in self._combinations.values()
                if c.research_status == "approved"]

    def synergistic(self) -> List[CombinationTherapy]:
        return self.by_outcome("synergistic")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "combinations": len(self._combinations),
            "diseases": len(self._disease_index),
            "components": len(self._component_index),
            "approved": len(self.approved()),
        }


def self_test() -> bool:
    research = CombinationTherapyResearch()
    research.add(CombinationTherapy(
        "CB1", "D_melanoma",
        ["T_dabrafenib", "T_trametinib"],
        rationale="dual BRAF+MEK blockade",
        interaction_outcome="synergistic", research_status="approved",
        documented_limitations=["pyrexia", "skin toxicity"]))
    research.add(CombinationTherapy(
        "CB2", "D_melanoma",
        ["T_dabrafenib", "T_trametinib", "T_pembrolizumab"],
        rationale="triple combination",
        interaction_outcome="synergistic", research_status="in_trials",
        documented_limitations=["toxicity"]))
    research.add(CombinationTherapy(
        "CB3", "D_t2d",
        ["T_metformin", "T_glp1"],
        rationale="complementary mechanisms",
        interaction_outcome="additive", research_status="approved"))
    assert len(research.for_disease("D_melanoma")) == 2
    assert len(research.with_component("T_dabrafenib")) == 2
    assert len(research.by_outcome("synergistic")) == 2
    assert len(research.approved()) == 2
    assert len(research.synergistic()) == 2
    print("combination_therapy_research: OK")
    return True


if __name__ == "__main__":
    self_test()
