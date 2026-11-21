# DESI∞ INFINITY SYSTEM — Scientific Discovery Engine
# Version: 6.2.0
# Module: scientific_discovery_engine.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Scientific Discovery Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def rank_hypotheses(records: list[dict]) -> list[dict]:
    """Expected fields: name, evidence_score, reproducibility_score, falsifiability_score."""
    keys = (
        "evidence_score",
        "reproducibility_score",
        "falsifiability_score"
    )
    ranked = []
    for item in records:
        if any(key not in item for key in keys):
            raise ValueError("Hypothesis record is incomplete.")
        if any(not 0 <= item[key] <= 1 for key in keys):
            raise ValueError("Scores must be in [0,1].")
        score = sum(item[key] for key in keys) / 3
        ranked.append({
            "name": str(item.get("name", "unnamed")),
            "score": score,
            "evidence": dict(item)
        })
    return sorted(
        ranked,
        key=lambda x: x["score"],
        reverse=True
    )
