"""DESI Infinity System - Host-Pathogen Response Engine (v6.2.0).

Models host immune response programs to pathogens: response type,
magnitude, timing, and tissue localization. Research-only annotations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

RESPONSE_TYPES = ("innate", "adaptive_humoral", "adaptive_cellular",
                  "interferon", "inflammatory", "cytokine_storm",
                  "tolerance", "unknown")
TIMING = ("immediate", "early", "late", "chronic", "unknown")
MAGNITUDE = ("low", "moderate", "high", "extreme", "unknown")
SOURCES = ("curated", "literature", "predicted")


class HostResponseError(Exception):
    """Base host response error."""


@dataclass
class HostResponseProfile:
    profile_id: str
    pathogen_id: str
    response_type: str = "unknown"
    timing: str = "unknown"
    magnitude: str = "unknown"
    key_mediators: List[str] = field(default_factory=list)
    tissue: str = ""
    duration_days: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise HostResponseError("profile_id required")
        if not self.pathogen_id or not isinstance(self.pathogen_id, str):
            raise HostResponseError("pathogen_id required")
        if self.response_type not in RESPONSE_TYPES:
            raise HostResponseError(f"invalid response_type: {self.response_type!r}")
        if self.timing not in TIMING:
            raise HostResponseError(f"invalid timing: {self.timing!r}")
        if self.magnitude not in MAGNITUDE:
            raise HostResponseError(f"invalid magnitude: {self.magnitude!r}")
        if self.source not in SOURCES:
            raise HostResponseError(f"invalid source: {self.source!r}")
        if self.duration_days is not None:
            if not isinstance(self.duration_days, (int, float)) or self.duration_days < 0:
                raise HostResponseError("duration_days must be non-negative or None")


class HostPathogenResponseEngine:
    """Response registry with mediator / type / timing queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, HostResponseProfile] = {}
        self._pathogen_index: Dict[str, List[str]] = {}
        self._mediator_index: Dict[str, List[str]] = {}

    def add(self, profile: HostResponseProfile) -> HostResponseProfile:
        if profile.profile_id in self._profiles:
            raise HostResponseError(f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        self._pathogen_index.setdefault(profile.pathogen_id, []).append(profile.profile_id)
        for m in profile.key_mediators:
            self._mediator_index.setdefault(m, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> HostResponseProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise HostResponseError(f"unknown profile_id: {profile_id}") from exc

    def for_pathogen(self, pathogen_id: str) -> List[HostResponseProfile]:
        return [self.get(pid) for pid in self._pathogen_index.get(pathogen_id, [])]

    def by_type(self, response_type: str) -> List[HostResponseProfile]:
        if response_type not in RESPONSE_TYPES:
            raise HostResponseError(f"invalid response_type: {response_type!r}")
        return [p for p in self._profiles.values() if p.response_type == response_type]

    def by_timing(self, timing: str) -> List[HostResponseProfile]:
        if timing not in TIMING:
            raise HostResponseError(f"invalid timing: {timing!r}")
        return [p for p in self._profiles.values() if p.timing == timing]

    def by_mediator(self, mediator: str) -> List[HostResponseProfile]:
        return [self.get(pid) for pid in self._mediator_index.get(mediator, [])]

    def extreme_responses(self) -> List[HostResponseProfile]:
        return [p for p in self._profiles.values()
                if p.magnitude in ("high", "extreme")]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "pathogens": len(self._pathogen_index),
            "mediators": len(self._mediator_index),
        }


def self_test() -> bool:
    engine = HostPathogenResponseEngine()
    engine.add(HostResponseProfile(
        "R1", "NCBITaxon:2697049", "interferon", "immediate", "high",
        ["IFN-alpha", "IFN-beta"], "respiratory_epithelium", 10.0))
    engine.add(HostResponseProfile(
        "R2", "NCBITaxon:2697049", "cytokine_storm", "late", "extreme",
        ["IL-6", "TNF-alpha"], "systemic", 21.0))
    engine.add(HostResponseProfile(
        "R3", "NCBITaxon:11320", "adaptive_humoral", "late", "moderate",
        ["IgG"], "systemic", 14.0))
    assert len(engine.for_pathogen("NCBITaxon:2697049")) == 2
    assert engine.by_type("cytokine_storm")[0].profile_id == "R2"
    assert engine.by_timing("immediate")[0].profile_id == "R1"
    assert len(engine.by_mediator("IL-6")) == 1
    assert len(engine.extreme_responses()) == 2
    print("host_pathogen_response_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
