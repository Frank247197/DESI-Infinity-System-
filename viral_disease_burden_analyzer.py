"""DESI Infinity System - Viral Disease Burden Analyzer (v6.2.0).

Models disease burden metrics: DALYs, YLLs, YLDs, mortality, and
morbidity per virus/region/year. Research data only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

BURDEN_METRICS = ("dalys", "ylls", "ylds", "deaths", "incidence",
                  "prevalence", "other")
SOURCES = ("curated", "literature", "predicted")


class BurdenError(Exception):
    """Base burden error."""


@dataclass
class BurdenRecord:
    record_id: str
    virus_id: str
    region: str
    year: int
    metric: str
    value: float
    per_100k: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not isinstance(self.record_id, str):
            raise BurdenError("record_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise BurdenError("virus_id required")
        if self.metric not in BURDEN_METRICS:
            raise BurdenError(f"invalid metric: {self.metric!r}")
        if self.source not in SOURCES:
            raise BurdenError(f"invalid source: {self.source!r}")
        if not isinstance(self.year, int) or not (1900 <= self.year <= 2100):
            raise BurdenError("year must be a 4-digit year")
        if not isinstance(self.value, (int, float)) or self.value < 0:
            raise BurdenError("value must be non-negative numeric")


class ViralDiseaseBurdenAnalyzer:
    """Aggregates burden metrics across regions/years."""

    def __init__(self) -> None:
        self._records: List[BurdenRecord] = []
        self._virus_index: Dict[str, List[int]] = {}

    def add(self, record: BurdenRecord) -> None:
        idx = len(self._records)
        self._records.append(record)
        self._virus_index.setdefault(record.virus_id, []).append(idx)

    def for_virus(self, virus_id: str) -> List[BurdenRecord]:
        return [self._records[i] for i in self._virus_index.get(virus_id, [])]

    def for_metric(self, virus_id: str, metric: str) -> List[BurdenRecord]:
        if metric not in BURDEN_METRICS:
            raise BurdenError(f"invalid metric: {metric!r}")
        return [r for r in self.for_virus(virus_id) if r.metric == metric]

    def total_by_metric(self, virus_id: str, metric: str) -> float:
        return round(sum(r.value for r in self.for_metric(virus_id, metric)), 2)

    def regional_breakdown(self, virus_id: str, metric: str) -> Dict[str, float]:
        grouped: Dict[str, float] = {}
        for r in self.for_metric(virus_id, metric):
            grouped[r.region] = grouped.get(r.region, 0.0) + r.value
        return {k: round(v, 2) for k, v in grouped.items()}

    def highest_burden_region(self, virus_id: str, metric: str) -> Optional[str]:
        grouped = self.regional_breakdown(virus_id, metric)
        if not grouped:
            return None
        return max(grouped, key=lambda k: grouped[k])

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "viruses": len(self._virus_index),
        }


def self_test() -> bool:
    analyzer = ViralDiseaseBurdenAnalyzer()
    analyzer.add(BurdenRecord("B1", "VS_hiv1", "AFR", 2020, "dalys", 25000000))
    analyzer.add(BurdenRecord("B2", "VS_hiv1", "EU", 2020, "dalys", 500000))
    analyzer.add(BurdenRecord("B3", "VS_hiv1", "AFR", 2020, "deaths", 450000))
    assert len(analyzer.for_virus("VS_hiv1")) == 3
    assert len(analyzer.for_metric("VS_hiv1", "dalys")) == 2
    assert analyzer.total_by_metric("VS_hiv1", "dalys") == 25500000.0
    assert analyzer.highest_burden_region("VS_hiv1", "dalys") == "AFR"
    breakdown = analyzer.regional_breakdown("VS_hiv1", "dalys")
    assert breakdown["AFR"] == 25000000.0
    print("viral_disease_burden_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
