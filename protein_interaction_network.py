"""DESI Infinity System - Protein Interaction Network (v6.2.0).

Protein-protein interaction (PPI) graph with interaction evidence classes,
directions, and network centrality computations. Research-only; no
therapeutic inference.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INTERACTION_TYPES = ("binding", "phosphorylation", "ubiquitination",
                     "cleavage", "complex", "genetic_interaction", "other")
EVIDENCE_CLASSES = ("experimental", "database", "textmining",
                    "predicted", "unknown")
SOURCES = ("curated", "literature", "predicted")


class PPINetworkError(Exception):
    """Base PPI network error."""


@dataclass
class ProteinInteraction:
    interaction_id: str
    protein_a: str
    protein_b: str
    interaction_type: str = "binding"
    evidence_class: str = "unknown"
    confidence: float = 0.5
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.interaction_id or not isinstance(self.interaction_id, str):
            raise PPINetworkError("interaction_id required")
        if not self.protein_a or not self.protein_b:
            raise PPINetworkError("both protein_a and protein_b required")
        if self.protein_a == self.protein_b:
            raise PPINetworkError("self-interaction not allowed")
        if self.interaction_type not in INTERACTION_TYPES:
            raise PPINetworkError(f"invalid interaction_type: {self.interaction_type!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise PPINetworkError(f"invalid evidence_class: {self.evidence_class!r}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise PPINetworkError("confidence must be in [0, 1]")
        if self.source not in SOURCES:
            raise PPINetworkError(f"invalid source: {self.source!r}")


class ProteinInteractionNetwork:
    """Undirected PPI graph with neighbour and centrality queries."""

    def __init__(self) -> None:
        self._interactions: Dict[str, ProteinInteraction] = {}
        self._adjacency: Dict[str, Set[str]] = {}
        self._edge_index: Dict[str, Set[str]] = {}

    def add(self, interaction: ProteinInteraction) -> ProteinInteraction:
        if interaction.interaction_id in self._interactions:
            raise PPINetworkError(
                f"duplicate interaction_id: {interaction.interaction_id}")
        self._interactions[interaction.interaction_id] = interaction
        for a, b in ((interaction.protein_a, interaction.protein_b),
                     (interaction.protein_b, interaction.protein_a)):
            self._adjacency.setdefault(a, set()).add(b)
        for p in (interaction.protein_a, interaction.protein_b):
            self._edge_index.setdefault(p, set()).add(interaction.interaction_id)
        return interaction

    def get(self, interaction_id: str) -> ProteinInteraction:
        try:
            return self._interactions[interaction_id]
        except KeyError as exc:
            raise PPINetworkError(
                f"unknown interaction_id: {interaction_id}") from exc

    def neighbours(self, protein_id: str) -> List[str]:
        return sorted(self._adjacency.get(protein_id, set()))

    def interactions_of(self, protein_id: str) -> List[ProteinInteraction]:
        return [self.get(iid) for iid in self._edge_index.get(protein_id, set())]

    def degree(self, protein_id: str) -> int:
        return len(self._adjacency.get(protein_id, set()))

    def hubs(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise PPINetworkError("top_n must be positive")
        rows = [{"protein_id": p, "degree": self.degree(p)} for p in self._adjacency]
        rows.sort(key=lambda r: r["degree"], reverse=True)  # type: ignore
        return rows[:top_n]

    def shortest_path(self, source: str, target: str, max_depth: int = 6) -> List[str]:
        if source not in self._adjacency or target not in self._adjacency:
            return []
        frontier = [[source]]
        seen: Set[str] = {source}
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: List[List[str]] = []
            for path in frontier:
                node = path[-1]
                for nbr in self._adjacency.get(node, set()):
                    if nbr == target:
                        return path + [nbr]
                    if nbr not in seen:
                        seen.add(nbr)
                        next_frontier.append(path + [nbr])
            frontier = next_frontier
            depth += 1
        return []

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "interactions": len(self._interactions),
            "proteins": len(self._adjacency),
            "max_degree": max((self.degree(p) for p in self._adjacency), default=0),
        }


def self_test() -> bool:
    net = ProteinInteractionNetwork()
    net.add(ProteinInteraction("I1", "TP53", "MDM2", "binding", "experimental", 0.95))
    net.add(ProteinInteraction("I2", "TP53", "BAX", "binding", "experimental", 0.9))
    net.add(ProteinInteraction("I3", "MDM2", "AKT1", "phosphorylation", "database", 0.7))
    net.add(ProteinInteraction("I4", "AKT1", "MTOR", "binding", "experimental", 0.85))
    assert net.neighbours("TP53") == ["BAX", "MDM2"]
    assert net.degree("TP53") == 2
    assert net.shortest_path("TP53", "MTOR") == ["TP53", "MDM2", "AKT1", "MTOR"]
    assert net.hubs(1)[0]["protein_id"] == "TP53"
    assert net.stats()["interactions"] == 4
    print("protein_interaction_network: OK")
    return True


if __name__ == "__main__":
    self_test()
