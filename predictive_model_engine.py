# DESI∞ INFINITY SYSTEM — Predictive Model Engine
# Version: 6.2.0
# Module: predictive_model_engine.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Predictive Model Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def fit_linear(
    x: list[float],
    y: list[float]
) -> dict:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Need at least two paired observations.")
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    denominator = sum((value - mean_x) ** 2 for value in x)
    if denominator == 0:
        raise ValueError("Predictor values must vary.")
    slope = sum(
        (a - mean_x) * (b - mean_y)
        for a, b in zip(x, y)
    ) / denominator
    intercept = mean_y - slope * mean_x
    return {
        "slope": slope,
        "intercept": intercept,
        "predict": lambda value: slope * value + intercept
    }
