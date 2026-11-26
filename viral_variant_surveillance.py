"""DESI Infinity System - Viral Variant Surveillance (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STATUS = ("VOC", "VOI", "VUM", "monitored", "deprecated")
REGIONS = ("global", "africa", "americas", "asia", "europe", "oceania")

@dataclass
class VariantRecord:
    variant_id: str
    virus_id: str
    lineage: str
    status: str
    prevalence_pct: float
    first_detected: str
    regions: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.variant_id or not self.virus_id:
            raise ValueError("IDs required")
        if self.status not in STATUS:
            raise ValueError(f"invalid status: {self.status}")
        if not (0.0 <= self.prevalence_pct <= 100.0):
            raise ValueError("prevalence must be 0-100")
        for r in self.regions:
            if r not in REGIONS:
                raise ValueError(f"invalid region: {r}")

class VariantSurveillance:
    def __init__(self) -> None:
        self._records: Dict[str, VariantRecord] = {}

    def add(self, record: VariantRecord) -> None:
        if record.variant_id in self._records:
            raise ValueError(f"duplicate variant_id: {record.variant_id}")
        self._records[record.variant_id] = record

    def get_vocs(self, virus_id: str) -> List[VariantRecord]:
        return [r for r in self._records.values() if r.virus_id == virus_id and r.status == "VOC"]

    def regional_prevalence(self, virus_id: str, region: str) -> float:
        if region not in REGIONS:
            raise ValueError("invalid region")
        recs = [r for r in self._records.values() if r.virus_id == virus_id and region in r.regions]
        return round(sum(r.prevalence_pct for r in recs), 2)

def self_test() -> bool:
    surv = VariantSurveillance()
    surv.add(VariantRecord("V1", "VS_sars2", "B.1.1.7", "VOC", 60.0, "2020-09", ["europe", "americas"]))
    surv.add(VariantRecord("V2", "VS_sars2", "B.1.351", "VOC", 20.0, "2020-10", ["africa"]))
    surv.add(VariantRecord("V3", "VS_sars2", "B.1.621", "VOI", 5.0, "2021-01", ["americas"]))
    
    assert len(surv.get_vocs("VS_sars2")) == 2
    assert surv.regional_prevalence("VS_sars2", "americas") == 65.0
    assert surv.regional_prevalence("VS_sars2", "europe") == 60.0
    print("viral_variant_surveillance: OK")
    return True

if __name__ == "__main__":
    self_test()
