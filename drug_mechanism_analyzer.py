"""DESI Infinity System - Drug Mechanism Analyzer (v6.2.0).

Structured drug mechanism-of-action records: targets, pathway effects,
pharmacodynamic notes. NO dosing, NO prescribing, NO patient guidance.
Research annotation only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MECHANISM_CLASSES = ("inhibitor", "agonist", "antagonist", "modulator",
                     "blocker", "activator", "degrader", "gene_editor",
                     "other")
TARGET_TYPES = ("protein", "rna", "dna", "pathway", "cell", "other")
SOURCES = ("curated", "literature", "predicted")


class DrugMechanismError(Exception):
    """Base drug mechanism error."""


@dataclass
class DrugMechanism:
    mechanism_id: str
    drug_name: str
    mechanism_class: str
    target_names: List[str] = field(default_factory=list)
    target_type: str = "protein"
    affected_pathways: List[str] = field(default_factory=list)
    pharmacodynamic_note: str = ""
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mechanism_id or not isinstance(self.mechanism_id, str):
            raise DrugMechanismError("mechanism_id required")
        if not self.drug_name or not isinstance(self.drug_name, str):
            raise DrugMechanismError("drug_name required")
        if self.mechanism_class not in MECHANISM_CLASSES:
            raise DrugMechanismError(
                f"invalid mechanism_class: {self.mechanism_class!r}")
        if self.target_type not in TARGET_TYPES:
            raise DrugMechanismError(f"invalid target_type: {self.target_type!r}")
        if self.source not in SOURCES:
            raise DrugMechanismError(f"invalid source: {self.source!r}")


class DrugMechanismAnalyzer:
    """Mechanism store with drug / target / pathway queries."""

    def __init__(self) -> None:
        self._mechanisms: Dict[str, DrugMechanism] = {}
        self._drug_index: Dict[str, List[str]] = {}
        self._target_index: Dict[str, List[str]] = {}
        self._pathway_index: Dict[str, List[str]] = {}

    def add(self, mechanism: DrugMechanism) -> DrugMechanism:
        if mechanism.mechanism_id in self._mechanisms:
            raise DrugMechanismError(
                f"duplicate mechanism_id: {mechanism.mechanism_id}")
        self._mechanisms[mechanism.mechanism_id] = mechanism
        self._drug_index.setdefault(mechanism.drug_name, []).append(
            mechanism.mechanism_id)
        for t in mechanism.target_names:
            self._target_index.setdefault(t, []).append(mechanism.mechanism_id)
        for p in mechanism.affected_pathways:
            self._pathway_index.setdefault(p, []).append(mechanism.mechanism_id)
        return mechanism

    def get(self, mechanism_id: str) -> DrugMechanism:
        try:
            return self._mechanisms[mechanism_id]
        except KeyError as exc:
            raise DrugMechanismError(f"unknown mechanism_id: {mechanism_id}") from exc

    def for_drug(self, drug_name: str) -> List[DrugMechanism]:
        return [self.get(m) for m in self._drug_index.get(drug_name, [])]

    def by_target(self, target: str) -> List[DrugMechanism]:
        return [self.get(m) for m in self._target_index.get(target, [])]

    def by_pathway(self, pathway: str) -> List[DrugMechanism]:
        return [self.get(m) for m in self._pathway_index.get(pathway, [])]

    def by_class(self, mechanism_class: str) -> List[DrugMechanism]:
        if mechanism_class not in MECHANISM_CLASSES:
            raise DrugMechanismError(
                f"invalid mechanism_class: {mechanism_class!r}")
        return [m for m in self._mechanisms.values()
                if m.mechanism_class == mechanism_class]

    def shared_target_drugs(self, drug_a: str, drug_b: str) -> List[str]:
        a_recs = self.for_drug(drug_a)
        b_recs = self.for_drug(drug_b)
        a_targets = {t for r in a_recs for t in r.target_names}
        b_targets = {t for r in b_recs for t in r.target_names}
        return sorted(a_targets & b_targets)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "mechanisms": len(self._mechanisms),
            "drugs": len(self._drug_index),
            "targets": len(self._target_index),
            "pathways": len(self._pathway_index),
        }


def self_test() -> bool:
    analyzer = DrugMechanismAnalyzer()
    analyzer.add(DrugMechanism(
        "M1", "Imatinib", "inhibitor",
        target_names=["BCR-ABL1", "c-KIT", "PDGFR"],
        affected_pathways=["RTK_RAS"],
        disease_ids=["D_cml"]))
    analyzer.add(DrugMechanism(
        "M2", "Nilotinib", "inhibitor",
        target_names=["BCR-ABL1", "PDGFR"],
        affected_pathways=["RTK_RAS"],
        disease_ids=["D_cml"]))
    analyzer.add(DrugMechanism(
        "M3", "Pembrolizumab", "blocker",
        target_names=["PD-1"],
        affected_pathways=["immune_checkpoint"],
        disease_ids=["D_melanoma"]))
    assert len(analyzer.for_drug("Imatinib")) == 1
    assert len(analyzer.by_target("BCR-ABL1")) == 2
    assert len(analyzer.by_pathway("RTK_RAS")) == 2
    assert len(analyzer.by_class("blocker")) == 1
    assert analyzer.shared_target_drugs("Imatinib", "Nilotinib") == [
        "BCR-ABL1", "PDGFR"]
    print("drug_mechanism_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
