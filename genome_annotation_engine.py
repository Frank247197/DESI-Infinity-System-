"""DESI Infinity System - Genome Annotation Engine (v6.2.0).

Structured annotation of genomic features: genes, transcripts, regulatory
elements, repeats. Enforces chromosome, coordinate ordering, and strand
validation. All coordinates are 0-based half-open.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FEATURE_TYPES = ("gene", "transcript", "exon", "cds", "promoter",
                 "enhancer", "silencer", "utr", "repeat", "ev_element",
                 "regulatory", "other")
STRANDS = ("+", "-", ".")
SOURCES = ("curated", "literature", "predicted")


class GenomeAnnotationError(Exception):
    """Base annotation error."""


@dataclass
class GenomeFeature:
    feature_id: str
    chromosome: str
    start: int
    end: int
    feature_type: str
    strand: str = "."
    label: str = ""
    parent_id: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.feature_id or not isinstance(self.feature_id, str):
            raise GenomeAnnotationError("feature_id required")
        if not self.chromosome or not isinstance(self.chromosome, str):
            raise GenomeAnnotationError("chromosome required")
        if not isinstance(self.start, int) or not isinstance(self.end, int):
            raise GenomeAnnotationError("start and end must be ints")
        if self.start < 0 or self.end <= self.start:
            raise GenomeAnnotationError("require 0 <= start < end")
        if self.feature_type not in FEATURE_TYPES:
            raise GenomeAnnotationError(f"invalid feature_type: {self.feature_type!r}")
        if self.strand not in STRANDS:
            raise GenomeAnnotationError(f"invalid strand: {self.strand!r}")
        if self.source not in SOURCES:
            raise GenomeAnnotationError(f"invalid source: {self.source!r}")

    def length(self) -> int:
        return self.end - self.start

    def overlaps(self, other: "GenomeFeature") -> bool:
        if self.chromosome != other.chromosome:
            return False
        return self.start < other.end and other.start < self.end

    def contains_position(self, pos: int) -> bool:
        return self.start <= pos < self.end


class GenomeAnnotationEngine:
    """Annotation store with overlap, containment, and interval queries."""

    def __init__(self) -> None:
        self._features: Dict[str, GenomeFeature] = {}
        self._chrom_index: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}

    def add(self, feature: GenomeFeature) -> GenomeFeature:
        if feature.feature_id in self._features:
            raise GenomeAnnotationError(f"duplicate feature_id: {feature.feature_id}")
        self._features[feature.feature_id] = feature
        self._chrom_index.setdefault(feature.chromosome, []).append(feature.feature_id)
        self._type_index.setdefault(feature.feature_type, []).append(feature.feature_id)
        return feature

    def get(self, feature_id: str) -> GenomeFeature:
        try:
            return self._features[feature_id]
        except KeyError as exc:
            raise GenomeAnnotationError(f"unknown feature_id: {feature_id}") from exc

    def by_chromosome(self, chromosome: str) -> List[GenomeFeature]:
        return [self.get(fid) for fid in self._chrom_index.get(chromosome, [])]

    def by_type(self, feature_type: str) -> List[GenomeFeature]:
        if feature_type not in FEATURE_TYPES:
            raise GenomeAnnotationError(f"invalid feature_type: {feature_type!r}")
        return [self.get(fid) for fid in self._type_index.get(feature_type, [])]

    def overlaps(self, feature_id: str) -> List[GenomeFeature]:
        target = self.get(feature_id)
        return [f for f in self._features.values()
                if f.feature_id != feature_id and target.overlaps(f)]

    def features_at(self, chromosome: str, position: int) -> List[GenomeFeature]:
        return [f for f in self.by_chromosome(chromosome)
                if f.contains_position(position)]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "features": len(self._features),
            "chromosomes": len(self._chrom_index),
            "types": len(self._type_index),
        }


def self_test() -> bool:
    engine = GenomeAnnotationEngine()
    engine.add(GenomeFeature("F1", "1", 1000, 5000, "gene", "+", "GENE_A"))
    engine.add(GenomeFeature("F2", "1", 2000, 2500, "exon", "+",
                             "GENE_A exon 1", parent_id="F1"))
    engine.add(GenomeFeature("F3", "1", 1800, 2100, "promoter", "+",
                             "GENE_A promoter", parent_id="F1"))
    engine.add(GenomeFeature("F4", "2", 100, 200, "enhancer", "."))
    assert engine.get("F1").length() == 4000
    assert len(engine.overlaps("F2")) == 2
    assert engine.features_at("1", 2050)[0].feature_id in {"F1", "F2"}
    assert len(engine.by_type("exon")) == 1
    assert engine.stats()["features"] == 4
    print("genome_annotation_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
