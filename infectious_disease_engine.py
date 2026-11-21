"""DESI Infinity System - Infectious Disease Engine (v6.2.0).

Links pathogens to infectious diseases with structured transmission and
clinical-course metadata (incubation, R0, case fatality). Distinguishes
ACTIVE infection (pathogen present with disease) from prior exposure or
endogenous viral elements — callers must declare the state explicitly.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INFECTION_STATES = ("active", "latent", "prior_exposure", "ev_element", "unknown")
TRANSMISSION_ROUTES = ("airborne", "droplet", "contact", "vector", "foodborne",
                       "waterborne", "bloodborne", "sexual", "vertical", "unknown")
SOURCES = ("curated", "literature", "predicted")


class InfectiousDiseaseError(Exception):
    """Base infectious disease error."""


@dataclass
class InfectiousDiseaseRecord:
    disease_id: str
    name: str
    pathogen_ids: List[str]
    infection_state: str = "unknown"
    transmission_routes: List[str] = field(default_factory=list)
    incubation_days: Optional[float] = None
    r0: Optional[float] = None
    case_fatality_ratio: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise InfectiousDiseaseError("disease_id required")
        if not self.pathogen_ids:
            raise InfectiousDiseaseError("at least one pathogen_id required")
        if self.infection_state not in INFECTION_STATES:
            raise InfectiousDiseaseError(f"invalid infection_state: {self.infection_state!r}")
        for r in self.transmission_routes:
            if r not in TRANSMISSION_ROUTES:
                raise InfectiousDiseaseError(f"invalid transmission_route: {r!r}")
        if self.source not in SOURCES:
            raise InfectiousDiseaseError(f"invalid source: {self.source!r}")
        for name, v in (("incubation_days", self.incubation_days), ("r0", self.r0),
                        ("case_fatality_ratio", self.case_fatality_ratio)):
            if v is not None and (not isinstance(v, (int, float)) or v < 0):
                raise InfectiousDiseaseError(f"{name} must be non-negative numeric or None")

    def is_active_infection(self) -> bool:
        return self.infection_state == "active"

    def to_dict(self) -> Dict[str, object]:
        return {
            "disease_id": self.disease_id, "name": self.name,
            "pathogen_ids": list(self.pathogen_ids),
            "infection_state": self.infection_state,
            "transmission_routes": list(self.transmission_routes),
            "incubation_days": self.incubation_days, "r0": self.r0,
            "case_fatality_ratio": self.case_fatality_ratio, "source": self.source,
        }


class InfectiousDiseaseEngine:
    """Registry of infectious diseases with explicit state separation."""

    def __init__(self) -> None:
        self._records: Dict[str, InfectiousDiseaseRecord] = {}
        self._pathogen_index: Dict[str, List[str]] = {}

    def add(self, record: InfectiousDiseaseRecord) -> InfectiousDiseaseRecord:
        if record.disease_id in self._records:
            raise InfectiousDiseaseError(f"duplicate disease_id: {record.disease_id}")
        self._records[record.disease_id] = record
        for pid in record.pathogen_ids:
            self._pathogen_index.setdefault(pid, []).append(record.disease_id)
        return record

    def get(self, disease_id: str) -> InfectiousDiseaseRecord:
        try:
            return self._records[disease_id]
        except KeyError as exc:
            raise InfectiousDiseaseError(f"unknown disease_id: {disease_id}") from exc

    def for_pathogen(self, pathogen_id: str) -> List[InfectiousDiseaseRecord]:
        return [self.get(did) for did in self._pathogen_index.get(pathogen_id, [])]

    def active_only(self) -> List[InfectiousDiseaseRecord]:
        return [r for r in self._records.values() if r.is_active_infection()]

    def not_active(self) -> List[InfectiousDiseaseRecord]:
        return [r for r in self._records.values() if not r.is_active_infection()]

    def by_route(self, route: str) -> List[InfectiousDiseaseRecord]:
        if route not in TRANSMISSION_ROUTES:
            raise InfectiousDiseaseError(f"invalid transmission_route: {route!r}")
        return [r for r in self._records.values() if route in r.transmission_routes]

    def high_transmission(self, min_r0: float = 1.0) -> List[InfectiousDiseaseRecord]:
        return [r for r in self._records.values()
                if r.r0 is not None and r.r0 >= min_r0]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "active": len(self.active_only()),
            "not_active": len(self.not_active()),
            "pathogens": len(self._pathogen_index),
        }


def self_test() -> bool:
    engine = InfectiousDiseaseEngine()
    engine.add(InfectiousDiseaseRecord("D_flu", "Influenza", ["NCBITaxon:11320"],
                                       infection_state="active",
                                       transmission_routes=["droplet", "contact"],
                                       r0=1.3, incubation_days=2.0))
    engine.add(InfectiousDiseaseRecord("D_herv", "HERV-K annotation",
                                       ["EV:HERVK"], infection_state="ev_element"))
    assert engine.for_pathogen("NCBITaxon:11320")[0].disease_id == "D_flu"
    assert len(engine.active_only()) == 1
    assert len(engine.not_active()) == 1
    assert len(engine.by_route("droplet")) == 1
    assert engine.high_transmission(1.2)[0].disease_id == "D_flu"
    print("019 infectious_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
