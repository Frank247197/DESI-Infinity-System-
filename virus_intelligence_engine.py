"""DESI Infinity System - Virus Intelligence Engine (v6.2.0).

Central intelligence for viruses: Baltimore classification, genome type,
host range, and explicit sequence origin (pathogen vs human EV).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

BALTIMORE = ("I", "II", "III", "IV", "V", "VI", "VII", "unclassified")
GENOME_TYPES = ("dsDNA", "ssDNA", "dsRNA", "positive_ssRNA",
                "negative_ssRNA", "retrovirus", "unknown")
ENVELOPE = ("enveloped", "non_enveloped", "unknown")
SEQUENCE_ORIGINS = ("pathogen_genome", "human_endogenous_viral_element",
                    "human_sequence", "environmental", "unknown")
SOURCES = ("curated", "literature", "predicted")


class VirusIntelligenceError(Exception):
    """Base virus intelligence error."""


@dataclass
class VirusRecord:
    virus_id: str
    name: str
    family: str = "unknown"
    genus: str = "unknown"
    baltimore_class: str = "unclassified"
    genome_type: str = "unknown"
    envelope: str = "unknown"
    genome_size_kb: float = 0.0
    sequence_origin: str = "pathogen_genome"
    host_range: List[str] = field(default_factory=list)
    tissue_tropism: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise VirusIntelligenceError("virus_id required")
        if not self.name or not isinstance(self.name, str):
            raise VirusIntelligenceError("name required")
        if self.baltimore_class not in BALTIMORE:
            raise VirusIntelligenceError(f"invalid baltimore_class: {self.baltimore_class!r}")
        if self.genome_type not in GENOME_TYPES:
            raise VirusIntelligenceError(f"invalid genome_type: {self.genome_type!r}")
        if self.envelope not in ENVELOPE:
            raise VirusIntelligenceError(f"invalid envelope: {self.envelope!r}")
        if self.sequence_origin not in SEQUENCE_ORIGINS:
            raise VirusIntelligenceError(f"invalid sequence_origin: {self.sequence_origin!r}")
        if self.source not in SOURCES:
            raise VirusIntelligenceError(f"invalid source: {self.source!r}")
        if not isinstance(self.genome_size_kb, (int, float)) or self.genome_size_kb < 0:
            raise VirusIntelligenceError("genome_size_kb must be non-negative numeric")

    def is_active_virus(self) -> bool:
        return self.sequence_origin == "pathogen_genome"

    def is_human_ev(self) -> bool:
        return self.sequence_origin == "human_endogenous_viral_element"


class VirusIntelligenceEngine:
    """Virus registry with taxonomy and host-range queries."""

    def __init__(self) -> None:
        self._viruses: Dict[str, VirusRecord] = {}
        self._family_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, record: VirusRecord) -> VirusRecord:
        if record.virus_id in self._viruses:
            raise VirusIntelligenceError(f"duplicate virus_id: {record.virus_id}")
        self._viruses[record.virus_id] = record
        self._family_index.setdefault(record.family, []).append(record.virus_id)
        for did in record.disease_ids:
            self._disease_index.setdefault(did, []).append(record.virus_id)
        return record

    def get(self, virus_id: str) -> VirusRecord:
        try:
            return self._viruses[virus_id]
        except KeyError as exc:
            raise VirusIntelligenceError(f"unknown virus_id: {virus_id}") from exc

    def by_family(self, family: str) -> List[VirusRecord]:
        return [self.get(vid) for vid in self._family_index.get(family, [])]

    def by_baltimore(self, baltimore: str) -> List[VirusRecord]:
        if baltimore not in BALTIMORE:
            raise VirusIntelligenceError(f"invalid baltimore_class: {baltimore!r}")
        return [v for v in self._viruses.values() if v.baltimore_class == baltimore]

    def by_genome_type(self, genome_type: str) -> List[VirusRecord]:
        if genome_type not in GENOME_TYPES:
            raise VirusIntelligenceError(f"invalid genome_type: {genome_type!r}")
        return [v for v in self._viruses.values() if v.genome_type == genome_type]

    def for_disease(self, disease_id: str) -> List[VirusRecord]:
        return [self.get(vid) for vid in self._disease_index.get(disease_id, [])]

    def active_viruses(self) -> List[VirusRecord]:
        return [v for v in self._viruses.values() if v.is_active_virus()]

    def human_ev(self) -> List[VirusRecord]:
        return [v for v in self._viruses.values() if v.is_human_ev()]

    def by_tropism(self, tissue: str) -> List[VirusRecord]:
        return [v for v in self._viruses.values() if tissue in v.tissue_tropism]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "viruses": len(self._viruses),
            "active": len(self.active_viruses()),
            "ev_elements": len(self.human_ev()),
            "families": len(self._family_index),
        }


def self_test() -> bool:
    engine = VirusIntelligenceEngine()
    engine.add(VirusRecord(
        "NCBITaxon:11320", "Influenza A", "Orthomyxoviridae",
        "Alphainfluenzavirus", "V", "negative_ssRNA", "enveloped",
        13.5, "pathogen_genome", ["human", "avian"],
        ["respiratory_epithelium"], ["D_flu"]))
    engine.add(VirusRecord(
        "EV:HERVK", "HERV-K", "Retroviridae", "Betaretrovirus",
        "VI", "retrovirus", "enveloped", 9.5,
        "human_endogenous_viral_element", ["human"], [], []))
    assert engine.by_family("Orthomyxoviridae")[0].virus_id == "NCBITaxon:11320"
    assert len(engine.by_baltimore("V")) == 1
    assert engine.for_disease("D_flu")[0].name == "Influenza A"
    assert len(engine.active_viruses()) == 1
    assert len(engine.human_ev()) == 1
    assert len(engine.by_tropism("respiratory_epithelium")) == 1
    print("virus_intelligence_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
