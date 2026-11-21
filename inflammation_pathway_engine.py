"""DESI Infinity System - Inflammation Pathway Engine (v6.2.0).

Pathway-level inflammation modeling: classical, alternative, and
resolution programs with mediators, triggers, and tissue outcomes.
Research-only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

PROGRAM_TYPES = ("acute", "chronic", "resolution", "para_inflammation",
                 "unknown")
MEDIATOR_CLASSES = ("cytokine", "eicosanoid", "complement", "kinin",
                    "reactive_oxygen", "enzyme", "other")
SOURCES = ("curated", "literature", "predicted")


class InflammationPathwayError(Exception):
    """Base inflammation pathway error."""


@dataclass
class InflammationPathway:
    pathway_id: str
    name: str
    program_type: str = "unknown"
    mediators: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    affected_tissues: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pathway_id or not isinstance(self.pathway_id, str):
            raise InflammationPathwayError("pathway_id required")
        if not self.name or not isinstance(self.name, str):
            raise InflammationPathwayError("name required")
        if self.program_type not in PROGRAM_TYPES:
            raise InflammationPathwayError(
                f"invalid program_type: {self.program_type!r}")
        if self.source not in SOURCES:
            raise InflammationPathwayError(f"invalid source: {self.source!r}")


class InflammationPathwayEngine:
    """Registry with program / mediator / disease queries."""

    def __init__(self) -> None:
        self._pathways: Dict[str, InflammationPathway] = {}
        self._mediator_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, pathway: InflammationPathway) -> InflammationPathway:
        if pathway.pathway_id in self._pathways:
            raise InflammationPathwayError(
                f"duplicate pathway_id: {pathway.pathway_id}")
        self._pathways[pathway.pathway_id] = pathway
        for m in pathway.mediators:
            self._mediator_index.setdefault(m, []).append(pathway.pathway_id)
        for did in pathway.disease_ids:
            self._disease_index.setdefault(did, []).append(pathway.pathway_id)
        return pathway

    def get(self, pathway_id: str) -> InflammationPathway:
        try:
            return self._pathways[pathway_id]
        except KeyError as exc:
            raise InflammationPathwayError(f"unknown pathway_id: {pathway_id}") from exc

    def by_program(self, program_type: str) -> List[InflammationPathway]:
        if program_type not in PROGRAM_TYPES:
            raise InflammationPathwayError(
                f"invalid program_type: {program_type!r}")
        return [p for p in self._pathways.values() if p.program_type == program_type]

    def by_mediator(self, mediator: str) -> List[InflammationPathway]:
        return [self.get(pid) for pid in self._mediator_index.get(mediator, [])]

    def for_disease(self, disease_id: str) -> List[InflammationPathway]:
        return [self.get(pid) for pid in self._disease_index.get(disease_id, [])]

    def resolution_pathways(self) -> List[InflammationPathway]:
        return self.by_program("resolution")

    def chronic_programs(self) -> List[InflammationPathway]:
        return self.by_program("chronic")

    def shared_mediators(self, a_id: str, b_id: str) -> List[str]:
        a = set(self.get(a_id).mediators)
        b = set(self.get(b_id).mediators)
        return sorted(a & b)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "pathways": len(self._pathways),
            "acute": len(self.by_program("acute")),
            "chronic": len(self.by_program("chronic")),
            "resolution": len(self.resolution_pathways()),
        }


def self_test() -> bool:
    engine = InflammationPathwayEngine()
    engine.add(InflammationPathway(
        "P_acute", "Acute innate inflammation", "acute",
        mediators=["IL-1beta", "TNF", "PGE2"],
        triggers=["infection", "tissue_damage"],
        affected_tissues=["vasculature"],
        disease_ids=["D_sepsis"]))
    engine.add(InflammationPathway(
        "P_chronic", "Chronic low-grade inflammation", "chronic",
        mediators=["IL-6", "CRP", "TNF"],
        triggers=["obesity", "aging"],
        affected_tissues=["adipose", "liver"],
        disease_ids=["D_t2d", "D_nafld"]))
    engine.add(InflammationPathway(
        "P_res", "Specialized pro-resolving", "resolution",
        mediators=["resolvin_D1", "lipoxin_A4"],
        triggers=["acute_inflammation_resolution"],
        disease_ids=[]))
    assert len(engine.by_program("acute")) == 1
    assert engine.by_mediator("TNF")[0].pathway_id == "P_acute"
    assert "D_nafld" in engine.chronic_programs()[0].disease_ids
    assert engine.shared_mediators("P_acute", "P_chronic") == ["TNF"]
    assert len(engine.resolution_pathways()) == 1
    print("inflammation_pathway_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
