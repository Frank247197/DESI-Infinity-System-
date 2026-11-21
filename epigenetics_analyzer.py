"""DESI Infinity System - Epigenetics Analyzer (v6.2.0).

Models epigenetic marks (DNA methylation, histone modifications,
chromatin accessibility) with genomic localization and gene linkage.
Research-only annotations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MARK_TYPES = ("dna_methylation", "h3k4me3", "h3k4me1", "h3k27ac",
              "h3k27me3", "h3k9me3", "h3k36me3", "atac", "other")
REGIONS = ("promoter", "enhancer", "gene_body", "intergenic", "cgi",
           "repeat", "unknown")
EFFECTS = ("activating", "repressive", "poised", "unknown")
SOURCES = ("curated", "literature", "predicted")


class EpigeneticsError(Exception):
    """Base epigenetics error."""


@dataclass
class EpigeneticMark:
    mark_id: str
    mark_type: str
    chromosome: str
    start: int
    end: int
    region: str = "unknown"
    effect: str = "unknown"
    associated_genes: List[str] = field(default_factory=list)
    tissue: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mark_id or not isinstance(self.mark_id, str):
            raise EpigeneticsError("mark_id required")
        if self.mark_type not in MARK_TYPES:
            raise EpigeneticsError(f"invalid mark_type: {self.mark_type!r}")
        if self.region not in REGIONS:
            raise EpigeneticsError(f"invalid region: {self.region!r}")
        if self.effect not in EFFECTS:
            raise EpigeneticsError(f"invalid effect: {self.effect!r}")
        if self.source not in SOURCES:
            raise EpigeneticsError(f"invalid source: {self.source!r}")
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise EpigeneticsError("start and end must be ints")
        if self.start < 0 or self.end <= self.start:
            raise EpigeneticsError("require 0 <= start < end")

    def length(self) -> int:
        return self.end - self.start


class EpigeneticsAnalyzer:
    """Mark store with mark-type / gene / region queries."""

    def __init__(self) -> None:
        self._marks: Dict[str, EpigeneticMark] = {}
        self._type_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, mark: EpigeneticMark) -> EpigeneticMark:
        if mark.mark_id in self._marks:
            raise EpigeneticsError(f"duplicate mark_id: {mark.mark_id}")
        self._marks[mark.mark_id] = mark
        self._type_index.setdefault(mark.mark_type, []).append(mark.mark_id)
        for g in mark.associated_genes:
            self._gene_index.setdefault(g, []).append(mark.mark_id)
        return mark

    def get(self, mark_id: str) -> EpigeneticMark:
        try:
            return self._marks[mark_id]
        except KeyError as exc:
            raise EpigeneticsError(f"unknown mark_id: {mark_id}") from exc

    def by_type(self, mark_type: str) -> List[EpigeneticMark]:
        if mark_type not in MARK_TYPES:
            raise EpigeneticsError(f"invalid mark_type: {mark_type!r}")
        return [self.get(mid) for mid in self._type_index.get(mark_type, [])]

    def for_gene(self, gene_symbol: str) -> List[EpigeneticMark]:
        return [self.get(mid) for mid in self._gene_index.get(gene_symbol, [])]

    def activating_marks(self, gene_symbol: str) -> List[EpigeneticMark]:
        return [m for m in self.for_gene(gene_symbol) if m.effect == "activating"]

    def repressive_marks(self, gene_symbol: str) -> List[EpigeneticMark]:
        return [m for m in self.for_gene(gene_symbol) if m.effect == "repressive"]

    def by_region(self, region: str) -> List[EpigeneticMark]:
        if region not in REGIONS:
            raise EpigeneticsError(f"invalid region: {region!r}")
        return [m for m in self._marks.values() if m.region == region]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "marks": len(self._marks),
            "mark_types": len(self._type_index),
            "genes": len(self._gene_index),
        }


def self_test() -> bool:
    analyzer = EpigeneticsAnalyzer()
    analyzer.add(EpigeneticMark(
        "E1", "h3k4me3", "1", 1000, 2000, "promoter", "activating",
        ["GENE_A"], "liver"))
    analyzer.add(EpigeneticMark(
        "E2", "h3k27ac", "1", 1500, 2500, "enhancer", "activating",
        ["GENE_A"], "liver"))
    analyzer.add(EpigeneticMark(
        "E3", "dna_methylation", "1", 1000, 1200, "promoter", "repressive",
        ["GENE_B"], "liver"))
    assert len(analyzer.by_type("h3k4me3")) == 1
    assert len(analyzer.for_gene("GENE_A")) == 2
    assert len(analyzer.activating_marks("GENE_A")) == 2
    assert len(analyzer.repressive_marks("GENE_B")) == 1
    assert len(analyzer.by_region("promoter")) == 2
    print("epigenetics_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
