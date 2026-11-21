# DESI∞ INFINITY SYSTEM — Nanosensor Engine
# Version: 6.2.0
# Module: nanosensor_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Nanosensor Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

import math

def calibrate_signal(
    signal: float,
    slope: float,
    intercept: float,
    signal_sd: float = 0.0,
    slope_sd: float = 0.0
) -> dict:
    if slope == 0 or min(signal_sd, slope_sd) < 0:
        raise ValueError(
            "Slope must be non-zero and standard deviations non-negative."
        )
    estimate = (signal - intercept) / slope
    uncertainty = math.sqrt(
        (signal_sd / slope) ** 2
        + (
            ((signal - intercept) * slope_sd) / (slope * slope)
        ) ** 2
    )
    return {
        "estimate": estimate,
        "standard_uncertainty": uncertainty
    }
