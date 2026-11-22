"""DESI Infinity System - Disease Simulation Engine (v6.2.0).

Deterministic compartmental simulation runner for discrete-time SIR-like
models. Simulated outputs are LABELLED as simulation, NOT predictions of
real-world outcomes. NO clinical use.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)


class DiseaseSimulationError(Exception):
    """Base disease simulation error."""


@dataclass
class SimulationConfig:
    sim_id: str
    population: int
    initial_infected: int
    beta: float
    gamma: float
    days: int
    compartment_names: List[str] = field(
        default_factory=lambda: ["S", "I", "R"])

    def __post_init__(self) -> None:
        if not self.sim_id or not isinstance(self.sim_id, str):
            raise DiseaseSimulationError("sim_id required")
        if not isinstance(self.population, int) or self.population <= 0:
            raise DiseaseSimulationError("population must be positive int")
        if not isinstance(self.initial_infected, int) or self.initial_infected < 0:
            raise DiseaseSimulationError("initial_infected must be non-negative int")
        if self.initial_infected > self.population:
            raise DiseaseSimulationError("initial_infected cannot exceed population")
        if not 0.0 <= float(self.beta) <= 10.0:
            raise DiseaseSimulationError("beta out of supported range [0, 10]")
        if not 0.0 <= float(self.gamma) <= 10.0:
            raise DiseaseSimulationError("gamma out of supported range [0, 10]")
        if not isinstance(self.days, int) or self.days <= 0:
            raise DiseaseSimulationError("days must be positive int")
        if len(self.compartment_names) != 3:
            raise DiseaseSimulationError(
                "compartment_names must be [S, I, R] of length 3")


@dataclass
class SimulationResult:
    sim_id: str
    daily_states: List[Dict[str, float]]
    peak_infected: float
    peak_day: int
    cumulative_infected: float
    is_simulation: bool = True
    notes: str = "Simulated outcome; NOT a prediction of real-world events."

    def __post_init__(self) -> None:
        if not self.is_simulation:
            raise DiseaseSimulationError("SimulationResult must be marked as simulation")


class DiseaseSimulationEngine:
    """Deterministic discrete-time SIR simulator."""

    def __init__(self) -> None:
        self._results: Dict[str, SimulationResult] = {}

    def run_sir(self, config: SimulationConfig) -> SimulationResult:
        S = float(config.population - config.initial_infected)
        I = float(config.initial_infected)
        R = 0.0
        N = float(config.population)
        states: List[Dict[str, float]] = []
        peak = I
        peak_day = 0
        cumulative = I

        for day in range(config.days):
            new_infections = config.beta * S * I / N
            new_recoveries = config.gamma * I
            S = max(0.0, S - new_infections)
            I = max(0.0, I + new_infections - new_recoveries)
            R = min(N, R + new_recoveries)
            cumulative += new_infections
            if I > peak:
                peak = I
                peak_day = day + 1
            states.append({
                config.compartment_names[0]: round(S, 3),
                config.compartment_names[1]: round(I, 3),
                config.compartment_names[2]: round(R, 3),
            })

        result = SimulationResult(
            sim_id=config.sim_id,
            daily_states=states,
            peak_infected=round(peak, 3),
            peak_day=peak_day,
            cumulative_infected=round(cumulative, 3),
        )
        self._results[config.sim_id] = result
        return result

    def get(self, sim_id: str) -> SimulationResult:
        try:
            return self._results[sim_id]
        except KeyError as exc:
            raise DiseaseSimulationError(f"unknown sim_id: {sim_id}") from exc

    def summary(self, sim_id: str) -> Dict[str, object]:
        r = self.get(sim_id)
        return {
            "sim_id": r.sim_id,
            "peak_infected": r.peak_infected,
            "peak_day": r.peak_day,
            "cumulative_infected": r.cumulative_infected,
            "is_simulation": r.is_simulation,
            "notes": r.notes,
        }

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "simulations": len(self._results)}


def self_test() -> bool:
    engine = DiseaseSimulationEngine()
    result = engine.run_sir(SimulationConfig(
        "SIM1", population=100000, initial_infected=10,
        beta=0.3, gamma=0.1, days=90))
    assert result.is_simulation is True
    assert len(result.daily_states) == 90
    assert result.peak_infected > 0
    summary = engine.summary("SIM1")
    assert summary["is_simulation"] is True
    assert "Simulated outcome" in summary["notes"]
    try:
        DiseaseSimulationError  # sanity
        engine.run_sir(SimulationConfig(
            "BAD", population=100, initial_infected=200,
            beta=0.3, gamma=0.1, days=30))
        raise AssertionError("expected initial_infected validation failure")
    except DiseaseSimulationError:
        pass
    print("disease_simulation_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
