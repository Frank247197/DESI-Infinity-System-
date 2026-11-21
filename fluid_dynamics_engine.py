# DESI∞ INFINITY SYSTEM — Fluid Dynamics Engine
# Version: 6.2.0
# Module: fluid_dynamics_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Fluid Dynamics Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def reynolds_number(
    density_kg_m3: float,
    velocity_m_s: float,
    characteristic_length_m: float,
    dynamic_viscosity_pa_s: float
) -> float:
    """Calculate Reynolds number for a flowing fluid."""
    if min(density_kg_m3, characteristic_length_m, dynamic_viscosity_pa_s) <= 0:
        raise ValueError("Density, length, and viscosity must be positive.")
    return (
        density_kg_m3
        * abs(velocity_m_s)
        * characteristic_length_m
        / dynamic_viscosity_pa_s
    )

def volumetric_flow_rate(
    area_m2: float,
    velocity_m_s: float
) -> float:
    if area_m2 < 0:
        raise ValueError("Area must be non-negative.")
    return area_m2 * velocity_m_s
