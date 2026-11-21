"""DESI Infinity System - Parasite Intelligence Engine (v6.2.0).

Registry for parasites (protozoa, helminths, ectoparasites) with life
cycle stages, vectors, host range, and disease linkage. Research only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PARASITE_CLASSES = ("protozoa", "helminth_nematode", "helminth_cestode",
                    "helminth_trematode", "ectoparasite", "unknown")
LIFE_STAGES = ("sporozoite", "merozoite", "trophozoite", "gametocyte",
               "egg", "larva", "adult", "cyst", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ParasiteError(Exception):
    """Base parasite error."""


@dataclass
class ParasiteProfile:
    parasite_id: str
    species: str
    parasite_class: str = "unknown"
    life_stages: List[str] = field(default_factory=list)
    vectors: List[str] = field(default_factory=list)
    host_range: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    geographic_range: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.parasite_id or not isinstance(self.parasite_id, str):
            raise ParasiteError("parasite_id required")
        if not self.species or not isinstance(self.species, str):
            raise ParasiteError("species required")
        if self.parasite_class not in PARASITE_CLASSES:
            raise ParasiteError(f"invalid parasite_class: {self.parasite_class!r}")
        if self.source not in SOURCES:
            raise ParasiteError(f"invalid source: {self.source!r}")
        for s in self.life_stages:
            if s not in LIFE_STAGES:
                raise ParasiteError(f"invalid life_stage: {s!r}")

    def requires_vector(self) -> bool:
        return len(self.vectors) > 0


class ParasiteIntelligenceEngine:
    """Parasite registry with vector / class / geography queries."""

    def __init__(self) -> None:
        self._parasites: Dict[str, ParasiteProfile] = {}
        self._class_index: Dict[str, List[str]] = {}
        self._vector_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, profile: ParasiteProfile) -> ParasiteProfile:
        if profile.parasite_id in self._parasites:
            raise ParasiteError(f"duplicate parasite_id: {profile.parasite_id}")
        self._parasites[profile.parasite_id] = profile
        self._class_index.setdefault(profile.parasite_class, []).append(profile.parasite_id)
        for v in profile.vectors:
            self._vector_index.setdefault(v, []).append(profile.parasite_id)
        for did in profile.disease_ids:
            self._disease_index.setdefault(did, []).append(profile.parasite_id)
        return profile

    def get(self, parasite_id: str) -> ParasiteProfile:
        try:
            return self._parasites[parasite_id]
        except KeyError as exc:
            raise ParasiteError(f"unknown parasite_id: {parasite_id}") from exc

    def by_class(self, parasite_class: str) -> List[ParasiteProfile]:
        if parasite_class not in PARASITE_CLASSES:
            raise ParasiteError(f"invalid parasite_class: {parasite_class!r}")
        return [self.get(pid) for pid in self._class_index.get(parasite_class, [])]

    def by_vector(self, vector: str) -> List[ParasiteProfile]:
        return [self.get(pid) for pid in self._vector_index.get(vector, [])]

    def for_disease(self, disease_id: str) -> List[ParasiteProfile]:
        return [self.get(pid) for pid in self._disease_index.get(disease_id, [])]

    def vector_borne(self) -> List[ParasiteProfile]:
        return [p for p in self._parasites.values() if p.requires_vector()]

    def in_region(self, region: str) -> List[ParasiteProfile]:
        return [p for p in self._parasites.values() if region in p.geographic_range]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "parasites": len(self._parasites),
            "protozoa": len(self.by_class("protozoa")),
            "helminths": sum(
                len(self.by_class(c)) for c in
                ("helminth_nematode", "helminth_cestode", "helminth_trematode")),
            "vector_borne": len(self.vector_borne()),
        }


def self_test() -> bool:
    engine = ParasiteIntelligenceEngine()
    engine.add(ParasiteProfile(
        "NCBITaxon:5833", "Plasmodium falciparum", "protozoa",
        life_stages=["sporozoite", "merozoite", "trophozoite", "gametocyte"],
        vectors=["Anopheles gambiae"],
        host_range=["human"],
        disease_ids=["D_malaria"],
        geographic_range=["sub_saharan_africa", "southeast_asia"]))
    engine.add(ParasiteProfile(
        "NCBITaxon:6181", "Schistosoma mansoni", "helminth_trematode",
        life_stages=["egg", "larva", "adult"],
        vectors=["Biomphalaria glabrata"],
        host_range=["human"],
        disease_ids=["D_schistosomiasis"],
        geographic_range=["sub_saharan_africa"]))
    assert engine.by_class("protozoa")[0].parasite_id == "NCBITaxon:5833"
    assert engine.by_vector("Anopheles gambiae")[0].species == "Plasmodium falciparum"
    assert engine.for_disease("D_malaria")[0].parasite_id == "NCBITaxon:5833"
    assert len(engine.vector_borne()) == 2
    assert len(engine.in_region("sub_saharan_africa")) == 2
    print("parasite_intelligence_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
