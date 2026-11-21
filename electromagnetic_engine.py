# DESI∞ INFINITY SYSTEM — Electromagnetic Engine
# Version: 6.2.0
# Module: electromagnetic_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Electromagnetic Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

import math

def magnetic_force(
    charge_c: float,
    velocity_m_s: tuple[float, float, float],
    magnetic_field_t: tuple[float, float, float]
) -> tuple[float, float, float]:
    """Return q(v × B) in newtons."""
    if len(velocity_m_s) != 3 or len(magnetic_field_t) != 3:
        raise ValueError("Velocity and field must be three-dimensional.")
    vx, vy, vz = velocity_m_s
    bx, by, bz = magnetic_field_t
    return (
        charge_c * (vy * bz - vz * by),
        charge_c * (vz * bx - vx * bz),
        charge_c * (vx * by - vy * bx)
    )

def vector_magnitude(vector: tuple[float, ...]) -> float:
    return math.sqrt(sum(value ** 2 for value in vector))
