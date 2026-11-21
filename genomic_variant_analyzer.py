"""DESI Infinity System - Genomic Variant Analyzer (v6.2.0).

Analyzes genomic variants with strict separation of human, pathogen, and
endogenous viral element contexts. Provides population frequency queries
and co-occurrence analysis without clinical interpretation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CONTEXTS = ("human", "pathogen", "ev_element", "unknown")
VARIANT_CLASSES = ("SNV", "MNV", "indel", "CNV", "SV", "other")
SOURCES = ("curated", "literature", "predicted")


class GenomicVariantError(Exception):
    """Base genomic variant error."""


@dataclass
class GenomicVariant:
    variant_id: str
    genome_context: str
    variant_class: str
    chromosome: str = ""
    position: Optional[int] = None
    gene_symbol: str = ""
    population_frequency: Optional[float] = None
    populations: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.variant_id or not isinstance(self.variant_id, str):
            raise GenomicVariantError("variant_id required")
        if self.genome_context not in CONTEXTS:
            raise GenomicVariantError(f"invalid genome_context: {self.genome_context!r}")
        if self.variant_class not in VARIANT_CLASSES:
            raise GenomicVariantError(f"invalid variant_class: {self.variant_class!r}")
        if self.source not in SOURCES:
            raise GenomicVariantError(f"invalid source: {self.source!r}")
        if self.position is not None:
            if not isinstance(self.position, int) or self.position <= 0:
                raise GenomicVariantError("position must be a positive int or None")
        if self.population_frequency is not None:
            if not isinstance(self.population_frequency, (int, float)):
                raise GenomicVariantError("population_frequency must be numeric or None")
            if not 0.0 <= float(self.population_frequency) <= 1.0:
                raise GenomicVariantError("population_frequency must be in [0, 1]")


class GenomicVariantAnalyzer:
    """Variant store with strict context-separated queries."""

    def __init__(self) -> None:
        self._variants: Dict[str, GenomicVariant] = {}
        self._gene_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._population_index: Dict[str, List[str]] = {}

    def add(self, variant: GenomicVariant) -> GenomicVariant:
        if variant.variant_id in self._variants:
            raise GenomicVariantError(f"duplicate variant_id: {variant.variant_id}")
        self._variants[variant.variant_id] = variant
        if variant.gene_symbol:
            self._gene_index.setdefault(variant.gene_symbol, []).append(variant.variant_id)
        for did in variant.disease_ids:
            self._disease_index.setdefault(did, []).append(variant.variant_id)
        for pop in variant.populations:
            self._population_index.setdefault(pop, []).append(variant.variant_id)
        return variant

    def get(self, variant_id: str) -> GenomicVariant:
        try:
            return self._variants[variant_id]
        except KeyError as exc:
            raise GenomicVariantError(f"unknown variant_id: {variant_id}") from exc

    def by_context(self, context: str) -> List[GenomicVariant]:
        if context not in CONTEXTS:
            raise GenomicVariantError(f"invalid genome_context: {context!r}")
        return [v for v in self._variants.values() if v.genome_context == context]

    def by_gene(self, gene_symbol: str) -> List[GenomicVariant]:
        return [self.get(vid) for vid in self._gene_index.get(gene_symbol, [])]

    def for_disease(self, disease_id: str) -> List[GenomicVariant]:
        return [self.get(vid) for vid in self._disease_index.get(disease_id, [])]

    def human_disease_variants(self, disease_id: str) -> List[GenomicVariant]:
        return [v for v in self.for_disease(disease_id) if v.genome_context == "human"]

    def common_variants(self, threshold: float = 0.01) -> List[GenomicVariant]:
        return [v for v in self._variants.values()
                if v.population_frequency is not None
                and v.population_frequency >= threshold]

    def rare_variants(self, threshold: float = 0.01) -> List[GenomicVariant]:
        return [v for v in self._variants.values()
                if v.population_frequency is not None
                and v.population_frequency < threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "variants": len(self._variants),
            "human": len(self.by_context("human")),
            "pathogen": len(self.by_context("pathogen")),
            "ev_element": len(self.by_context("ev_element")),
            "common": len(self.common_variants()),
        }


def self_test() -> bool:
    analyzer = GenomicVariantAnalyzer()
    analyzer.add(GenomicVariant(
        "V1", "human", "SNV", "17", 7676154, "TP53",
        population_frequency=0.002,
        populations=["EUR", "AFR"], disease_ids=["D_cancer"]))
    analyzer.add(GenomicVariant(
        "V2", "human", "SNV", "1", 1000, "GENE_X",
        population_frequency=0.05, populations=["AFR"]))
    analyzer.add(GenomicVariant(
        "V3", "pathogen", "SNV", gene_symbol="S",
        disease_ids=["D_covid19"]))
    analyzer.add(GenomicVariant(
        "V4", "ev_element", "indel"))
    assert len(analyzer.by_context("human")) == 2
    assert analyzer.by_gene("TP53")[0].variant_id == "V1"
    assert analyzer.human_disease_variants("D_cancer")[0].variant_id == "V1"
    assert len(analyzer.common_variants(0.01)) == 1
    assert len(analyzer.rare_variants(0.01)) == 1
    assert analyzer.stats()["ev_element"] == 1
    print("genomic_variant_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
