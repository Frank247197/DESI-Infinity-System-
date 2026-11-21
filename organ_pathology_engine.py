"""DESI Infinity System - Organ Pathology Engine (v6.2.0).

Organ-level pathology registry: organ systems, pathology categories,
severity, and outcome annotations. Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ORGANS = ("heart", "lung", "liver", "kidney", "pancreas", "brain",
          "spinal_cord", "skin", "muscle", "bone", "bone_marrow",
          "spleen", "lymph_node", "thyroid", "adrenal", "intestine",
          "stomach", "bladder", "eye", "ear", "other")
PATHOLOGY_CATEGORIES = ("degenerative", "inflammatory", "infectious",
                        "neoplastic", "vascular", "metabolic", "genetic",
                        "traumatic", "developmental", "other")
FUNCTIONAL_IMPACT = ("none", "mild", "moderate", "severe", "failure",
                     "unknown")
SOURCES = ("curated", "literature", "predicted")


class OrganPathologyError(Exception):
    """Base organ pathology error."""


@dataclass
class OrganPathology:
    pathology_id: str
    organ: str
    disease_id: str
    pathology_category: str = "other"
    functional_impact: str = "unknown"
    description: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pathology_id or not isinstance(self.pathology_id, str):
            raise OrganPathologyError("pathology_id required")
        if self.organ not in ORGANS:
            raise OrganPathologyError(f"invalid organ: {self.organ!r}")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise OrganPathologyError("disease_id required")
        if self.pathology_category not in PATHOLOGY_CATEGORIES:
            raise OrganPathologyError(
                f"invalid pathology_category: {self.pathology_category!r}")
        if self.functional_impact not in FUNCTIONAL_IMPACT:
            raise OrganPathologyError(
                f"invalid functional_impact: {self.functional_impact!r}")
        if self.source not in SOURCES:
            raise OrganPathologyError(f"invalid source: {self.source!r}")


class OrganPathologyEngine:
    """Registry with organ / category / impact queries."""

    def __init__(self) -> None:
        self._pathologies: Dict[str, OrganPathology] = {}
        self._organ_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, pathology: OrganPathology) -> OrganPathology:
        if pathology.pathology_id in self._pathologies:
            raise OrganPathologyError(
                f"duplicate pathology_id: {pathology.pathology_id}")
        self._pathologies[pathology.pathology_id] = pathology
        self._organ_index.setdefault(pathology.organ, []).append(pathology.pathology_id)
        self._disease_index.setdefault(pathology.disease_id, []).append(
            pathology.pathology_id)
        return pathology

    def get(self, pathology_id: str) -> OrganPathology:
        try:
            return self._pathologies[pathology_id]
        except KeyError as exc:
            raise OrganPathologyError(f"unknown pathology_id: {pathology_id}") from exc

    def by_organ(self, organ: str) -> List[OrganPathology]:
        if organ not in ORGANS:
            raise OrganPathologyError(f"invalid organ: {organ!r}")
        return [self.get(p) for p in self._organ_index.get(organ, [])]

    def by_category(self, category: str) -> List[OrganPathology]:
        if category not in PATHOLOGY_CATEGORIES:
            raise OrganPathologyError(f"invalid category: {category!r}")
        return [p for p in self._pathologies.values()
                if p.pathology_category == category]

    def for_disease(self, disease_id: str) -> List[OrganPathology]:
        return [self.get(p) for p in self._disease_index.get(disease_id, [])]

    def multi_organ_diseases(self, min_organs: int = 2) -> List[str]:
        counts: Dict[str, int] = {}
        for p in self._pathologies.values():
            counts.setdefault(p.disease_id, set()).add(p.organ)
        return sorted(d for d, orgs in counts.items() if len(orgs) >= min_organs)

    def severe_impact(self) -> List[OrganPathology]:
        return [p for p in self._pathologies.values()
                if p.functional_impact in ("severe", "failure")]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "pathologies": len(self._pathologies),
            "organs": len(self._organ_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    engine = OrganPathologyEngine()
    engine.add(OrganPathology(
        "OP1", "heart", "D_heart_failure", "degenerative",
        "severe", "ventricular remodeling"))
    engine.add(OrganPathology(
        "OP2", "kidney", "D_heart_failure", "vascular",
        "moderate", "renal artery narrowing"))
    engine.add(OrganPathology(
        "OP3", "liver", "D_nafld", "metabolic",
        "moderate", "hepatic steatosis"))
    engine.add(OrganPathology(
        "OP4", "liver", "D_nafld", "inflammatory",
        "severe", "steatohepatitis"))
    assert len(engine.by_organ("liver")) == 2
    assert len(engine.by_category("inflammatory")) == 1
    assert len(engine.for_disease("D_heart_failure")) == 2
    assert "D_heart_failure" in engine.multi_organ_diseases()
    assert len(engine.severe_impact()) == 2
    print("organ_pathology_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
