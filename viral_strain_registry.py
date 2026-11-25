"""DESI Infinity System - Viral Strain Registry (v6.2.0).

Strain-level registry (lineages, clades, isolates) with parent species,
country, collection year, and reference accession. Research data only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CLADE_CLASSES = ("clade", "lineage", "sublineage", "variant_of_concern",
                 "variant_of_interest", "isolate", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ViralStrainError(Exception):
    """Base viral strain error."""


@dataclass
class ViralStrain:
    strain_id: str
    species_id: str
    name: str
    clade_class: str = "unknown"
    country: str = ""
    collection_year: Optional[int] = None
    reference_accession: str = ""
    defining_mutations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.strain_id or not isinstance(self.strain_id, str):
            raise ViralStrainError("strain_id required")
        if not self.species_id or not isinstance(self.species_id, str):
            raise ViralStrainError("species_id required")
        if not self.name or not isinstance(self.name, str):
            raise ViralStrainError("name required")
        if self.clade_class not in CLADE_CLASSES:
            raise ViralStrainError(f"invalid clade_class: {self.clade_class!r}")
        if self.source not in SOURCES:
            raise ViralStrainError(f"invalid source: {self.source!r}")
        if self.collection_year is not None:
            if not isinstance(self.collection_year, int) or not (
                    1900 <= self.collection_year <= 2100):
                raise ViralStrainError(
                    "collection_year must be a 4-digit year or None")

    def is_voc(self) -> bool:
        return self.clade_class == "variant_of_concern"


class ViralStrainRegistry:
    """Strain registry with species / clade / country queries."""

    def __init__(self) -> None:
        self._strains: Dict[str, ViralStrain] = {}
        self._species_index: Dict[str, List[str]] = {}
        self._country_index: Dict[str, List[str]] = {}

    def add(self, strain: ViralStrain) -> ViralStrain:
        if strain.strain_id in self._strains:
            raise ViralStrainError(f"duplicate strain_id: {strain.strain_id}")
        self._strains[strain.strain_id] = strain
        self._species_index.setdefault(strain.species_id, []).append(strain.strain_id)
        if strain.country:
            self._country_index.setdefault(strain.country, []).append(strain.strain_id)
        return strain

    def get(self, strain_id: str) -> ViralStrain:
        try:
            return self._strains[strain_id]
        except KeyError as exc:
            raise ViralStrainError(f"unknown strain_id: {strain_id}") from exc

    def for_species(self, species_id: str) -> List[ViralStrain]:
        return [self.get(s) for s in self._species_index.get(species_id, [])]

    def by_clade_class(self, clade_class: str) -> List[ViralStrain]:
        if clade_class not in CLADE_CLASSES:
            raise ViralStrainError(f"invalid clade_class: {clade_class!r}")
        return [s for s in self._strains.values() if s.clade_class == clade_class]

    def variants_of_concern(self) -> List[ViralStrain]:
        return [s for s in self._strains.values() if s.is_voc()]

    def by_country(self, country: str) -> List[ViralStrain]:
        return [self.get(s) for s in self._country_index.get(country, [])]

    def by_year_range(self, year_min: int, year_max: int) -> List[ViralStrain]:
        if year_min > year_max:
            raise ViralStrainError("year_min > year_max")
        return [s for s in self._strains.values()
                if s.collection_year is not None
                and year_min <= s.collection_year <= year_max]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "strains": len(self._strains),
            "species": len(self._species_index),
            "countries": len(self._country_index),
            "voc": len(self.variants_of_concern()),
        }


def self_test() -> bool:
    registry = ViralStrainRegistry()
    registry.add(ViralStrain(
        "STR_b117", "VS_sars2", "B.1.1.7",
        clade_class="variant_of_concern", country="GBR",
        collection_year=2020, reference_accession="EPI_ISL_601443",
        defining_mutations=["N501Y", "P681H"]))
    registry.add(ViralStrain(
        "STR_b1351", "VS_sars2", "B.1.351",
        clade_class="variant_of_concern", country="ZAF",
        collection_year=2020, defining_mutations=["E484K", "N501Y"]))
    registry.add(ViralStrain(
        "STR_cal07", "VS_flu_a", "A/California/07/2009",
        clade_class="isolate", country="USA", collection_year=2009))
    assert len(registry.for_species("VS_sars2")) == 2
    assert len(registry.variants_of_concern()) == 2
    assert len(registry.by_country("USA")) == 1
    assert len(registry.by_year_range(2020, 2021)) == 2
    assert registry.stats()["voc"] == 2
    print("viral_strain_registry: OK")
    return True


if __name__ == "__main__":
    self_test()
