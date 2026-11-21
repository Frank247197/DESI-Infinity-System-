"""DESI Infinity System - Gene Expression Analyzer (v6.2.0).

Stores gene expression measurements (log2 TPM, fold change) with tissue
and condition annotations. Provides differential-expression helpers.
Research-only; no clinical interpretation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CONDITIONS = ("normal", "tumor", "disease", "treated", "untreated",
              "knockout", "other")
SOURCES = ("curated", "literature", "predicted")


class GeneExpressionError(Exception):
    """Base gene expression error."""


@dataclass
class ExpressionMeasurement:
    measurement_id: str
    gene_symbol: str
    tissue: str
    condition: str
    log2_tpm: Optional[float] = None
    fold_change: Optional[float] = None
    p_value: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.measurement_id or not isinstance(self.measurement_id, str):
            raise GeneExpressionError("measurement_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise GeneExpressionError("gene_symbol required")
        if not self.tissue or not isinstance(self.tissue, str):
            raise GeneExpressionError("tissue required")
        if self.condition not in CONDITIONS:
            raise GeneExpressionError(f"invalid condition: {self.condition!r}")
        if self.source not in SOURCES:
            raise GeneExpressionError(f"invalid source: {self.source!r}")
        if self.log2_tpm is not None and not isinstance(self.log2_tpm, (int, float)):
            raise GeneExpressionError("log2_tpm must be numeric or None")
        if self.p_value is not None:
            if not isinstance(self.p_value, (int, float)) or not 0.0 <= float(self.p_value) <= 1.0:
                raise GeneExpressionError("p_value must be in [0, 1] or None")

    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value is not None and self.p_value < alpha


class GeneExpressionAnalyzer:
    """Expression store with differential and rank queries."""

    def __init__(self) -> None:
        self._measurements: Dict[str, ExpressionMeasurement] = {}
        self._gene_index: Dict[str, List[str]] = {}
        self._tissue_index: Dict[str, List[str]] = {}

    def add(self, m: ExpressionMeasurement) -> ExpressionMeasurement:
        if m.measurement_id in self._measurements:
            raise GeneExpressionError(f"duplicate measurement_id: {m.measurement_id}")
        self._measurements[m.measurement_id] = m
        self._gene_index.setdefault(m.gene_symbol, []).append(m.measurement_id)
        self._tissue_index.setdefault(m.tissue, []).append(m.measurement_id)
        return m

    def get(self, measurement_id: str) -> ExpressionMeasurement:
        try:
            return self._measurements[measurement_id]
        except KeyError as exc:
            raise GeneExpressionError(
                f"unknown measurement_id: {measurement_id}") from exc

    def for_gene(self, gene_symbol: str) -> List[ExpressionMeasurement]:
        return [self.get(mid) for mid in self._gene_index.get(gene_symbol, [])]

    def for_tissue(self, tissue: str) -> List[ExpressionMeasurement]:
        return [self.get(mid) for mid in self._tissue_index.get(tissue, [])]

    def differential(self, gene_symbol: str, alpha: float = 0.05
                     ) -> List[ExpressionMeasurement]:
        return [m for m in self.for_gene(gene_symbol) if m.is_significant(alpha)]

    def upregulated(self, gene_symbol: str, min_fc: float = 2.0
                    ) -> List[ExpressionMeasurement]:
        return [m for m in self.for_gene(gene_symbol)
                if m.fold_change is not None and m.fold_change >= min_fc]

    def downregulated(self, gene_symbol: str, max_fc: float = 0.5
                      ) -> List[ExpressionMeasurement]:
        return [m for m in self.for_gene(gene_symbol)
                if m.fold_change is not None and m.fold_change <= max_fc]

    def highest_expression(self, tissue: str, top_n: int = 5
                           ) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise GeneExpressionError("top_n must be positive")
        rows = [{"gene_symbol": m.gene_symbol, "log2_tpm": m.log2_tpm}
                for m in self.for_tissue(tissue) if m.log2_tpm is not None]
        rows.sort(key=lambda r: r["log2_tpm"], reverse=True)  # type: ignore
        return rows[:top_n]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "measurements": len(self._measurements),
            "genes": len(self._gene_index),
            "tissues": len(self._tissue_index),
        }


def self_test() -> bool:
    analyzer = GeneExpressionAnalyzer()
    analyzer.add(ExpressionMeasurement(
        "M1", "TP53", "breast", "normal", log2_tpm=6.2, fold_change=1.0, p_value=0.5))
    analyzer.add(ExpressionMeasurement(
        "M2", "TP53", "breast", "tumor", log2_tpm=8.5, fold_change=3.2, p_value=0.001))
    analyzer.add(ExpressionMeasurement(
        "M3", "CDKN1A", "breast", "tumor", log2_tpm=9.1, fold_change=0.4, p_value=0.002))
    assert len(analyzer.for_gene("TP53")) == 2
    assert len(analyzer.differential("TP53")) == 1
    assert analyzer.upregulated("TP53", 2.0)[0].measurement_id == "M2"
    assert analyzer.downregulated("CDKN1A", 0.5)[0].measurement_id == "M3"
    top = analyzer.highest_expression("breast", 1)
    assert top[0]["gene_symbol"] == "CDKN1A"
    print("gene_expression_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
