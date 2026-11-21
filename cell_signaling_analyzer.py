"""DESI Infinity System - Cell Signaling Analyzer (v6.2.0).

Models signal transduction cascades: ligand -> receptor -> kinase ->
transcription factor. Supports cascade reachability and enrichment
queries. Research-only; no therapeutic inference.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MOLECULE_ROLES = ("ligand", "receptor", "kinase", "phosphatase",
                  "gtpase", "adapter", "transcription_factor",
                  "second_messenger", "other")
SIGNAL_OUTCOMES = ("proliferation", "survival", "death", "differentiation",
                   "migration", "metabolic", "other")
SOURCES = ("curated", "literature", "predicted")


class CellSignalingError(Exception):
    """Base cell signaling error."""


@dataclass
class SignalingStep:
    step_id: str
    from_molecule: str
    to_molecule: str
    role: str = "other"
    effect: str = "activating"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.step_id or not isinstance(self.step_id, str):
            raise CellSignalingError("step_id required")
        if not self.from_molecule or not self.to_molecule:
            raise CellSignalingError("molecules required")
        if self.role not in MOLECULE_ROLES:
            raise CellSignalingError(f"invalid role: {self.role!r}")
        if self.source not in SOURCES:
            raise CellSignalingError(f"invalid source: {self.source!r}")


@dataclass
class SignalingCascade:
    cascade_id: str
    name: str
    outcome: str = "other"
    tissue: str = ""
    steps: List[SignalingStep] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cascade_id or not isinstance(self.cascade_id, str):
            raise CellSignalingError("cascade_id required")
        if self.outcome not in SIGNAL_OUTCOMES:
            raise CellSignalingError(f"invalid outcome: {self.outcome!r}")
        if self.source not in SOURCES:
            raise CellSignalingError(f"invalid source: {self.source!r}")


class CellSignalingAnalyzer:
    """Cascade registry with reachability and outcome queries."""

    def __init__(self) -> None:
        self._cascades: Dict[str, SignalingCascade] = {}
        self._outcome_index: Dict[str, List[str]] = {}

    def add(self, cascade: SignalingCascade) -> SignalingCascade:
        if cascade.cascade_id in self._cascades:
            raise CellSignalingError(f"duplicate cascade_id: {cascade.cascade_id}")
        self._cascades[cascade.cascade_id] = cascade
        self._outcome_index.setdefault(cascade.outcome, []).append(cascade.cascade_id)
        return cascade

    def get(self, cascade_id: str) -> SignalingCascade:
        try:
            return self._cascades[cascade_id]
        except KeyError as exc:
            raise CellSignalingError(f"unknown cascade_id: {cascade_id}") from exc

    def by_outcome(self, outcome: str) -> List[SignalingCascade]:
        if outcome not in SIGNAL_OUTCOMES:
            raise CellSignalingError(f"invalid outcome: {outcome!r}")
        return [self.get(c) for c in self._outcome_index.get(outcome, [])]

    def cascade_path(self, cascade_id: str) -> List[str]:
        c = self.get(cascade_id)
        if not c.steps:
            return []
        adj: Dict[str, List[str]] = {}
        for s in c.steps:
            adj.setdefault(s.from_molecule, []).append(s.to_molecule)
        start = c.steps[0].from_molecule
        path = [start]
        current = start
        seen = {start}
        while True:
            nexts = [n for n in adj.get(current, []) if n not in seen]
            if not nexts:
                break
            current = nexts[0]
            seen.add(current)
            path.append(current)
        return path

    def molecules_in_cascade(self, cascade_id: str) -> Set[str]:
        c = self.get(cascade_id)
        mols: Set[str] = set()
        for s in c.steps:
            mols.add(s.from_molecule)
            mols.add(s.to_molecule)
        return mols

    def reachable_from(self, cascade_id: str, molecule: str) -> Set[str]:
        c = self.get(cascade_id)
        adj: Dict[str, List[str]] = {}
        for s in c.steps:
            adj.setdefault(s.from_molecule, []).append(s.to_molecule)
        reached: Set[str] = set()
        frontier = [molecule]
        while frontier:
            current = frontier.pop()
            for nxt in adj.get(current, []):
                if nxt not in reached:
                    reached.add(nxt)
                    frontier.append(nxt)
        return reached

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "cascades": len(self._cascades),
            "outcomes": len(self._outcome_index),
        }


def self_test() -> bool:
    analyzer = CellSignalingAnalyzer()
    analyzer.add(SignalingCascade(
        "CS1", "EGFR-MAPK cascade", outcome="proliferation", tissue="epithelium",
        steps=[
            SignalingStep("S1", "EGF", "EGFR", role="ligand"),
            SignalingStep("S2", "EGFR", "GRB2", role="adapter"),
            SignalingStep("S3", "GRB2", "SOS", role="adapter"),
            SignalingStep("S4", "SOS", "RAS", role="gtpase"),
            SignalingStep("S5", "RAS", "MAPK", role="kinase"),
        ]))
    analyzer.add(SignalingCascade(
        "CS2", "PI3K-AKT cascade", outcome="survival",
        steps=[
            SignalingStep("S6", "RTK", "PI3K", role="kinase"),
            SignalingStep("S7", "PI3K", "AKT", role="kinase"),
        ]))
    assert len(analyzer.by_outcome("proliferation")) == 1
    assert analyzer.cascade_path("CS1")[0] == "EGF"
    assert "EGFR" in analyzer.molecules_in_cascade("CS1")
    reachable = analyzer.reachable_from("CS1", "EGFR")
    assert "MAPK" in reachable
    assert analyzer.stats()["cascades"] == 2
    print("cell_signaling_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
