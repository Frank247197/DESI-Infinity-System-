"""DESI Infinity System - Proteomics Engine (v6.2.0).

Protein abundance measurement store with PTMs, quantification method,
and sample condition. Provides differential and rank analyses.
Research-only annotations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PTM_TYPES = ("phosphorylation", "acetylation", "methylation",
             "ubiquitination", "glycosylation", "sumoylation", "none")
QUANT_METHODS = ("ms_dda", "ms_dia", "srm", "mrm", "antibody", "other")
CONDITIONS = ("normal", "tumor", "disease", "treated", "untreated", "other")
SOURCES = ("curated", "literature", "predicted")


class ProteomicsError(Exception):
    """Base proteomics error."""


@dataclass
class ProteinMeasurement:
    measurement_id: str
    protein_id: str
    gene_symbol: str
    tissue: str
    condition: str
    abundance: Optional[float] = None
    fold_change: Optional[float] = None
    ptm_type: str = "none"
    ptm_site: str = ""
    quant_method: str = "other"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.measurement_id or not isinstance(self.measurement_id, str):
            raise ProteomicsError("measurement_id required")
        if not self.protein_id or not isinstance(self.protein_id, str):
            raise ProteomicsError("protein_id required")
        if self.condition not in CONDITIONS:
            raise ProteomicsError(f"invalid condition: {self.condition!r}")
        if self.ptm_type not in PTM_TYPES:
            raise ProteomicsError(f"invalid ptm_type: {self.ptm_type!r}")
        if self.quant_method not in QUANT_METHODS:
            raise ProteomicsError(f"invalid quant_method: {self.quant_method!r}")
        if self.source not in SOURCES:
            raise ProteomicsError(f"invalid source: {self.source!r}")

    def is_upregulated(self, threshold: float = 1.5) -> bool:
        return self.fold_change is not None and self.fold_change >= threshold

    def is_downregulated(self, threshold: float = 0.67) -> bool:
        return self.fold_change is not None and self.fold_change <= threshold


class ProteomicsEngine:
    """Measurement store with protein / PTM / fold-change queries."""

    def __init__(self) -> None:
        self._measurements: Dict[str, ProteinMeasurement] = {}
        self._protein_index: Dict[str, List[str]] = {}
        self._ptm_index: Dict[str, List[str]] = {}

    def add(self, m: ProteinMeasurement) -> ProteinMeasurement:
        if m.measurement_id in self._measurements:
            raise ProteomicsError(f"duplicate measurement_id: {m.measurement_id}")
        self._measurements[m.measurement_id] = m
        self._protein_index.setdefault(m.protein_id, []).append(m.measurement_id)
        if m.ptm_type != "none":
            self._ptm_index.setdefault(m.ptm_type, []).append(m.measurement_id)
        return m

    def get(self, measurement_id: str) -> ProteinMeasurement:
        try:
            return self._measurements[measurement_id]
        except KeyError as exc:
            raise ProteomicsError(f"unknown measurement_id: {measurement_id}") from exc

    def for_protein(self, protein_id: str) -> List[ProteinMeasurement]:
        return [self.get(mid) for mid in self._protein_index.get(protein_id, [])]

    def by_ptm(self, ptm_type: str) -> List[ProteinMeasurement]:
        if ptm_type not in PTM_TYPES:
            raise ProteomicsError(f"invalid ptm_type: {ptm_type!r}")
        return [self.get(mid) for mid in self._ptm_index.get(ptm_type, [])]

    def upregulated(self, threshold: float = 1.5) -> List[ProteinMeasurement]:
        return [m for m in self._measurements.values()
                if m.is_upregulated(threshold)]

    def downregulated(self, threshold: float = 0.67) -> List[ProteinMeasurement]:
        return [m for m in self._measurements.values()
                if m.is_downregulated(threshold)]

    def top_abundance(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise ProteomicsError("top_n must be positive")
        rows = [{"protein_id": m.protein_id, "abundance": m.abundance}
                for m in self._measurements.values() if m.abundance is not None]
        rows.sort(key=lambda r: r["abundance"], reverse=True)  # type: ignore
        return rows[:top_n]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "measurements": len(self._measurements),
            "proteins": len(self._protein_index),
            "ptm_types": len(self._ptm_index),
        }


def self_test() -> bool:
    engine = ProteomicsEngine()
    engine.add(ProteinMeasurement(
        "PM1", "P04637", "TP53", "breast", "tumor",
        abundance=850.0, fold_change=2.3, quant_method="ms_dia"))
    engine.add(ProteinMeasurement(
        "PM2", "P04637", "TP53", "breast", "normal",
        abundance=370.0, fold_change=1.0, quant_method="ms_dia"))
    engine.add(ProteinMeasurement(
        "PM3", "P00533", "EGFR", "lung", "tumor",
        abundance=1200.0, fold_change=1.8,
        ptm_type="phosphorylation", ptm_site="Y1068",
        quant_method="ms_dia"))
    assert len(engine.for_protein("P04637")) == 2
    assert len(engine.by_ptm("phosphorylation")) == 1
    assert len(engine.upregulated(2.0)) == 1
    assert len(engine.downregulated(0.7)) == 0
    assert engine.top_abundance(1)[0]["protein_id"] == "P00533"
    print("proteomics_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
