"""DESI Infinity System - Bacterial Genome Analyzer (v6.2.0).

Analyzes bacterial genome metadata: size, GC content, plasmid count,
Gram stain, and AMR gene carriage. Research only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

GRAM_STAIN = ("positive", "negative", "variable", "unknown")
SOURCES = ("curated", "literature", "predicted")
SEQUENCE_ORIGINS = ("pathogen_genome", "environmental", "unknown")


class BacterialGenomeError(Exception):
    """Base bacterial genome error."""


@dataclass
class BacterialGenomeProfile:
    profile_id: str
    species: str
    strain: str = ""
    genome_size_mb: float = 0.0
    gc_content: float = 0.0
    plasmid_count: int = 0
    gram_stain: str = "unknown"
    sequence_origin: str = "pathogen_genome"
    amr_genes: List[str] = field(default_factory=list)
    virulence_factors: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise BacterialGenomeError("profile_id required")
        if not self.species or not isinstance(self.species, str):
            raise BacterialGenomeError("species required")
        if self.gram_stain not in GRAM_STAIN:
            raise BacterialGenomeError(f"invalid gram_stain: {self.gram_stain!r}")
        if self.sequence_origin not in SEQUENCE_ORIGINS:
            raise BacterialGenomeError(f"invalid sequence_origin: {self.sequence_origin!r}")
        if self.source not in SOURCES:
            raise BacterialGenomeError(f"invalid source: {self.source!r}")
        if not isinstance(self.genome_size_mb, (int, float)) or self.genome_size_mb < 0:
            raise BacterialGenomeError("genome_size_mb must be non-negative")
        if not 0.0 <= float(self.gc_content) <= 1.0:
            raise BacterialGenomeError("gc_content must be in [0, 1]")
        if not isinstance(self.plasmid_count, int) or self.plasmid_count < 0:
            raise BacterialGenomeError("plasmid_count must be non-negative int")

    def is_mdr_candidate(self, threshold: int = 3) -> bool:
        return len(self.amr_genes) >= threshold


class BacterialGenomeAnalyzer:
    """Bacterial genome registry with AMR and virulence queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, BacterialGenomeProfile] = {}
        self._species_index: Dict[str, List[str]] = {}
        self._amr_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, profile: BacterialGenomeProfile) -> BacterialGenomeProfile:
        if profile.profile_id in self._profiles:
            raise BacterialGenomeError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        self._species_index.setdefault(profile.species, []).append(profile.profile_id)
        for g in profile.amr_genes:
            self._amr_index.setdefault(g, []).append(profile.profile_id)
        for did in profile.disease_ids:
            self._disease_index.setdefault(did, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> BacterialGenomeProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise BacterialGenomeError(f"unknown profile_id: {profile_id}") from exc

    def by_species(self, species: str) -> List[BacterialGenomeProfile]:
        return [self.get(pid) for pid in self._species_index.get(species, [])]

    def by_gram(self, gram: str) -> List[BacterialGenomeProfile]:
        if gram not in GRAM_STAIN:
            raise BacterialGenomeError(f"invalid gram_stain: {gram!r}")
        return [p for p in self._profiles.values() if p.gram_stain == gram]

    def by_amr_gene(self, gene: str) -> List[BacterialGenomeProfile]:
        return [self.get(pid) for pid in self._amr_index.get(gene, [])]

    def for_disease(self, disease_id: str) -> List[BacterialGenomeProfile]:
        return [self.get(pid) for pid in self._disease_index.get(disease_id, [])]

    def mdr_candidates(self, threshold: int = 3) -> List[BacterialGenomeProfile]:
        return [p for p in self._profiles.values() if p.is_mdr_candidate(threshold)]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "species": len(self._species_index),
            "amr_genes": len(self._amr_index),
            "mdr": len(self.mdr_candidates()),
        }


def self_test() -> bool:
    analyzer = BacterialGenomeAnalyzer()
    analyzer.add(BacterialGenomeProfile(
        "B1", "Escherichia coli", "K-12",
        genome_size_mb=4.6, gc_content=0.51, plasmid_count=1,
        gram_stain="negative",
        amr_genes=["blaTEM", "tetA"],
        virulence_factors=["fimbriae"],
        disease_ids=["D_uti"]))
    analyzer.add(BacterialGenomeProfile(
        "B2", "Klebsiella pneumoniae", "ST258",
        genome_size_mb=5.5, gc_content=0.57, plasmid_count=3,
        gram_stain="negative",
        amr_genes=["KPC", "NDM", "CTX-M", "aac6"],
        disease_ids=["D_hnf"]))
    assert analyzer.by_species("Escherichia coli")[0].profile_id == "B1"
    assert len(analyzer.by_gram("negative")) == 2
    assert analyzer.by_amr_gene("KPC")[0].profile_id == "B2"
    assert analyzer.for_disease("D_uti")[0].profile_id == "B1"
    assert len(analyzer.mdr_candidates(3)) == 1
    print("bacterial_genome_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
