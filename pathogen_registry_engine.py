"""DESI Infinity System - Pathogen Registry Engine (v6.2.0).

Central pathogen registry (virus, bacterium, fungus, parasite, prion)
with taxonomy lineage, genome accession, host range, and linkage to
disease IDs. Enforces genome_context separation via `sequence_origin`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

KINGDOMS = ("virus", "bacteria", "fungus", "parasite", "prion", "unknown")
SEQUENCE_ORIGINS = ("pathogen_genome", "human_endogenous_viral_element",
                    "human_sequence", "environmental", "unknown")
TRANSMISSION_MODES = ("airborne", "droplet", "contact", "vector",
                      "foodborne", "waterborne", "bloodborne", "sexual",
                      "vertical", "unknown")
SOURCES = ("curated", "literature", "predicted")


class PathogenRegistryError(Exception):
    """Base pathogen registry error."""


@dataclass
class PathogenRecord:
    pathogen_id: str
    name: str
    kingdom: str
    taxonomy_lineage: List[str] = field(default_factory=list)
    sequence_origin: str = "pathogen_genome"
    genome_accession: str = ""
    host_range: List[str] = field(default_factory=list)
    transmission_modes: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pathogen_id or not isinstance(self.pathogen_id, str):
            raise PathogenRegistryError("pathogen_id required")
        if not self.name or not isinstance(self.name, str):
            raise PathogenRegistryError("name required")
        if self.kingdom not in KINGDOMS:
            raise PathogenRegistryError(f"invalid kingdom: {self.kingdom!r}")
        if self.sequence_origin not in SEQUENCE_ORIGINS:
            raise PathogenRegistryError(f"invalid sequence_origin: {self.sequence_origin!r}")
        if self.source not in SOURCES:
            raise PathogenRegistryError(f"invalid source: {self.source!r}")
        for m in self.transmission_modes:
            if m not in TRANSMISSION_MODES:
                raise PathogenRegistryError(f"invalid transmission_mode: {m!r}")

    def is_active_pathogen_sequence(self) -> bool:
        """True only when the record represents the pathogen's own genome."""
        return self.sequence_origin == "pathogen_genome"

    def is_human_ev(self) -> bool:
        return self.sequence_origin == "human_endogenous_viral_element"


class PathogenRegistryEngine:
    """Registry with kingdom / transmission / origin queries."""

    def __init__(self) -> None:
        self._pathogens: Dict[str, PathogenRecord] = {}
        self._kingdom_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, record: PathogenRecord) -> PathogenRecord:
        if record.pathogen_id in self._pathogens:
            raise PathogenRegistryError(f"duplicate pathogen_id: {record.pathogen_id}")
        self._pathogens[record.pathogen_id] = record
        self._kingdom_index.setdefault(record.kingdom, []).append(record.pathogen_id)
        for did in record.disease_ids:
            self._disease_index.setdefault(did, []).append(record.pathogen_id)
        return record

    def get(self, pathogen_id: str) -> PathogenRecord:
        try:
            return self._pathogens[pathogen_id]
        except KeyError as exc:
            raise PathogenRegistryError(f"unknown pathogen_id: {pathogen_id}") from exc

    def by_kingdom(self, kingdom: str) -> List[PathogenRecord]:
        if kingdom not in KINGDOMS:
            raise PathogenRegistryError(f"invalid kingdom: {kingdom!r}")
        return [self.get(pid) for pid in self._kingdom_index.get(kingdom, [])]

    def for_disease(self, disease_id: str) -> List[PathogenRecord]:
        return [self.get(pid) for pid in self._disease_index.get(disease_id, [])]

    def active_pathogens(self) -> List[PathogenRecord]:
        return [p for p in self._pathogens.values() if p.is_active_pathogen_sequence()]

    def human_ev_elements(self) -> List[PathogenRecord]:
        return [p for p in self._pathogens.values() if p.is_human_ev()]

    def by_transmission(self, mode: str) -> List[PathogenRecord]:
        if mode not in TRANSMISSION_MODES:
            raise PathogenRegistryError(f"invalid transmission_mode: {mode!r}")
        return [p for p in self._pathogens.values() if mode in p.transmission_modes]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "pathogens": len(self._pathogens),
            "viruses": len(self.by_kingdom("virus")),
            "bacteria": len(self.by_kingdom("bacteria")),
            "ev_elements": len(self.human_ev_elements()),
        }


def self_test() -> bool:
    engine = PathogenRegistryEngine()
    engine.add(PathogenRecord(
        "NCBITaxon:11320", "Influenza A virus", "virus",
        taxonomy_lineage=["Orthomyxoviridae", "Alphainfluenzavirus"],
        sequence_origin="pathogen_genome",
        genome_accession="NC_007373",
        host_range=["human", "avian", "swine"],
        transmission_modes=["droplet", "contact"],
        disease_ids=["D_flu"]))
    engine.add(PathogenRecord(
        "EV:HERVK113", "HERV-K endogenous element", "virus",
        sequence_origin="human_endogenous_viral_element",
        host_range=["human"],
        disease_ids=[]))
    assert engine.by_kingdom("virus")[0].pathogen_id == "NCBITaxon:11320"
    assert engine.for_disease("D_flu")[0].name == "Influenza A virus"
    assert len(engine.active_pathogens()) == 1
    assert len(engine.human_ev_elements()) == 1
    assert len(engine.by_transmission("droplet")) == 1
    print("pathogen_registry_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
