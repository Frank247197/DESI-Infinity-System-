# DESI∞ INFINITY SYSTEM — Scientific Hypothesis Engine
# Version: 6.2.0
# Module: scientific_hypothesis_engine.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Scientific Hypothesis Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def evaluate_hypothesis(
    predicted: dict[str, float],
    observed: dict[str, float],
    tolerance: float = 0.05
) -> dict:
    if set(predicted) != set(observed) or tolerance < 0:
        raise ValueError(
            "Keys must match and tolerance must be non-negative."
        )
    errors = {
        key: abs(predicted[key] - observed[key])
        for key in predicted
    }
    passed = {
        key: errors[key] <= tolerance
        for key in errors
    }
    return {
        "errors": errors,
        "within_tolerance": passed,
        "overall_match": all(passed.values())
    }
