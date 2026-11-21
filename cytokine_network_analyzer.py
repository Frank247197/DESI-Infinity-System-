"""DESI Infinity System - Cytokine Network Analyzer (v6.2.0).

Models cytokine signaling networks: producers, targets, effects, and
pleiotropy. Supports reachability queries across the cytokine network.
Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FAMILIES = ("interleukin", "interferon", "chemokine", "tumor_necrosis",
            "transforming_growth", "colony_stimulating", "other")
SIGNAL_TYPES = ("pro_inflammatory", "anti_inflammatory", "mixed", "unknown")
SOURCES = ("curated", "literature", "predicted")


class CytokineNetworkError(Exception):
    """Base cytokine network error."""


@dataclass
class Cytokine:
    cytokine_id: str
    name: str
    family: str = "other"
    signal_type: str = "unknown"
    cellular_sources: List[str] = field(default_factory=list)
    cellular_targets: List[str] = field(default_factory=list)
    receptor: str = ""
    induces: List[str] = field(default_factory=list)
    suppresses: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cytokine_id or not isinstance(self.cytokine_id, str):
            raise CytokineNetworkError("cytokine_id required")
        if not self.name or not isinstance(self.name, str):
            raise CytokineNetworkError("name required")
        if self.family not in FAMILIES:
            raise CytokineNetworkError(f"invalid family: {self.family!r}")
        if self.signal_type not in SIGNAL_TYPES:
            raise CytokineNetworkError(f"invalid signal_type: {self.signal_type!r}")
        if self.source not in SOURCES:
            raise CytokineNetworkError(f"invalid source: {self.source!r}")


class CytokineNetworkAnalyzer:
    """Cytokine network with induction/suppression reachability."""

    def __init__(self) -> None:
        self._cytokines: Dict[str, Cytokine] = {}
        self._family_index: Dict[str, List[str]] = {}
        self._signal_index: Dict[str, List[str]] = {}

    def add(self, cytokine: Cytokine) -> Cytokine:
        if cytokine.cytokine_id in self._cytokines:
            raise CytokineNetworkError(f"duplicate cytokine_id: {cytokine.cytokine_id}")
        self._cytokines[cytokine.cytokine_id] = cytokine
        self._family_index.setdefault(cytokine.family, []).append(cytokine.cytokine_id)
        self._signal_index.setdefault(cytokine.signal_type, []).append(
            cytokine.cytokine_id)
        return cytokine

    def get(self, cytokine_id: str) -> Cytokine:
        try:
            return self._cytokines[cytokine_id]
        except KeyError as exc:
            raise CytokineNetworkError(f"unknown cytokine_id: {cytokine_id}") from exc

    def by_family(self, family: str) -> List[Cytokine]:
        if family not in FAMILIES:
            raise CytokineNetworkError(f"invalid family: {family!r}")
        return [self.get(cid) for cid in self._family_index.get(family, [])]

    def by_signal_type(self, signal_type: str) -> List[Cytokine]:
        if signal_type not in SIGNAL_TYPES:
            raise CytokineNetworkError(f"invalid signal_type: {signal_type!r}")
        return [self.get(cid) for cid in self._signal_index.get(signal_type, [])]

    def induces_closure(self, start_id: str, max_depth: int = 6) -> Set[str]:
        self.get(start_id)
        reached: Set[str] = set()
        frontier = [start_id]
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: List[str] = []
            for cid in frontier:
                for target in self.get(cid).induces:
                    if target not in reached:
                        reached.add(target)
                        if target in self._cytokines:
                            next_frontier.append(target)
            frontier = next_frontier
            depth += 1
        return reached

    def suppressive_cytokines(self) -> List[Cytokine]:
        return [c for c in self._cytokines.values() if c.suppresses]

    def cross_talk(self, a_id: str, b_id: str) -> bool:
        a = self.get(a_id)
        b = self.get(b_id)
        return (b_id in a.induces or a_id in b.induces
                or b_id in a.suppresses or a_id in b.suppresses)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "cytokines": len(self._cytokines),
            "pro_inflammatory": len(self.by_signal_type("pro_inflammatory")),
            "anti_inflammatory": len(self.by_signal_type("anti_inflammatory")),
            "families": len(self._family_index),
        }


def self_test() -> bool:
    analyzer = CytokineNetworkAnalyzer()
    analyzer.add(Cytokine(
        "IL1B", "IL-1beta", "interleukin", "pro_inflammatory",
        ["macrophage", "monocyte"], ["endothelium", "liver"],
        "IL1R1", induces=["IL6", "TNF"], suppresses=[]))
    analyzer.add(Cytokine(
        "IL6", "IL-6", "interleukin", "pro_inflammatory",
        ["macrophage", "t_cell"], ["liver", "b_cell"],
        "IL6R", induces=["CRP"], suppresses=[]))
    analyzer.add(Cytokine(
        "TNF", "TNF-alpha", "tumor_necrosis", "pro_inflammatory",
        ["macrophage"], ["endothelium", "adipocyte"],
        "TNFRSF1A", induces=["IL1B"], suppresses=[]))
    analyzer.add(Cytokine(
        "IL10", "IL-10", "interleukin", "anti_inflammatory",
        ["treg", "macrophage"], ["macrophage", "dendritic_cell"],
        "IL10RA", induces=[], suppresses=["TNF", "IL1B"]))
    assert analyzer.by_family("interleukin")[0].cytokine_id == "IL1B"
    assert len(analyzer.by_signal_type("pro_inflammatory")) == 3
    reached = analyzer.induces_closure("TNF")
    assert "IL1B" in reached and "IL6" in reached
    assert len(analyzer.suppressive_cytokines()) == 1
    assert analyzer.cross_talk("IL1B", "IL10") is True
    print("cytokine_network_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
