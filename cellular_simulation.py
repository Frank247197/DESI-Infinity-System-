# DESI∞ INFINITY SYSTEM — Cellular Simulation
# Version: 6.2.0
# Module: cellular_simulation.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Cellular Simulation"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def simulate_states(
    initial: dict[str, int],
    transitions: dict[str, dict[str, float]],
    steps: int
) -> list[dict[str, int]]:
    """Deterministic expected-count transition model; counts may be fractional."""
    if steps < 0 or isinstance(steps, bool):
        raise ValueError("steps must be a non-negative integer.")
    if any(v < 0 for v in initial.values()):
        raise ValueError("Initial counts cannot be negative.")
    states = set(initial) | set(transitions)
    for source, row in transitions.items():
        if (
            set(row) - states
            or any(p < 0 for p in row.values())
            or abs(sum(row.values()) - 1) > 1e-9
        ):
            raise ValueError(f"Invalid transition row for {source}.")
    current = {s: float(initial.get(s, 0)) for s in states}
    history = [dict(current)]
    for _ in range(steps):
        nxt = {s: 0.0 for s in states}
        for source, count in current.items():
            row = transitions.get(source, {source: 1.0})
            for target, probability in row.items():
                nxt[target] += count * probability
        current = nxt
        history.append(dict(current))
    return history
