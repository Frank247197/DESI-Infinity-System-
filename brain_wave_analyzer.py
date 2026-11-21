# DESI∞ INFINITY SYSTEM — Brain-Wave Signal Analyzer
# Version: 6.2.0
# Module: brain_wave_analyzer.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Brain-Wave Signal Analyzer"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def band_power(
    spectrum: dict[float, float],
    low_hz: float,
    high_hz: float
) -> float:
    """Integrate non-negative power bins within a frequency interval using bin sums."""
    if low_hz < 0 or high_hz <= low_hz:
        raise ValueError("Invalid frequency band.")
    if any(f < 0 or p < 0 for f, p in spectrum.items()):
        raise ValueError("Frequencies and powers must be non-negative.")
    return sum(
        float(p) for f, p in spectrum.items()
        if low_hz <= f < high_hz
    )

def relative_band_power(
    spectrum: dict[float, float],
    low_hz: float,
    high_hz: float
) -> float:
    total = sum(spectrum.values())
    if total <= 0:
        return 0.0
    return band_power(spectrum, low_hz, high_hz) / total
