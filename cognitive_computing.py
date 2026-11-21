# DESI∞ INFINITY SYSTEM — Cognitive Computing
# Version: 6.2.0
# Module: cognitive_computing.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Cognitive Computing"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def aggregate_evidence(
    evidence: dict[str, float],
    weights: dict[str, float]
) -> dict:
    """Compute normalized weighted score; inputs are model scores, not human diagnoses."""
    if set(evidence) != set(weights):
        raise ValueError("Evidence and weights must have identical keys.")
    if any(not 0 <= v <= 1 for v in evidence.values()):
        raise ValueError("Evidence scores must be in [0,1].")
    if any(not 0 <= w <= 1 for w in weights.values()):
        raise ValueError("Weights must be in [0,1].")
    total = sum(weights.values())
    score = (
        sum(evidence[k] * weights[k] for k in evidence) / total
        if total else 0.0
    )
    return {
        "score": score,
        "weight_total": total,
        "contributions": {
            k: evidence[k] * weights[k] for k in evidence
        }
    }
