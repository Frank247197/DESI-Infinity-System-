"""DESI Infinity System - Epigenomic Data Engine (v6.2.0).

Stores epigenomic datasets (ChIP-seq, ATAC-seq, bisulfite-seq, Hi-C)
with sample metadata, QC metrics, and processed-file references. Data
catalogue only — no processing pipeline execution.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ASSAY_TYPES = ("chip_seq", "atac_seq", "bisulfite_seq", "hic", "cut_and_run",
               "methylation_array", "other")
ORGANISMS = ("human", "mouse", "other")
QC_STATUS = ("pass", "warn", "fail", "unknown")
SOURCES = ("curated", "literature", "predicted")


class EpigenomicDataError(Exception):
    """Base epigenomic data error."""


@dataclass
class EpigenomicDataset:
    dataset_id: str
    assay_type: str
    organism: str
    tissue: str
    mark_or_factor: str = ""
    sample_count: int = 0
    genome_build: str = ""
    file_url: str = ""
    qc_status: str = "unknown"
    qc_metrics: Dict[str, float] = field(default_factory=dict)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.dataset_id or not isinstance(self.dataset_id, str):
            raise EpigenomicDataError("dataset_id required")
        if self.assay_type not in ASSAY_TYPES:
            raise EpigenomicDataError(f"invalid assay_type: {self.assay_type!r}")
        if self.organism not in ORGANISMS:
            raise EpigenomicDataError(f"invalid organism: {self.organism!r}")
        if self.qc_status not in QC_STATUS:
            raise EpigenomicDataError(f"invalid qc_status: {self.qc_status!r}")
        if self.source not in SOURCES:
            raise EpigenomicDataError(f"invalid source: {self.source!r}")
        if not isinstance(self.sample_count, int) or self.sample_count < 0:
            raise EpigenomicDataError("sample_count must be non-negative int")


class EpigenomicDataEngine:
    """Dataset catalogue with assay / organism / QC queries."""

    def __init__(self) -> None:
        self._datasets: Dict[str, EpigenomicDataset] = {}
        self._assay_index: Dict[str, List[str]] = {}
        self._factor_index: Dict[str, List[str]] = {}

    def add(self, dataset: EpigenomicDataset) -> EpigenomicDataset:
        if dataset.dataset_id in self._datasets:
            raise EpigenomicDataError(f"duplicate dataset_id: {dataset.dataset_id}")
        self._datasets[dataset.dataset_id] = dataset
        self._assay_index.setdefault(dataset.assay_type, []).append(dataset.dataset_id)
        if dataset.mark_or_factor:
            self._factor_index.setdefault(dataset.mark_or_factor, []).append(
                dataset.dataset_id)
        return dataset

    def get(self, dataset_id: str) -> EpigenomicDataset:
        try:
            return self._datasets[dataset_id]
        except KeyError as exc:
            raise EpigenomicDataError(f"unknown dataset_id: {dataset_id}") from exc

    def by_assay(self, assay_type: str) -> List[EpigenomicDataset]:
        if assay_type not in ASSAY_TYPES:
            raise EpigenomicDataError(f"invalid assay_type: {assay_type!r}")
        return [self.get(did) for did in self._assay_index.get(assay_type, [])]

    def by_factor(self, factor: str) -> List[EpigenomicDataset]:
        return [self.get(did) for did in self._factor_index.get(factor, [])]

    def passing_qc(self) -> List[EpigenomicDataset]:
        return [d for d in self._datasets.values() if d.qc_status == "pass"]

    def failures(self) -> List[EpigenomicDataset]:
        return [d for d in self._datasets.values() if d.qc_status == "fail"]

    def total_samples(self, assay_type: str = None) -> int:
        if assay_type is None:
            return sum(d.sample_count for d in self._datasets.values())
        return sum(d.sample_count for d in self.by_assay(assay_type))

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "datasets": len(self._datasets),
            "passing_qc": len(self.passing_qc()),
            "failing_qc": len(self.failures()),
            "samples": self.total_samples(),
        }


def self_test() -> bool:
    engine = EpigenomicDataEngine()
    engine.add(EpigenomicDataset(
        "D1", "chip_seq", "human", "liver", "H3K27ac",
        sample_count=12, genome_build="GRCh38",
        qc_status="pass", qc_metrics={"FRiP": 0.35, "NSC": 1.12}))
    engine.add(EpigenomicDataset(
        "D2", "atac_seq", "human", "liver", "",
        sample_count=8, genome_build="GRCh38", qc_status="pass"))
    engine.add(EpigenomicDataset(
        "D3", "bisulfite_seq", "human", "liver", "5mC",
        sample_count=4, genome_build="GRCh38", qc_status="fail"))
    assert len(engine.by_assay("chip_seq")) == 1
    assert engine.by_factor("H3K27ac")[0].dataset_id == "D1"
    assert len(engine.passing_qc()) == 2
    assert len(engine.failures()) == 1
    assert engine.total_samples() == 24
    assert engine.total_samples("chip_seq") == 12
    print("epigenomic_data_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
