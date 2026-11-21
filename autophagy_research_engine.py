"""DESI Infinity System - Autophagy Research Engine (v6.2.0).

Models autophagic processes (macroautophagy, microautophagy, CMA) with
key regulators, cargo, and disease links. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

AUTOPHAGY_TYPES = ("macroautophagy", "microautophagy", "chaperone_mediated",
                   "mitophagy", "pexophagy", "xenophagy", "other")
STAGES = ("initiation", "nucleation", "elongation", "fusion", "degradation",
          "other")
SOURCES = ("curated", "literature", "predicted")


class AutophagyError(Exception):
    """Base autophagy error."""


@dataclass
class AutophagyStep:
    step_id: str
    autophagic_type: str
    stage: str
    key_proteins: List[str] = field(default_factory=list)
    cargo: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.step_id or not isinstance(self.step_id, str):
            raise AutophagyError("step_id required")
        if self.autophagic_type not in AUTOPHAGY_TYPES:
            raise AutophagyError(f"invalid autophagic_type: {self.autophagic_type!r}")
        if self.stage not in STAGES:
            raise AutophagyError(f"invalid stage: {self.stage!r}")
        if self.source not in SOURCES:
            raise AutophagyError(f"invalid source: {self.source!r}")


@dataclass
class AutophagyAssociation:
    association_id: str
    disease_id: str
    autophagic_type: str
    direction: str = "unknown"  # "up", "down", "dysregulated"
    evidence_class: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.association_id or not isinstance(self.association_id, str):
            raise AutophagyError("association_id required")
        if self.autophagic_type not in AUTOPHAGY_TYPES:
            raise AutophagyError(f"invalid autophagic_type: {self.autophagic_type!r}")
        if self.direction not in ("up", "down", "dysregulated", "unknown"):
            raise AutophagyError(f"invalid direction: {self.direction!r}")


class AutophagyResearchEngine:
    """Step + association registry with type / stage / disease queries."""

    def __init__(self) -> None:
        self._steps: Dict[str, AutophagyStep] = {}
        self._associations: Dict[str, AutophagyAssociation] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add_step(self, step: AutophagyStep) -> AutophagyStep:
        if step.step_id in self._steps:
            raise AutophagyError(f"duplicate step_id: {step.step_id}")
        self._steps[step.step_id] = step
        self._type_index.setdefault(step.autophagic_type, []).append(step.step_id)
        return step

    def add_association(self, assoc: AutophagyAssociation) -> AutophagyAssociation:
        if assoc.association_id in self._associations:
            raise AutophagyError(f"duplicate association_id: {assoc.association_id}")
        self._associations[assoc.association_id] = assoc
        self._disease_index.setdefault(assoc.disease_id, []).append(assoc.association_id)
        return assoc

    def get_step(self, step_id: str) -> AutophagyStep:
        try:
            return self._steps[step_id]
        except KeyError as exc:
            raise AutophagyError(f"unknown step_id: {step_id}") from exc

    def by_type(self, autophagic_type: str) -> List[AutophagyStep]:
        if autophagic_type not in AUTOPHAGY_TYPES:
            raise AutophagyError(f"invalid autophagic_type: {autophagic_type!r}")
        return [self.get_step(s) for s in self._type_index.get(autophagic_type, [])]

    def by_stage(self, stage: str) -> List[AutophagyStep]:
        if stage not in STAGES:
            raise AutophagyError(f"invalid stage: {stage!r}")
        return [s for s in self._steps.values() if s.stage == stage]

    def for_disease(self, disease_id: str) -> List[AutophagyAssociation]:
        return [self._associations[a] for a in self._disease_index.get(disease_id, [])]

    def up_in_disease(self, disease_id: str) -> List[AutophagyAssociation]:
        return [a for a in self.for_disease(disease_id) if a.direction == "up"]

    def down_in_disease(self, disease_id: str) -> List[AutophagyAssociation]:
        return [a for a in self.for_disease(disease_id) if a.direction == "down"]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "steps": len(self._steps),
            "associations": len(self._associations),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    engine = AutophagyResearchEngine()
    engine.add_step(AutophagyStep(
        "S1", "macroautophagy", "initiation",
        key_proteins=["ULK1", "ATG13", "FIP200"],
        cargo=[]))
    engine.add_step(AutophagyStep(
        "S2", "macroautophagy", "elongation",
        key_proteins=["ATG5", "ATG12", "ATG16L1", "LC3"],
        cargo=["damaged_mitochondria", "protein_aggregates"]))
    engine.add_step(AutophagyStep(
        "S3", "chaperone_mediated", "degradation",
        key_proteins=["HSC70", "LAMP2A"],
        cargo=["KFERQ_motif_proteins"]))
    engine.add_association(AutophagyAssociation(
        "A1", "D_neurodegeneration", "macroautophagy",
        direction="down", evidence_class="literature"))
    engine.add_association(AutophagyAssociation(
        "A2", "D_cancer", "macroautophagy",
        direction="up"))
    engine.add_association(AutophagyAssociation(
        "A3", "D_neurodegeneration", "chaperone_mediated",
        direction="down"))
    assert len(engine.by_type("macroautophagy")) == 2
    assert len(engine.by_stage("initiation")) == 1
    assert len(engine.for_disease("D_neurodegeneration")) == 2
    assert len(engine.down_in_disease("D_neurodegeneration")) == 2
    assert len(engine.up_in_disease("D_cancer")) == 1
    print("autophagy_research_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
