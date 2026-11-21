"""DESI Infinity System - Pathogen Mutation Tracker (v6.2.0).

Tracks mutations in pathogen genomes over time with lineage assignment,
first-detection dates, and frequency trajectories. Research only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

EFFECT_CLASSES = ("immune_escape", "transmissibility_increase",
                  "drug_resistance", "diagnostic_escape", "neutral",
                  "unknown")
SOURCES = ("curated", "literature", "predicted")


class PathogenMutationError(Exception):
    """Base pathogen mutation error."""


@dataclass
class PathogenMutation:
    mutation_id: str
    pathogen_id: str
    gene: str
    aa_change: str = ""
    effect_class: str = "unknown"
    lineage: str = ""
    first_detected: str = ""
    frequency: float = 0.0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mutation_id or not isinstance(self.mutation_id, str):
            raise PathogenMutationError("mutation_id required")
        if not self.pathogen_id or not isinstance(self.pathogen_id, str):
            raise PathogenMutationError("pathogen_id required")
        if not self.gene or not isinstance(self.gene, str):
            raise PathogenMutationError("gene required")
        if self.effect_class not in EFFECT_CLASSES:
            raise PathogenMutationError(f"invalid effect_class: {self.effect_class!r}")
        if self.source not in SOURCES:
            raise PathogenMutationError(f"invalid source: {self.source!r}")
        if not 0.0 <= float(self.frequency) <= 1.0:
            raise PathogenMutationError("frequency must be in [0, 1]")


class PathogenMutationTracker:
    """Mutation registry with lineage / effect / trajectory queries."""

    def __init__(self) -> None:
        self._mutations: Dict[str, PathogenMutation] = {}
        self._lineage_index: Dict[str, List[str]] = {}
        self._pathogen_index: Dict[str, List[str]] = {}

    def add(self, mutation: PathogenMutation) -> PathogenMutation:
        if mutation.mutation_id in self._mutations:
            raise PathogenMutationError(f"duplicate mutation_id: {mutation.mutation_id}")
        self._mutations[mutation.mutation_id] = mutation
        if mutation.lineage:
            self._lineage_index.setdefault(mutation.lineage, []).append(mutation.mutation_id)
        self._pathogen_index.setdefault(mutation.pathogen_id, []).append(mutation.mutation_id)
        return mutation

    def get(self, mutation_id: str) -> PathogenMutation:
        try:
            return self._mutations[mutation_id]
        except KeyError as exc:
            raise PathogenMutationError(f"unknown mutation_id: {mutation_id}") from exc

    def for_pathogen(self, pathogen_id: str) -> List[PathogenMutation]:
        return [self.get(mid) for mid in self._pathogen_index.get(pathogen_id, [])]

    def by_lineage(self, lineage: str) -> List[PathogenMutation]:
        return [self.get(mid) for mid in self._lineage_index.get(lineage, [])]

    def by_effect(self, effect: str) -> List[PathogenMutation]:
        if effect not in EFFECT_CLASSES:
            raise PathogenMutationError(f"invalid effect_class: {effect!r}")
        return [m for m in self._mutations.values() if m.effect_class == effect]

    def high_frequency(self, threshold: float = 0.5) -> List[PathogenMutation]:
        return [m for m in self._mutations.values() if m.frequency >= threshold]

    def escape_mutations(self) -> List[PathogenMutation]:
        return [m for m in self._mutations.values()
                if m.effect_class in ("immune_escape", "diagnostic_escape")]

    def resistance_mutations(self) -> List[PathogenMutation]:
        return self.by_effect("drug_resistance")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "mutations": len(self._mutations),
            "lineages": len(self._lineage_index),
            "pathogens": len(self._pathogen_index),
        }


def self_test() -> bool:
    tracker = PathogenMutationTracker()
    tracker.add(PathogenMutation(
        "M1", "NCBITaxon:2697049", "S", "N501Y",
        "transmissibility_increase", "B.1.1.7", "2020-09", 0.85))
    tracker.add(PathogenMutation(
        "M2", "NCBITaxon:2697049", "S", "E484K",
        "immune_escape", "B.1.351", "2020-10", 0.6))
    tracker.add(PathogenMutation(
        "M3", "NCBITaxon:2697049", "RdRp", "P323L",
        "neutral", "", "2020-03", 0.95))
    assert len(tracker.for_pathogen("NCBITaxon:2697049")) == 3
    assert tracker.by_lineage("B.1.1.7")[0].mutation_id == "M1"
    assert len(tracker.by_effect("immune_escape")) == 1
    assert len(tracker.high_frequency(0.8)) == 2
    assert len(tracker.escape_mutations()) == 1
    print("pathogen_mutation_tracker: OK")
    return True


if __name__ == "__main__":
    self_test()
