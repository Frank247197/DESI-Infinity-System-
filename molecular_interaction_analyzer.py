"""DESI Infinity System - Molecular Interaction Analyzer (v6.2.0).

Generic molecular interaction registry (protein-DNA, protein-RNA,
protein-ligand, protein-protein) with evidence classes and directionality.
Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MOLECULE_TYPES = ("protein", "dna", "rna", "ligand", "metabolite", "other")
INTERACTION_TYPES = ("binding", "catalysis", "regulation", "transport",
                     "modification", "other")
EVIDENCE_CLASSES = ("experimental", "computational", "curated",
                    "textmining", "predicted", "unknown")
SOURCES = ("curated", "literature", "predicted")


class MolecularInteractionError(Exception):
    """Base molecular interaction error."""


@dataclass
class MolecularInteraction:
    interaction_id: str
    molecule_a: str
    type_a: str
    molecule_b: str
    type_b: str
    interaction_type: str = "binding"
    evidence_class: str = "unknown"
    affinity_kd_nm: float = 0.0
    directionality: str = "symmetric"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.interaction_id or not isinstance(self.interaction_id, str):
            raise MolecularInteractionError("interaction_id required")
        if not self.molecule_a or not self.molecule_b:
            raise MolecularInteractionError("both molecules required")
        if self.type_a not in MOLECULE_TYPES or self.type_b not in MOLECULE_TYPES:
            raise MolecularInteractionError("invalid molecule type")
        if self.interaction_type not in INTERACTION_TYPES:
            raise MolecularInteractionError(
                f"invalid interaction_type: {self.interaction_type!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise MolecularInteractionError(
                f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise MolecularInteractionError(f"invalid source: {self.source!r}")
        if not isinstance(self.affinity_kd_nm, (int, float)) or self.affinity_kd_nm < 0:
            raise MolecularInteractionError("affinity_kd_nm must be non-negative")


class MolecularInteractionAnalyzer:
    """Registry with molecule / type / affinity queries."""

    def __init__(self) -> None:
        self._interactions: Dict[str, MolecularInteraction] = {}
        self._molecule_index: Dict[str, List[str]] = {}

    def add(self, interaction: MolecularInteraction) -> MolecularInteraction:
        if interaction.interaction_id in self._interactions:
            raise MolecularInteractionError(
                f"duplicate interaction_id: {interaction.interaction_id}")
        self._interactions[interaction.interaction_id] = interaction
        for m in (interaction.molecule_a, interaction.molecule_b):
            self._molecule_index.setdefault(m, []).append(interaction.interaction_id)
        return interaction

    def get(self, interaction_id: str) -> MolecularInteraction:
        try:
            return self._interactions[interaction_id]
        except KeyError as exc:
            raise MolecularInteractionError(
                f"unknown interaction_id: {interaction_id}") from exc

    def for_molecule(self, molecule_id: str) -> List[MolecularInteraction]:
        return [self.get(iid) for iid in self._molecule_index.get(molecule_id, [])]

    def by_type(self, interaction_type: str) -> List[MolecularInteraction]:
        if interaction_type not in INTERACTION_TYPES:
            raise MolecularInteractionError(
                f"invalid interaction_type: {interaction_type!r}")
        return [i for i in self._interactions.values()
                if i.interaction_type == interaction_type]

    def by_evidence(self, evidence_class: str) -> List[MolecularInteraction]:
        if evidence_class not in EVIDENCE_CLASSES:
            raise MolecularInteractionError(
                f"invalid evidence_class: {evidence_class!r}")
        return [i for i in self._interactions.values()
                if i.evidence_class == evidence_class]

    def high_affinity(self, threshold_nm: float = 100.0) -> List[MolecularInteraction]:
        return [i for i in self._interactions.values()
                if 0 < i.affinity_kd_nm <= threshold_nm]

    def experimental(self) -> List[MolecularInteraction]:
        return self.by_evidence("experimental")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "interactions": len(self._interactions),
            "molecules": len(self._molecule_index),
            "experimental": len(self.experimental()),
        }


def self_test() -> bool:
    analyzer = MolecularInteractionAnalyzer()
    analyzer.add(MolecularInteraction(
        "MI1", "TP53", "protein", "DNA_consensus", "dna",
        "binding", "experimental", affinity_kd_nm=5.0))
    analyzer.add(MolecularInteraction(
        "MI2", "MDM2", "protein", "TP53", "protein",
        "binding", "experimental", affinity_kd_nm=0.6))
    analyzer.add(MolecularInteraction(
        "MI3", "ATP", "ligand", "EGFR", "protein",
        "binding", "computational", affinity_kd_nm=150.0))
    assert len(analyzer.for_molecule("TP53")) == 2
    assert len(analyzer.by_type("binding")) == 3
    assert len(analyzer.by_evidence("experimental")) == 2
    assert len(analyzer.high_affinity(10.0)) == 2
    assert analyzer.stats()["molecules"] == 5
    print("molecular_interaction_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
