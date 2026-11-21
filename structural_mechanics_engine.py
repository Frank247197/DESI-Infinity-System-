# DESI∞ INFINITY SYSTEM — Structural Mechanics Engine
# Version: 6.2.0
# Module: structural_mechanics_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Structural Mechanics Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def axial_deformation(
    force_n: float,
    length_m: float,
    area_m2: float,
    youngs_modulus_pa: float
) -> float:
    """Calculate small-strain axial deformation of a uniform bar."""
    if min(length_m, area_m2, youngs_modulus_pa) <= 0:
        raise ValueError("Length, area, and modulus must be positive.")
    return force_n * length_m / (area_m2 * youngs_modulus_pa)

def factor_of_safety(
    failure_load_n: float,
    applied_load_n: float
) -> float:
    if failure_load_n < 0 or applied_load_n <= 0:
        raise ValueError("Failure load must be non-negative; applied load positive.")
    return failure_load_n / applied_load_n
