"""DESI Infinity System - Antibody Research Engine (v6.2.0).

Antibody research registry: isotype, target antigen, origin (natural,
vaccine, therapeutic), and neutralization spectrum. Research-only
annotations; not prescribing or recommending biologics.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ISOTYPES = ("IgG", "IgM", "IgA", "IgD", "IgE", "nanobody", "unknown")
ORIGINS = ("natural_infection", "vaccine_induced", "therapeutic",
           "engineered", "unknown")
SPECTRUM = ("narrow", "moderate", "broad", "unknown")
SOURCES = ("curated", "literature", "predicted")


class AntibodyError(Exception):
    """Base antibody error."""


@dataclass
class AntibodyRecord:
    antibody_id: str
    name: str
    isotype: str = "unknown"
    target_antigen: str = ""
    target_pathogen_id: str = ""
    origin: str = "unknown"
    spectrum: str = "unknown"
    cross_reactivity: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.antibody_id or not isinstance(self.antibody_id, str):
            raise AntibodyError("antibody_id required")
        if not self.name or not isinstance(self.name, str):
            raise AntibodyError("name required")
        if self.isotype not in ISOTYPES:
            raise AntibodyError(f"invalid isotype: {self.isotype!r}")
        if self.origin not in ORIGINS:
            raise AntibodyError(f"invalid origin: {self.origin!r}")
        if self.spectrum not in SPECTRUM:
            raise AntibodyError(f"invalid spectrum: {self.spectrum!r}")
        if self.source not in SOURCES:
            raise AntibodyError(f"invalid source: {self.source!r}")


class AntibodyResearchEngine:
    """Antibody registry with target / isotype / origin queries."""

    def __init__(self) -> None:
        self._antibodies: Dict[str, AntibodyRecord] = {}
        self._target_index: Dict[str, List[str]] = {}
        self._pathogen_index: Dict[str, List[str]] = {}
        self._isotype_index: Dict[str, List[str]] = {}

    def add(self, record: AntibodyRecord) -> AntibodyRecord:
        if record.antibody_id in self._antibodies:
            raise AntibodyError(f"duplicate antibody_id: {record.antibody_id}")
        self._antibodies[record.antibody_id] = record
        if record.target_antigen:
            self._target_index.setdefault(record.target_antigen, []).append(
                record.antibody_id)
        if record.target_pathogen_id:
            self._pathogen_index.setdefault(record.target_pathogen_id, []).append(
                record.antibody_id)
        self._isotype_index.setdefault(record.isotype, []).append(record.antibody_id)
        return record

    def get(self, antibody_id: str) -> AntibodyRecord:
        try:
            return self._antibodies[antibody_id]
        except KeyError as exc:
            raise AntibodyError(f"unknown antibody_id: {antibody_id}") from exc

    def by_target(self, antigen: str) -> List[AntibodyRecord]:
        return [self.get(aid) for aid in self._target_index.get(antigen, [])]

    def by_pathogen(self, pathogen_id: str) -> List[AntibodyRecord]:
        return [self.get(aid) for aid in self._pathogen_index.get(pathogen_id, [])]

    def by_isotype(self, isotype: str) -> List[AntibodyRecord]:
        if isotype not in ISOTYPES:
            raise AntibodyError(f"invalid isotype: {isotype!r}")
        return [self.get(aid) for aid in self._isotype_index.get(isotype, [])]

    def by_origin(self, origin: str) -> List[AntibodyRecord]:
        if origin not in ORIGINS:
            raise AntibodyError(f"invalid origin: {origin!r}")
        return [a for a in self._antibodies.values() if a.origin == origin]

    def broadly_neutralizing(self) -> List[AntibodyRecord]:
        return [a for a in self._antibodies.values() if a.spectrum == "broad"]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "antibodies": len(self._antibodies),
            "targets": len(self._target_index),
            "pathogens": len(self._pathogen_index),
            "bNAbs": len(self.broadly_neutralizing()),
        }


def self_test() -> bool:
    engine = AntibodyResearchEngine()
    engine.add(AntibodyRecord(
        "AB1", "VRC01", "IgG", "gp120", "NCBITaxon:11676",
        "engineered", "broad", ["HIV-1 clade A", "HIV-1 clade B"],
        ["D_hiv"]))
    engine.add(AntibodyRecord(
        "AB2", "anti-S IgG", "IgG", "spike", "NCBITaxon:2697049",
        "vaccine_induced", "moderate", [], ["D_covid19"]))
    assert engine.by_target("gp120")[0].antibody_id == "AB1"
    assert engine.by_pathogen("NCBITaxon:2697049")[0].name == "anti-S IgG"
    assert len(engine.by_isotype("IgG")) == 2
    assert engine.by_origin("engineered")[0].antibody_id == "AB1"
    assert len(engine.broadly_neutralizing()) == 1
    print("antibody_research_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
