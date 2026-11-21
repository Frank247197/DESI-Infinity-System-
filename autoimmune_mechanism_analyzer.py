"""DESI Infinity System - Autoimmune Mechanism Analyzer (v6.2.0).

Mechanism-level analysis of autoimmune diseases: tolerance breakdown,
autoantigen origin, effector arms, and HLA contribution. Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

TOLERANCE_FAILURES = ("central_failure", "peripheral_failure",
                      "molecular_mimicry", "epitope_spreading",
                      "bystander_activation", "unknown")
EFFECTOR_ARMS = ("autoantibody", "cd4_t_cell", "cd8_t_cell", "complement",
                 "nk_cell", "neutrophil", "unknown")
SOURCES = ("curated", "literature", "predicted")


class AutoimmuneMechanismError(Exception):
    """Base autoimmune mechanism error."""


@dataclass
class AutoimmuneMechanism:
    mechanism_id: str
    disease_id: str
    name: str
    tolerance_failure: str = "unknown"
    effector_arms: List[str] = field(default_factory=list)
    autoantigens: List[str] = field(default_factory=list)
    hla_alleles: List[str] = field(default_factory=list)
    infectious_trigger: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mechanism_id or not isinstance(self.mechanism_id, str):
            raise AutoimmuneMechanismError("mechanism_id required")
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise AutoimmuneMechanismError("disease_id required")
        if self.tolerance_failure not in TOLERANCE_FAILURES:
            raise AutoimmuneMechanismError(
                f"invalid tolerance_failure: {self.tolerance_failure!r}")
        if self.source not in SOURCES:
            raise AutoimmuneMechanismError(f"invalid source: {self.source!r}")
        for a in self.effector_arms:
            if a not in EFFECTOR_ARMS:
                raise AutoimmuneMechanismError(f"invalid effector_arm: {a!r}")


class AutoimmuneMechanismAnalyzer:
    """Registry with tolerance / effector / HLA / antigen queries."""

    def __init__(self) -> None:
        self._mechanisms: Dict[str, AutoimmuneMechanism] = {}
        self._disease_index: Dict[str, List[str]] = {}
        self._hla_index: Dict[str, List[str]] = {}
        self._antigen_index: Dict[str, List[str]] = {}

    def add(self, mechanism: AutoimmuneMechanism) -> AutoimmuneMechanism:
        if mechanism.mechanism_id in self._mechanisms:
            raise AutoimmuneMechanismError(
                f"duplicate mechanism_id: {mechanism.mechanism_id}")
        self._mechanisms[mechanism.mechanism_id] = mechanism
        self._disease_index.setdefault(mechanism.disease_id, []).append(
            mechanism.mechanism_id)
        for h in mechanism.hla_alleles:
            self._hla_index.setdefault(h, []).append(mechanism.mechanism_id)
        for a in mechanism.autoantigens:
            self._antigen_index.setdefault(a, []).append(mechanism.mechanism_id)
        return mechanism

    def get(self, mechanism_id: str) -> AutoimmuneMechanism:
        try:
            return self._mechanisms[mechanism_id]
        except KeyError as exc:
            raise AutoimmuneMechanismError(
                f"unknown mechanism_id: {mechanism_id}") from exc

    def for_disease(self, disease_id: str) -> List[AutoimmuneMechanism]:
        return [self.get(mid) for mid in self._disease_index.get(disease_id, [])]

    def by_tolerance_failure(self, failure: str) -> List[AutoimmuneMechanism]:
        if failure not in TOLERANCE_FAILURES:
            raise AutoimmuneMechanismError(f"invalid tolerance_failure: {failure!r}")
        return [m for m in self._mechanisms.values() if m.tolerance_failure == failure]

    def by_effector_arm(self, arm: str) -> List[AutoimmuneMechanism]:
        if arm not in EFFECTOR_ARMS:
            raise AutoimmuneMechanismError(f"invalid effector_arm: {arm!r}")
        return [m for m in self._mechanisms.values() if arm in m.effector_arms]

    def by_hla(self, hla: str) -> List[AutoimmuneMechanism]:
        return [self.get(mid) for mid in self._hla_index.get(hla, [])]

    def by_autoantigen(self, antigen: str) -> List[AutoimmuneMechanism]:
        return [self.get(mid) for mid in self._antigen_index.get(antigen, [])]

    def mimicry_mechanisms(self) -> List[AutoimmuneMechanism]:
        return [m for m in self._mechanisms.values()
                if m.tolerance_failure == "molecular_mimicry"]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "mechanisms": len(self._mechanisms),
            "diseases": len(self._disease_index),
            "mimicry": len(self.mimicry_mechanisms()),
        }


def self_test() -> bool:
    analyzer = AutoimmuneMechanismAnalyzer()
    analyzer.add(AutoimmuneMechanism(
        "AM_t1d", "D_t1d", "Beta cell autoimmunity",
        tolerance_failure="peripheral_failure",
        effector_arms=["cd4_t_cell", "cd8_t_cell"],
        autoantigens=["GAD65", "IA-2"],
        hla_alleles=["HLA-DR3", "HLA-DR4"]))
    analyzer.add(AutoimmuneMechanism(
        "AM_rheu", "D_rheumatic_fever", "Rheumatic fever mimicry",
        tolerance_failure="molecular_mimicry",
        effector_arms=["autoantibody", "complement"],
        autoantigens=["cardiac_myosin"],
        infectious_trigger="Streptococcus pyogenes"))
    assert analyzer.for_disease("D_t1d")[0].mechanism_id == "AM_t1d"
    assert analyzer.by_tolerance_failure("peripheral_failure")[0].mechanism_id == "AM_t1d"
    assert analyzer.by_effector_arm("cd8_t_cell")[0].mechanism_id == "AM_t1d"
    assert analyzer.by_hla("HLA-DR4")[0].mechanism_id == "AM_t1d"
    assert analyzer.by_autoantigen("GAD65")[0].mechanism_id == "AM_t1d"
    assert len(analyzer.mimicry_mechanisms()) == 1
    print("autoimmune_mechanism_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
