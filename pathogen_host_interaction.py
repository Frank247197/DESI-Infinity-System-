"""DESI Infinity System - Pathogen-Host Interaction Engine (v6.2.0).

Stores pathogen-host protein-protein interactions with interaction type,
evidence class, and directionality. Research-only; no clinical claims.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INTERACTION_TYPES = ("binding", "cleavage", "phosphorylation",
                     "ubiquitination", "inhibition", "activation",
                     "mimicry", "other")
EVIDENCE_CLASSES = ("experimental", "predicted", "literature", "unknown")
SOURCES = ("curated", "literature", "predicted")


class HostInteractionError(Exception):
    """Base host-interaction error."""


@dataclass
class PathogenHostInteraction:
    interaction_id: str
    pathogen_id: str
    pathogen_protein: str
    host_protein: str
    interaction_type: str = "binding"
    evidence_class: str = "unknown"
    host_tissue: str = ""
    biological_effect: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.interaction_id or not isinstance(self.interaction_id, str):
            raise HostInteractionError("interaction_id required")
        if not self.pathogen_id or not isinstance(self.pathogen_id, str):
            raise HostInteractionError("pathogen_id required")
        if not self.pathogen_protein or not isinstance(self.pathogen_protein, str):
            raise HostInteractionError("pathogen_protein required")
        if not self.host_protein or not isinstance(self.host_protein, str):
            raise HostInteractionError("host_protein required")
        if self.interaction_type not in INTERACTION_TYPES:
            raise HostInteractionError(f"invalid interaction_type: {self.interaction_type!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise HostInteractionError(f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise HostInteractionError(f"invalid source: {self.source!r}")


class PathogenHostInteractionEngine:
    """Registry with host-protein / pathogen-protein / type queries."""

    def __init__(self) -> None:
        self._interactions: Dict[str, PathogenHostInteraction] = {}
        self._host_index: Dict[str, List[str]] = {}
        self._pathogen_index: Dict[str, List[str]] = {}
        self._pathogen_protein_index: Dict[str, List[str]] = {}

    def add(self, interaction: PathogenHostInteraction) -> PathogenHostInteraction:
        if interaction.interaction_id in self._interactions:
            raise HostInteractionError(
                f"duplicate interaction_id: {interaction.interaction_id}")
        self._interactions[interaction.interaction_id] = interaction
        self._host_index.setdefault(interaction.host_protein, []).append(
            interaction.interaction_id)
        self._pathogen_index.setdefault(interaction.pathogen_id, []).append(
            interaction.interaction_id)
        self._pathogen_protein_index.setdefault(interaction.pathogen_protein, []).append(
            interaction.interaction_id)
        return interaction

    def get(self, interaction_id: str) -> PathogenHostInteraction:
        try:
            return self._interactions[interaction_id]
        except KeyError as exc:
            raise HostInteractionError(f"unknown interaction_id: {interaction_id}") from exc

    def by_host_protein(self, host_protein: str) -> List[PathogenHostInteraction]:
        return [self.get(iid) for iid in self._host_index.get(host_protein, [])]

    def by_pathogen(self, pathogen_id: str) -> List[PathogenHostInteraction]:
        return [self.get(iid) for iid in self._pathogen_index.get(pathogen_id, [])]

    def by_pathogen_protein(self, pathogen_protein: str
                            ) -> List[PathogenHostInteraction]:
        return [self.get(iid) for iid in self._pathogen_protein_index.get(
            pathogen_protein, [])]

    def by_type(self, interaction_type: str) -> List[PathogenHostInteraction]:
        if interaction_type not in INTERACTION_TYPES:
            raise HostInteractionError(f"invalid interaction_type: {interaction_type!r}")
        return [i for i in self._interactions.values()
                if i.interaction_type == interaction_type]

    def experimentally_supported(self) -> List[PathogenHostInteraction]:
        return [i for i in self._interactions.values()
                if i.evidence_class == "experimental"]

    def host_targets(self, pathogen_id: str) -> List[str]:
        return sorted({i.host_protein for i in self.by_pathogen(pathogen_id)})

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "interactions": len(self._interactions),
            "host_proteins": len(self._host_index),
            "pathogens": len(self._pathogen_index),
        }


def self_test() -> bool:
    engine = PathogenHostInteractionEngine()
    engine.add(PathogenHostInteraction(
        "I1", "NCBITaxon:2697049", "Nsp1", "RPS3", "binding",
        "experimental", "respiratory_epithelium",
        "translational shutdown"))
    engine.add(PathogenHostInteraction(
        "I2", "NCBITaxon:2697049", "PLpro", "IRF3", "cleavage",
        "experimental", "myeloid", "immune suppression"))
    engine.add(PathogenHostInteraction(
        "I3", "NCBITaxon:2697049", "Orf9b", "TOMM70", "binding",
        "predicted", "mitochondria", "immune evasion"))
    assert engine.by_host_protein("RPS3")[0].interaction_id == "I1"
    assert len(engine.by_pathogen("NCBITaxon:2697049")) == 3
    assert len(engine.by_pathogen_protein("Nsp1")) == 1
    assert engine.by_type("cleavage")[0].interaction_id == "I2"
    assert set(engine.host_targets("NCBITaxon:2697049")) == {"RPS3", "IRF3", "TOMM70"}
    print("pathogen_host_interaction: OK")
    return True


if __name__ == "__main__":
    self_test()
