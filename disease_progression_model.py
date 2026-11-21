"""DESI Infinity System - Disease Progression Model (v6.2.0).

Stores documented disease stage definitions and progression transitions.
Predictions of progression are explicitly labelled; nothing here is a
clinical prognosis for any individual. Supports research on natural
history and stage-based analysis.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STAGE_KINDS = ("preclinical", "early", "moderate", "advanced", "terminal", "remission", "unknown")
TRANSITION_SOURCES = ("curated", "literature", "predicted")


class ProgressionError(Exception):
    """Base progression error."""


@dataclass
class Stage:
    stage_id: str
    disease_id: str
    name: str
    kind: str = "unknown"
    description: str = ""
    typical_duration_months: Optional[float] = None
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.stage_id or not self.disease_id:
            raise ProgressionError("stage_id and disease_id required")
        if not self.name:
            raise ProgressionError("name required")
        if self.kind not in STAGE_KINDS:
            raise ProgressionError(f"invalid kind: {self.kind!r}")
        if self.typical_duration_months is not None:
            if not isinstance(self.typical_duration_months, (int, float)) or self.typical_duration_months < 0:
                raise ProgressionError("typical_duration_months must be non-negative or None")


@dataclass
class Transition:
    from_stage_id: str
    to_stage_id: str
    probability: Optional[float] = None
    time_months: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.from_stage_id or not self.to_stage_id:
            raise ProgressionError("stage ids required")
        if self.probability is not None:
            if not 0.0 <= float(self.probability) <= 1.0:
                raise ProgressionError("probability must be in [0, 1]")
        if self.source not in TRANSITION_SOURCES:
            raise ProgressionError(f"invalid source: {self.source!r}")

    def is_prediction(self) -> bool:
        return self.source == "predicted"


class DiseaseProgressionModel:
    """Stage registry with transition graph."""

    def __init__(self) -> None:
        self._stages: Dict[str, Stage] = {}
        self._transitions: List[Transition] = []

    def add_stage(self, stage: Stage) -> None:
        if stage.stage_id in self._stages:
            raise ProgressionError(f"duplicate stage: {stage.stage_id}")
        self._stages[stage.stage_id] = stage

    def get_stage(self, stage_id: str) -> Stage:
        try:
            return self._stages[stage_id]
        except KeyError as exc:
            raise ProgressionError(f"unknown stage: {stage_id}") from exc

    def add_transition(self, transition: Transition) -> None:
        self.get_stage(transition.from_stage_id)
        self.get_stage(transition.to_stage_id)
        self._transitions.append(transition)

    def stages_for_disease(self, disease_id: str) -> List[Stage]:
        return [s for s in self._stages.values() if s.disease_id == disease_id]

    def transitions_for_disease(self, disease_id: str) -> List[Transition]:
        ids = {s.stage_id for s in self.stages_for_disease(disease_id)}
        return [t for t in self._transitions
                if t.from_stage_id in ids and t.to_stage_id in ids]

    def reachable_stages(self, start_stage_id: str, max_depth: int = 16) -> List[str]:
        self.get_stage(start_stage_id)
        seen: set = set()
        frontier = [start_stage_id]
        depth = 0
        while frontier and depth < max_depth:
            nxt = []
            for sid in frontier:
                for t in self._transitions:
                    if t.from_stage_id == sid and t.to_stage_id not in seen:
                        seen.add(t.to_stage_id)
                        nxt.append(t.to_stage_id)
            frontier = nxt
            depth += 1
        return sorted(seen)

    def predictions(self) -> List[Transition]:
        return [t for t in self._transitions if t.is_prediction()]

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "stages": len(self._stages),
                "transitions": len(self._transitions),
                "predictions": len(self.predictions())}


def self_test() -> bool:
    m = DiseaseProgressionModel()
    m.add_stage(Stage("S1", "D1", "Stage I", "early"))
    m.add_stage(Stage("S2", "D1", "Stage II", "moderate"))
    m.add_stage(Stage("S3", "D1", "Stage III", "advanced"))
    m.add_transition(Transition("S1", "S2", probability=0.6, source="curated"))
    m.add_transition(Transition("S2", "S3", probability=0.4, source="predicted"))
    assert len(m.stages_for_disease("D1")) == 3
    assert m.reachable_stages("S1") == ["S2", "S3"]
    assert len(m.predictions()) == 1
    assert len(m.transitions_for_disease("D1")) == 2
    print("014 disease_progression_model: OK")
    return True


if __name__ == "__main__":
    self_test()
