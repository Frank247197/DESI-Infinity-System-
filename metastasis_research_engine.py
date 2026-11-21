"""DESI Infinity System - Metastasis Research Engine (v6.2.0).

Stores metastasis events (primary site -> secondary site) with organ
tropism, timing, and research annotation. Research only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ORGAN_SITES = ("lung", "liver", "bone", "brain", "lymph_node", "adrenal",
               "peritoneum", "pleura", "skin", "ovary", "other")
SOURCES = ("curated", "literature", "predicted")


class MetastasisError(Exception):
    """Base metastasis error."""


@dataclass
class MetastasisEvent:
    event_id: str
    cancer_id: str
    primary_site: str
    secondary_site: str
    months_to_metastasis: Optional[float] = None
    evidence_source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id or not isinstance(self.event_id, str):
            raise MetastasisError("event_id required")
        if not self.cancer_id or not isinstance(self.cancer_id, str):
            raise MetastasisError("cancer_id required")
        if self.primary_site not in ORGAN_SITES:
            raise MetastasisError(f"invalid primary_site: {self.primary_site!r}")
        if self.secondary_site not in ORGAN_SITES:
            raise MetastasisError(f"invalid secondary_site: {self.secondary_site!r}")
        if self.evidence_source not in SOURCES:
            raise MetastasisError(f"invalid evidence_source: {self.evidence_source!r}")
        if self.months_to_metastasis is not None:
            if not isinstance(self.months_to_metastasis, (int, float)) or self.months_to_metastasis < 0:
                raise MetastasisError("months_to_metastasis must be non-negative or None")


class MetastasisResearchEngine:
    """Registry + tropism and timing analyses."""

    def __init__(self) -> None:
        self._events: List[MetastasisEvent] = []
        self._by_cancer: Dict[str, List[int]] = {}

    def add(self, event: MetastasisEvent) -> None:
        idx = len(self._events)
        self._events.append(event)
        self._by_cancer.setdefault(event.cancer_id, []).append(idx)

    def for_cancer(self, cancer_id: str) -> List[MetastasisEvent]:
        return [self._events[i] for i in self._by_cancer.get(cancer_id, [])]

    def tropism(self, cancer_id: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for e in self.for_cancer(cancer_id):
            counts[e.secondary_site] = counts.get(e.secondary_site, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))

    def top_secondary_site(self, cancer_id: str) -> Optional[str]:
        trop = self.tropism(cancer_id)
        if not trop:
            return None
        return max(trop, key=lambda k: trop[k])

    def average_time_to_metastasis(self, cancer_id: str) -> Optional[float]:
        vals = [e.months_to_metastasis for e in self.for_cancer(cancer_id)
                if e.months_to_metastasis is not None]
        if not vals:
            return None
        return round(sum(vals) / len(vals), 2)

    def to_organ(self, organ: str) -> List[MetastasisEvent]:
        if organ not in ORGAN_SITES:
            raise MetastasisError(f"invalid organ: {organ!r}")
        return [e for e in self._events if e.secondary_site == organ]

    def from_organ(self, organ: str) -> List[MetastasisEvent]:
        if organ not in ORGAN_SITES:
            raise MetastasisError(f"invalid organ: {organ!r}")
        return [e for e in self._events if e.primary_site == organ]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "events": len(self._events),
            "cancers": len(self._by_cancer),
            "organs": len({e.secondary_site for e in self._events}),
        }


def self_test() -> bool:
    engine = MetastasisResearchEngine()
    engine.add(MetastasisEvent("E1", "C_breast", "other", "bone",
                               months_to_metastasis=24.0))
    engine.add(MetastasisEvent("E2", "C_breast", "other", "lung",
                               months_to_metastasis=30.0))
    engine.add(MetastasisEvent("E3", "C_breast", "other", "bone",
                               months_to_metastasis=18.0))
    engine.add(MetastasisEvent("E4", "C_luad", "lung", "brain",
                               months_to_metastasis=12.0))
    assert engine.top_secondary_site("C_breast") == "bone"
    assert engine.average_time_to_metastasis("C_breast") == 24.0
    assert len(engine.to_organ("bone")) == 2
    assert len(engine.from_organ("lung")) == 1
    assert engine.stats()["events"] == 4
    print("metastasis_research_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
