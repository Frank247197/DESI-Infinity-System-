"""DESI Infinity System - Viral Transmission Research (v6.2.0).

Structured transmission research data: routes, estimated parameters
(R0 range, serial interval), and evidence class. Values are curated
research estimates, not predictions of future transmission.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ROUTES = ("airborne", "droplet", "direct_contact", "fomite", "vector",
          "sexual", "bloodborne", "vertical", "foodborne", "waterborne",
          "zoonotic_spillover", "unknown")
EVIDENCE_CLASSES = ("outbreak_analysis", "modeling_study",
                    "contact_tracing", "literature_review", "predicted",
                    "unknown")
SOURCES = ("curated", "literature", "predicted")


class TransmissionError(Exception):
    """Base transmission error."""


@dataclass
class TransmissionRecord:
    record_id: str
    virus_id: str
    routes: List[str] = field(default_factory=list)
    r0_min: Optional[float] = None
    r0_max: Optional[float] = None
    serial_interval_days: Optional[float] = None
    incubation_days: Optional[float] = None
    evidence_class: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not isinstance(self.record_id, str):
            raise TransmissionError("record_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise TransmissionError("virus_id required")
        for r in self.routes:
            if r not in ROUTES:
                raise TransmissionError(f"invalid route: {r!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise TransmissionError(
                f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise TransmissionError(f"invalid source: {self.source!r}")
        for label, val in (("r0_min", self.r0_min), ("r0_max", self.r0_max),
                           ("serial_interval_days", self.serial_interval_days),
                           ("incubation_days", self.incubation_days)):
            if val is not None:
                if not isinstance(val, (int, float)) or val < 0:
                    raise TransmissionError(
                        f"{label} must be non-negative numeric or None")
        if (self.r0_min is not None and self.r0_max is not None
                and self.r0_min > self.r0_max):
            raise TransmissionError("r0_min > r0_max")

    def r0_range(self) -> Optional[Dict[str, float]]:
        if self.r0_min is None and self.r0_max is None:
            return None
        return {"min": self.r0_min or 0.0, "max": self.r0_max or 0.0}


class ViralTransmissionResearch:
    """Transmission record store with route and R0 queries."""

    def __init__(self) -> None:
        self._records: Dict[str, TransmissionRecord] = {}
        self._virus_index: Dict[str, List[str]] = {}

    def add(self, record: TransmissionRecord) -> TransmissionRecord:
        if record.record_id in self._records:
            raise TransmissionError(f"duplicate record_id: {record.record_id}")
        self._records[record.record_id] = record
        self._virus_index.setdefault(record.virus_id, []).append(record.record_id)
        return record

    def get(self, record_id: str) -> TransmissionRecord:
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise TransmissionError(f"unknown record_id: {record_id}") from exc

    def for_virus(self, virus_id: str) -> List[TransmissionRecord]:
        return [self.get(r) for r in self._virus_index.get(virus_id, [])]

    def by_route(self, route: str) -> List[TransmissionRecord]:
        if route not in ROUTES:
            raise TransmissionError(f"invalid route: {route!r}")
        return [r for r in self._records.values() if route in r.routes]

    def high_r0(self, threshold: float = 2.0) -> List[TransmissionRecord]:
        return [r for r in self._records.values()
                if r.r0_max is not None and r.r0_max >= threshold]

    def routes_for(self, virus_id: str) -> List[str]:
        routes = set()
        for r in self.for_virus(virus_id):
            routes.update(r.routes)
        return sorted(routes)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "viruses": len(self._virus_index),
            "high_r0": len(self.high_r0()),
        }


def self_test() -> bool:
    engine = ViralTransmissionResearch()
    engine.add(TransmissionRecord(
        "TR1", "VS_sars2",
        routes=["airborne", "droplet", "direct_contact", "fomite"],
        r0_min=2.5, r0_max=5.7, serial_interval_days=5.2,
        incubation_days=5.0, evidence_class="outbreak_analysis"))
    engine.add(TransmissionRecord(
        "TR2", "VS_flu_a",
        routes=["droplet", "direct_contact"],
        r0_min=1.2, r0_max=1.6, incubation_days=2.0,
        evidence_class="literature_review"))
    engine.add(TransmissionRecord(
        "TR3", "VS_hiv1", routes=["sexual", "bloodborne", "vertical"],
        evidence_class="literature_review"))
    assert len(engine.for_virus("VS_sars2")) == 1
    assert len(engine.by_route("droplet")) == 2
    assert len(engine.high_r0(2.0)) == 1
    assert engine.routes_for("VS_hiv1") == ["bloodborne", "sexual", "vertical"]
    assert engine.get("TR1").r0_range()["max"] == 5.7
    print("viral_transmission_research: OK")
    return True


if __name__ == "__main__":
    self_test()
