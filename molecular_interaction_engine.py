# DESI∞ INFINITY SYSTEM — Molecular Interaction Engine
# Version: 6.2.0
# Module: molecular_interaction_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Molecular Interaction Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

COULOMB_CONSTANT = 8.9875517923e9

def coulomb_energy(
    charges_c: list[float],
    positions_m: list[tuple[float, float, float]]
) -> float:
    """Pairwise electrostatic potential energy in joules in vacuum."""
    if len(charges_c) != len(positions_m):
        raise ValueError("Each charge needs a position.")
    energy = 0.0
    for i in range(len(charges_c)):
        for j in range(i + 1, len(charges_c)):
            distance = sum(
                (positions_m[i][k] - positions_m[j][k]) ** 2
                for k in range(3)
            ) ** 0.5
            if distance == 0:
                raise ValueError(
                    "Distinct charges cannot occupy identical coordinates."
                )
            energy += (
                COULOMB_CONSTANT * charges_c[i] * charges_c[j] / distance
            )
    return energy
