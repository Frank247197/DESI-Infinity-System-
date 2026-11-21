# DESI∞ INFINITY SYSTEM — Thermodynamics Engine
# Version: 6.2.0
# Module: thermodynamics_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Thermodynamics Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def ideal_gas_pressure(
    moles: float,
    temperature_k: float,
    volume_m3: float
) -> float:
    """Calculate ideal-gas pressure in pascals."""
    gas_constant = 8.314462618
    if moles < 0 or temperature_k < 0 or volume_m3 <= 0:
        raise ValueError("Invalid ideal-gas inputs.")
    return moles * gas_constant * temperature_k / volume_m3

def heat_transfer(
    mass_kg: float,
    specific_heat_j_kg_k: float,
    temperature_change_k: float
) -> float:
    if mass_kg < 0 or specific_heat_j_kg_k < 0:
        raise ValueError("Mass and specific heat must be non-negative.")
    return mass_kg * specific_heat_j_kg_k * temperature_change_k
