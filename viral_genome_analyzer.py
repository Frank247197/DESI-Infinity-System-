"""DESI Infinity System - Viral Genome Analyzer (v6.2.0).

Analyzes viral genome composition (GC content, coding density, ORF count,
segmentation). Requires explicit sequence_origin; human EV sequences are
annotated as such, never as active viral genomes.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

NUCLEOTIDES = set("ACGTUNacgtun")
SEQUENCE_ORIGINS = ("pathogen_genome", "human_endogenous_viral_element",
                    "human_sequence", "environmental", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ViralGenomeError(Exception):
    """Base viral genome error."""


@dataclass
class ViralGenomeProfile:
    profile_id: str
    virus_id: str
    sequence: str
    sequence_origin: str = "pathogen_genome"
    orf_count: int = 0
    segmented: bool = False
    segment_count: int = 1
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise ViralGenomeError("profile_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise ViralGenomeError("virus_id required")
        if not self.sequence:
            raise ViralGenomeError("sequence required")
        invalid = set(self.sequence) - NUCLEOTIDES
        if invalid:
            raise ViralGenomeError(f"invalid nucleotide characters: {sorted(invalid)}")
        if self.sequence_origin not in SEQUENCE_ORIGINS:
            raise ViralGenomeError(f"invalid sequence_origin: {self.sequence_origin!r}")
        if self.source not in SOURCES:
            raise ViralGenomeError(f"invalid source: {self.source!r}")
        if not isinstance(self.orf_count, int) or self.orf_count < 0:
            raise ViralGenomeError("orf_count must be non-negative int")
        if self.segmented and self.segment_count < 2:
            raise ViralGenomeError("segmented genomes require segment_count >= 2")

    def gc_content(self) -> float:
        s = self.sequence.upper().replace("U", "T")
        if not s:
            return 0.0
        gc = s.count("G") + s.count("C")
        return round(gc / len(s), 4)

    def length_nt(self) -> int:
        return len(self.sequence)

    def coding_density(self) -> float:
        if self.length_nt() == 0 or self.orf_count == 0:
            return 0.0
        avg_orf_nt = 300
        return round(min(1.0, (self.orf_count * avg_orf_nt) / self.length_nt()), 4)

    def is_active_virus(self) -> bool:
        return self.sequence_origin == "pathogen_genome"


class ViralGenomeAnalyzer:
    """Genome profile registry with compositional analyses."""

    def __init__(self) -> None:
        self._profiles: Dict[str, ViralGenomeProfile] = {}
        self._by_virus: Dict[str, List[str]] = {}

    def add(self, profile: ViralGenomeProfile) -> ViralGenomeProfile:
        if profile.profile_id in self._profiles:
            raise ViralGenomeError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        self._by_virus.setdefault(profile.virus_id, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> ViralGenomeProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise ViralGenomeError(f"unknown profile_id: {profile_id}") from exc

    def for_virus(self, virus_id: str) -> List[ViralGenomeProfile]:
        return [self.get(pid) for pid in self._by_virus.get(virus_id, [])]

    def high_gc(self, threshold: float = 0.5) -> List[ViralGenomeProfile]:
        return [p for p in self._profiles.values() if p.gc_content() >= threshold]

    def low_gc(self, threshold: float = 0.4) -> List[ViralGenomeProfile]:
        return [p for p in self._profiles.values() if p.gc_content() < threshold]

    def segmented_genomes(self) -> List[ViralGenomeProfile]:
        return [p for p in self._profiles.values() if p.segmented]

    def human_ev(self) -> List[ViralGenomeProfile]:
        return [p for p in self._profiles.values()
                if p.sequence_origin == "human_endogenous_viral_element"]

    def compare_gc(self, a_id: str, b_id: str) -> Dict[str, float]:
        a = self.get(a_id).gc_content()
        b = self.get(b_id).gc_content()
        return {"profile_a": a, "profile_b": b, "delta": round(a - b, 4)}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "viruses": len(self._by_virus),
            "ev_elements": len(self.human_ev()),
        }


def self_test() -> bool:
    analyzer = ViralGenomeAnalyzer()
    analyzer.add(ViralGenomeProfile(
        "G1", "NCBITaxon:11320",
        "ACGTACGTACGTACGTACGTACGTACGTACGT",
        sequence_origin="pathogen_genome",
        orf_count=12, segmented=True, segment_count=8))
    analyzer.add(ViralGenomeProfile(
        "G2", "NCBITaxon:2697049",
        "GCGCGCGCGCGCGCGC",
        sequence_origin="pathogen_genome", orf_count=10))
    assert 0.0 <= analyzer.get("G1").gc_content() <= 1.0
    assert analyzer.get("G2").gc_content() == 1.0
    assert len(analyzer.high_gc(0.5)) == 1
    assert len(analyzer.segmented_genomes()) == 1
    assert analyzer.compare_gc("G1", "G2")["delta"] < 0
    print("viral_genome_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
