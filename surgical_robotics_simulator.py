# DESI∞ INFINITY SYSTEM — Surgical Robotics Simulator
# Version: 6.2.0
# Module: surgical_robotics_simulator.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Surgical Robotics Simulator"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def validate_trajectory(
    points: list[tuple[float, float, float]],
    bounds: tuple[tuple[float, float], ...]
) -> dict:
    """Offline geometry validation only; no robot/device control."""
    if len(bounds) != 3 or any(lo >= hi for lo, hi in bounds):
        raise ValueError("Three valid axis bounds are required.")
    violations = []
    for i, point in enumerate(points):
        if len(point) != 3:
            raise ValueError("Each point must have three coordinates.")
        for axis, value in enumerate(point):
            lo, hi = bounds[axis]
            if not lo <= value <= hi:
                violations.append({
                    "point": i,
                    "axis": axis,
                    "value": value
                })
    return {
        "point_count": len(points),
        "within_workspace": not violations,
        "violations": violations
    }
