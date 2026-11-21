"""DESI Infinity System - Viral Sequence Analyzer (v6.2.0).

Sequence-level analyses: motif search, k-mer profiling, and Shannon
entropy of nucleotide composition. All sequences must declare origin so
human EV sequences are never treated as active viruses.
"""
from __future__ import annotations

import logging
import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

VALID_NT = set("ACGTUNacgtun")
SEQUENCE_ORIGINS = ("pathogen_genome", "human_endogenous_viral_element",
                    "human_sequence", "environmental", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ViralSequenceError(Exception):
    """Base viral sequence error."""


@dataclass
class SequenceAnnotation:
    annotation_id: str
    sequence_id: str
    sequence: str
    sequence_origin: str = "pathogen_genome"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.annotation_id or not isinstance(self.annotation_id, str):
            raise ViralSequenceError("annotation_id required")
        if not self.sequence_id or not isinstance(self.sequence_id, str):
            raise ViralSequenceError("sequence_id required")
        if not self.sequence:
            raise ViralSequenceError("sequence required")
        invalid = set(self.sequence) - VALID_NT
        if invalid:
            raise ViralSequenceError(f"invalid nucleotides: {sorted(invalid)}")
        if self.sequence_origin not in SEQUENCE_ORIGINS:
            raise ViralSequenceError(f"invalid sequence_origin: {self.sequence_origin!r}")
        if self.source not in SOURCES:
            raise ViralSequenceError(f"invalid source: {self.source!r}")

    def length(self) -> int:
        return len(self.sequence)

    def composition(self) -> Dict[str, int]:
        upper = self.sequence.upper().replace("U", "T")
        counts = Counter(upper)
        return {nt: counts.get(nt, 0) for nt in ("A", "C", "G", "T")}

    def kmer_profile(self, k: int = 3) -> Dict[str, int]:
        if k <= 0 or k > self.length():
            raise ViralSequenceError(f"k must be between 1 and {self.length()}")
        upper = self.sequence.upper().replace("U", "T")
        kmers: Dict[str, int] = {}
        for i in range(len(upper) - k + 1):
            km = upper[i:i + k]
            kmers[km] = kmers.get(km, 0) + 1
        return dict(sorted(kmers.items(), key=lambda kv: kv[1], reverse=True))

    def entropy(self) -> float:
        counts = self.composition()
        total = sum(counts.values())
        if total == 0:
            return 0.0
        h = 0.0
        for c in counts.values():
            if c == 0:
                continue
            p = c / total
            h -= p * math.log2(p)
        return round(h, 4)


class ViralSequenceAnalyzer:
    """Registry + search + comparative analyses over viral sequences."""

    def __init__(self) -> None:
        self._annotations: Dict[str, SequenceAnnotation] = {}
        self._by_sequence: Dict[str, List[str]] = {}

    def add(self, annotation: SequenceAnnotation) -> SequenceAnnotation:
        if annotation.annotation_id in self._annotations:
            raise ViralSequenceError(f"duplicate annotation_id: {annotation.annotation_id}")
        self._annotations[annotation.annotation_id] = annotation
        self._by_sequence.setdefault(annotation.sequence_id, []).append(annotation.annotation_id)
        return annotation

    def get(self, annotation_id: str) -> SequenceAnnotation:
        try:
            return self._annotations[annotation_id]
        except KeyError as exc:
            raise ViralSequenceError(f"unknown annotation_id: {annotation_id}") from exc

    def for_sequence(self, sequence_id: str) -> List[SequenceAnnotation]:
        return [self.get(aid) for aid in self._by_sequence.get(sequence_id, [])]

    def search_motif(self, motif: str) -> List[SequenceAnnotation]:
        if not motif or not isinstance(motif, str):
            raise ViralSequenceError("motif required")
        m = motif.upper().replace("U", "T")
        return [a for a in self._annotations.values()
                if m in a.sequence.upper().replace("U", "T")]

    def high_entropy(self, threshold: float = 1.5) -> List[SequenceAnnotation]:
        return [a for a in self._annotations.values() if a.entropy() >= threshold]

    def by_origin(self, origin: str) -> List[SequenceAnnotation]:
        if origin not in SEQUENCE_ORIGINS:
            raise ViralSequenceError(f"invalid origin: {origin!r}")
        return [a for a in self._annotations.values() if a.sequence_origin == origin]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "annotations": len(self._annotations),
            "sequences": len(self._by_sequence),
            "ev_elements": len(self.by_origin("human_endogenous_viral_element")),
        }


def self_test() -> bool:
    analyzer = ViralSequenceAnalyzer()
    analyzer.add(SequenceAnnotation(
        "A1", "SEQ1", "ATGCGTACGTAGCTAGCTAGCTAUG",
        sequence_origin="pathogen_genome"))
    analyzer.add(SequenceAnnotation(
        "A2", "SEQ2", "GGGGCCCCAAAATTTT",
        sequence_origin="human_endogenous_viral_element"))
    assert analyzer.get("A1").length() == 26
    assert analyzer.search_motif("ATGC")[0].annotation_id == "A1"
    prof = analyzer.get("A1").kmer_profile(2)
    assert isinstance(prof, dict) and len(prof) > 0
    assert len(analyzer.high_entropy(1.0)) >= 1
    assert len(analyzer.by_origin("human_endogenous_viral_element")) == 1
    print("viral_sequence_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
