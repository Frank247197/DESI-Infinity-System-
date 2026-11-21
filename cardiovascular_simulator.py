# DESI∞ INFINITY SYSTEM — Cardiovascular Simulator
# Version: 6.2.0
# Module: cardiovascular_simulator.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Cardiovascular Simulator"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def hemodynamics(
    mean_pressure_pa: float,
    flow_m3_s: float
) -> dict:
    """Compute hydraulic resistance and power; inputs must use SI units."""
    if flow_m3_s <= 0:
        raise ValueError("Flow must be positive.")
    resistance = mean_pressure_pa / flow_m3_s
    return {
        "pressure_pa": mean_pressure_pa,
        "flow_m3_s": flow_m3_s,
        "resistance_pa_s_m3": resistance,
        "hydraulic_power_w": mean_pressure_pa * flow_m3_s
    }
