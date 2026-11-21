"""DESI Infinity System - Neurological Disease Engine (v6.2.0).

Stores neurological disorders across neurodegenerative, psychiatric,
neurodevelopmental, cerebrovascular, and epileptic categories, with
affected brain regions, neurotransmitters, and gene associations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

NEURO_CATEGORIES = ("neurodegenerative", "psychiatric", "neurodevelopmental",
                    "cerebrovascular", "epileptic", "demyelinating",
                    "neuromuscular", "other")
SOURCES = ("curated", "literature", "predicted")


class NeurologicalError(Exception):
    """Base neurological error."""


@dataclass
class NeurologicalDisease:
    disease_id: str
    name: str
    category: str = "other"
    affected_brain_regions: List[str] = field(default_factory=list)
    neurotransmitters: List[str] = field(default_factory=list)
    gene_associations: List[str] = field(default_factory=list)
    biomarkers: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise NeurologicalError("disease_id required")
        if self.category not in NEURO_CATEGORIES:
            raise NeurologicalError(f"invalid category: {self.category!r}")
        if self.source not in SOURCES:
            raise NeurologicalError(f"invalid source: {self.source!r}")


class NeurologicalDiseaseEngine:
    """Registry with category / region / neurotransmitter / gene queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, NeurologicalDisease] = {}
        self._region_index: Dict[str, List[str]] = {}
        self._nt_index: Dict[str, List[str]] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disease: NeurologicalDisease) -> NeurologicalDisease:
        if disease.disease_id in self._diseases:
            raise NeurologicalError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for r in disease.affected_brain_regions:
            self._region_index.setdefault(r, []).append(disease.disease_id)
        for n in disease.neurotransmitters:
            self._nt_index.setdefault(n, []).append(disease.disease_id)
        for g in disease.gene_associations:
            self._gene_index.setdefault(g, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> NeurologicalDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise NeurologicalError(f"unknown disease_id: {disease_id}") from exc

    def by_category(self, category: str) -> List[NeurologicalDisease]:
        if category not in NEURO_CATEGORIES:
            raise NeurologicalError(f"invalid category: {category!r}")
        return [d for d in self._diseases.values() if d.category == category]

    def by_region(self, region: str) -> List[NeurologicalDisease]:
        return [self.get(did) for did in self._region_index.get(region, [])]

    def by_neurotransmitter(self, nt: str) -> List[NeurologicalDisease]:
        return [self.get(did) for did in self._nt_index.get(nt, [])]

    def by_gene(self, gene_symbol: str) -> List[NeurologicalDisease]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "regions": len(self._region_index),
            "neurotransmitters": len(self._nt_index),
            "genes": len(self._gene_index),
        }


def self_test() -> bool:
    engine = NeurologicalDiseaseEngine()
    engine.add(NeurologicalDisease(
        "D_alz", "Alzheimer disease", "neurodegenerative",
        affected_brain_regions=["hippocampus", "cortex"],
        neurotransmitters=["acetylcholine"],
        gene_associations=["APP", "PSEN1", "APOE"],
        biomarkers=["amyloid_beta", "tau"]))
    engine.add(NeurologicalDisease(
        "D_pd", "Parkinson disease", "neurodegenerative",
        affected_brain_regions=["substantia_nigra"],
        neurotransmitters=["dopamine"],
        gene_associations=["SNCA", "LRRK2"]))
    assert engine.by_category("neurodegenerative")[0].disease_id == "D_alz"
    assert engine.by_region("substantia_nigra")[0].disease_id == "D_pd"
    assert engine.by_neurotransmitter("dopamine")[0].disease_id == "D_pd"
    assert len(engine.by_gene("APOE")) == 1
    assert engine.stats()["diseases"] == 2
    print("neurological_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
