"""DESI Infinity System - Disease Prevalence Analyzer (v6.2.0).

Stores prevalence measurements per disease/region/period with structured
metadata (denominator, method, source). Provides region comparison and
time-series summaries. Absent data is explicitly reported as unavailable.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

METRIC_KINDS = ("point", "period", "lifetime")
SOURCES = ("curated", "literature", "predicted")


class PrevalenceError(Exception):
    """Base prevalence error."""


@dataclass
class PrevalenceRecord:
    disease_id: str
    region: str
    period: str
    value_per_100k: float
    metric_kind: str = "point"
    year: Optional[int] = None
    source: str = "curated"
    methodology: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise PrevalenceError("disease_id required")
        if not self.region or not isinstance(self.region, str):
            raise PrevalenceError("region required")
        if not isinstance(self.value_per_100k, (int, float)) or self.value_per_100k < 0:
            raise PrevalenceError("value_per_100k must be non-negative numeric")
        if self.metric_kind not in METRIC_KINDS:
            raise PrevalenceError(f"invalid metric_kind: {self.metric_kind!r}")
        if self.source not in SOURCES:
            raise PrevalenceError(f"invalid source: {self.source!r}")
        if self.year is not None and not isinstance(self.year, int):
            raise PrevalenceError("year must be int or None")

    def to_dict(self) -> Dict[str, object]:
        return {
            "disease_id": self.disease_id, "region": self.region,
            "period": self.period, "value_per_100k": self.value_per_100k,
            "metric_kind": self.metric_kind, "year": self.year,
            "source": self.source, "methodology": self.methodology,
            "evidence_ids": list(self.evidence_ids),
        }


class DiseasePrevalenceAnalyzer:
    """Prevalence storage with regional/time aggregation."""

    def __init__(self) -> None:
        self._records: List[PrevalenceRecord] = []

    def add(self, record: PrevalenceRecord) -> None:
        self._records.append(record)

    def for_disease(self, disease_id: str) -> List[PrevalenceRecord]:
        return [r for r in self._records if r.disease_id == disease_id]

    def for_region(self, region: str) -> List[PrevalenceRecord]:
        return [r for r in self._records if r.region == region]

    def region_comparison(self, disease_id: str) -> Dict[str, float]:
        out: Dict[str, List[float]] = {}
        for r in self.for_disease(disease_id):
            out.setdefault(r.region, []).append(r.value_per_100k)
        return {region: round(sum(vals) / len(vals), 2) for region, vals in out.items()}

    def time_series(self, disease_id: str, region: Optional[str] = None
                    ) -> List[Dict[str, object]]:
        rows = [r for r in self.for_disease(disease_id)
                if r.year is not None and (region is None or r.region == region)]
        rows.sort(key=lambda r: r.year)  # type: ignore[arg-type,return-value]
        return [{"year": r.year, "value_per_100k": r.value_per_100k} for r in rows]

    def highest_prevalence(self, top_n: int = 5) -> List[PrevalenceRecord]:
        if top_n <= 0:
            raise PrevalenceError("top_n must be positive")
        return sorted(self._records, key=lambda r: r.value_per_100k, reverse=True)[:top_n]

    def available_regions(self, disease_id: str) -> List[str]:
        return sorted({r.region for r in self.for_disease(disease_id)})

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "records": len(self._records),
                "diseases": len({r.disease_id for r in self._records})}


def self_test() -> bool:
    analyzer = DiseasePrevalenceAnalyzer()
    analyzer.add(PrevalenceRecord("D1", "EU", "2020", 500.0, year=2020))
    analyzer.add(PrevalenceRecord("D1", "EU", "2022", 700.0, year=2022))
    analyzer.add(PrevalenceRecord("D1", "US", "2020", 650.0, year=2020))
    assert analyzer.region_comparison("D1") == {"EU": 600.0, "US": 650.0}
    ts = analyzer.time_series("D1", "EU")
    assert [p["year"] for p in ts] == [2020, 2022]
    assert analyzer.highest_prevalence(1)[0].value_per_100k == 700.0
    assert analyzer.available_regions("D1") == ["EU", "US"]
    print("011 disease_prevalence_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
