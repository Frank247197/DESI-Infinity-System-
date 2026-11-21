"""DESI Infinity System - Cellular Mechanism Engine (v6.2.0).

Registry of cellular mechanisms (signaling, transport, metabolism,
homeostasis, stress responses) with molecular mediators and disease
links. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MECHANISM_CLASSES = ("signaling", "transport", "metabolism", "homeostasis",
                     "stress_response", "differentiation", "migration",
                     "proliferation", "death", "other")
COMPARTMENTS = ("plasma_membrane", "cytoplasm", "nucleus", "mitochondria",
                "er", "golgi", "lysosome", "cytoskeleton", "other")
SOURCES = ("curated", "literature", "predicted")


class CellularMechanismError(Exception):
    """Base cellular mechanism error."""


@dataclass
class CellularMechanism:
    mechanism_id: str
    name: str
    mechanism_class: str
    compartments: List[str] = field(default_factory=list)
    key_molecules: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mechanism_id or not isinstance(self.mechanism_id, str):
            raise CellularMechanismError("mechanism_id required")
        if not self.name or not isinstance(self.name, str):
            raise CellularMechanismError("name required")
        if self.mechanism_class not in MECHANISM_CLASSES:
            raise CellularMechanismError(
                f"invalid mechanism_class: {self.mechanism_class!r}")
        if self.source not in SOURCES:
            raise CellularMechanismError(f"invalid source: {self.source!r}")
        for c in self.compartments:
            if c not in COMPARTMENTS:
                raise CellularMechanismError(f"invalid compartment: {c!r}")


class CellularMechanismEngine:
    """Registry with class / compartment / molecule / disease queries."""

    def __init__(self) -> None:
        self._mechanisms: Dict[str, CellularMechanism] = {}
        self._class_index: Dict[str, List[str]] = {}
        self._molecule_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, mechanism: CellularMechanism) -> CellularMechanism:
        if mechanism.mechanism_id in self._mechanisms:
            raise CellularMechanismError(
                f"duplicate mechanism_id: {mechanism.mechanism_id}")
        self._mechanisms[mechanism.mechanism_id] = mechanism
        self._class_index.setdefault(mechanism.mechanism_class, []).append(
            mechanism.mechanism_id)
        for m in mechanism.key_molecules:
            self._molecule_index.setdefault(m, []).append(mechanism.mechanism_id)
        for did in mechanism.disease_ids:
            self._disease_index.setdefault(did, []).append(mechanism.mechanism_id)
        return mechanism

    def get(self, mechanism_id: str) -> CellularMechanism:
        try:
            return self._mechanisms[mechanism_id]
        except KeyError as exc:
            raise CellularMechanismError(
                f"unknown mechanism_id: {mechanism_id}") from exc

    def by_class(self, mechanism_class: str) -> List[CellularMechanism]:
        if mechanism_class not in MECHANISM_CLASSES:
            raise CellularMechanismError(
                f"invalid mechanism_class: {mechanism_class!r}")
        return [self.get(m) for m in self._class_index.get(mechanism_class, [])]

    def by_molecule(self, molecule: str) -> List[CellularMechanism]:
        return [self.get(m) for m in self._molecule_index.get(molecule, [])]

    def for_disease(self, disease_id: str) -> List[CellularMechanism]:
        return [self.get(m) for m in self._disease_index.get(disease_id, [])]

    def by_compartment(self, compartment: str) -> List[CellularMechanism]:
        if compartment not in COMPARTMENTS:
            raise CellularMechanismError(
                f"invalid compartment: {compartment!r}")
        return [m for m in self._mechanisms.values()
                if compartment in m.compartments]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "mechanisms": len(self._mechanisms),
            "classes": len(self._class_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    engine = CellularMechanismEngine()
    engine.add(CellularMechanism(
        "CM1", "Receptor tyrosine kinase signaling", "signaling",
        compartments=["plasma_membrane", "cytoplasm"],
        key_molecules=["EGFR", "GRB2", "SOS", "RAS", "MAPK"],
        disease_ids=["D_cancer"]))
    engine.add(CellularMechanism(
        "CM2", "Mitochondrial apoptosis", "death",
        compartments=["mitochondria"],
        key_molecules=["BAX", "BAK", "CYCS", "APAF1", "CASP9"],
        disease_ids=["D_cancer", "D_neurodegeneration"]))
    engine.add(CellularMechanism(
        "CM3", "Autophagic flux", "homeostasis",
        compartments=["cytoplasm", "lysosome"],
        key_molecules=["ATG5", "ATG7", "LC3", "BECN1"],
        disease_ids=["D_neurodegeneration"]))
    assert len(engine.by_class("signaling")) == 1
    assert len(engine.by_molecule("BAX")) == 1
    assert len(engine.for_disease("D_cancer")) == 2
    assert len(engine.by_compartment("mitochondria")) == 1
    assert engine.stats()["mechanisms"] == 3
    print("cellular_mechanism_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
