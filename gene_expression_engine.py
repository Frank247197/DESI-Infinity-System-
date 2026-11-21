# DESI∞ INFINITY SYSTEM — Gene Expression Engine
# Version: 6.2.0
# Module: gene_expression_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Gene Expression Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

import math

def normalize_counts(
    counts: dict[str, list[float]],
    library_size: float = 1_000_000
) -> dict:
    """Return counts-per-million and log2 fold changes between first two samples."""
    if library_size <= 0:
        raise ValueError("library_size must be positive.")
    if not counts:
        return {"cpm": {}, "log2_fold_change": {}}
    width = {len(v) for v in counts.values()}
    if len(width) != 1 or not width or next(iter(width)) < 1:
        raise ValueError("Rows must have equal non-zero sample counts.")
    if any(x < 0 or not math.isfinite(x) for row in counts.values() for x in row):
        raise ValueError("Counts must be finite and non-negative.")
    totals = [
        sum(row[i] for row in counts.values())
        for i in range(next(iter(width)))
    ]
    cpm = {
        gene: [
            (x / totals[i] * library_size if totals[i] else 0.0)
            for i, x in enumerate(row)
        ]
        for gene, row in counts.items()
    }
    lfc = {
        gene: math.log2((values[1] + 0.5) / (values[0] + 0.5))
        if len(values) > 1 else None
        for gene, values in cpm.items()
    }
    return {"cpm": cpm, "log2_fold_change": lfc}
