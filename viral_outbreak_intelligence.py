"""DESI Infinity System - Viral Outbreak Intelligence (v6.2.0).

Structured outbreak records: pathogen, location, time, case counts,
and evidence class. Outbreak records are historical/research records,
NOT real-time alerts or clinical advice.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

OUTBREAK_STATUS = ("ongoing", "resolved", "declared_over", "unknown")
EVIDENCE_CLASSES = ("who_notification", "national_report",
                    "modeling_estimate", "media_report", "predicted",
                    "unknown")
SOURCES = ("curated", "literature", "predicted")


class OutbreakError(Exception):
    """Base outbreak error."""


@dataclass
class OutbreakRecord:
    outbreak_id: str
    virus_id: str
    location: str
    start_date: str = ""
    end_date: str = ""
    cases: Optional[int] = None
    deaths: Optional[int] = None
    status: str = "unknown"
    evidence_class: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.outbreak_id or not isinstance(self.outbreak_id, str):
            raise OutbreakError("outbreak_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise OutbreakError("virus_id required")
        if not self.location or not isinstance(self.location, str):
            raise OutbreakError("location required")
        if self.status not in OUTBREAK_STATUS:
            raise OutbreakError(f"invalid status: {self.status!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise OutbreakError(
                f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise OutbreakError(f"invalid source: {self.source!r}")
        for label, val in (("cases", self.cases), ("deaths", self.deaths)):
            if val is not None and (not isinstance(val, int) or val < 0):
                raise OutbreakError(f"{label} must be non-negative int or None")
        if (self.cases is not None and self.deaths is not None
                and self.deaths > self.cases):
            raise OutbreakError("deaths > cases")

    def crude_cfr(self) -> Optional[float]:
        if self.cases and self.deaths is not None and self.cases > 0:
            return round(self.deaths / self.cases, 6)
        return None


class ViralOutbreakIntelligence:
    """Outbreak store with virus/location/status queries."""

    def __init__(self) -> None:
        self._outbreaks: Dict[str, OutbreakRecord] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._location_index: Dict[str, List[str]] = {}

    def add(self, record: OutbreakRecord) -> OutbreakRecord:
        if record.outbreak_id in self._outbreaks:
            raise OutbreakError(f"duplicate outbreak_id: {record.outbreak_id}")
        self._outbreaks[record.outbreak_id] = record
        self._virus_index.setdefault(record.virus_id, []).append(record.outbreak_id)
        self._location_index.setdefault(record.location, []).append(
            record.outbreak_id)
        return record

    def get(self, outbreak_id: str) -> OutbreakRecord:
        try:
            return self._outbreaks[outbreak_id]
        except KeyError as exc:
            raise OutbreakError(f"unknown outbreak_id: {outbreak_id}") from exc

    def for_virus(self, virus_id: str) -> List[OutbreakRecord]:
        return [self.get(o) for o in self._virus_index.get(virus_id, [])]

    def for_location(self, location: str) -> List[OutbreakRecord]:
        return [self.get(o) for o in self._location_index.get(location, [])]

    def ongoing(self) -> List[OutbreakRecord]:
        return [o for o in self._outbreaks.values() if o.status == "ongoing"]

    def largest_by_cases(self, top_n: int = 5) -> List[OutbreakRecord]:
        if top_n <= 0:
            raise OutbreakError("top_n must be positive")
        rows = [o for o in self._outbreaks.values() if o.cases is not None]
        rows.sort(key=lambda o: o.cases, reverse=True)  # type: ignore
        return rows[:top_n]

    def cfr_summary(self, virus_id: str) -> Dict[str, object]:
        recs = self.for_virus(virus_id)
        cfrs = [o.crude_cfr() for o in recs if o.crude_cfr() is not None]
        if not cfrs:
            return {"virus_id": virus_id, "status": "no_data"}
        return {"virus_id": virus_id, "n": len(cfrs),
                "mean_cfr": round(sum(cfrs) / len(cfrs), 6),
                "max_cfr": max(cfrs), "min_cfr": min(cfrs)}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "outbreaks": len(self._outbreaks),
            "viruses": len(self._virus_index),
            "locations": len(self._location_index),
            "ongoing": len(self.ongoing()),
        }


def self_test() -> bool:
    engine = ViralOutbreakIntelligence()
    engine.add(OutbreakRecord(
        "OB1", "VS_ebola", "West Africa", "2014-03", "2016-01",
        cases=28600, deaths=11325, status="declared_over",
        evidence_class="who_notification"))
    engine.add(OutbreakRecord(
        "OB2", "VS_sars2", "Global", "2019-12", "", cases=700000000,
        deaths=6900000, status="ongoing",
        evidence_class="who_notification"))
    engine.add(OutbreakRecord(
        "OB3", "VS_cholera_vibrio", "Haiti", "2010-10", "2019-01",
        cases=820000, deaths=9792, status="declared_over",
        evidence_class="national_report"))
    assert len(engine.for_virus("VS_ebola")) == 1
    assert len(engine.for_location("Haiti")) == 1
    assert len(engine.ongoing()) == 1
    assert engine.largest_by_cases(1)[0].outbreak_id == "OB2"
    summary = engine.cfr_summary("VS_ebola")
    assert summary["mean_cfr"] > 0.3
    assert engine.get("OB1").crude_cfr() is not None
    print("viral_outbreak_intelligence: OK")
    return True


if __name__ == "__main__":
    self_test()
