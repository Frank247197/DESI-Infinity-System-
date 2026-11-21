# DESI∞ INFINITY SYSTEM — Protein Folding Research
# Version: 6.2.0
# Module: protein_folding_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Protein Folding Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

HYDROPATHY = dict(zip(
    "ACDEFGHIKLMNPQRSTVWY",
    [
        1.8, 2.5, -3.5, -3.5, 2.8,
        -3.2, -3.2, -3.9, 4.5, -1.6,
        3.8, -3.5, -3.5, -3.5, -4.5,
        -0.8, -0.7, -0.9, -1.3, 4.2
    ]
))

def sequence_profile(sequence: str, window: int = 7) -> dict:
    """Return sliding-window hydropathy scores using the Kyte-Doolittle scale."""
    seq = sequence.strip().upper()
    if not seq or set(seq) - set(HYDROPATHY):
        raise ValueError("Use a non-empty standard amino-acid sequence.")
    if isinstance(window, bool) or not isinstance(window, int) or not 1 <= window <= len(seq):
        raise ValueError("window must be an integer between 1 and sequence length.")
    scores = [
        sum(HYDROPATHY[x] for x in seq[i:i + window]) / window
        for i in range(len(seq) - window + 1)
    ]
    return {
        "length": len(seq),
        "window": window,
        "hydropathy": scores,
        "mean_hydropathy": sum(HYDROPATHY[x] for x in seq) / len(seq)
    }
