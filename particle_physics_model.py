# DESI∞ INFINITY SYSTEM — Particle Physics Model
# Version: 6.2.0
# Module: particle_physics_model.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Particle Physics Model"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def relativistic_energy(
    mass_kg: float,
    velocity_m_s: float,
    light_speed_m_s: float = 299792458.0
) -> float:
    """Calculate total relativistic energy in joules."""
    if mass_kg < 0 or light_speed_m_s <= 0:
        raise ValueError("Mass must be non-negative and light speed positive.")
    if abs(velocity_m_s) >= light_speed_m_s:
        raise ValueError("Velocity magnitude must be below light speed.")
    import math
    gamma = 1.0 / math.sqrt(
        1.0 - (velocity_m_s / light_speed_m_s) ** 2
    )
    return gamma * mass_kg * light_speed_m_s ** 2

def rest_energy(mass_kg: float) -> float:
    if mass_kg < 0:
        raise ValueError("Mass must be non-negative.")
    return mass_kg * 299792458.0 ** 2
