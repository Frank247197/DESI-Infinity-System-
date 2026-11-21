# DESI∞ INFINITY SYSTEM — Thermal Management Engine
# Version: 6.2.0
# Module: thermal_management_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Thermal Management Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def cooling_power(
    mass_flow_kg_s: float,
    specific_heat_j_kg_k: float,
    temperature_drop_k: float
) -> float:
    """Estimate sensible heat transfer rate in watts."""
    if mass_flow_kg_s < 0 or specific_heat_j_kg_k < 0 or temperature_drop_k < 0:
        raise ValueError("Inputs must be non-negative.")
    return mass_flow_kg_s * specific_heat_j_kg_k * temperature_drop_k

def thermal_resistance(
    temperature_difference_k: float,
    heat_flow_w: float
) -> float:
    if heat_flow_w <= 0:
        raise ValueError("Heat flow must be positive.")
    return temperature_difference_k / heat_flow_w
