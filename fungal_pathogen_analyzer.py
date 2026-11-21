"""DESI Infinity System - Fungal Pathogen Analyzer (v6.2.0).

Registry for fungal pathogens with morphology, antifungal resistance
genes, host range, and disease linkage. Research only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MORPHOLOGY = ("yeast", "mold", "dimorphic", "dermatophyte", "unknown")
RESISTANCE_CLASSES = ("azoles", "echinocandins", "polyenes", "pyrimidine_analogs", "none")
SOURCES = ("curated", "literature", "predicted")


class FungalPathogenError(Exception):
    """Base fungal pathogen error."""


@dataclass
class FungalPathogenProfile:
    profile_id: str
    species: str
    morphology: str = "unknown"
    genome_size_mb: float = 0.0
    gc_content: float = 0.0
    resistance_classes: List[str] = field(default_factory=list)
    resistance_genes: List[str] = field(default_factory=list)
    host_range: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise FungalPathogenError("profile_id required")
        if not self.species or not isinstance(self.species, str):
            raise FungalPathogenError("species required")
        if self.morphology not in MORPHOLOGY:
            raise FungalPathogenError(f"invalid morphology: {self.morphology!r}")
        if self.source not in SOURCES:
            raise FungalPathogenError(f"invalid source: {self.source!r}")
        for rc in self.resistance_classes:
            if rc not in RESISTANCE_CLASSES:
                raise FungalPathogenError(f"invalid resistance_class: {rc!r}")
        if not 0.0 <= float(self.gc_content) <= 1.0:
            raise FungalPathogenError("gc_content must be in [0, 1]")

    def is_multidrug_resistant(self, threshold: int = 2) -> bool:
        classes = {c for c in self.resistance_classes if c != "none"}
        return len(classes) >= threshold


class FungalPathogenAnalyzer:
    """Fungal pathogen registry with resistance queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, FungalPathogenProfile] = {}
        self._species_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, profile: FungalPathogenProfile) -> FungalPathogenProfile:
        if profile.profile_id in self._profiles:
            raise FungalPathogenError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        self._species_index.setdefault(profile.species, []).append(profile.profile_id)
        for g in profile.resistance_genes:
            self._gene_index.setdefault(g, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> FungalPathogenProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise FungalPathogenError(f"unknown profile_id: {profile_id}") from exc

    def by_species(self, species: str) -> List[FungalPathogenProfile]:
        return [self.get(pid) for pid in self._species_index.get(species, [])]

    def by_morphology(self, morphology: str) -> List[FungalPathogenProfile]:
        if morphology not in MORPHOLOGY:
            raise FungalPathogenError(f"invalid morphology: {morphology!r}")
        return [p for p in self._profiles.values() if p.morphology == morphology]

    def by_resistance_class(self, resistance_class: str) -> List[FungalPathogenProfile]:
        if resistance_class not in RESISTANCE_CLASSES:
            raise FungalPathogenError(f"invalid resistance_class: {resistance_class!r}")
        return [p for p in self._profiles.values() if resistance_class in p.resistance_classes]

    def by_resistance_gene(self, gene: str) -> List[FungalPathogenProfile]:
        return [self.get(pid) for pid in self._gene_index.get(gene, [])]

    def multidrug_resistant(self) -> List[FungalPathogenProfile]:
        return [p for p in self._profiles.values() if p.is_multidrug_resistant()]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "species": len(self._species_index),
            "mdr": len(self.multidrug_resistant()),
        }


def self_test() -> bool:
    analyzer = FungalPathogenAnalyzer()
    analyzer.add(FungalPathogenProfile(
        "F1", "Candida auris", "yeast",
        genome_size_mb=12.5, gc_content=0.45,
        resistance_classes=["azoles", "echinocandins"],
        resistance_genes=["ERG11", "FKS1"],
        host_range=["human"],
        disease_ids=["D_candidiasis"]))
    analyzer.add(FungalPathogenProfile(
        "F2", "Aspergillus fumigatus", "mold",
        genome_size_mb=29.0, gc_content=0.49,
        resistance_classes=["azoles"],
        resistance_genes=["cyp51A"],
        host_range=["human"],
        disease_ids=["D_aspergillosis"]))
    assert analyzer.by_species("Candida auris")[0].profile_id == "F1"
    assert analyzer.by_morphology("mold")[0].profile_id == "F2"
    assert len(analyzer.by_resistance_class("azoles")) == 2
    assert analyzer.by_resistance_gene("FKS1")[0].profile_id == "F1"
    assert len(analyzer.multidrug_resistant()) == 1
    print("fungal_pathogen_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
