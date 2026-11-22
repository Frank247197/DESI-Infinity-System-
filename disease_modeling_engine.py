"""DESI Infinity System - Disease Modeling Engine (v6.2.0).

Builds abstract, deterministic disease models from structured components
(state variables, parameters, and rules). The model itself is symbolic;
the caller supplies real parameters with documented sources.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MODEL_TYPES = ("compartmental", "agent_based", "state_transition",
               "differential_equation", "network", "other")
VARIABLE_TYPES = ("continuous", "discrete", "boolean", "categorical")
SOURCES = ("curated", "literature", "predicted")


class DiseaseModelingError(Exception):
    """Base disease modeling error."""


@dataclass
class ModelVariable:
    name: str
    var_type: str = "continuous"
    unit: str = ""
    initial_value: float = 0.0

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise DiseaseModelingError("name required")
        if self.var_type not in VARIABLE_TYPES:
            raise DiseaseModelingError(f"invalid var_type: {self.var_type!r}")


@dataclass
class ModelParameter:
    name: str
    value: float
    unit: str = ""
    source_note: str = ""

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise DiseaseModelingError("name required")
        if not isinstance(self.value, (int, float)):
            raise DiseaseModelingError("value must be numeric")


@dataclass
class DiseaseModel:
    model_id: str
    disease_id: str
    name: str
    model_type: str
    variables: List[ModelVariable] = field(default_factory=list)
    parameters: List[ModelParameter] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model_id or not isinstance(self.model_id, str):
            raise DiseaseModelingError("model_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise DiseaseModelingError("disease_id required")
        if not self.name or not isinstance(self.name, str):
            raise DiseaseModelingError("name required")
        if self.model_type not in MODEL_TYPES:
            raise DiseaseModelingError(f"invalid model_type: {self.model_type!r}")
        if self.source not in SOURCES:
            raise DiseaseModelingError(f"invalid source: {self.source!r}")


class DiseaseModelingEngine:
    """Model registry with type / disease / variable queries."""

    def __init__(self) -> None:
        self._models: Dict[str, DiseaseModel] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._type_index: Dict[str, List[str]] = {}

    def add(self, model: DiseaseModel) -> DiseaseModel:
        if model.model_id in self._models:
            raise DiseaseModelingError(f"duplicate model_id: {model.model_id}")
        self._models[model.model_id] = model
        self._disease_index.setdefault(model.disease_id, []).append(model.model_id)
        self._type_index.setdefault(model.model_type, []).append(model.model_id)
        return model

    def get(self, model_id: str) -> DiseaseModel:
        try:
            return self._models[model_id]
        except KeyError as exc:
            raise DiseaseModelingError(f"unknown model_id: {model_id}") from exc

    def for_disease(self, disease_id: str) -> List[DiseaseModel]:
        return [self.get(m) for m in self._disease_index.get(disease_id, [])]

    def by_type(self, model_type: str) -> List[DiseaseModel]:
        if model_type not in MODEL_TYPES:
            raise DiseaseModelingError(f"invalid model_type: {model_type!r}")
        return [self.get(m) for m in self._type_index.get(model_type, [])]

    def model_variables(self, model_id: str) -> List[str]:
        return [v.name for v in self.get(model_id).variables]

    def model_parameters(self, model_id: str) -> Dict[str, float]:
        return {p.name: p.value for p in self.get(model_id).parameters}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "models": len(self._models),
            "diseases": len(self._disease_index),
            "types": len(self._type_index),
        }


def self_test() -> bool:
    engine = DiseaseModelingEngine()
    engine.add(DiseaseModel(
        "M1", "D_influenza", "SIR influenza model", "compartmental",
        variables=[
            ModelVariable("S", "continuous", "people", 1000000),
            ModelVariable("I", "continuous", "people", 10),
            ModelVariable("R", "continuous", "people", 0),
        ],
        parameters=[
            ModelParameter("beta", 0.3, "1/day", "literature"),
            ModelParameter("gamma", 0.1, "1/day", "literature"),
        ],
        rules=["dS/dt = -beta*S*I/N",
               "dI/dt = beta*S*I/N - gamma*I",
               "dR/dt = gamma*I"]))
    engine.add(DiseaseModel(
        "M2", "D_t2d", "Glucose-insulin minimal model",
        "differential_equation",
        variables=[ModelVariable("G", "continuous", "mg/dL", 90),
                   ModelVariable("I", "continuous", "mU/L", 5)],
        parameters=[ModelParameter("Si", 0.02, "1/(mU/L)/min", "literature")]))
    assert len(engine.for_disease("D_influenza")) == 1
    assert len(engine.by_type("compartmental")) == 1
    assert "beta" in engine.model_parameters("M1")
    assert "S" in engine.model_variables("M1")
    print("disease_modeling_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
