# DESI∞ INFINITY SYSTEM — Neuroplasticity Model
# Version: 6.2.0
# Module: neuroplasticity_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Neuroplasticity Model"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def update_strength(
    strength: float,
    practice: float,
    decay: float,
    learning_rate: float
) -> float:
    """One discrete learning/decay step; parameters are abstract, not biological constants."""
    values = (strength, practice, decay, learning_rate)
    if any(not 0 <= x <= 1 for x in values):
        raise ValueError("All inputs must be between 0 and 1.")
    updated = strength * (1 - decay) + learning_rate * practice * (1 - strength)
    return min(1.0, max(0.0, updated))


def simulate_learning(
    initial: float,
    practice_schedule: list[float],
    decay: float = 0.01,
    learning_rate: float = 0.1
) -> list[float]:
    state = initial
    history = [state]
    for practice in practice_schedule:
        state = update_strength(state, practice, decay, learning_rate)
        history.append(state)
    return history
