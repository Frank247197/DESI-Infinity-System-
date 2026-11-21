# DESI∞ INFINITY SYSTEM — Genome Evolution
# Version: 6.2.0
# Module: genome_evolution.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Genome Evolution"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def compare_sequences(reference: str, sample: str) -> dict:
    """Compare equal-length aligned sequences; this is not a clinical interpretation."""
    a, b = reference.upper().strip(), sample.upper().strip()
    allowed = set("ACGTN")
    if not a or len(a) != len(b):
        raise ValueError("Sequences must be non-empty and equally aligned.")
    if set(a + b) - allowed:
        raise ValueError("Sequences may contain only A, C, G, T, or N.")
    comparable = [
        (x, y) for x, y in zip(a, b) if "N" not in (x, y)
    ]
    changes = [
        (i, x, y)
        for i, (x, y) in enumerate(zip(a, b))
        if x != y and "N" not in (x, y)
    ]
    return {
        "length": len(a),
        "compared_sites": len(comparable),
        "substitutions": len(changes),
        "p_distance": len(changes) / len(comparable) if comparable else None,
        "differences": changes
    }
