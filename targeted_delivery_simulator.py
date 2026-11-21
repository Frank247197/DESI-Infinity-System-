# DESI∞ INFINITY SYSTEM — Targeted Delivery Research Simulator
# Version: 6.2.0
# Module: targeted_delivery_simulator.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Targeted Delivery Research Simulator"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

import math

def release_fraction(time_s: float, rate_per_s: float) -> float:
    """Fraction released by a first-order process, bounded between zero and one."""
    if time_s < 0 or rate_per_s < 0:
        raise ValueError("Time and rate must be non-negative.")
    return 1.0 - math.exp(-rate_per_s * time_s)

def release_curve(
    times_s: list[float],
    rate_per_s: float
) -> list[float]:
    if any(t < 0 for t in times_s):
        raise ValueError("Times must be non-negative.")
    return [
        release_fraction(t, rate_per_s) for t in times_s
    ]
