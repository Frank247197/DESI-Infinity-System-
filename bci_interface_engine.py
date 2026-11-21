# DESI∞ INFINITY SYSTEM — BCI Interface Research
# Version: 6.2.0
# Module: bci_interface_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — BCI Interface Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

import math

def extract_features(
    samples: list[float],
    sampling_rate_hz: float
) -> dict:
    """Compute mean, RMS, variance, and zero-crossing rate from a numeric signal."""
    if sampling_rate_hz <= 0 or not math.isfinite(sampling_rate_hz):
        raise ValueError("Sampling rate must be finite and positive.")
    if not samples or any(not math.isfinite(float(x)) for x in samples):
        raise ValueError("Provide finite signal samples.")
    values = [float(x) for x in samples]
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    crossings = sum(
        (a < 0 <= b) or (b < 0 <= a)
        for a, b in zip(values, values[1:])
    )
    return {
        "mean": mean,
        "rms": math.sqrt(sum(x * x for x in values) / len(values)),
        "variance": variance,
        "zero_crossing_rate": crossings / max(1, len(values) - 1),
        "duration_seconds": len(values) / sampling_rate_hz
    }
