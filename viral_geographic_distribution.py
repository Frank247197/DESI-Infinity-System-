"""DESI Infinity System - Viral Geographic Distribution (v6.2.0).

Structured records of viral geographic presence by country/region/year
with evidence basis. Explicitly returns "no_data" rather than fabricating
absence of a virus.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PRESENCE_STATUS = ("endemic", "epidemic", "sporadic", "eliminated",
                   "not_reported", "unknown")
EVIDENCE_CLASSES = ("surveillance_report", "case_report", "serology",
                    "genomic_surveillance", "predicted", "unknown")
SOURCES = ("curated", "literature", "predicted")


class GeographicError(Exception):
    """Base geographic error."""


@dataclass
class DistributionRecord:
    record_id: str
    virus_id: str
    country: str
    region: str = ""
    presence: str = "unknown"
    year: Optional[int] = None
    evidence_class: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not isinstance(self.record_id, str):
            raise GeographicError("record_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise GeographicError("virus_id required")
        if not self.country or not isinstance(self.country, str):
            raise GeographicError("country required")
        if self.presence not in PRESENCE_STATUS:
            raise GeographicError(f"invalid presence: {self.presence!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise GeographicError(
                f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise GeographicError(f"invalid source: {self.source!r}")
        if self.year is not None:
            if not isinstance(self.year, int) or not (1900 <= self.year <= 2100):
                raise GeographicError("year must be a 4-digit year or None")


class ViralGeographicDistribution:
    """Distribution registry with country / presence / virus queries."""

    def __init__(self) -> None:
        self._records: Dict[str, DistributionRecord] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._country_index: Dict[str, List[str]] = {}

    def add(self, record: DistributionRecord) -> DistributionRecord:
        if record.record_id in self._records:
            raise GeographicError(f"duplicate record_id: {record.record_id}")
        self._records[record.record_id] = record
        self._virus_index.setdefault(record.virus_id, []).append(record.record_id)
        self._country_index.setdefault(record.country, []).append(record.record_id)
        return record

    def get(self, record_id: str) -> DistributionRecord:
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise GeographicError(f"unknown record_id: {record_id}") from exc

    def for_virus(self, virus_id: str) -> List[DistributionRecord]:
        return [self.get(r) for r in self._virus_index.get(virus_id, [])]

    def for_country(self, country: str) -> List[DistributionRecord]:
        return [self.get(r) for r in self._country_index.get(country, [])]

    def countries_with(self, virus_id: str, presence: str) -> List[str]:
        if presence not in PRESENCE_STATUS:
            raise GeographicError(f"invalid presence: {presence!r}")
        return sorted({r.country for r in self.for_virus(virus_id)
                       if r.presence == presence})

    def coverage(self, virus_id: str) -> Dict[str, object]:
        recs = self.for_virus(virus_id)
        if not recs:
            return {"virus_id": virus_id, "status": "no_data"}
        by_presence: Dict[str, List[str]] = {}
        for r in recs:
            by_presence.setdefault(r.presence, []).append(r.country)
        return {
            "virus_id": virus_id,
            "status": "ok",
            "records": len(recs),
            "by_presence": {k: sorted(set(v)) for k, v in by_presence.items()},
        }

    def by_year(self, year: int) -> List[DistributionRecord]:
        if not isinstance(year, int) or not (1900 <= year <= 2100):
            raise GeographicError("year must be a 4-digit year")
        return [r for r in self._records.values() if r.year == year]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "viruses": len(self._virus_index),
            "countries": len(self._country_index),
        }


def self_test() -> bool:
    db = ViralGeographicDistribution()
    db.add(DistributionRecord(
        "G1", "VS_flu_a", "USA", presence="endemic", year=2023))
    db.add(DistributionRecord(
        "G2", "VS_flu_a", "CHN", presence="endemic", year=2023))
    db.add(DistributionRecord(
        "G3", "VS_sars2", "GBR", presence="epidemic", year=2021))
    db.add(DistributionRecord(
        "G4", "VS_polio", "PAK", presence="endemic", year=2022))
    db.add(DistributionRecord(
        "G5", "VS_polio", "NGA", presence="endemic", year=2022))
    assert len(db.for_virus("VS_flu_a")) == 2
    assert len(db.for_country("USA")) == 1
    assert db.countries_with("VS_flu_a", "endemic") == ["CHN", "USA"]
    cov = db.coverage("VS_flu_a")
    assert cov["status"] == "ok"
    assert db.coverage("VS_unknown")["status"] == "no_data"
    assert len(db.by_year(2022)) == 2
    print("viral_geographic_distribution: OK")
    return True


if __name__ == "__main__":
    self_test()
