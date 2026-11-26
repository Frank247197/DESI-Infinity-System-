"""DESI Infinity System - Viral Pathogenesis Analyzer (v6.2.0).

Documents mechanisms by which viruses cause disease: direct cytopathic
effect, immune-mediated, oncogenic, systemic inflammation. Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MECHANISMS = ("cytopathic_effect", "immune_mediated", "oncogenic",
              "systemic_inflammation", "apoptosis_induction",
              "syncytium_formation", "latency_reactivation", "other")
TARGET_TISSUES = ("respiratory", "gastrointestinal", "neurological",
                  "hepatic", "renal", "hematopoietic", "epithelial",
                  "lymphoid", "other")
SOURCES = ("curated", "literature", "predicted")


class PathogenesisError(Exception):
    """Base pathogenesis error."""


@dataclass
class PathogenesisProfile:
    profile_id: str
    virus_id: str
    mechanisms: List[str] = field(default_factory=list)
    target_tissues: List[str] = field(default_factory=list)
    viral_load_correlate: bool = False
    severity_contributors: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise PathogenesisError("profile_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise PathogenesisError("virus_id required")
        if self.source not in SOURCES:
            raise PathogenesisError(f"invalid source: {self.source!r}")
        for m in self.mechanisms:
            if m not in MECHANISMS:
                raise PathogenesisError(f"invalid mechanism: {m!r}")
        for t in self.target_tissues:
            if t not in TARGET_TISSUES:
                raise PathogenesisError(f"invalid target_tissue: {t!r}")


class ViralPathogenesisAnalyzer:
    """Pathogenesis profile store with mechanism/tissue queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, PathogenesisProfile] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._mechanism_index: Dict[str, List[str]] = {}
        self._tissue_index: Dict[str, List[str]] = {}

    def add(self, profile: PathogenesisProfile) -> PathogenesisProfile:
        if profile.profile_id in self._profiles:
            raise PathogenesisError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        self._virus_index.setdefault(profile.virus_id, []).append(profile.profile_id)
        for m in profile.mechanisms:
            self._mechanism_index.setdefault(m, []).append(profile.profile_id)
        for t in profile.target_tissues:
            self._tissue_index.setdefault(t, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> PathogenesisProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise PathogenesisError(f"unknown profile_id: {profile_id}") from exc

    def for_virus(self, virus_id: str) -> List[PathogenesisProfile]:
        return [self.get(p) for p in self._virus_index.get(virus_id, [])]

    def by_mechanism(self, mechanism: str) -> List[PathogenesisProfile]:
        if mechanism not in MECHANISMS:
            raise PathogenesisError(f"invalid mechanism: {mechanism!r}")
        return [self.get(p) for p in self._mechanism_index.get(mechanism, [])]

    def by_tissue(self, tissue: str) -> List[PathogenesisProfile]:
        if tissue not in TARGET_TISSUES:
            raise PathogenesisError(f"invalid target_tissue: {tissue!r}")
        return [self.get(p) for p in self._tissue_index.get(tissue, [])]

    def oncogenic_viruses(self) -> List[PathogenesisProfile]:
        return self.by_mechanism("oncogenic")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "viruses": len(self._virus_index),
            "mechanisms": len(self._mechanism_index),
        }


def self_test() -> bool:
    analyzer = ViralPathogenesisAnalyzer()
    analyzer.add(PathogenesisProfile(
        "PP1", "VS_sars2", ["cytopathic_effect", "systemic_inflammation"],
        ["respiratory"], viral_load_correlate=True))
    analyzer.add(PathogenesisProfile(
        "PP2", "VS_hiv1", ["immune_mediated"],
        ["lymphoid", "hematopoietic"]))
    analyzer.add(PathogenesisProfile(
        "PP3", "VS_hpv16", ["oncogenic"],
        ["epithelial"], severity_contributors=["E6", "E7"]))
    assert len(analyzer.for_virus("VS_sars2")) == 1
    assert len(analyzer.by_mechanism("oncogenic")) == 1
    assert len(analyzer.by_tissue("respiratory")) == 1
    assert len(analyzer.oncogenic_viruses()) == 1
    print("viral_pathogenesis_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
