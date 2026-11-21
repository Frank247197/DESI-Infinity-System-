"""DESI Infinity System - Dermatological Disease Engine (v6.2.0).

Stores skin diseases across inflammatory, infectious, neoplastic,
autoimmune, and genetic categories with affected skin layers, morphology
descriptors, biomarkers, and gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

DERM_CATEGORIES = ("inflammatory", "infectious", "neoplastic", "autoimmune",
                   "genetic", "papulosquamous", "vesiculobullous", "other")
SKIN_LAYERS = ("epidermis", "basal_layer", "spinous_layer", "granular_layer",
               "stratum_corneum", "dermis", "hypodermis", "hair_follicle",
               "sebaceous_gland", "sweat_gland")
SOURCES = ("curated", "literature", "predicted")


class DermatologicalError(Exception):
    """Base dermatological error."""


@dataclass
class DermatologicalDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_layers: List[str] = field(default_factory=list)
    morphology: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise DermatologicalError("disease_id required")
        if self.category not in DERM_CATEGORIES:
            raise DermatologicalError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise DermatologicalError(f"invalid source: {self.source!r}")
        for l in self.affected_layers:
            if l not in SKIN_LAYERS:
                raise DermatologicalError(f"invalid affected_layer: {l!r}")


class DermatologicalDiseaseEngine:
    """Registry with layer / morphology / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, DermatologicalDisease] = {}
        self._layer_index: Dict[str, List[str]] = {}
        self._morphology_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: DermatologicalDisease) -> DermatologicalDisease:
        if disease.disease_id in self._diseases:
            raise DermatologicalError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for l in disease.affected_layers:
            self._layer_index.setdefault(l, []).append(disease.disease_id)
        for m in disease.morphology:
            self._morphology_index.setdefault(m, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> DermatologicalDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise DermatologicalError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[DermatologicalDisease]:
        if category not in DERM_CATEGORIES:
            raise DermatologicalError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_layer(self, layer: str) -> List[DermatologicalDisease]:
        if layer not in SKIN_LAYERS:
            raise DermatologicalError(f"invalid layer: {layer!r}")
        return [self.get(did) for did in self._layer_index.get(layer, [])]

    def by_morphology(self, morphology: str) -> List[DermatologicalDisease]:
        return [self.get(did) for did in self._morphology_index.get(morphology, [])]

    def by_gene(self, gene_symbol: str) -> List[DermatologicalDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "layers": len(self._layer_index),
            "morphologies": len(self._morphology_index),
        }


def self_test() -> bool:
    engine = DermatologicalDiseaseEngine()
    engine.add(DermatologicalDisease(
        "D_psoriasis", "Psoriasis", "papulosquamous",
        affected_layers=["epidermis", "dermis"],
        morphology=["plaque", "scale"],
        biomarkers=["IL-17"],
        gene_associations=["HLA-C"]))
    engine.add(DermatologicalDisease(
        "D_pemphigus", "Pemphigus vulgaris", "vesiculobullous",
        affected_layers=["epidermis"],
        morphology=["blister"],
        biomarkers=["anti-desmoglein"],
        gene_associations=["HLA-DRB1"]))
    assert engine.by_category("papulosquamous")[0].disease_id == "D_psoriasis"
    assert engine.by_layer("epidermis")[0].disease_id == "D_psoriasis"
    assert engine.by_morphology("blister")[0].disease_id == "D_pemphigus"
    assert engine.by_gene("HLA-C")[0].disease_id == "D_psoriasis"
    print("dermatological_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
