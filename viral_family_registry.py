"""DESI Infinity System - Viral Family Registry (v6.2.0).

Family-level registry of viral families with genome type, envelope
status, host kingdom ranges, and representative genera. Research data
only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

GENOME_TYPES = ("dsDNA", "ssDNA", "dsRNA", "positive_ssRNA",
                "negative_ssRNA", "reverse_transcribing", "unknown")
ENVELOPE = ("enveloped", "non_enveloped", "unknown")
HOST_KINGDOMS = ("animalia", "plantae", "fungi", "bacteria", "archaea",
                 "protista", "unknown")
SOURCES = ("curated", "literature", "predicted")


class ViralFamilyError(Exception):
    """Base viral family error."""


@dataclass
class ViralFamily:
    family_id: str
    name: str
    genome_type: str = "unknown"
    envelope: str = "unknown"
    host_kingdoms: List[str] = field(default_factory=list)
    representative_genera: List[str] = field(default_factory=list)
    genome_size_kb_min: float = 0.0
    genome_size_kb_max: float = 0.0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.family_id or not isinstance(self.family_id, str):
            raise ViralFamilyError("family_id required")
        if not self.name or not isinstance(self.name, str):
            raise ViralFamilyError("name required")
        if self.genome_type not in GENOME_TYPES:
            raise ViralFamilyError(f"invalid genome_type: {self.genome_type!r}")
        if self.envelope not in ENVELOPE:
            raise ViralFamilyError(f"invalid envelope: {self.envelope!r}")
        if self.source not in SOURCES:
            raise ViralFamilyError(f"invalid source: {self.source!r}")
        for k in self.host_kingdoms:
            if k not in HOST_KINGDOMS:
                raise ViralFamilyError(f"invalid host_kingdom: {k!r}")
        if self.genome_size_kb_min < 0 or self.genome_size_kb_max < 0:
            raise ViralFamilyError("genome size must be non-negative")
        if self.genome_size_kb_max and self.genome_size_kb_max < self.genome_size_kb_min:
            raise ViralFamilyError("genome_size_kb_max < min")

    def genome_size_range(self) -> Dict[str, float]:
        return {"min_kb": self.genome_size_kb_min,
                "max_kb": self.genome_size_kb_max}


class ViralFamilyRegistry:
    """Family registry with genome/host/envelope queries."""

    def __init__(self) -> None:
        self._families: Dict[str, ViralFamily] = {}
        self._genome_index: Dict[str, List[str]] = {}
        self._host_index: Dict[str, List[str]] = {}

    def add(self, family: ViralFamily) -> ViralFamily:
        if family.family_id in self._families:
            raise ViralFamilyError(f"duplicate family_id: {family.family_id}")
        self._families[family.family_id] = family
        self._genome_index.setdefault(family.genome_type, []).append(family.family_id)
        for k in family.host_kingdoms:
            self._host_index.setdefault(k, []).append(family.family_id)
        return family

    def get(self, family_id: str) -> ViralFamily:
        try:
            return self._families[family_id]
        except KeyError as exc:
            raise ViralFamilyError(f"unknown family_id: {family_id}") from exc

    def by_genome_type(self, genome_type: str) -> List[ViralFamily]:
        if genome_type not in GENOME_TYPES:
            raise ViralFamilyError(f"invalid genome_type: {genome_type!r}")
        return [self.get(f) for f in self._genome_index.get(genome_type, [])]

    def by_host_kingdom(self, kingdom: str) -> List[ViralFamily]:
        if kingdom not in HOST_KINGDOMS:
            raise ViralFamilyError(f"invalid host_kingdom: {kingdom!r}")
        return [self.get(f) for f in self._host_index.get(kingdom, [])]

    def by_envelope(self, envelope: str) -> List[ViralFamily]:
        if envelope not in ENVELOPE:
            raise ViralFamilyError(f"invalid envelope: {envelope!r}")
        return [f for f in self._families.values() if f.envelope == envelope]

    def enveloped_families(self) -> List[ViralFamily]:
        return self.by_envelope("enveloped")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "families": len(self._families),
            "genome_types": len(self._genome_index),
            "host_kingdoms": len(self._host_index),
        }


def self_test() -> bool:
    registry = ViralFamilyRegistry()
    registry.add(ViralFamily(
        "VF_ortho", "Orthomyxoviridae", "negative_ssRNA", "enveloped",
        host_kingdoms=["animalia"], representative_genera=["Alphainfluenzavirus"],
        genome_size_kb_min=10.0, genome_size_kb_max=15.0))
    registry.add(ViralFamily(
        "VF_corona", "Coronaviridae", "positive_ssRNA", "enveloped",
        host_kingdoms=["animalia"], representative_genera=["Betacoronavirus"],
        genome_size_kb_min=26.0, genome_size_kb_max=32.0))
    registry.add(ViralFamily(
        "VF_parvo", "Parvoviridae", "ssDNA", "non_enveloped",
        host_kingdoms=["animalia"], genome_size_kb_min=4.0,
        genome_size_kb_max=6.0))
    assert len(registry.by_genome_type("negative_ssRNA")) == 1
    assert len(registry.by_host_kingdom("animalia")) == 3
    assert len(registry.enveloped_families()) == 2
    assert registry.get("VF_corona").genome_size_range()["max_kb"] == 32.0
    print("viral_family_registry: OK")
    return True


if __name__ == "__main__":
    self_test()
