"""DESI Infinity System - Viral Infection Research (v6.2.0).

Structured infection-state records (acute, chronic, latent, asymptomatic)
with duration and disease linkage. Research data only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INFECTION_STATES = ("acute", "chronic", "latent", "asymptomatic",
                    "subclinical", "unknown")
TRANSMISSION_STAGES = ("incubation", "peak", "convalescent",
                       "persistent", "unknown")
SOURCES = ("curated", "literature", "predicted")


class InfectionResearchError(Exception):
    """Base infection research error."""


@dataclass
class InfectionProfile:
    profile_id: str
    virus_id: str
    state: str
    duration_days_min: float = 0.0
    duration_days_max: float = 0.0
    transmission_stages: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.profile_id or not isinstance(self.profile_id, str):
            raise InfectionResearchError("profile_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise InfectionResearchError("virus_id required")
        if self.state not in INFECTION_STATES:
            raise InfectionResearchError(f"invalid state: {self.state!r}")
        if self.source not in SOURCES:
            raise InfectionResearchError(f"invalid source: {self.source!r}")
        if self.duration_days_min < 0 or self.duration_days_max < 0:
            raise InfectionResearchError("durations must be non-negative")
        if self.duration_days_max and self.duration_days_max < self.duration_days_min:
            raise InfectionResearchError("duration_days_max < min")
        for stage in self.transmission_stages:
            if stage not in TRANSMISSION_STAGES:
                raise InfectionResearchError(
                    f"invalid transmission_stage: {stage!r}")


class ViralInfectionResearch:
    """Infection profile store with state and disease queries."""

    def __init__(self) -> None:
        self._profiles: Dict[str, InfectionProfile] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, profile: InfectionProfile) -> InfectionProfile:
        if profile.profile_id in self._profiles:
            raise InfectionResearchError(
                f"duplicate profile_id: {profile.profile_id}")
        self._profiles[profile.profile_id] = profile
        self._virus_index.setdefault(profile.virus_id, []).append(profile.profile_id)
        for did in profile.disease_ids:
            self._disease_index.setdefault(did, []).append(profile.profile_id)
        return profile

    def get(self, profile_id: str) -> InfectionProfile:
        try:
            return self._profiles[profile_id]
        except KeyError as exc:
            raise InfectionResearchError(
                f"unknown profile_id: {profile_id}") from exc

    def for_virus(self, virus_id: str) -> List[InfectionProfile]:
        return [self.get(p) for p in self._virus_index.get(virus_id, [])]

    def by_state(self, state: str) -> List[InfectionProfile]:
        if state not in INFECTION_STATES:
            raise InfectionResearchError(f"invalid state: {state!r}")
        return [p for p in self._profiles.values() if p.state == state]

    def for_disease(self, disease_id: str) -> List[InfectionProfile]:
        return [self.get(p) for p in self._disease_index.get(disease_id, [])]

    def chronic_infections(self) -> List[InfectionProfile]:
        return self.by_state("chronic")

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "profiles": len(self._profiles),
            "viruses": len(self._virus_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    research = ViralInfectionResearch()
    research.add(InfectionProfile(
        "IP1", "VS_hiv1", "chronic", duration_days_min=365.0,
        duration_days_max=0.0, transmission_stages=["persistent"],
        disease_ids=["D_aids"]))
    research.add(InfectionProfile(
        "IP2", "VS_flu_a", "acute", duration_days_min=5.0,
        duration_days_max=10.0, transmission_stages=["incubation", "peak"]))
    research.add(InfectionProfile(
        "IP3", "VS_hsv1", "latent", duration_days_min=0.0,
        duration_days_max=0.0, transmission_stages=["persistent"]))
    assert len(research.for_virus("VS_hiv1")) == 1
    assert len(research.by_state("chronic")) == 1
    assert len(research.for_disease("D_aids")) == 1
    assert len(research.chronic_infections()) == 1
    print("viral_infection_research: OK")
    return True


if __name__ == "__main__":
    self_test()
