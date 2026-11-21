# DESI∞ INFINITY SYSTEM — Regenerative Medicine Research Model
# Version: 6.2.0
# Module: regenerative_medicine_model.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Regenerative Medicine Research Model"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def logistic_growth(
    initial: float,
    rate: float,
    capacity: float,
    time_points: list[float]
) -> list[float]:
    """Closed-form logistic curve; abstract population model, not tissue prediction."""
    import math

    if initial <= 0 or capacity <= 0 or initial > capacity or rate < 0:
        raise ValueError(
            "Require 0 < initial <= capacity and rate >= 0."
        )
    return [
        capacity / (
            1 + ((capacity - initial) / initial) * math.exp(-rate * t)
        )
        for t in time_points
    ]
