"""DESI Infinity System - Rare Disease Analyzer (v6.2.0).

Tracks rare diseases against standard prevalence thresholds (EU < 5 per
10,000; US < 200,000 persons). Stores orphan designation status and
diagnostic delay metadata. Does not diagnose patients; organizes
documented rare disease research metadata.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

EU_RARE_THRESHOLD_PER_10K = 5.0
US_RARE_POPULATION_THRESHOLD = 200_000


class RareDiseaseError(Exception):
    """Base rare disease error."""


@dataclass
class RareDiseaseRecord:
    disease_id: str
    name: str
    prevalence_per_10k: Optional[float] = None
    affected_population: Optional[int] = None
    orphan_designation_regions: List[str] = field(default_factory=list)
    average_diagnostic_delay_years: Optional[float] = None
    inheritance: str = "unknown"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.disease_id or not self.name:
            raise RareDiseaseError("disease_id and name required")
        if self.prevalence_per_10k is not None:
            if not isinstance(self.prevalence_per_10k, (int, float)) or self.prevalence_per_10k < 0:
                raise RareDiseaseError("prevalence_per_10k must be non-negative or None")
        if self.affected_population is not None:
            if not isinstance(self.affected_population, int) or self.affected_population < 0:
                raise RareDiseaseError("affected_population must be non-negative int")

    def is_rare_eu(self) -> Optional[bool]:
        if self.prevalence_per_10k is None:
            return None
        return self.prevalence_per_10k < EU_RARE_THRESHOLD_PER_10K

    def is_rare_us(self) -> Optional[bool]:
        if self.affected_population is None:
            return None
        return self.affected_population < US_RARE_POPULATION_THRESHOLD

    def is_orphan_designated(self) -> bool:
        return bool(self.orphan_designation_regions)


class RareDiseaseAnalyzer:
    """Rare disease registry with criteria checks and summaries."""

    def __init__(self) -> None:
        self._records: Dict[str, RareDiseaseRecord] = {}

    def add(self, record: RareDiseaseRecord) -> None:
        if record.disease_id in self._records:
            raise RareDiseaseError(f"duplicate disease_id: {record.disease_id}")
        self._records[record.disease_id] = record

    def get(self, disease_id: str) -> RareDiseaseRecord:
        try:
            return self._records[disease_id]
        except KeyError as exc:
            raise RareDiseaseError(f"unknown disease_id: {disease_id}") from exc

    def orphans(self) -> List[RareDiseaseRecord]:
        return [r for r in self._records.values() if r.is_orphan_designated()]

    def rare_eu(self) -> List[RareDiseaseRecord]:
        return [r for r in self._records.values() if r.is_rare_eu() is True]

    def rare_us(self) -> List[RareDiseaseRecord]:
        return [r for r in self._records.values() if r.is_rare_us() is True]

    def by_inheritance(self, mode: str) -> List[RareDiseaseRecord]:
        return [r for r in self._records.values() if r.inheritance == mode]

    def long_diagnostic_delay(self, years_threshold: float = 5.0) -> List[RareDiseaseRecord]:
        return [r for r in self._records.values()
                if r.average_diagnostic_delay_years is not None
                and r.average_diagnostic_delay_years >= years_threshold]

    def criteria_coverage(self) -> Dict[str, int]:
        total = len(self._records)
        return {
            "total": total,
            "with_prevalence": sum(1 for r in self._records.values()
                                   if r.prevalence_per_10k is not None),
            "with_population": sum(1 for r in self._records.values()
                                   if r.affected_population is not None),
            "orphan": len(self.orphans()),
        }

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "records": len(self._records)}


def self_test() -> bool:
    a = RareDiseaseAnalyzer()
    a.add(RareDiseaseRecord("RD1", "Disease One", prevalence_per_10k=1.2,
                            affected_population=50_000, orphan_designation_regions=["EU"],
                            average_diagnostic_delay_years=7.5))
    a.add(RareDiseaseRecord("RD2", "Disease Two", prevalence_per_10k=4.9,
                            affected_population=300_000, average_diagnostic_delay_years=2.0))
    assert a.get("RD1").is_rare_eu() is True
    assert a.get("RD2").is_rare_us() is False
    assert len(a.orphans()) == 1
    assert len(a.long_diagnostic_delay(5.0)) == 1
    cov = a.criteria_coverage()
    assert cov["with_prevalence"] == 2 and cov["orphan"] == 1
    print("017 rare_disease_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
