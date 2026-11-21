"""DESI Infinity System - Molecular Dynamics Analyzer (v6.2.0).

Stores molecular dynamics simulation metadata and summary metrics
(RMSD, RMSF, gyration radius, H-bond count). Research record-keeping;
no predictions about drug efficacy.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FORCE_FIELDS = ("amber", "charmm", "opls", "gromos", "martini", "other")
ENSEMBLES = ("nvt", "npt", "nve", "other")
SOURCES = ("curated", "literature", "predicted")


class MolecularDynamicsError(Exception):
    """Base molecular dynamics error."""


@dataclass
class MDTrajectory:
    trajectory_id: str
    system_id: str
    force_field: str = "other"
    ensemble: str = "other"
    duration_ns: float = 0.0
    temperature_k: float = 300.0
    rmsd_nm: Optional[float] = None
    rmsf_nm: Optional[float] = None
    radius_gyration_nm: Optional[float] = None
    hbond_mean: Optional[float] = None
    stable: bool = False
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.trajectory_id or not isinstance(self.trajectory_id, str):
            raise MolecularDynamicsError("trajectory_id required")
        if not self.system_id or not isinstance(self.system_id, str):
            raise MolecularDynamicsError("system_id required")
        if self.force_field not in FORCE_FIELDS:
            raise MolecularDynamicsError(
                f"invalid force_field: {self.force_field!r}")
        if self.ensemble not in ENSEMBLES:
            raise MolecularDynamicsError(f"invalid ensemble: {self.ensemble!r}")
        if self.source not in SOURCES:
            raise MolecularDynamicsError(f"invalid source: {self.source!r}")
        if self.duration_ns <= 0:
            raise MolecularDynamicsError("duration_ns must be > 0")
        if self.temperature_k <= 0:
            raise MolecularDynamicsError("temperature_k must be > 0")

    def stability_flag(self, rmsd_threshold: float = 0.3) -> bool:
        if self.rmsd_nm is None:
            return False
        return self.rmsd_nm <= rmsd_threshold


class MolecularDynamicsAnalyzer:
    """Trajectory registry with system / force-field / stability queries."""

    def __init__(self) -> None:
        self._trajectories: Dict[str, MDTrajectory] = {}
        self._system_index: Dict[str, List[str]] = {}
        self._ff_index: Dict[str, List[str]] = {}

    def add(self, trajectory: MDTrajectory) -> MDTrajectory:
        if trajectory.trajectory_id in self._trajectories:
            raise MolecularDynamicsError(
                f"duplicate trajectory_id: {trajectory.trajectory_id}")
        self._trajectories[trajectory.trajectory_id] = trajectory
        self._system_index.setdefault(trajectory.system_id, []).append(
            trajectory.trajectory_id)
        self._ff_index.setdefault(trajectory.force_field, []).append(
            trajectory.trajectory_id)
        return trajectory

    def get(self, trajectory_id: str) -> MDTrajectory:
        try:
            return self._trajectories[trajectory_id]
        except KeyError as exc:
            raise MolecularDynamicsError(
                f"unknown trajectory_id: {trajectory_id}") from exc

    def for_system(self, system_id: str) -> List[MDTrajectory]:
        return [self.get(t) for t in self._system_index.get(system_id, [])]

    def by_force_field(self, force_field: str) -> List[MDTrajectory]:
        if force_field not in FORCE_FIELDS:
            raise MolecularDynamicsError(
                f"invalid force_field: {force_field!r}")
        return [self.get(t) for t in self._ff_index.get(force_field, [])]

    def stable_trajectories(self, rmsd_threshold: float = 0.3) -> List[MDTrajectory]:
        return [t for t in self._trajectories.values()
                if t.stability_flag(rmsd_threshold)]

    def long_simulations(self, min_ns: float = 100.0) -> List[MDTrajectory]:
        return [t for t in self._trajectories.values() if t.duration_ns >= min_ns]

    def summary(self, system_id: str) -> Dict[str, object]:
        recs = self.for_system(system_id)
        if not recs:
            return {"system_id": system_id, "trajectories": 0}
        rmsds = [t.rmsd_nm for t in recs if t.rmsd_nm is not None]
        return {
            "system_id": system_id,
            "trajectories": len(recs),
            "mean_rmsd_nm": round(sum(rmsds) / len(rmsds), 4) if rmsds else None,
            "stable_count": len([t for t in recs if t.stability_flag()]),
        }

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "trajectories": len(self._trajectories),
            "systems": len(self._system_index),
            "force_fields": len(self._ff_index),
        }


def self_test() -> bool:
    analyzer = MolecularDynamicsAnalyzer()
    analyzer.add(MDTrajectory(
        "T1", "SYS_kinase", "amber", "npt",
        duration_ns=200.0, temperature_k=310.0,
        rmsd_nm=0.25, rmsf_nm=0.15, radius_gyration_nm=2.3, hbond_mean=8.4,
        stable=True))
    analyzer.add(MDTrajectory(
        "T2", "SYS_kinase", "charmm", "npt",
        duration_ns=500.0, temperature_k=310.0,
        rmsd_nm=0.42, rmsf_nm=0.22, hbond_mean=6.5, stable=False))
    analyzer.add(MDTrajectory(
        "T3", "SYS_p53", "amber", "nvt",
        duration_ns=50.0, temperature_k=300.0, rmsd_nm=0.18))
    assert len(analyzer.for_system("SYS_kinase")) == 2
    assert len(analyzer.by_force_field("amber")) == 2
    assert len(analyzer.stable_trajectories(0.3)) == 2
    assert len(analyzer.long_simulations(300.0)) == 1
    s = analyzer.summary("SYS_kinase")
    assert s["trajectories"] == 2
    print("molecular_dynamics_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
