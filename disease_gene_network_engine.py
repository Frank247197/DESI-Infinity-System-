"""DESI Infinity System - Disease-Gene Network Engine (v6.2.0).

Bipartite disease-gene network with evidence-backed associations. Supports
shared-gene discovery across diseases and gene-level disease clustering.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ASSOCIATION_TYPES = ("causal", "susceptibility", "biomarker",
                     "therapeutic_target", "modifier", "other")
EVIDENCE_LEVELS = ("strong", "moderate", "weak", "unknown")
SOURCES = ("curated", "literature", "predicted")


class DiseaseGeneNetworkError(Exception):
    """Base disease-gene network error."""


@dataclass
class DiseaseGeneAssociation:
    disease_id: str
    gene_symbol: str
    association_type: str = "other"
    evidence_level: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise DiseaseGeneNetworkError("disease_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise DiseaseGeneNetworkError("gene_symbol required")
        if self.association_type not in ASSOCIATION_TYPES:
            raise DiseaseGeneNetworkError(
                f"invalid association_type: {self.association_type!r}")
        if self.evidence_level not in EVIDENCE_LEVELS:
            raise DiseaseGeneNetworkError(
                f"invalid evidence_level: {self.evidence_level!r}")
        if self.source not in SOURCES:
            raise DiseaseGeneNetworkError(f"invalid source: {self.source!r}")


class DiseaseGeneNetworkEngine:
    """Bipartite disease-gene network with shared-gene queries."""

    def __init__(self) -> None:
        self._associations: List[DiseaseGeneAssociation] = []
        self._disease_genes: Dict[str, Set[str]] = {}
        self._gene_diseases: Dict[str, Set[str]] = {}

    def add(self, assoc: DiseaseGeneAssociation) -> DiseaseGeneAssociation:
        self._associations.append(assoc)
        self._disease_genes.setdefault(assoc.disease_id, set()).add(assoc.gene_symbol)
        self._gene_diseases.setdefault(assoc.gene_symbol, set()).add(assoc.disease_id)
        return assoc

    def genes_for_disease(self, disease_id: str) -> List[str]:
        return sorted(self._disease_genes.get(disease_id, set()))

    def diseases_for_gene(self, gene_symbol: str) -> List[str]:
        return sorted(self._gene_diseases.get(gene_symbol, set()))

    def shared_genes(self, disease_a: str, disease_b: str) -> List[str]:
        return sorted(self._disease_genes.get(disease_a, set())
                      & self._disease_genes.get(disease_b, set()))

    def shared_diseases(self, gene_a: str, gene_b: str) -> List[str]:
        return sorted(self._gene_diseases.get(gene_a, set())
                      & self._gene_diseases.get(gene_b, set()))

    def multi_disease_genes(self, min_diseases: int = 2) -> List[str]:
        return sorted(g for g, ds in self._gene_diseases.items()
                      if len(ds) >= min_diseases)

    def gene_degree(self, gene_symbol: str) -> int:
        return len(self._gene_diseases.get(gene_symbol, set()))

    def top_genes(self, top_n: int = 5) -> List[Dict[str, object]]:
        if top_n <= 0:
            raise DiseaseGeneNetworkError("top_n must be positive")
        rows = [{"gene_symbol": g, "disease_count": self.gene_degree(g)}
                for g in self._gene_diseases]
        rows.sort(key=lambda r: r["disease_count"], reverse=True)  # type: ignore
        return rows[:top_n]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "associations": len(self._associations),
            "diseases": len(self._disease_genes),
            "genes": len(self._gene_diseases),
            "multi_disease_genes": len(self.multi_disease_genes()),
        }


def self_test() -> bool:
    engine = DiseaseGeneNetworkEngine()
    engine.add(DiseaseGeneAssociation("D_breast_cancer", "TP53", "causal", "strong"))
    engine.add(DiseaseGeneAssociation("D_breast_cancer", "BRCA1", "causal", "strong"))
    engine.add(DiseaseGeneAssociation("D_breast_cancer", "BRCA2", "causal", "strong"))
    engine.add(DiseaseGeneAssociation("D_ovarian_cancer", "BRCA1", "causal", "strong"))
    engine.add(DiseaseGeneAssociation("D_ovarian_cancer", "BRCA2", "causal", "strong"))
    engine.add(DiseaseGeneAssociation("D_li_fraumeni", "TP53", "causal", "strong"))
    assert engine.genes_for_disease("D_breast_cancer") == ["BRCA1", "BRCA2", "TP53"]
    assert engine.shared_genes("D_breast_cancer", "D_ovarian_cancer") == [
        "BRCA1", "BRCA2"]
    assert "TP53" in engine.multi_disease_genes()
    assert engine.gene_degree("BRCA1") == 2
    assert engine.top_genes(1)[0]["gene_symbol"] in ("TP53", "BRCA1", "BRCA2")
    print("disease_gene_network_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
