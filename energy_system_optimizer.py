# DESI∞ INFINITY SYSTEM — Energy System Optimizer
# Version: 6.2.0
# Module: energy_system_optimizer.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Energy System Optimizer"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def size_storage(
    demand_wh: float,
    autonomy_hours: float,
    nominal_voltage_v: float,
    usable_fraction: float = 0.8
) -> dict:
    """Estimate idealized storage capacity; excludes real-world losses and safety margins."""
    if min(demand_wh, autonomy_hours, nominal_voltage_v) <= 0:
        raise ValueError("Demand, autonomy, and voltage must be positive.")
    if not 0 < usable_fraction <= 1:
        raise ValueError("Usable fraction must be in (0,1].")
    energy_wh = demand_wh * autonomy_hours / usable_fraction
    return {
        "required_energy_wh": energy_wh,
        "nominal_capacity_ah": energy_wh / nominal_voltage_v,
        "assumption": "Idealized estimate; not a certified battery design."
    }
