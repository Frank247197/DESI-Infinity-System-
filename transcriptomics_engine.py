"""DESI Infinity System - Transcriptomics Engine (v6.2.0).

Transcript-level quantification store: isoforms, splicing patterns, and
differential transcript usage. Supports gene-level roll-ups. Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

SPLICE_TYPES = ("constitutive", "alternative", "cryptic", "retained_intron",
                "skipped_exon", "unknown")
CONDITIONS = ("normal", "tumor", "disease", "treated", "untreated", "other")
SOURCES = ("curated", "literature", "predicted")


class TranscriptomicsError(Exception):
    """Base transcriptomics error."""


@dataclass
class TranscriptMeasurement:
    transcript_id: str
    gene_symbol: str
    tissue: str
    condition: str
    tpm: Optional[float] = None
    splice_type: str = "unknown"
    is_canonical: bool = False
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.transcript_id or not isinstance(self.transcript_id, str):
            raise TranscriptomicsError("transcript_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise TranscriptomicsError("gene_symbol required")
        if self.condition not in CONDITIONS:
            raise TranscriptomicsError(f"invalid condition: {self.condition!r}")
        if self.splice_type not in SPLICE_TYPES:
            raise TranscriptomicsError(f"invalid splice_type: {self.splice_type!r}")
        if self.source not in SOURCES:
            raise TranscriptomicsError(f"invalid source: {self.source!r}")
        if self.tpm is not None and (not isinstance(self.tpm, (int, float)) or self.tpm < 0):
            raise TranscriptomicsError("tpm must be non-negative numeric or None")


class TranscriptomicsEngine:
    """Transcript store with isoform and gene roll-up analyses."""

    def __init__(self) -> None:
        self._transcripts: Dict[str, TranscriptMeasurement] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, m: TranscriptMeasurement) -> TranscriptMeasurement:
        if m.transcript_id in self._transcripts:
            raise TranscriptomicsError(f"duplicate transcript_id: {m.transcript_id}")
        self._transcripts[m.transcript_id] = m
        self._gene_index.setdefault(m.gene_symbol, []).append(m.transcript_id)
        return m

    def get(self, transcript_id: str) -> TranscriptMeasurement:
        try:
            return self._transcripts[transcript_id]
        except KeyError as exc:
            raise TranscriptomicsError(
                f"unknown transcript_id: {transcript_id}") from exc

    def for_gene(self, gene_symbol: str) -> List[TranscriptMeasurement]:
        return [self.get(tid) for tid in self._gene_index.get(gene_symbol, [])]

    def canonical_transcripts(self, gene_symbol: str) -> List[TranscriptMeasurement]:
        return [m for m in self.for_gene(gene_symbol) if m.is_canonical]

    def by_splice_type(self, splice_type: str) -> List[TranscriptMeasurement]:
        if splice_type not in SPLICE_TYPES:
            raise TranscriptomicsError(f"invalid splice_type: {splice_type!r}")
        return [m for m in self._transcripts.values() if m.splice_type == splice_type]

    def gene_tpm(self, gene_symbol: str, condition: str = None) -> float:
        total = 0.0
        for m in self.for_gene(gene_symbol):
            if condition is not None and m.condition != condition:
                continue
            if m.tpm is not None:
                total += m.tpm
        return round(total, 3)

    def isoform_switch_candidates(self, gene_symbol: str) -> List[str]:
        """Canonical isoform under `normal` absent under `tumor`/`disease`."""
        by_cond: Dict[str, List[TranscriptMeasurement]] = {}
        for m in self.for_gene(gene_symbol):
            by_cond.setdefault(m.condition, []).append(m)
        switches: List[str] = []
        normals = {m.transcript_id for m in by_cond.get("normal", []) if m.is_canonical}
        for other_cond, recs in by_cond.items():
            if other_cond == "normal":
                continue
            present = {m.transcript_id for m in recs}
            if normals and not (normals & present):
                switches.append(other_cond)
        return sorted(switches)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "transcripts": len(self._transcripts),
            "genes": len(self._gene_index),
            "canonical": sum(1 for m in self._transcripts.values() if m.is_canonical),
        }


def self_test() -> bool:
    engine = TranscriptomicsEngine()
    engine.add(TranscriptMeasurement(
        "T1", "GENE_A", "liver", "normal", tpm=50.0,
        splice_type="constitutive", is_canonical=True))
    engine.add(TranscriptMeasurement(
        "T2", "GENE_A", "liver", "tumor", tpm=30.0,
        splice_type="alternative", is_canonical=False))
    engine.add(TranscriptMeasurement(
        "T3", "GENE_A", "liver", "tumor", tpm=20.0,
        splice_type="retained_intron", is_canonical=False))
    assert len(engine.for_gene("GENE_A")) == 3
    assert len(engine.canonical_transcripts("GENE_A")) == 1
    assert engine.gene_tpm("GENE_A") == 100.0
    assert engine.gene_tpm("GENE_A", "tumor") == 50.0
    assert engine.by_splice_type("alternative")[0].transcript_id == "T2"
    assert engine.isoform_switch_candidates("GENE_A") == ["tumor"]
    print("transcriptomics_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
