"""DESI Infinity System - Disease-Protein Network Engine (v6.2.0).

Bipartite disease-protein network with association evidence and
protein-level disease aggregation. Complements the gene network at the
protein layer.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ASSOCIATION_TYPES = ("causal", "biomarker", "therapeutic_target",
                     "interaction_partner", "modifier", "other")
EVIDENCE_LEVELS = ("strong", "moderate", "weak", "unknown")
SOURCES = ("curated", "literature", "predicted")


class DiseaseProteinNetworkError(Exception):
    """Base disease-protein network error."""


@dataclass
class DiseaseProteinAssociation:
    disease_id: str
    protein_id: str
    association_type: str = "other"
    evidence_level: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise DiseaseProteinNetworkError("disease_id required")
        if not self.protein_id or not isinstance(self.protein_id, str):
            raise DiseaseProteinNetworkError("protein_id required")
        if self.association_type not in ASSOCIATION_TYPES:
            raise DiseaseProteinNetworkError(
                f"invalid association_type: {self.association_type!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise DiseaseProteinNetworkError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise DiseaseProteinNetworkError(f"invalid source: {self.source!r}")


class DiseaseProteinNetworkEngine:
    """Bipartite disease-protein network with shared-protein queries."""

    def __init__(self) -> None:
        self._associations: List[DiseaseProteinAssociation] = []
        self._disease_proteins: Dict[str, Set[str]] = {}
        self._protein_diseases: Dict[str, Set[str]] = {}

    def add(self, assoc: DiseaseProteinAssociation) -> DiseaseProteinAssociation:
        self._associations.append(assoc)
        self._disease_proteins.setdefault(assoc.disease_id, set()).add(assoc.protein_id)
        self._protein_diseases.setdefault(assoc.protein_id, set()).add(assoc.disease_id)
        return assoc

    def proteins_for_disease(self, disease_id: str) -> List[str]:
        return sorted(self._disease_proteins.get(disease_id, set()))

    def diseases_for_protein(self, protein_id: str) -> List[str]:
        return sorted(self._protein_diseases.get(protein_id, set()))

    def shared_proteins(self, disease_a: str, disease_b: str) -> List[str]:
        return sorted(self._disease_proteins.get(disease_a, set())
                      & self._disease_proteins.get(disease_b, set()))

    def multi_disease_proteins(self, min_diseases: int = 2) -> List[str]:
        return sorted(p for p, ds in self._protein_diseases.items()
                      if len(ds) >= min_diseases)

    def protein_degree(self, protein_id: str) -> int:
        return len(self._protein_diseases.get(protein_id, set()))

    def top_proteins(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise DiseaseProteinNetworkError("top_n must be positive")
        rows = [{"protein_id": p, "disease_count": self.protein_degree(p)}
                for p in self._protein_diseases]
        rows.sort(key=lambda r: r["disease_count"], reverse=True)  # type: ignore
        return rows[:top_n]

    def by_association_type(self, assoc_type: str) -> List[DiseaseProteinAssociation]:
        if assoc_type not in ASSOCIATION_TYPES:
            raise DiseaseProteinNetworkError(
                f"invalid association_type: {assoc_type!r}")
        return [a for a in self._associations if a.association_type == assoc_type]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "associations": len(self._associations),
            "diseases": len(self._disease_proteins),
            "proteins": len(self._protein_diseases),
            "multi_disease_proteins": len(self.multi_disease_proteins()),
        }


def self_test() -> bool:
    engine = DiseaseProteinNetworkEngine()
    engine.add(DiseaseProteinAssociation(
        "D_alz", "P05067", "causal", "strong"))     # APP
    engine.add(DiseaseProteinAssociation(
        "D_alz", "P10636", "causal", "strong"))     # MAPT
    engine.add(DiseaseProteinAssociation(
        "D_pd", "P37840", "causal", "strong"))      # SNCA
    engine.add(DiseaseProteinAssociation(
        "D_pd", "P10636", "biomarker", "moderate"))  # MAPT
    engine.add(DiseaseProteinAssociation(
        "D_ftd", "P10636", "causal", "strong"))      # MAPT
    assert engine.proteins_for_disease("D_alz") == ["P05067", "P10636"]
    assert engine.shared_proteins("D_alz", "D_pd") == ["P10636"]
    assert "P10636" in engine.multi_disease_proteins()
    assert engine.protein_degree("P10636") == 3
    assert len(engine.by_association_type("causal")) == 4
    print("disease_protein_network_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
