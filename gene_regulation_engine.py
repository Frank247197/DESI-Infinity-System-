"""DESI Infinity System - Gene Regulation Engine (v6.2.0).

Models transcriptional and post-transcriptional regulation: enhancers,
silencers, transcription factors, microRNAs, and epigenetic modifiers.
Research-only annotations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

REGULATOR_TYPES = ("transcription_factor", "enhancer", "silencer",
                   "promoter", "mirna", "lncrna", "insulator",
                   "epigenetic_modifier", "other")
EFFECTS = ("activating", "repressing", "dual", "unknown")
SOURCES = ("curated", "literature", "predicted")


class GeneRegulationError(Exception):
    """Base gene regulation error."""


@dataclass
class RegulatoryInteraction:
    interaction_id: str
    regulator_id: str
    regulator_type: str
    target_gene: str
    effect: str = "unknown"
    tissue: str = ""
    evidence_class: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.interaction_id or not isinstance(self.interaction_id, str):
            raise GeneRegulationError("interaction_id required")
        if not self.regulator_id or not isinstance(self.regulator_id, str):
            raise GeneRegulationError("regulator_id required")
        if not self.target_gene or not isinstance(self.target_gene, str):
            raise GeneRegulationError("target_gene required")
        if self.regulator_type not in REGULATOR_TYPES:
            raise GeneRegulationError(f"invalid regulator_type: {self.regulator_type!r}")
        if self.effect not in EFFECTS:
            raise GeneRegulationError(f"invalid effect: {self.effect!r}")
        if self.source not in SOURCES:
            raise GeneRegulationError(f"invalid source: {self.source!r}")


class GeneRegulationEngine:
    """Regulatory interaction registry with target/regulator/effect queries."""

    def __init__(self) -> None:
        self._interactions: Dict[str, RegulatoryInteraction] = {}
        self._target_index: Dict[str, List[str]] = {}
        self._regulator_index: Dict[str, List[str]] = {}
        self._tissue_index: Dict[str, List[str]] = {}

    def add(self, interaction: RegulatoryInteraction) -> RegulatoryInteraction:
        if interaction.interaction_id in self._interactions:
            raise GeneRegulationError(
                f"duplicate interaction_id: {interaction.interaction_id}")
        self._interactions[interaction.interaction_id] = interaction
        self._target_index.setdefault(interaction.target_gene, []).append(
            interaction.interaction_id)
        self._regulator_index.setdefault(interaction.regulator_id, []).append(
            interaction.interaction_id)
        if interaction.tissue:
            self._tissue_index.setdefault(interaction.tissue, []).append(
                interaction.interaction_id)
        return interaction

    def get(self, interaction_id: str) -> RegulatoryInteraction:
        try:
            return self._interactions[interaction_id]
        except KeyError as exc:
            raise GeneRegulationError(
                f"unknown interaction_id: {interaction_id}") from exc

    def for_target(self, gene_symbol: str) -> List[RegulatoryInteraction]:
        return [self.get(iid) for iid in self._target_index.get(gene_symbol, [])]

    def for_regulator(self, regulator_id: str) -> List[RegulatoryInteraction]:
        return [self.get(iid) for iid in self._regulator_index.get(regulator_id, [])]

    def activators_of(self, gene_symbol: str) -> List[RegulatoryInteraction]:
        return [i for i in self.for_target(gene_symbol) if i.effect == "activating"]

    def repressors_of(self, gene_symbol: str) -> List[RegulatoryInteraction]:
        return [i for i in self.for_target(gene_symbol) if i.effect == "repressing"]

    def by_tissue(self, tissue: str) -> List[RegulatoryInteraction]:
        return [self.get(iid) for iid in self._tissue_index.get(tissue, [])]

    def regulator_fanout(self, regulator_id: str) -> int:
        return len(self.for_regulator(regulator_id))

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "interactions": len(self._interactions),
            "targets": len(self._target_index),
            "regulators": len(self._regulator_index),
            "tissues": len(self._tissue_index),
        }


def self_test() -> bool:
    engine = GeneRegulationEngine()
    engine.add(RegulatoryInteraction(
        "R1", "TP53", "transcription_factor", "CDKN1A",
        "activating", "ubiquitous"))
    engine.add(RegulatoryInteraction(
        "R2", "MYC", "transcription_factor", "CDKN1A",
        "repressing", "ubiquitous"))
    engine.add(RegulatoryInteraction(
        "R3", "miR-34a", "mirna", "CDKN1A", "repressing"))
    engine.add(RegulatoryInteraction(
        "R4", "TP53", "transcription_factor", "BAX", "activating"))
    assert len(engine.for_target("CDKN1A")) == 3
    assert len(engine.activators_of("CDKN1A")) == 1
    assert len(engine.repressors_of("CDKN1A")) == 2
    assert engine.regulator_fanout("TP53") == 2
    assert engine.stats()["interactions"] == 4
    print("gene_regulation_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
