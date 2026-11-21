# DESI∞ INFINITY SYSTEM — Quantum Computing Research
# Version: 6.2.0
# Module: quantum_computing_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Quantum Computing Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def normalize_state(amplitudes: list[complex]) -> list[complex]:
    """Normalize a state vector; amplitudes are a mathematical simulation."""
    import math
    if not amplitudes:
        raise ValueError("State vector cannot be empty.")
    norm = math.sqrt(sum(abs(a) ** 2 for a in amplitudes))
    if norm == 0:
        raise ValueError("State vector cannot have zero norm.")
    return [a / norm for a in amplitudes]

def measurement_probabilities(amplitudes: list[complex]) -> list[float]:
    state = normalize_state(amplitudes)
    return [abs(a) ** 2 for a in state]
