"""DESI Infinity System - Viral Lifecycle Knowledge Engine (v6.2.0).

Models viral lifecycle stages (entry, uncoating, replication, assembly,
egress) with key proteins, host factors, and inhibitors. Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

LIFECYCLE_STAGES = ("attachment", "entry", "uncoating", "replication",
                    "transcription", "translation", "assembly", "egress",
                    "maturation", "other")
SOURCES = ("curated", "literature", "predicted")


class LifecycleError(Exception):
    """Base lifecycle error."""


@dataclass
class LifecycleStage:
    stage_id: str
    virus_id: str
    stage: str
    viral_proteins: List[str] = field(default_factory=list)
    host_factors: List[str] = field(default_factory=list)
    known_inhibitors: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.stage_id or not isinstance(self.stage_id, str):
            raise LifecycleError("stage_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise LifecycleError("virus_id required")
        if self.stage not in LIFECYCLE_STAGES:
            raise LifecycleError(f"invalid stage: {self.stage!r}")
        if self.source not in SOURCES:
            raise LifecycleError(f"invalid source: {self.source!r}")


class ViralLifecycleKnowledgeEngine:
    """Lifecycle profile store with stage/protein/inhibitor queries."""

    def __init__(self) -> None:
        self._stages: Dict[str, LifecycleStage] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._stage_index: Dict[str, List[str]] = {}
        self._protein_index: Dict[str, List[str]] = {}

    def add(self, stage: LifecycleStage) -> LifecycleStage:
        if stage.stage_id in self._stages:
            raise LifecycleError(f"duplicate stage_id: {stage.stage_id}")
        self._stages[stage.stage_id] = stage
        self._virus_index.setdefault(stage.virus_id, []).append(stage.stage_id)
        self._stage_index.setdefault(stage.stage, []).append(stage.stage_id)
        for p in stage.viral_proteins:
            self._protein_index.setdefault(p, []).append(stage.stage_id)
        return stage

    def get(self, stage_id: str) -> LifecycleStage:
        try:
            return self._stages[stage_id]
        except KeyError as exc:
            raise LifecycleError(f"unknown stage_id: {stage_id}") from exc

    def for_virus(self, virus_id: str) -> List[LifecycleStage]:
        return [self.get(s) for s in self._virus_index.get(virus_id, [])]

    def by_stage(self, stage: str) -> List[LifecycleStage]:
        if stage not in LIFECYCLE_STAGES:
            raise LifecycleError(f"invalid stage: {stage!r}")
        return [self.get(s) for s in self._stage_index.get(stage, [])]

    def by_protein(self, protein: str) -> List[LifecycleStage]:
        return [self.get(s) for s in self._protein_index.get(protein, [])]

    def inhibited_stages(self) -> List[LifecycleStage]:
        return [s for s in self._stages.values() if s.known_inhibitors]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "stages": len(self._stages),
            "viruses": len(self._virus_index),
            "viral_proteins": len(self._protein_index),
        }


def self_test() -> bool:
    engine = ViralLifecycleKnowledgeEngine()
    engine.add(LifecycleStage(
        "LS1", "VS_sars2", "entry", viral_proteins=["S"],
        host_factors=["ACE2", "TMPRSS2"], known_inhibitors=["camostat"]))
    engine.add(LifecycleStage(
        "LS2", "VS_sars2", "replication", viral_proteins=["RdRp", "Nsp12"],
        known_inhibitors=["remdesivir", "nirmatrelvir"]))
    engine.add(LifecycleStage(
        "LS3", "VS_hiv1", "entry", viral_proteins=["gp120", "gp41"],
        host_factors=["CD4", "CCR5"], known_inhibitors=["maraviroc"]))
    assert len(engine.for_virus("VS_sars2")) == 2
    assert len(engine.by_stage("entry")) == 2
    assert len(engine.by_protein("RdRp")) == 1
    assert len(engine.inhibited_stages()) == 3
    print("viral_lifecycle_knowledge_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
