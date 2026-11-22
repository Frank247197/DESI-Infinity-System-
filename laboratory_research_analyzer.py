"""DESI Infinity System - Laboratory Research Analyzer (v6.2.0).

Structured storage of laboratory research measurements (assay type,
analyte, unit, reference range) with cohort-level aggregations.
Research data only; no clinical reference ranges are produced.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ASSAY_TYPES = ("immunoassay", "pcr", "sequencing", "mass_spec",
               "chromatography", "microscopy", "flow_cytometry", "other")
SAMPLE_TYPES = ("serum", "plasma", "whole_blood", "urine", "csf", "tissue",
                "saliva", "other")
SOURCES = ("curated", "literature", "predicted")


class LaboratoryResearchError(Exception):
    """Base laboratory research error."""


@dataclass
class LabMeasurement:
    measurement_id: str
    cohort_id: str
    assay_type: str
    sample_type: str
    analyte: str
    value: float
    unit: str
    group: str = "control"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.measurement_id or not isinstance(self.measurement_id, str):
            raise LaboratoryResearchError("measurement_id required")
        if not self.cohort_id or not isinstance(self.cohort_id, str):
            raise LaboratoryResearchError("cohort_id required")
        if self.assay_type not in ASSAY_TYPES:
            raise LaboratoryResearchError(f"invalid assay_type: {self.assay_type!r}")
        if self.sample_type not in SAMPLE_TYPES:
            raise LaboratoryResearchError(
                f"invalid sample_type: {self.sample_type!r}")
        if not self.analyte or not isinstance(self.analyte, str):
            raise LaboratoryResearchError("analyte required")
        if not self.unit or not isinstance(self.unit, str):
            raise LaboratoryResearchError("unit required")
        if not isinstance(self.value, (int, float)):
            raise LaboratoryResearchError("value must be numeric")
        if self.source not in SOURCES:
            raise LaboratoryResearchError(f"invalid source: {self.source!r}")


class LaboratoryResearchAnalyzer:
    """Measurement store with cohort and analyte aggregation."""

    def __init__(self) -> None:
        self._measurements: Dict[str, LabMeasurement] = {}
        self._cohort_index: Dict[str, List[str]] = {}
        self._analyte_index: Dict[str, List[str]] = {}

    def add(self, m: LabMeasurement) -> LabMeasurement:
        if m.measurement_id in self._measurements:
            raise LaboratoryResearchError(
                f"duplicate measurement_id: {m.measurement_id}")
        self._measurements[m.measurement_id] = m
        self._cohort_index.setdefault(m.cohort_id, []).append(m.measurement_id)
        self._analyte_index.setdefault(m.analyte, []).append(m.measurement_id)
        return m

    def get(self, measurement_id: str) -> LabMeasurement:
        try:
            return self._measurements[measurement_id]
        except KeyError as exc:
            raise LaboratoryResearchError(
                f"unknown measurement_id: {measurement_id}") from exc

    def for_cohort(self, cohort_id: str) -> List[LabMeasurement]:
        return [self.get(m) for m in self._cohort_index.get(cohort_id, [])]

    def for_analyte(self, analyte: str) -> List[LabMeasurement]:
        return [self.get(m) for m in self._analyte_index.get(analyte, [])]

    def mean_for_analyte(self, analyte: str, group: Optional[str] = None
                         ) -> Optional[float]:
        vals = [m.value for m in self.for_analyte(analyte)
                if group is None or m.group == group]
        if not vals:
            return None
        return round(sum(vals) / len(vals), 4)

    def compare_groups(self, analyte: str, group_a: str, group_b: str
                       ) -> Dict[str, object]:
        a = [m.value for m in self.for_analyte(analyte) if m.group == group_a]
        b = [m.value for m in self.for_analyte(analyte) if m.group == group_b]
        mean_a = round(sum(a) / len(a), 4) if a else None
        mean_b = round(sum(b) / len(b), 4) if b else None
        delta = (round(mean_a - mean_b, 4)
                 if mean_a is not None and mean_b is not None else None)
        return {"analyte": analyte, "n_a": len(a), "n_b": len(b),
                "mean_a": mean_a, "mean_b": mean_b, "delta": delta}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "measurements": len(self._measurements),
            "cohorts": len(self._cohort_index),
            "analytes": len(self._analyte_index),
        }


def self_test() -> bool:
    analyzer = LaboratoryResearchAnalyzer()
    analyzer.add(LabMeasurement(
        "M1", "C1", "immunoassay", "serum", "IL-6", 12.5, "pg/mL", "patient"))
    analyzer.add(LabMeasurement(
        "M2", "C1", "immunoassay", "serum", "IL-6", 15.3, "pg/mL", "patient"))
    analyzer.add(LabMeasurement(
        "M3", "C1", "immunoassay", "serum", "IL-6", 4.1, "pg/mL", "control"))
    analyzer.add(LabMeasurement(
        "M4", "C1", "immunoassay", "serum", "IL-6", 3.8, "pg/mL", "control"))
    assert len(analyzer.for_cohort("C1")) == 4
    assert len(analyzer.for_analyte("IL-6")) == 4
    assert analyzer.mean_for_analyte("IL-6", "patient") == 13.9
    cmp = analyzer.compare_groups("IL-6", "patient", "control")
    assert cmp["delta"] is not None and cmp["delta"] > 0
    print("laboratory_research_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
