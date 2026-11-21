"""DESI Infinity System - Disease Epidemiology Engine (v6.2.0).

Aggregates prevalence, incidence, and mortality into epidemiological
summaries per disease/region/period. Reports data availability gaps
explicitly rather than fabricating metrics.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

METRIC_TYPES = ("prevalence", "incidence", "mortality", "case_fatality")
SOURCES = ("curated", "literature", "predicted")


class EpidemiologyError(Exception):
    """Base epidemiology error."""


@dataclass
class EpidemiologicMetric:
    disease_id: str
    region: str
    period: str
    metric_type: str
    value: float
    year: Optional[int] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise EpidemiologyError("disease_id required")
        if not self.region or not isinstance(self.region, str):
            raise EpidemiologyError("region required")
        if self.metric_type not in METRIC_TYPES:
            raise EpidemiologyError(f"invalid metric_type: {self.metric_type!r}")
        if not isinstance(self.value, (int, float)) or self.value < 0:
            raise EpidemiologyError("value must be non-negative numeric")
        if self.source not in SOURCES:
            raise EpidemiologyError(f"invalid source: {self.source!r}")

    def to_dict(self) -> Dict[str, object]:
        return {"disease_id": self.disease_id, "region": self.region,
                "period": self.period, "metric_type": self.metric_type,
                "value": self.value, "year": self.year, "source": self.source,
                "evidence_ids": list(self.evidence_ids)}


class DiseaseEpidemiologyEngine:
    """Epidemiologic metric store with aggregation and gap detection."""

    def __init__(self) -> None:
        self._metrics: List[EpidemiologicMetric] = []

    def add(self, metric: EpidemiologicMetric) -> None:
        self._metrics.append(metric)

    def for_disease(self, disease_id: str) -> List[EpidemiologicMetric]:
        return [m for m in self._metrics if m.disease_id == disease_id]

    def for_region(self, region: str) -> List[EpidemiologicMetric]:
        return [m for m in self._metrics if m.region == region]

    def by_type(self, metric_type: str) -> List[EpidemiologicMetric]:
        if metric_type not in METRIC_TYPES:
            raise EpidemiologyError(f"invalid metric_type: {metric_type!r}")
        return [m for m in self._metrics if m.metric_type == metric_type]

    def summary(self, disease_id: str) -> Dict[str, object]:
        recs = self.for_disease(disease_id)
        by_type: Dict[str, List[float]] = {}
        for r in recs:
            by_type.setdefault(r.metric_type, []).append(r.value)
        return {
            "disease_id": disease_id,
            "records": len(recs),
            "regions": sorted({r.region for r in recs}),
            "by_type": {k: {"count": len(v), "mean": round(sum(v) / len(v), 3)}
                        for k, v in by_type.items()},
            "available_types": sorted(by_type.keys()),
            "missing_types": [t for t in METRIC_TYPES if t not in by_type],
        }

    def region_table(self, disease_id: str) -> Dict[str, Dict[str, float]]:
        out: Dict[str, Dict[str, float]] = {}
        for r in self.for_disease(disease_id):
            out.setdefault(r.region, {})[r.metric_type] = r.value
        return out

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "metrics": len(self._metrics),
                "diseases": len({m.disease_id for m in self._metrics})}


def self_test() -> bool:
    eng = DiseaseEpidemiologyEngine()
    eng.add(EpidemiologicMetric("D1", "EU", "2022", "prevalence", 500.0, year=2022))
    eng.add(EpidemiologicMetric("D1", "EU", "2022", "incidence", 120.0, year=2022))
    eng.add(EpidemiologicMetric("D1", "US", "2022", "prevalence", 600.0, year=2022))
    s = eng.summary("D1")
    assert s["records"] == 3
    assert "mortality" in s["missing_types"]
    assert "prevalence" in eng.region_table("D1")["EU"]
    print("013 disease_epidemiology_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
