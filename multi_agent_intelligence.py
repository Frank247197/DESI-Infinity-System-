# DESI∞ INFINITY SYSTEM — Multi-Agent Intelligence
# Version: 6.2.0
# Module: multi_agent_intelligence.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Multi-Agent Intelligence"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def consensus(agent_outputs: list[dict]) -> dict:
    """Each output requires value and confidence in [0,1]; ties are reported."""
    if not agent_outputs:
        raise ValueError("At least one agent output is required.")
    totals = {}
    for item in agent_outputs:
        confidence = float(item["confidence"])
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be in [0,1].")
        key = str(item["value"])
        totals[key] = totals.get(key, 0.0) + confidence

    best = max(totals.values())
    winners = sorted(k for k, v in totals.items() if v == best)
    denominator = sum(totals.values())

    return {
        "winner": winners[0] if len(winners) == 1 else None,
        "ties": winners if len(winners) > 1 else [],
        "weighted_votes": totals,
        "normalized_support": {
            k: v / denominator for k, v in totals.items()
        } if denominator else {}
    }
