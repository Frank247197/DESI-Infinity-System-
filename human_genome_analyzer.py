"""DESI Infinity System - Human Genome Analyzer (v6.2.0).

Analyzes human genome-level features: chromosome content, gene density,
regulatory region counts. Explicitly distinguishes HUMAN genomic content
from pathogen or endogenous-viral-element origins.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CHROMOSOMES = tuple(str(i) for i in range(1, 23)) + ("X", "Y", "MT")
REGION_TYPES = ("coding", "regulatory", "repeat", "non_coding",
                "endogenous_viral", "other")
SOURCES = ("curated", "literature", "predicted")


class HumanGenomeError(Exception):
    """Base human genome error."""


@dataclass
class ChromosomeProfile:
    chromosome: str
    length_bp: int
    gene_count: int = 0
    coding_region_bp: int = 0
    regulatory_region_count: int = 0
    ev_element_count: int = 0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.chromosome not in CHROMOSOMES:
            raise HumanGenomeError(f"invalid chromosome: {self.chromosome!r}")
        if not isinstance(self.length_bp, int) or self.length_bp <= 0:
            raise HumanGenomeError("length_bp must be positive int")
        if not isinstance(self.gene_count, int) or self.gene_count < 0:
            raise HumanGenomeError("gene_count must be non-negative int")
        if self.coding_region_bp < 0 or self.coding_region_bp > self.length_bp:
            raise HumanGenomeError("coding_region_bp must be within [0, length_bp]")
        if self.source not in SOURCES:
            raise HumanGenomeError(f"invalid source: {self.source!r}")

    def gene_density(self) -> float:
        return round(self.gene_count / self.length_bp * 1_000_000, 4)

    def coding_fraction(self) -> float:
        return round(self.coding_region_bp / self.length_bp, 6)


class HumanGenomeAnalyzer:
    """Per-chromosome registry with density and coding fraction queries."""

    def __init__(self) -> None:
        self._chromosomes: Dict[str, ChromosomeProfile] = {}

    def add(self, profile: ChromosomeProfile) -> ChromosomeProfile:
        if profile.chromosome in self._chromosomes:
            raise HumanGenomeError(f"duplicate chromosome: {profile.chromosome}")
        self._chromosomes[profile.chromosome] = profile
        return profile

    def get(self, chromosome: str) -> ChromosomeProfile:
        try:
            return self._chromosomes[chromosome]
        except KeyError as exc:
            raise HumanGenomeError(f"unknown chromosome: {chromosome}") from exc

    def total_length(self) -> int:
        return sum(p.length_bp for p in self._chromosomes.values())

    def total_genes(self) -> int:
        return sum(p.gene_count for p in self._chromosomes.values())

    def total_ev_elements(self) -> int:
        return sum(p.ev_element_count for p in self._chromosomes.values())

    def highest_gene_density(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise HumanGenomeError("top_n must be positive")
        rows = [{"chromosome": p.chromosome, "gene_density": p.gene_density()}
                for p in self._chromosomes.values()]
        rows.sort(key=lambda r: r["gene_density"], reverse=True)  # type: ignore
        return rows[:top_n]

    def high_ev_chromosomes(self, threshold: int = 100) -> List[ChromosomeProfile]:
        return [p for p in self._chromosomes.values()
                if p.ev_element_count >= threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "chromosomes": len(self._chromosomes),
            "total_length_bp": self.total_length(),
            "total_genes": self.total_genes(),
            "total_ev_elements": self.total_ev_elements(),
        }


def self_test() -> bool:
    analyzer = HumanGenomeAnalyzer()
    analyzer.add(ChromosomeProfile(
        "1", 248_956_422, gene_count=2058,
        coding_region_bp=80_000_000, regulatory_region_count=300_000,
        ev_element_count=250))
    analyzer.add(ChromosomeProfile(
        "21", 46_709_983, gene_count=233,
        coding_region_bp=15_000_000, regulatory_region_count=50_000,
        ev_element_count=80))
    assert analyzer.get("1").gene_density() > analyzer.get("21").gene_density()
    assert analyzer.total_genes() == 2291
    assert analyzer.total_ev_elements() == 330
    top = analyzer.highest_gene_density(1)
    assert top[0]["chromosome"] == "1"
    assert len(analyzer.high_ev_chromosomes(100)) == 1
    print("human_genome_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
