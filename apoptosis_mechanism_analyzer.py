"""DESI Infinity System - Apoptosis Mechanism Analyzer (v6.2.0).

Models apoptotic pathways (intrinsic, extrinsic, perforin/granzyme) with
key regulators and disease links. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

APOPTOSIS_PATHWAYS = ("intrinsic_mitochondrial", "extrinsic_death_receptor",
                      "perforin_granzyme", "other")
ROLE_TYPES = ("pro_apoptotic", "anti_apoptotic", "initiator_caspase",
              "executioner_caspase", "adaptor", "other")
SOURCES = ("curated", "literature", "predicted")


class ApoptosisError(Exception):
    """Base apoptosis error."""


@dataclass
class ApoptosisComponent:
    component_id: str
    name: str
    pathway: str
    role: str = "other"
    interacts_with: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.component_id or not isinstance(self.component_id, str):
            raise ApoptosisError("component_id required")
        if not self.name or not isinstance(self.name, str):
            raise ApoptosisError("name required")
        if self.pathway not in APOPTOSIS_PATHWAYS:
            raise ApoptosisError(f"invalid pathway: {self.pathway!r}")
        if self.role not in ROLE_TYPES:
            raise ApoptosisError(f"invalid role: {self.role!r}")
        if self.source not in SOURCES:
            raise ApoptosisError(f"invalid source: {self.source!r}")


class ApoptosisMechanismAnalyzer:
    """Registry with pathway / role / interaction queries."""

    def __init__(self) -> None:
        self._components: Dict[str, ApoptosisComponent] = {}
        self._pathway_index: Dict[str, List[str]] = {}
        self._role_index: Dict[str, List[str]] = {}

    def add(self, component: ApoptosisComponent) -> ApoptosisComponent:
        if component.component_id in self._components:
            raise ApoptosisError(f"duplicate component_id: {component.component_id}")
        self._components[component.component_id] = component
        self._pathway_index.setdefault(component.pathway, []).append(
            component.component_id)
        self._role_index.setdefault(component.role, []).append(component.component_id)
        return component

    def get(self, component_id: str) -> ApoptosisComponent:
        try:
            return self._components[component_id]
        except KeyError as exc:
            raise ApoptosisError(f"unknown component_id: {component_id}") from exc

    def by_pathway(self, pathway: str) -> List[ApoptosisComponent]:
        if pathway not in APOPTOSIS_PATHWAYS:
            raise ApoptosisError(f"invalid pathway: {pathway!r}")
        return [self.get(c) for c in self._pathway_index.get(pathway, [])]

    def by_role(self, role: str) -> List[ApoptosisComponent]:
        if role not in ROLE_TYPES:
            raise ApoptosisError(f"invalid role: {role!r}")
        return [self.get(c) for c in self._role_index.get(role, [])]

    def for_disease(self, disease_id: str) -> List[ApoptosisComponent]:
        return [c for c in self._components.values() if disease_id in c.disease_ids]

    def partners(self, component_id: str) -> List[ApoptosisComponent]:
        comp = self.get(component_id)
        return [self.get(p) for p in comp.interacts_with if p in self._components]

    def pathway_summary(self) -> Dict[str, int]:
        return {p: len(v) for p, v in self._pathway_index.items()}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "components": len(self._components),
            "pathways": len(self._pathway_index),
            "pro_apoptotic": len(self.by_role("pro_apoptotic")),
        }


def self_test() -> bool:
    analyzer = ApoptosisMechanismAnalyzer()
    analyzer.add(ApoptosisComponent(
        "C_BAX", "BAX", "intrinsic_mitochondrial", "pro_apoptotic",
        interacts_with=["C_BCL2", "C_CYCS"], disease_ids=["D_cancer"]))
    analyzer.add(ApoptosisComponent(
        "C_BCL2", "BCL2", "intrinsic_mitochondrial", "anti_apoptotic",
        interacts_with=["C_BAX"], disease_ids=["D_lymphoma"]))
    analyzer.add(ApoptosisComponent(
        "C_CYCS", "Cytochrome c", "intrinsic_mitochondrial", "other",
        interacts_with=["C_CASP9"]))
    analyzer.add(ApoptosisComponent(
        "C_CASP9", "Caspase-9", "intrinsic_mitochondrial", "initiator_caspase",
        interacts_with=["C_CASP3"]))
    assert len(analyzer.by_pathway("intrinsic_mitochondrial")) == 4
    assert len(analyzer.by_role("pro_apoptotic")) == 1
    assert len(analyzer.for_disease("D_cancer")) == 1
    assert len(analyzer.partners("C_BAX")) == 2
    assert analyzer.stats()["components"] == 4
    print("apoptosis_mechanism_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
