"""DESI Infinity System - Molecular Biology Engine (v6.2.0).

Central registry for molecular processes (transcription, translation,
replication, recombination, repair, splicing) with key molecular actors,
location, and disease links. Research annotations only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PROCESS_TYPES = ("transcription", "translation", "replication", "repair",
                 "recombination", "splicing", "epigenetic_modification",
                 "protein_folding", "degradation", "other")
LOCATIONS = ("nucleus", "cytoplasm", "mitochondria", "er", "golgi",
             "membrane", "extracellular", "unknown")
SOURCES = ("curated", "literature", "predicted")


class MolecularBiologyError(Exception):
    """Base molecular biology error."""


@dataclass
class MolecularProcess:
    process_id: str
    name: str
    process_type: str
    location: str = "unknown"
    key_actors: List[str] = field(default_factory=list)
    required_molecules: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.process_id or not isinstance(self.process_id, str):
            raise MolecularBiologyError("process_id required")
        if not self.name or not isinstance(self.name, str):
            raise MolecularBiologyError("name required")
        if self.process_type not in PROCESS_TYPES:
            raise MolecularBiologyError(
                f"invalid process_type: {self.process_type!r}")
        if self.location not in LOCATIONS:
            raise MolecularBiologyError(f"invalid location: {self.location!r}")
        if self.source not in SOURCES:
            raise MolecularBiologyError(f"invalid source: {self.source!r}")


class MolecularBiologyEngine:
    """Process registry with type / actor / disease queries."""

    def __init__(self) -> None:
        self._processes: Dict[str, MolecularProcess] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._actor_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, process: MolecularProcess) -> MolecularProcess:
        if process.process_id in self._processes:
            raise MolecularBiologyError(
                f"duplicate process_id: {process.process_id}")
        self._processes[process.process_id] = process
        self._type_index.setdefault(process.process_type, []).append(process.process_id)
        for a in process.key_actors:
            self._actor_index.setdefault(a, []).append(process.process_id)
        for did in process.disease_ids:
            self._disease_index.setdefault(did, []).append(process.process_id)
        return process

    def get(self, process_id: str) -> MolecularProcess:
        try:
            return self._processes[process_id]
        except KeyError as exc:
            raise MolecularBiologyError(f"unknown process_id: {process_id}") from exc

    def by_type(self, process_type: str) -> List[MolecularProcess]:
        if process_type not in PROCESS_TYPES:
            raise MolecularBiologyError(
                f"invalid process_type: {process_type!r}")
        return [self.get(p) for p in self._type_index.get(process_type, [])]

    def by_actor(self, actor: str) -> List[MolecularProcess]:
        return [self.get(p) for p in self._actor_index.get(actor, [])]

    def for_disease(self, disease_id: str) -> List[MolecularProcess]:
        return [self.get(p) for p in self._disease_index.get(disease_id, [])]

    def by_location(self, location: str) -> List[MolecularProcess]:
        if location not in LOCATIONS:
            raise MolecularBiologyError(f"invalid location: {location!r}")
        return [p for p in self._processes.values() if p.location == location]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "processes": len(self._processes),
            "types": len(self._type_index),
            "actors": len(self._actor_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    engine = MolecularBiologyEngine()
    engine.add(MolecularProcess(
        "MP1", "DNA replication", "replication", "nucleus",
        key_actors=["POLA1", "MCM2-7", "PCNA"],
        required_molecules=["dNTPs", "ATP"],
        disease_ids=["D_cancer"]))
    engine.add(MolecularProcess(
        "MP2", "mRNA splicing", "splicing", "nucleus",
        key_actors=["SF3B1", "U2AF1"],
        required_molecules=["snRNPs"],
        disease_ids=["D_mds"]))
    assert len(engine.by_type("replication")) == 1
    assert len(engine.by_actor("POLA1")) == 1
    assert len(engine.for_disease("D_mds")) == 1
    assert len(engine.by_location("nucleus")) == 2
    assert engine.stats()["processes"] == 2
    print("molecular_biology_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
