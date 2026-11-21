# DESI∞ INFINITY SYSTEM — Optimization Engine
# Version: 6.2.0
# Module: optimization_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Optimization Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def grid_search(
    objective,
    parameter_ranges: dict[str, list[float]],
    maximize: bool = False
) -> dict:
    """Search a finite parameter grid and return the best evaluated point."""
    if not parameter_ranges or any(not values for values in parameter_ranges.values()):
        raise ValueError("Every parameter needs at least one candidate value.")
    import itertools
    names = list(parameter_ranges)
    best_parameters = None
    best_score = None
    for combination in itertools.product(
        *(parameter_ranges[name] for name in names)
    ):
        parameters = dict(zip(names, combination))
        score = float(objective(parameters))
        if best_score is None or (
            score > best_score if maximize else score < best_score
        ):
            best_score = score
            best_parameters = parameters
    return {
        "parameters": best_parameters,
        "objective_value": best_score,
        "evaluations": __import__("math").prod(
            len(values) for values in parameter_ranges.values()
        )
    }
