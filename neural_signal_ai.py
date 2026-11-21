# DESI∞ INFINITY SYSTEM — Neural Signal Analysis
# Version: 6.2.0
# Module: neural_signal_ai.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Neural Signal Analysis"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def moving_average(values: list[float], window: int) -> list[float]:
    if isinstance(window, bool) or not isinstance(window, int) or window < 1 or window > len(values):
        raise ValueError("Invalid window.")
    if any(not __import__("math").isfinite(float(x)) for x in values):
        raise ValueError("Values must be finite.")
    prefix = [0.0]
    for x in values:
        prefix.append(prefix[-1] + float(x))
    return [
        (prefix[i + window] - prefix[i]) / window
        for i in range(len(values) - window + 1)
    ]

def detect_events(values: list[float], threshold: float) -> list[int]:
    if not __import__("math").isfinite(threshold):
        raise ValueError("Threshold must be finite.")
    return [i for i, x in enumerate(values) if x >= threshold]
