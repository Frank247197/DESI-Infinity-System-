"""DESI Infinity System - Viral Epidemiology Analyzer (v6.2.0).

Aggregates viral epidemiological records (incidence, prevalence,
mortality, CFR) with region/year strata. Missing data is reported, not
fabricated. All values are research estimates.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

METRICS = ("incidence_per_100k", "prevalence_per_100k",
           "mortality_per_100k", "case_fatality_ratio")
SOURCES = ("curated", "literature", "predicted")


class ViralEpidemiologyError(Exception):
    """Base epidemiology error."""


@dataclass
class EpiRecord:
    record_id: str
    virus_id: str
    region: str
    year: int
    metric: str
    value: float
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not isinstance(self.record_id, str):
            raise ViralEpidemiologyError("record_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise ViralEpidemiologyError("virus_id required")
        if self.metric not in METRICS:
            raise ViralEpidemiologyError(f"invalid metric: {self.metric!r}")
        if self.source not in SOURCES:
            raise ViralEpidemiologyError(f"invalid source: {self.source!r}")
        if not isinstance(self.year, int) or not (1900 <= self.year <= 2100):
            raise ViralEpidemiologyError("year must be a 4-digit year")
        if not isinstance(self.value, (int, float)) or self.value < 0:
            raise ViralEpidemiologyError("value must be non-negative numeric")


class ViralEpidemiologyAnalyzer:
    """Aggregations across region/year/metric."""

    def __init__(self) -> None:
        self._records: List[EpiRecord] = []
        self._virus_index: Dict[str, List[int]] = {}

    def add(self, record: EpiRecord) -> None:
        idx = len(self._records)
        self._records.append(record)
        self._virus_index.setdefault(record.virus_id, []).append(idx)

    def for_virus(self, virus_id: str) -> List[EpiRecord]:
        return [self._records[i] for i in self._virus_index.get(virus_id, [])]

    def for_metric(self, virus_id: str, metric: str) -> List[EpiRecord]:
        if metric not in METRICS:
            raise ViralEpidemiologyError(f"invalid metric: {metric!r}")
        return [r for r in self.for_virus(virus_id) if r.metric == metric]

    def mean_by_region(self, virus_id: str, metric: str) -> Dict[str, float]:
        recs = self.for_metric(virus_id, metric)
        grouped: Dict[str, List[float]] = {}
        for r in recs:
            grouped.setdefault(r.region, []).append(r.value)
        return {region: round(sum(vals) / len(vals), 4)
                for region, vals in grouped.items()}

    def time_series(self, virus_id: str, metric: str,
                    region: Optional[str] = None) -> List[Dict[str, object]]:
        recs = [r for r in self.for_metric(virus_id, metric)
                if region is None or r.region == region]
        recs.sort(key=lambda r: r.year)
        return [{"year": r.year, "region": r.region, "value": r.value}
                for r in recs]

    def highest_value(self, virus_id: str, metric: str) -> Optional[EpiRecord]:
        recs = self.for_metric(virus_id, metric)
        if not recs:
            return None
        return max(recs, key=lambda r: r.value)

    def coverage_status(self, virus_id: str) -> Dict[str, object]:
        recs = self.for_virus(virus_id)
        if not recs:
            return {"virus_id": virus_id, "status": "no_data"}
        metrics = {r.metric for r in recs}
        return {
            "virus_id": virus_id,
            "status": "ok",
            "records": len(recs),
            "metrics_present": sorted(metrics),
            "metrics_missing": [m for m in METRICS if m not in metrics],
        }

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "viruses": len(self._virus_index),
        }


def self_test() -> bool:
    analyzer = ViralEpidemiologyAnalyzer()
    analyzer.add(EpiRecord("E1", "VS_hiv1", "EU", 2020,
                            "prevalence_per_100k", 200.0))
    analyzer.add(EpiRecord("E2", "VS_hiv1", "AFR", 2020,
                            "prevalence_per_100k", 3500.0))
    analyzer.add(EpiRecord("E3", "VS_hiv1", "AFR", 2021,
                            "prevalence_per_100k", 3300.0))
    analyzer.add(EpiRecord("E4", "VS_hiv1", "GLOBAL", 2020,
                            "case_fatality_ratio", 0.015))
    assert len(analyzer.for_virus("VS_hiv1")) == 4
    assert len(analyzer.for_metric("VS_hiv1", "prevalence_per_100k")) == 3
    means = analyzer.mean_by_region("VS_hiv1", "prevalence_per_100k")
    assert means["AFR"] == 3400.0
    ts = analyzer.time_series("VS_hiv1", "prevalence_per_100k", "AFR")
    assert [p["year"] for p in ts] == [2020, 2021]
    assert analyzer.highest_value(
        "VS_hiv1", "prevalence_per_100k").value == 3500.0
    cov = analyzer.coverage_status("VS_hiv1")
    assert "incidence_per_100k" in cov["metrics_missing"]
    print("viral_epidemiology_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
