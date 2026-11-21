# DESI∞ INFINITY SYSTEM — Nanocarrier Research Optimizer
# Version: 6.2.0
# Module: nanocarrier_optimizer.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Nanocarrier Research Optimizer"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def rank_candidates(
    candidates: list[dict[str, float]],
    weights: dict[str, float]
) -> list[dict]:
    """Higher-is-better normalized scoring; criteria must already be on a 0..1 scale."""
    if not weights or any(w < 0 for w in weights.values()):
        raise ValueError("Weights must be non-negative.")
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("At least one weight must be positive.")
    ranked = []
    for candidate in candidates:
        if set(weights) - set(candidate):
            raise ValueError("Candidate is missing a weighted criterion.")
        if any(not 0 <= candidate[k] <= 1 for k in weights):
            raise ValueError("Scores must be normalized to [0,1].")
        score = sum(
            candidate[k] * weights[k] for k in weights
        ) / total
        ranked.append({"candidate": candidate, "score": score})
    return sorted(
        ranked,
        key=lambda x: x["score"],
        reverse=True
    )
