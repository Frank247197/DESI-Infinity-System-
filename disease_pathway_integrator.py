"""DESI Infinity System - Disease Pathway Integrator (v6.2.0).

Integrates disease-pathway evidence across curated pathway sources.
Provides disease pathway portfolios and pathway-overlap between diseases.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ROLES = ("driver", "modifier", "downstream", "biomarker",
         "therapeutic_target", "other")
EVIDENCE_LEVELS = ("strong", "moderate", "weak", "unknown")
SOURCES = ("curated", "literature", "predicted")


class PathwayIntegrationError(Exception):
    """Base pathway integration error."""


@dataclass
class DiseasePathwayLink:
    disease_id: str
    pathway_id: str
    role: str = "other"
    evidence_level: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise PathwayIntegrationError("disease_id required")
        if not self.pathway_id or not isinstance(self.pathway_id, str):
            raise PathwayIntegrationError("pathway_id required")
        if self.role not in ROLES:
            raise PathwayIntegrationError(f"invalid role: {self.role!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise PathwayIntegrationError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise PathwayIntegrationError(f"invalid source: {self.source!r}")


class DiseasePathwayIntegrator:
    """Disease-pathway integration with overlap analysis."""

    def __init__(self) -> None:
        self._links: List[DiseasePathwayLink] = []
        self._disease_pathways: Dict[str, Set[str]] = {}
        self._pathway_diseases: Dict[str, Set[str]] = {}

    def add(self, link: DiseasePathwayLink) -> DiseasePathwayLink:
        self._links.append(link)
        self._disease_pathways.setdefault(link.disease_id, set()).add(link.pathway_id)
        self._pathway_diseases.setdefault(link.pathway_id, set()).add(link.disease_id)
        return link

    def pathways_for_disease(self, disease_id: str) -> List[str]:
        return sorted(self._disease_pathways.get(disease_id, set()))

    def diseases_for_pathway(self, pathway_id: str) -> List[str]:
        return sorted(self._pathway_diseases.get(pathway_id, set()))

    def shared_pathways(self, disease_a: str, disease_b: str) -> List[str]:
        return sorted(self._disease_pathways.get(disease_a, set())
                      & self._disease_pathways.get(disease_b, set()))

    def shared_diseases(self, pathway_a: str, pathway_b: str) -> List[str]:
        return sorted(self._pathway_diseases.get(pathway_a, set())
                      & self._pathway_diseases.get(pathway_b, set()))

    def driver_pathways(self, disease_id: str) -> List[str]:
        return sorted({l.pathway_id for l in self._links
                       if l.disease_id == disease_id and l.role == "driver"})

    def jaccard(self, disease_a: str, disease_b: str) -> float:
        a = self._disease_pathways.get(disease_a, set())
        b = self._disease_pathways.get(disease_b, set())
        union = a | b
        if not union:
            return 0.0
        return round(len(a & b) / len(union), 4)

    def top_pathways(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise PathwayIntegrationError("top_n must be positive")
        rows = [{"pathway_id": p, "disease_count": len(ds)}
                for p, ds in self._pathway_diseases.items()]
        rows.sort(key=lambda r: r["disease_count"], reverse=True)  # type: ignore
        return rows[:top_n]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "links": len(self._links),
            "diseases": len(self._disease_pathways),
            "pathways": len(self._pathway_diseases),
        }


def self_test() -> bool:
    integrator = DiseasePathwayIntegrator()
    integrator.add(DiseasePathwayLink(
        "D_t2d", "insulin_signaling", "driver", "strong"))
    integrator.add(DiseasePathwayLink(
        "D_t2d", "glucose_metabolism", "downstream", "strong"))
    integrator.add(DiseasePathwayLink(
        "D_t2d", "AMPK_signaling", "modifier", "moderate"))
    integrator.add(DiseasePathwayLink(
        "D_obesity", "insulin_signaling", "driver", "strong"))
    integrator.add(DiseasePathwayLink(
        "D_obesity", "AMPK_signaling", "modifier", "moderate"))
    assert integrator.pathways_for_disease("D_t2d") == [
        "AMPK_signaling", "glucose_metabolism", "insulin_signaling"]
    assert integrator.shared_pathways("D_t2d", "D_obesity") == [
        "AMPK_signaling", "insulin_signaling"]
    assert integrator.driver_pathways("D_t2d") == ["insulin_signaling"]
    assert integrator.jaccard("D_t2d", "D_obesity") == round(2 / 3, 4)
    assert integrator.top_pathways(1)[0]["pathway_id"] in (
        "insulin_signaling", "AMPK_signaling")
    print("disease_pathway_integrator: OK")
    return True


if __name__ == "__main__":
    self_test()
