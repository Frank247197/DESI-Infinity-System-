"""DESI Infinity System - Cancer Genomics Engine (v6.2.0).

Stores cancer genome profiles with mutation burden, copy-number alteration
summary, mutational signatures, and driver-gene status. Research data only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

SIGNATURE_CLASSES = ("SBS1", "SBS2", "SBS3", "SBS4", "SBS5", "SBS13",
                     "SBS17", "SBS22", "SBS29", "SBS40", "unknown")
DRIVER_STATUS = ("amplified", "deleted", "mutated", "fusion",
                 "wild_type", "unknown")
SOURCES = ("curated", "literature", "predicted")


class CancerGenomicsError(Exception):
    """Base cancer genomics error."""


@dataclass
class CancerGenomeProfile:
    profile_id: str
    cancer_id: str
    tumor_mutation_burden: Optional[float] = None
    microsatellite_instability: Optional[bool] = None
    mutational_signatures: List[str] = field(default_factory=list)
    driver_status: Dict[str, str] = field(default_factory=dict)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise CancerGenomicsError("profile_id required")
        if not self.cancer_id or not isinstance(self.cancer_id, str):
            raise CancerGenomicsError("cancer_id required")
        if self.source not in SOURCES:
            raise CancerGenomicsError(f"invalid source: {self.source!r}")
        for s in self.mutational_signatures:
            if s not in SIGNATURE_CLASSES:
                raise CancerGenomicsError(f"unknown signature: {s!r}")
        for g, st in self.driver_status.items():
            if st not in DRIVER_STATUS:
                raise CancerGenomicsError(f"invalid driver_status for {g!r}: {st!r}")
        if self.tumor_mutation_burden is not None:
            if not isinstance(self.tumor_mutation_burden, (int, float)) or self.tumor_mutation_burden < 0:
                raise CancerGenomicsError("tumor_mutation_burden must be non-negative or None")

    def is_hypermutated(self, threshold: float = 10.0) -> bool:
        return (self.tumor_mutation_burden is not None
                and self.tumor_mutation_burden >= threshold)


class CancerGenomicsEngine:
    """Registry with signature / driver-status / hypermutation queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, CancerGenomeProfile] = {}
        self._signature_index: Dict[str, List[str]] = {}

    def add(self, profile: CancerGenomeProfile) -> CancerGenomeProfile:
        if profile.profile_id in self._profiles:
            raise CancerGenomicsError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        for s in profile.mutational_signatures:
            self._signature_index.setdefault(s, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> CancerGenomeProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise CancerGenomicsError(f"unknown profile_id: {profile_id}") from exc

    def for_cancer(self, cancer_id: str) -> List[CancerGenomeProfile]:
        return [p for p in self._profiles.values() if p.cancer_id == cancer_id]

    def by_signature(self, signature: str) -> List[CancerGenomeProfile]:
        if signature not in SIGNATURE_CLASSES:
            raise CancerGenomicsError(f"unknown signature: {signature!r}")
        return [self.get(pid) for pid in self._signature_index.get(signature, [])]

    def hypermutated(self, threshold: float = 10.0) -> List[CancerGenomeProfile]:
        return [p for p in self._profiles.values() if p.is_hypermutated(threshold)]

    def msi_high(self) -> List[CancerGenomeProfile]:
        return [p for p in self._profiles.values() if p.microsatellite_instability is True]

    def driver_summary(self, cancer_id: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for p in self.for_cancer(cancer_id):
            for st in p.driver_status.values():
                counts[st] = counts.get(st, 0) + 1
        return counts

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "signatures": len(self._signature_index),
            "hypermutated": len(self.hypermutated()),
        }


def self_test() -> bool:
    engine = CancerGenomicsEngine()
    engine.add(CancerGenomeProfile(
        "P1", "C_colorectal", tumor_mutation_burden=45.0,
        microsatellite_instability=True,
        mutational_signatures=["SBS1", "SBS5", "SBS22"],
        driver_status={"KRAS": "mutated", "TP53": "mutated", "BRAF": "wild_type"}))
    engine.add(CancerGenomeProfile(
        "P2", "C_luad", tumor_mutation_burden=3.5,
        mutational_signatures=["SBS4"],
        driver_status={"EGFR": "mutated", "ALK": "fusion"}))
    assert engine.by_signature("SBS1")[0].profile_id == "P1"
    assert len(engine.hypermutated()) == 1
    assert len(engine.msi_high()) == 1
    assert engine.driver_summary("C_colorectal")["mutated"] == 2
    assert engine.stats()["profiles"] == 2
    print("cancer_genomics_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
