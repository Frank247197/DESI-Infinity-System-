# DESI∞ INFINITY SYSTEM — Neurodegeneration Research Model
# Version: 6.2.0
# Module: neurodegeneration_model.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Neurodegeneration Research Model"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def simulate_marker(
    initial: float,
    rate: float,
    years: int,
    intervention_factor: float = 1.0
) -> list[float]:
    """Exponential marker model; parameters are hypothetical and not clinical predictions."""
    import math

    if initial < 0 or rate < 0 or years < 0 or intervention_factor < 0:
        raise ValueError("Inputs must be non-negative.")
    effective = rate * intervention_factor
    return [
        initial * math.exp(effective * t)
        for t in range(years + 1)
    ]
