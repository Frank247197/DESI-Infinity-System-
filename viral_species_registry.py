"""DESI Infinity System - Viral Species Registry (v6.2.0).

Species-level viral registry with ICTV-style species names, type species
flag, family/genus assignment, and human-pathogenic annotation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PATHOGENICITY = ("human_pathogen", "animal_pathogen", "plant_pathogen",
                 "bacterial_pathogen", "non_pathogenic", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ViralSpeciesError(Exception):
    """Base viral species error."""


@dataclass
class ViralSpecies:
    species_id: str
    name: str
    family_id: str = ""
    genus_id: str = ""
    type_species: bool = False
    pathogenicity: str = "unknown"
    disease_ids: List[str] = field(default_factory=list)
    genome_accessions: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.species_id or not isinstance(self.species_id, str):
            raise ViralSpeciesError("species_id required")
        if not self.name or not isinstance(self.name, str):
            raise ViralSpeciesError("name required")
        if self.pathogenicity not in PATHOGENICITY:
            raise ViralSpeciesError(
                f"invalid pathogenicity: {self.pathogenicity!r}")
        if self.source not in SOURCES:
            raise ViralSpeciesError(f"invalid source: {self.source!r}")

    def is_human_pathogen(self) -> bool:
        return self.pathogenicity == "human_pathogen"


class ViralSpeciesRegistry:
    """Species registry with family/genus/pathogenicity queries."""

    def __init__(self) -> None:
        self._species: Dict[str, ViralSpecies] = {}
        self._family_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, species: ViralSpecies) -> ViralSpecies:
        if species.species_id in self._species:
            raise ViralSpeciesError(f"duplicate species_id: {species.species_id}")
        self._species[species.species_id] = species
        if species.family_id:
            self._family_index.setdefault(species.family_id, []).append(
                species.species_id)
        for did in species.disease_ids:
            self._disease_index.setdefault(did, []).append(species.species_id)
        return species

    def get(self, species_id: str) -> ViralSpecies:
        try:
            return self._species[species_id]
        except KeyError as exc:
            raise ViralSpeciesError(f"unknown species_id: {species_id}") from exc

    def for_family(self, family_id: str) -> List[ViralSpecies]:
        return [self.get(s) for s in self._family_index.get(family_id, [])]

    def for_disease(self, disease_id: str) -> List[ViralSpecies]:
        return [self.get(s) for s in self._disease_index.get(disease_id, [])]

    def human_pathogens(self) -> List[ViralSpecies]:
        return [s for s in self._species.values() if s.is_human_pathogen()]

    def type_species(self) -> List[ViralSpecies]:
        return [s for s in self._species.values() if s.type_species]

    def by_pathogenicity(self, pathogenicity: str) -> List[ViralSpecies]:
        if pathogenicity not in PATHOGENICITY:
            raise ViralSpeciesError(
                f"invalid pathogenicity: {pathogenicity!r}")
        return [s for s in self._species.values()
                if s.pathogenicity == pathogenicity]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "species": len(self._species),
            "human_pathogens": len(self.human_pathogens()),
            "families": len(self._family_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    registry = ViralSpeciesRegistry()
    registry.add(ViralSpecies(
        "VS_flu_a", "Influenza A virus", family_id="VF_ortho",
        genus_id="Alphainfluenzavirus", type_species=True,
        pathogenicity="human_pathogen", disease_ids=["D_flu"]))
    registry.add(ViralSpecies(
        "VS_sars2", "SARS-CoV-2", family_id="VF_corona",
        genus_id="Betacoronavirus", pathogenicity="human_pathogen",
        disease_ids=["D_covid19"]))
    registry.add(ViralSpecies(
        "VS_ibv", "Infectious bronchitis virus", family_id="VF_corona",
        pathogenicity="animal_pathogen"))
    assert len(registry.for_family("VF_corona")) == 2
    assert registry.for_disease("D_flu")[0].name == "Influenza A virus"
    assert len(registry.human_pathogens()) == 2
    assert registry.type_species()[0].species_id == "VS_flu_a"
    print("viral_species_registry: OK")
    return True


if __name__ == "__main__":
    self_test()
