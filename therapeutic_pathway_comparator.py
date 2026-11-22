"""DESI Infinity System - Therapeutic Pathway Comparator (v6.2.0).

Compares documented pathway-level therapeutic angles (pathway targets,
intervention points, evidence levels). Side-by-side research comparison
only — no clinical recommendation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INTERVENTION_POINTS = ("upstream_receptor", "kinase", "phosphatase",
                       "transcription_factor", "downstream_effector",
                       "feedback_loop", "other")
EVIDENCE_LEVELS = ("established", "emerging", "experimental", "hypothetical")
SOURCES = ("curated", "literature", "predicted")


class TherapeuticPathwayError(Exception):
    """Base therapeutic pathway error."""


@dataclass
class PathwayIntervention:
    intervention_id: str
    disease_id: str
    pathway_id: str
    intervention_point: str
    drug_class_or_modality: str = ""
    evidence_level: str = "emerging"
    known_limitations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.intervention_id or not isinstance(self.intervention_id, str):
            raise TherapeuticPathwayError("intervention_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise TherapeuticPathwayError("disease_id required")
        if not self.pathway_id or not isinstance(self.pathway_id, str):
            raise TherapeuticPathwayError("pathway_id required")
        if self.intervention_point not in INTERVENTION_POINTS:
            raise TherapeuticPathwayError(
                f"invalid intervention_point: {self.intervention_point!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise TherapeuticPathwayError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise TherapeuticPathwayError(f"invalid source: {self.source!r}")


class TherapeuticPathwayComparator:
    """Registry + comparison across pathway interventions per disease."""

    def __init__(self) -> None:
        self._interventions: Dict[str, PathwayIntervention] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._pathway_index: Dict[str, List[str]] = {}

    def add(self, intervention: PathwayIntervention) -> PathwayIntervention:
        if intervention.intervention_id in self._interventions:
            raise TherapeuticPathwayError(
                f"duplicate intervention_id: {intervention.intervention_id}")
        self._interventions[intervention.intervention_id] = intervention
        self._disease_index.setdefault(intervention.disease_id, []).append(
            intervention.intervention_id)
        self._pathway_index.setdefault(intervention.pathway_id, []).append(
            intervention.intervention_id)
        return intervention

    def get(self, intervention_id: str) -> PathwayIntervention:
        try:
            return self._interventions[intervention_id]
        except KeyError as exc:
            raise TherapeuticPathwayError(
                f"unknown intervention_id: {intervention_id}") from exc

    def for_disease(self, disease_id: str) -> List[PathwayIntervention]:
        return [self.get(i) for i in self._disease_index.get(disease_id, [])]

    def for_pathway(self, pathway_id: str) -> List[PathwayIntervention]:
        return [self.get(i) for i in self._pathway_index.get(pathway_id, [])]

    def by_evidence(self, level: str) -> List[PathwayIntervention]:
        if level not in EVIDENCE_LEVELS:
            raise TherapeuticPathwayError(f"invalid evidence_level: {level!r}")
        return [i for i in self._interventions.values()
                if i.evidence_level == level]

    def compare(self, disease_id: str) -> Dict[str, List[Dict[str, object]]]:
        grouped: Dict[str, List[Dict[str, object]]] = {}
        for i in self.for_disease(disease_id):
            grouped.setdefault(i.pathway_id, []).append({
                "intervention_id": i.intervention_id,
                "point": i.intervention_point,
                "modality": i.drug_class_or_modality,
                "evidence": i.evidence_level,
                "limitations": list(i.known_limitations),
            })
        return grouped

    def pathway_coverage(self, disease_id: str) -> int:
        return len({i.pathway_id for i in self.for_disease(disease_id)})

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "interventions": len(self._interventions),
            "diseases": len(self._disease_index),
            "pathways": len(self._pathway_index),
        }


def self_test() -> bool:
    comp = TherapeuticPathwayComparator()
    comp.add(PathwayIntervention(
        "PI1", "D_melanoma", "MAPK_pathway", "kinase",
        "BRAF inhibitor", "established",
        known_limitations=["paradoxical activation", "resistance"]))
    comp.add(PathwayIntervention(
        "PI2", "D_melanoma", "MAPK_pathway", "kinase",
        "MEK inhibitor", "established",
        known_limitations=["toxicity", "resistance"]))
    comp.add(PathwayIntervention(
        "PI3", "D_melanoma", "immune_checkpoint", "upstream_receptor",
        "anti-PD-1", "established",
        known_limitations=["autoimmune toxicity"]))
    comp.add(PathwayIntervention(
        "PI4", "D_melanoma", "PI3K_AKT", "kinase",
        "AKT inhibitor", "experimental",
        known_limitations=["narrow therapeutic index"]))
    assert len(comp.for_disease("D_melanoma")) == 4
    assert len(comp.for_pathway("MAPK_pathway")) == 2
    assert len(comp.by_evidence("experimental")) == 1
    cmp = comp.compare("D_melanoma")
    assert "MAPK_pathway" in cmp and len(cmp["MAPK_pathway"]) == 2
    assert comp.pathway_coverage("D_melanoma") == 3
    print("therapeutic_pathway_comparator: OK")
    return True


if __name__ == "__main__":
    self_test()
