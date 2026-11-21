# DESI∞ INFINITY SYSTEM — Molecular Dynamics Research Engine
# Version: 6.2.0
# Module: molecular_dynamics_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Molecular Dynamics Research Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def lennard_jones_energy(
    distance: float,
    epsilon: float = 1.0,
    sigma: float = 1.0
) -> float:
    """Dimensionless Lennard-Jones 12-6 potential; not a production MD force field."""
    if distance <= 0 or epsilon < 0 or sigma <= 0:
        raise ValueError(
            "distance and sigma must be positive; epsilon non-negative."
        )
    ratio = sigma / distance
    r6 = ratio ** 6
    return 4 * epsilon * (r6 * r6 - r6)

def pair_energy(
    positions: list[tuple[float, float, float]],
    epsilon: float = 1.0,
    sigma: float = 1.0
) -> float:
    total = 0.0
    for i, a in enumerate(positions):
        for b in positions[i + 1:]:
            distance = sum(
                (a[k] - b[k]) ** 2 for k in range(3)
            ) ** 0.5
            total += lennard_jones_energy(distance, epsilon, sigma)
    return total
