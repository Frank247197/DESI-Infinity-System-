"""DESI Infinity System - Cell Cycle Research Engine (v6.2.0).

Models cell cycle phases, checkpoints, cyclin/CDK complexes, and
dysregulation patterns. Research-only; no clinical use.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PHASES = ("G0", "G1", "S", "G2", "M", "other")
CHECKPOINTS = ("G1_S", "G2_M", "spindle", "other")
DYSREGULATION = ("hyperactivation", "loss_of_checkpoint", "arrest",
                 "aneuploidy", "unknown")
SOURCES = ("curated", "literature", "predicted")


class CellCycleError(Exception):
    """Base cell cycle error."""


@dataclass
class CellCycleComplex:
    complex_id: str
    name: str
    phase: str
    subunits: List[str] = field(default_factory=list)
    targets: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.complex_id or not isinstance(self.complex_id, str):
            raise CellCycleError("complex_id required")
        if self.phase not in PHASES:
            raise CellCycleError(f"invalid phase: {self.phase!r}")
        if self.source not in SOURCES:
            raise CellCycleError(f"invalid source: {self.source!r}")


@dataclass
class DysregulationEvent:
    event_id: str
    complex_id: str
    dysregulation: str
    disease_id: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.event_id or not isinstance(self.event_id, str):
            raise CellCycleError("event_id required")
        if self.dysregulation not in DYSREGULATION:
            raise CellCycleError(f"invalid dysregulation: {self.dysregulation!r}")
        if self.source not in SOURCES:
            raise CellCycleError(f"invalid source: {self.source!r}")


class CellCycleResearchEngine:
    """Registry with phase / complex / dysregulation queries."""

    def __init__(self) -> None:
        self._complexes: Dict[str, CellCycleComplex] = {}
        self._phase_index: Dict[str, List[str]] = {}
        self._events: Dict[str, DysregulationEvent] = {}
        self._complex_event_index: Dict[str, List[str]] = {}

    def add_complex(self, c: CellCycleComplex) -> CellCycleComplex:
        if c.complex_id in self._complexes:
            raise CellCycleError(f"duplicate complex_id: {c.complex_id}")
        self._complexes[c.complex_id] = c
        self._phase_index.setdefault(c.phase, []).append(c.complex_id)
        return c

    def add_event(self, e: DysregulationEvent) -> DysregulationEvent:
        if e.event_id in self._events:
            raise CellCycleError(f"duplicate event_id: {e.event_id}")
        if e.complex_id and e.complex_id not in self._complexes:
            raise CellCycleError(f"unknown complex_id: {e.complex_id}")
        self._events[e.event_id] = e
        if e.complex_id:
            self._complex_event_index.setdefault(e.complex_id, []).append(e.event_id)
        return e

    def get_complex(self, complex_id: str) -> CellCycleComplex:
        try:
            return self._complexes[complex_id]
        except KeyError as exc:
            raise CellCycleError(f"unknown complex_id: {complex_id}") from exc

    def by_phase(self, phase: str) -> List[CellCycleComplex]:
        if phase not in PHASES:
            raise CellCycleError(f"invalid phase: {phase!r}")
        return [self.get_complex(c) for c in self._phase_index.get(phase, [])]

    def events_for_complex(self, complex_id: str) -> List[DysregulationEvent]:
        return [self._events[e] for e in self._complex_event_index.get(complex_id, [])]

    def by_dysregulation(self, kind: str) -> List[DysregulationEvent]:
        if kind not in DYSREGULATION:
            raise CellCycleError(f"invalid dysregulation: {kind!r}")
        return [e for e in self._events.values() if e.dysregulation == kind]

    def for_disease(self, disease_id: str) -> List[DysregulationEvent]:
        return [e for e in self._events.values() if e.disease_id == disease_id]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "complexes": len(self._complexes),
            "phases": len(self._phase_index),
            "events": len(self._events),
        }


def self_test() -> bool:
    engine = CellCycleResearchEngine()
    engine.add_complex(CellCycleComplex(
        "CC1", "Cyclin D-CDK4/6", "G1",
        subunits=["CCND1", "CDK4", "CDK6"],
        targets=["RB1"]))
    engine.add_complex(CellCycleComplex(
        "CC2", "Cyclin E-CDK2", "G1",
        subunits=["CCNE1", "CDK2"],
        targets=["RB1", "E2F1"]))
    engine.add_complex(CellCycleComplex(
        "CC3", "Cyclin B-CDK1", "M",
        subunits=["CCNB1", "CDK1"],
        targets=["APC_C"]))
    engine.add_event(DysregulationEvent(
        "E1", "CC1", "hyperactivation", "D_cancer"))
    engine.add_event(DysregulationEvent(
        "E2", "CC2", "hyperactivation", "D_breast_cancer"))
    engine.add_event(DysregulationEvent(
        "E3", "", "aneuploidy", "D_cancer"))
    assert len(engine.by_phase("G1")) == 2
    assert len(engine.events_for_complex("CC1")) == 1
    assert len(engine.by_dysregulation("hyperactivation")) == 2
    assert len(engine.for_disease("D_cancer")) == 2
    print("cell_cycle_research_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
