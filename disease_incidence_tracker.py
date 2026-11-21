"""DESI Infinity System - Disease Incidence Tracker (v6.2.0).

Tracks new-case incidence counts per disease/region/period. Supports
crude rate computation given an explicit denominator population, and
trend comparison between adjacent periods. Missing denominators yield
"rate unavailable" rather than fabricated values.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

SOURCES = ("curated", "literature", "predicted")
PERIOD_UNITS = ("day", "week", "month", "quarter", "year")


class IncidenceError(Exception):
    """Base incidence error."""


@dataclass
class IncidenceRecord:
    disease_id: str
    region: str
    period: str
    new_cases: int
    population: Optional[int] = None
    period_unit: str = "year"
    year: Optional[int] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise IncidenceError("disease_id required")
        if not self.region or not isinstance(self.region, str):
            raise IncidenceError("region required")
        if not isinstance(self.new_cases, int) or self.new_cases < 0:
            raise IncidenceError("new_cases must be non-negative int")
        if self.population is not None:
            if not isinstance(self.population, int) or self.population <= 0:
                raise IncidenceError("population must be a positive int or None")
        if self.period_unit not in PERIOD_UNITS:
            raise IncidenceError(f"invalid period_unit: {self.period_unit!r}")
        if self.source not in SOURCES:
            raise IncidenceError(f"invalid source: {self.source!r}")

    def rate_per_100k(self) -> Optional[float]:
        if self.population is None or self.population <= 0:
            return None
        return round((self.new_cases / self.population) * 100_000, 4)

    def to_dict(self) -> Dict[str, object]:
        return {
            "disease_id": self.disease_id, "region": self.region,
            "period": self.period, "new_cases": self.new_cases,
            "population": self.population, "period_unit": self.period_unit,
            "year": self.year, "rate_per_100k": self.rate_per_100k(),
            "source": self.source, "evidence_ids": list(self.evidence_ids),
        }


class DiseaseIncidenceTracker:
    """Incidence storage with rate computation and trend comparison."""

    def __init__(self) -> None:
        self._records: List[IncidenceRecord] = []

    def add(self, record: IncidenceRecord) -> None:
        self._records.append(record)

    def for_disease(self, disease_id: str) -> List[IncidenceRecord]:
        return [r for r in self._records if r.disease_id == disease_id]

    def for_region(self, region: str) -> List[IncidenceRecord]:
        return [r for r in self._records if r.region == region]

    def rate_available(self, disease_id: str) -> List[IncidenceRecord]:
        return [r for r in self.for_disease(disease_id) if r.rate_per_100k() is not None]

    def rate_unavailable(self, disease_id: str) -> List[IncidenceRecord]:
        return [r for r in self.for_disease(disease_id) if r.rate_per_100k() is None]

    def trend(self, disease_id: str, region: str) -> Dict[str, object]:
        rows = [r for r in self.for_disease(disease_id)
                if r.region == region and r.year is not None]
        rows.sort(key=lambda r: r.year)  # type: ignore[arg-type,return-value]
        if len(rows) < 2:
            return {"disease_id": disease_id, "region": region,
                    "status": "insufficient_data", "points": len(rows)}
        first, last = rows[0], rows[-1]
        delta = last.new_cases - first.new_cases
        pct = round((delta / first.new_cases) * 100, 2) if first.new_cases else None
        return {
            "disease_id": disease_id, "region": region, "status": "ok",
            "from_year": first.year, "to_year": last.year,
            "delta_cases": delta, "percent_change": pct,
            "direction": "up" if delta > 0 else ("down" if delta < 0 else "flat"),
        }

    def totals(self, disease_id: str) -> Dict[str, int]:
        recs = self.for_disease(disease_id)
        return {
            "records": len(recs),
            "total_new_cases": sum(r.new_cases for r in recs),
            "with_rate": len(self.rate_available(disease_id)),
            "without_rate": len(self.rate_unavailable(disease_id)),
        }

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "diseases": len({r.disease_id for r in self._records}),
        }


def self_test() -> bool:
    tracker = DiseaseIncidenceTracker()
    tracker.add(IncidenceRecord("D1", "EU", "2020", 1000, population=500_000, year=2020))
    tracker.add(IncidenceRecord("D1", "EU", "2022", 1500, population=520_000, year=2022))
    tracker.add(IncidenceRecord("D1", "US", "2022", 900))  # no population
    assert tracker.rate_available("D1")[0].rate_per_100k() == 200.0
    trend = tracker.trend("D1", "EU")
    assert trend["status"] == "ok" and trend["direction"] == "up"
    assert len(tracker.rate_unavailable("D1")) == 1
    assert tracker.totals("D1")["total_new_cases"] == 3400
    print("012 disease_incidence_tracker: OK")
    return True


if __name__ == "__main__":
    self_test()
