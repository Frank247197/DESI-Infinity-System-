# DESI∞ INFINITY SYSTEM — Probability and Statistics Engine
# Version: 6.2.0
# Module: probability_statistics_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Probability and Statistics Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def descriptive_statistics(values: list[float]) -> dict:
    """Return mean, median, variance, and standard deviation."""
    import math
    if not values:
        raise ValueError("At least one value is required.")
    data = sorted(float(x) for x in values)
    if any(not math.isfinite(x) for x in data):
        raise ValueError("Values must be finite.")
    n = len(data)
    mean = sum(data) / n
    median = (
        data[n // 2] if n % 2
        else (data[n // 2 - 1] + data[n // 2]) / 2
    )
    variance = sum((x - mean) ** 2 for x in data) / n
    return {
        "count": n,
        "mean": mean,
        "median": median,
        "variance": variance,
        "standard_deviation": math.sqrt(variance),
        "minimum": data[0],
        "maximum": data[-1]
    }
