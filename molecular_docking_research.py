"""DESI Infinity System - Molecular Docking Research (v6.2.0).

Stores docking studies: receptor-ligand pairs, docking scores, poses,
and validation outcomes. Research record-keeping only; no therapeutic
claims.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

DOCKING_PROGRAMS = ("autodock_vina", "glide", "gold", "diffdock",
                    "rosetta", "other")
VALIDATION_RESULTS = ("pass", "marginal", "fail", "not_performed")
SOURCES = ("curated", "literature", "predicted")


class DockingResearchError(Exception):
    """Base docking research error."""


@dataclass
class DockingStudy:
    study_id: str
    receptor_id: str
    ligand_id: str
    docking_program: str = "other"
    best_score_kcal: float = 0.0
    rmsd_angstrom: float = 0.0
    pose_count: int = 1
    validation_result: str = "not_performed"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.study_id or not isinstance(self.study_id, str):
            raise DockingResearchError("study_id required")
        if not self.receptor_id or not self.ligand_id:
            raise DockingResearchError("receptor_id and ligand_id required")
        if self.docking_program not in DOCKING_PROGRAMS:
            raise DockingResearchError(
                f"invalid docking_program: {self.docking_program!r}")
        if self.validation_result not in VALIDATION_RESULTS:
            raise DockingResearchError(
                f"invalid validation_result: {self.validation_result!r}")
        if self.source not in SOURCES:
            raise DockingResearchError(f"invalid source: {self.source!r}")
        if not isinstance(self.pose_count, int) or self.pose_count < 1:
            raise DockingResearchError("pose_count must be >= 1")

    def is_strong_binder(self, threshold: float = -8.0) -> bool:
        return self.best_score_kcal <= threshold

    def is_validated(self) -> bool:
        return self.validation_result in ("pass", "marginal")


class MolecularDockingResearch:
    """Docking study registry with scoring and validation queries."""

    def __init__(self) -> None:
        self._studies: Dict[str, DockingStudy] = {}
        self._receptor_index: Dict[str, List[str]] = {}
        self._ligand_index: Dict[str, List[str]] = {}

    def add(self, study: DockingStudy) -> DockingStudy:
        if study.study_id in self._studies:
            raise DockingResearchError(f"duplicate study_id: {study.study_id}")
        self._studies[study.study_id] = study
        self._receptor_index.setdefault(study.receptor_id, []).append(study.study_id)
        self._ligand_index.setdefault(study.ligand_id, []).append(study.study_id)
        return study

    def get(self, study_id: str) -> DockingStudy:
        try:
            return self._studies[study_id]
        except KeyError as exc:
            raise DockingResearchError(f"unknown study_id: {study_id}") from exc

    def for_receptor(self, receptor_id: str) -> List[DockingStudy]:
        return [self.get(s) for s in self._receptor_index.get(receptor_id, [])]

    def for_ligand(self, ligand_id: str) -> List[DockingStudy]:
        return [self.get(s) for s in self._ligand_index.get(ligand_id, [])]

    def strong_binders(self, threshold: float = -8.0) -> List[DockingStudy]:
        return [s for s in self._studies.values() if s.is_strong_binder(threshold)]

    def validated(self) -> List[DockingStudy]:
        return [s for s in self._studies.values() if s.is_validated()]

    def top_hits(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise DockingResearchError("top_n must be positive")
        rows = [{"study_id": s.study_id, "ligand_id": s.ligand_id,
                 "best_score_kcal": s.best_score_kcal}
                for s in self._studies.values()]
        rows.sort(key=lambda r: r["best_score_kcal"])  # type: ignore
        return rows[:top_n]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "studies": len(self._studies),
            "receptors": len(self._receptor_index),
            "ligands": len(self._ligand_index),
            "validated": len(self.validated()),
        }


def self_test() -> bool:
    research = MolecularDockingResearch()
    research.add(DockingStudy(
        "DS1", "EGFR_kinase", "LIG_erlotinib",
        "autodock_vina", -9.2, 1.4, 9, "pass"))
    research.add(DockingStudy(
        "DS2", "EGFR_kinase", "LIG_gefitinib",
        "autodock_vina", -8.7, 2.0, 9, "marginal"))
    research.add(DockingStudy(
        "DS3", "EGFR_kinase", "LIG_random",
        "autodock_vina", -5.0, 3.1, 9, "fail"))
    assert len(research.for_receptor("EGFR_kinase")) == 3
    assert len(research.for_ligand("LIG_erlotinib")) == 1
    assert len(research.strong_binders()) == 2
    assert len(research.validated()) == 2
    assert research.top_hits(1)[0]["study_id"] == "DS1"
    print("molecular_docking_research: OK")
    return True


if __name__ == "__main__":
    self_test()
