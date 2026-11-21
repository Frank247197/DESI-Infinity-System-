# DESI∞ INFINITY SYSTEM — Quantum Materials Research
# Version: 6.2.0
# Module: quantum_materials_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Quantum Materials Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def band_gap_classification(band_gap_ev: float) -> str:
    """A simplified educational classification based on band-gap magnitude."""
    if band_gap_ev < 0:
        raise ValueError("Band gap cannot be negative.")
    if band_gap_ev == 0:
        return "metal_or_zero_gap"
    if band_gap_ev < 3.0:
        return "semiconductor_like"
    return "wide_band_gap_material"

def photon_wavelength_nm(energy_ev: float) -> float:
    """Calculate photon wavelength from energy using hc ≈ 1239.84 eV·nm."""
    if energy_ev <= 0:
        raise ValueError("Photon energy must be positive.")
    return 1239.841984 / energy_ev
