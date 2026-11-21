# DESI∞ INFINITY SYSTEM — Organ System Model
# Version: 6.2.0
# Module: organ_system_model.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Organ System Model"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def exchange_step(
    compartments: dict[str, float],
    transfers: list[tuple[str, str, float]],
    dt: float
) -> dict:
    """Transfer amount = rate * source amount * dt; small dt is recommended."""
    if dt < 0:
        raise ValueError("dt must be non-negative.")
    delta = {k: 0.0 for k in compartments}
    for source, target, rate in transfers:
        if (
            source not in compartments
            or target not in compartments
            or rate < 0
        ):
            raise ValueError("Invalid transfer definition.")
        amount = rate * compartments[source] * dt
        if amount > compartments[source] + delta[source] + 1e-12:
            raise ValueError(
                "Step would remove more than the available amount; reduce dt."
            )
        delta[source] -= amount
        delta[target] += amount
    result = {
        k: v + delta[k] for k, v in compartments.items()
    }
    if any(v < -1e-10 for v in result.values()):
        raise ValueError("Negative compartment state.")
    return {k: max(0.0, v) for k, v in result.items()}
