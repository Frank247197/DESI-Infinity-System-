# DESI∞ INFINITY SYSTEM — Differential Equation Solver
# Version: 6.2.0
# Module: differential_equation_solver.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Differential Equation Solver"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def euler_method(
    derivative,
    initial_y: float,
    start_x: float,
    step_size: float,
    steps: int
) -> list[tuple[float, float]]:
    """Numerically solve dy/dx=f(x,y) using explicit Euler integration."""
    if step_size <= 0 or steps < 0:
        raise ValueError("Step size must be positive and steps non-negative.")
    x, y = start_x, initial_y
    results = [(x, y)]
    for _ in range(steps):
        y += step_size * derivative(x, y)
        x += step_size
        results.append((x, y))
    return results
