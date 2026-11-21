"""DESI Infinity System - Genome Sequence Processor (v6.2.0).

Sequence processing utilities: normalization, k-mer counting, GC content,
reverse complement, and origin tagging. Origin tag is mandatory so
pathogen/human EV/human sequences remain distinguishable.
"""
from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

VALID_NT = set("ACGTUNacgtun")
ORIGINS = ("human", "pathogen", "ev_element", "environmental", "unknown")
COMPLEMENT = {"A": "T", "T": "A", "C": "G", "G": "C",
              "U": "A", "a": "t", "t": "a", "c": "g", "g": "c", "u": "a",
              "N": "N", "n": "n"}


class SequenceProcessingError(Exception):
    """Base sequence processing error."""


@dataclass
class SequenceRecord:
    sequence_id: str
    sequence: str
    origin: str = "unknown"
    description: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.sequence_id or not isinstance(self.sequence_id, str):
            raise SequenceProcessingError("sequence_id required")
        if not self.sequence or not isinstance(self.sequence, str):
            raise SequenceProcessingError("sequence required")
        invalid = set(self.sequence) - VALID_NT
        if invalid:
            raise SequenceProcessingError(f"invalid nucleotides: {sorted(invalid)}")
        if self.origin not in ORIGINS:
            raise SequenceProcessingError(f"invalid origin: {self.origin!r}")

    def normalize(self) -> str:
        return self.sequence.upper().replace("U", "T")

    def gc_content(self) -> float:
        s = self.normalize()
        if not s:
            return 0.0
        return round((s.count("G") + s.count("C")) / len(s), 4)

    def reverse_complement(self) -> str:
        try:
            return "".join(COMPLEMENT[b] for b in reversed(self.sequence))
        except KeyError as exc:
            raise SequenceProcessingError(
                f"cannot complement base: {exc.args[0]!r}") from exc

    def kmer_profile(self, k: int = 4) -> Dict[str, int]:
        s = self.normalize()
        if k <= 0 or k > len(s):
            raise SequenceProcessingError(f"k must be in [1, {len(s)}]")
        counts = Counter(s[i:i + k] for i in range(len(s) - k + 1))
        return dict(counts.most_common())


class GenomeSequenceProcessor:
    """Sequence store with motif search and origin-filtered batch ops."""

    def __init__(self) -> None:
        self._records: Dict[str, SequenceRecord] = {}

    def add(self, record: SequenceRecord) -> SequenceRecord:
        if record.sequence_id in self._records:
            raise SequenceProcessingError(
                f"duplicate sequence_id: {record.sequence_id}")
        self._records[record.sequence_id] = record
        return record

    def get(self, sequence_id: str) -> SequenceRecord:
        try:
            return self._records[sequence_id]
        except KeyError as exc:
            raise SequenceProcessingError(f"unknown sequence_id: {sequence_id}") from exc

    def by_origin(self, origin: str) -> List[SequenceRecord]:
        if origin not in ORIGINS:
            raise SequenceProcessingError(f"invalid origin: {origin!r}")
        return [r for r in self._records.values() if r.origin == origin]

    def find_motif(self, motif: str, origin: str = None) -> List[SequenceRecord]:
        if not motif or not isinstance(motif, str):
            raise SequenceProcessingError("motif required")
        m = motif.upper().replace("U", "T")
        pool = self.by_origin(origin) if origin else list(self._records.values())
        return [r for r in pool if m in r.normalize()]

    def gc_outliers(self, low: float = 0.3, high: float = 0.7) -> Dict[str, List[str]]:
        low_ids = [r.sequence_id for r in self._records.values() if r.gc_content() < low]
        high_ids = [r.sequence_id for r in self._records.values() if r.gc_content() > high]
        return {"low": sorted(low_ids), "high": sorted(high_ids)}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "human": len(self.by_origin("human")),
            "pathogen": len(self.by_origin("pathogen")),
            "ev": len(self.by_origin("ev_element")),
        }


def self_test() -> bool:
    proc = GenomeSequenceProcessor()
    proc.add(SequenceRecord("S1", "ATGCGTACGTAGCTAUG", origin="pathogen"))
    proc.add(SequenceRecord("S2", "GCGCGCGCGCGCGCGC", origin="human"))
    proc.add(SequenceRecord("S3", "ATATATATATATATAT", origin="ev_element"))
    assert proc.get("S1").normalize() == "ATGCGTACGTAGCTAT"
    assert proc.get("S2").gc_content() == 1.0
    assert proc.get("S1").reverse_complement()[:3] == "CAT"
    assert len(proc.by_origin("human")) == 1
    assert proc.find_motif("ATGC")[0].sequence_id == "S1"
    outliers = proc.gc_outliers(0.3, 0.7)
    assert "S2" in outliers["high"] and "S3" in outliers["low"]
    assert proc.stats()["ev"] == 1
    print("genome_sequence_processor: OK")
    return True


if __name__ == "__main__":
    self_test()
