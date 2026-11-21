"""DESI Infinity System - Metabolic Disease Engine (v6.2.0).

Stores inborn and acquired metabolic diseases with affected enzymes,
metabolite markers, and pathway references. Research-only; no dosing or
clinical guidance.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CATEGORIES = ("carbohydrate", "lipid", "amino_acid", "nucleotide",
              "mitochondrial", "lysosomal", "other")
SOURCES = ("curated", "literature", "predicted")


class MetabolicError(Exception):
    """Base metabolic disease error."""


@dataclass
class MetabolicDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_enzymes: List[str] = field(default_factory=list)
    metabolite_markers: List[str] = field(default_factory=list)
    pathway_ids: List[str] = field(default_factory=list)
    gene_symbols: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise MetabolicError("disease_id required")
        if self.category not in CATEGORIES:
            raise MetabolicError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise MetabolicError(f"invalid source: {self.source!r}")


class MetabolicDiseaseEngine:
    """Registry with enzyme / marker / pathway queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, MetabolicDisease] = {}
        self._enzyme_index: Dict[str, List[str]] = {}
        self._marker_index: Dict[str, List[str]] = {}
        self._pathway_index: Dict[str, List[str]] = {}

    def add(self, disease: MetabolicDisease) -> MetabolicDisease:
        if disease.disease_id in self._diseases:
            raise MetabolicError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for e in disease.affected_enzymes:
            self._enzyme_index.setdefault(e, []).append(disease.disease_id)
        for m in disease.metabolite_markers:
            self._marker_index.setdefault(m, []).append(disease.disease_id)
        for p in disease.pathway_ids:
            self._pathway_index.setdefault(p, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> MetabolicDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise MetabolicError(f"unknown disease_id: {disease_id}") from exc

    def by_enzyme(self, enzyme: str) -> List[MetabolicDisease]:
        return [self.get(did) for did in self._enzyme_index.get(enzyme, [])]

    def by_marker(self, marker: str) -> List[MetabolicDisease]:
        return [self.get(did) for did in self._marker_index.get(marker, [])]

    def by_pathway(self, pathway_id: str) -> List[MetabolicDisease]:
        return [self.get(did) for did in self._pathway_index.get(pathway_id, [])]

    def by_category(self, category: str) -> List[MetabolicDisease]:
        if category not in CATEGORIES:
            raise MetabolicError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "enzymes": len(self._enzyme_index),
            "pathways": len(self._pathway_index),
        }


def self_test() -> bool:
    engine = MetabolicDiseaseEngine()
    engine.add(MetabolicDisease("D_pku", "Phenylketonuria", "amino_acid",
                                affected_enzymes=["PAH"],
                                metabolite_markers=["phenylalanine"],
                                pathway_ids=["R-HSA-71182"],
                                gene_symbols=["PAH"]))
    engine.add(MetabolicDisease("D_gout", "Gout", "nucleotide",
                                affected_enzymes=["HGPRT"],
                                metabolite_markers=["urate"]))
    assert engine.by_enzyme("PAH")[0].disease_id == "D_pku"
    assert engine.by_marker("urate")[0].disease_id == "D_gout"
    assert engine.by_pathway("R-HSA-71182")[0].disease_id == "D_pku"
    assert len(engine.by_category("amino_acid")) == 1
    print("021 metabolic_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
