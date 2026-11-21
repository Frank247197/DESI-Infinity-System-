# DESI∞ INFINITY SYSTEM — Nanomaterial Property Engine
# Version: 6.2.0
# Module: nanomaterial_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Nanomaterial Property Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

import math

def sphere_properties(
    radius_m: float,
    density_kg_m3: float
) -> dict:
    if radius_m <= 0 or density_kg_m3 <= 0:
        raise ValueError("Radius and density must be positive.")
    volume = 4 * math.pi * radius_m ** 3 / 3
    area = 4 * math.pi * radius_m ** 2
    return {
        "radius_m": radius_m,
        "surface_area_m2": area,
        "volume_m3": volume,
        "mass_kg": volume * density_kg_m3,
        "surface_to_volume_per_m": area / volume
    }
