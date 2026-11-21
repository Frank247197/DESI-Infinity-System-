"""DESI Infinity System - Immune System Analyzer (v6.2.0).

Models immune system components (innate/adaptive branches, cell types,
signaling molecules, tissues) and their research-level associations to
diseases. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

BRANCHES = ("innate", "adaptive", "both", "unknown")
CELL_TYPES = ("neutrophil", "monocyte", "macrophage", "dendritic_cell",
              "nk_cell", "b_cell", "plasma_cell", "cd4_t_cell",
              "cd8_t_cell", "treg", "mast_cell", "basophil", "eosinophil")
SOURCES = ("curated", "literature", "predicted")


class ImmuneSystemError(Exception):
    """Base immune system error."""


@dataclass
class ImmuneComponent:
    component_id: str
    name: str
    branch: str = "unknown"
    cell_types: List[str] = field(default_factory=list)
    signaling_molecules: List[str] = field(default_factory=list)
    tissues: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.component_id or not isinstance(self.component_id, str):
            raise ImmuneSystemError("component_id required")
        if not self.name or not isinstance(self.name, str):
            raise ImmuneSystemError("name required")
        if self.branch not in BRANCHES:
            raise ImmuneSystemError(f"invalid branch: {self.branch!r}")
        if self.source not in SOURCES:
            raise ImmuneSystemError(f"invalid source: {self.source!r}")
        for ct in self.cell_types:
            if ct not in CELL_TYPES:
                raise ImmuneSystemError(f"invalid cell_type: {ct!r}")


class ImmuneSystemAnalyzer:
    """Component registry with branch / cell-type / disease queries."""

    def __init__(self) -> None:
        self._components: Dict[str, ImmuneComponent] = {}
        self._cell_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, component: ImmuneComponent) -> ImmuneComponent:
        if component.component_id in self._components:
            raise ImmuneSystemError(f"duplicate component_id: {component.component_id}")
        self._components[component.component_id] = component
        for ct in component.cell_types:
            self._cell_index.setdefault(ct, []).append(component.component_id)
        for did in component.disease_ids:
            self._disease_index.setdefault(did, []).append(component.component_id)
        return component

    def get(self, component_id: str) -> ImmuneComponent:
        try:
            return self._components[component_id]
        except KeyError as exc:
            raise ImmuneSystemError(f"unknown component_id: {component_id}") from exc

    def by_branch(self, branch: str) -> List[ImmuneComponent]:
        if branch not in BRANCHES:
            raise ImmuneSystemError(f"invalid branch: {branch!r}")
        return [c for c in self._components.values() if c.branch == branch]

    def by_cell_type(self, cell_type: str) -> List[ImmuneComponent]:
        if cell_type not in CELL_TYPES:
            raise ImmuneSystemError(f"invalid cell_type: {cell_type!r}")
        return [self.get(cid) for cid in self._cell_index.get(cell_type, [])]

    def for_disease(self, disease_id: str) -> List[ImmuneComponent]:
        return [self.get(cid) for cid in self._disease_index.get(disease_id, [])]

    def shared_molecules(self, comp_a: str, comp_b: str) -> List[str]:
        a = set(self.get(comp_a).signaling_molecules)
        b = set(self.get(comp_b).signaling_molecules)
        return sorted(a & b)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "components": len(self._components),
            "innate": len(self.by_branch("innate")),
            "adaptive": len(self.by_branch("adaptive")),
            "cell_types": len(self._cell_index),
        }


def self_test() -> bool:
    analyzer = ImmuneSystemAnalyzer()
    analyzer.add(ImmuneComponent(
        "IC_neutrophil", "Neutrophil response", "innate",
        cell_types=["neutrophil"], signaling_molecules=["IL-8", "TNF-alpha"],
        tissues=["blood", "tissue"], disease_ids=["D_sepsis"]))
    analyzer.add(ImmuneComponent(
        "IC_tcell", "T cell adaptive response", "adaptive",
        cell_types=["cd4_t_cell", "cd8_t_cell"],
        signaling_molecules=["IL-2", "IFN-gamma"],
        disease_ids=["D_viral_infection"]))
    assert len(analyzer.by_branch("innate")) == 1
    assert analyzer.by_cell_type("neutrophil")[0].component_id == "IC_neutrophil"
    assert analyzer.for_disease("D_sepsis")[0].name.startswith("Neutrophil")
    assert analyzer.stats()["adaptive"] == 1
    print("immune_system_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
