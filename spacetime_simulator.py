# DESI∞ INFINITY SYSTEM — Spacetime Research Simulator
# Version: 6.2.0
# Module: spacetime_simulator.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Spacetime Research Simulator"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def lorentz_factor(velocity_m_s: float, light_speed_m_s: float = 299792458.0) -> float:
    """Calculate the special-relativistic Lorentz factor."""
    if light_speed_m_s <= 0 or abs(velocity_m_s) >= light_speed_m_s:
        raise ValueError("Require positive light speed and |velocity| below light speed.")
    import math
    return 1.0 / math.sqrt(
        1.0 - (velocity_m_s / light_speed_m_s) ** 2
    )

def time_dilation(proper_time_s: float, velocity_m_s: float) -> float:
    if proper_time_s < 0:
        raise ValueError("Proper time must be non-negative.")
    return proper_time_s * lorentz_factor(velocity_m_s)
