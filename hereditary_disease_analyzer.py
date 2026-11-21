"""DESI Infinity System - Hereditary Disease Analyzer (v6.2.0).

Analyzes hereditary disease pedigree patterns and Mendelian transmission
modes at a research level. Accepts structured pedigree input and reports
compatible inheritance modes. NOT clinical genetic counseling.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MENDELIAN_MODES = ("autosomal_dominant", "autosomal_recessive",
                   "x_linked_dominant", "x_linked_recessive",
                   "mitochondrial", "incompatible", "unknown")
SEXES = ("M", "F", "unknown")
PHENOTYPES = ("affected", "unaffected", "unknown")


class HereditaryDiseaseError(Exception):
    """Base hereditary disease error."""


@dataclass
class Individual:
    individual_id: str
    sex: str = "unknown"
    phenotype: str = "unknown"
    father_id: str = ""
    mother_id: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.individual_id or not isinstance(self.individual_id, str):
            raise HereditaryDiseaseError("individual_id required")
        if self.sex not in SEXES:
            raise HereditaryDiseaseError(f"invalid sex: {self.sex!r}")
        if self.phenotype not in PHENOTYPES:
            raise HereditaryDiseaseError(f"invalid phenotype: {self.phenotype!r}")


@dataclass
class HereditaryDisease:
    disease_id: str
    name: str
    known_modes: List[str] = field(default_factory=list)
    candidate_genes: List[str] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise HereditaryDiseaseError("disease_id required")
        for m in self.known_modes:
            if m not in MENDELIAN_MODES:
                raise HereditaryDiseaseError(f"invalid inheritance mode: {m!r}")


class HereditaryDiseaseAnalyzer:
    """Pedigree store with compatibility heuristics."""

    def __init__(self) -> None:
        self._diseases: Dict[str, HereditaryDisease] = {}
        self._pedigrees: Dict[str, Dict[str, Individual]] = {}

    def register_disease(self, disease: HereditaryDisease) -> HereditaryDisease:
        if disease.disease_id in self._diseases:
            raise HereditaryDiseaseError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        return disease

    def add_individual(self, disease_id: str, individual: Individual) -> None:
        if disease_id not in self._diseases:
            raise HereditaryDiseaseError(f"unknown disease_id: {disease_id}")
        family = self._pedigrees.setdefault(disease_id, {})
        if individual.individual_id in family:
            raise HereditaryDiseaseError(
                f"duplicate individual_id: {individual.individual_id}")
        family[individual.individual_id] = individual

    def _check_ad(self, family: Dict[str, Individual]) -> bool:
        # affected child must have at least one affected parent
        for ind in family.values():
            if ind.phenotype != "affected":
                continue
            if not ind.father_id and not ind.mother_id:
                continue
            parents = [family[p] for p in (ind.father_id, ind.mother_id)
                       if p in family]
            if parents and all(p.phenotype != "affected" for p in parents):
                return False
        return True

    def _check_ar(self, family: Dict[str, Individual]) -> bool:
        # affected child with two unaffected parents is compatible
        for ind in family.values():
            if ind.phenotype != "affected":
                continue
            parents = [family[p] for p in (ind.father_id, ind.mother_id)
                       if p in family]
            if len(parents) == 2 and all(p.phenotype == "unaffected" for p in parents):
                return True
        return False

    def _check_x_linked(self, family: Dict[str, Individual]) -> bool:
        # affected father -> daughters must be affected (dominant) or carriers (recessive)
        for ind in family.values():
            if ind.sex != "F":
                continue
            if ind.father_id and ind.father_id in family:
                father = family[ind.father_id]
                if father.phenotype == "affected" and ind.phenotype == "unaffected":
                    if father.sex == "M" and father.phenotype == "affected":
                        return False
        return True

    def compatible_modes(self, disease_id: str) -> List[str]:
        family = self._pedigrees.get(disease_id, {})
        if not family:
            return ["unknown"]
        compatible: List[str] = []
        if self._check_ad(family):
            compatible.append("autosomal_dominant")
        if self._check_ar(family):
            compatible.append("autosomal_recessive")
        if self._check_x_linked(family):
            compatible.append("x_linked_dominant")
            compatible.append("x_linked_recessive")
        return compatible or ["incompatible"]

    def conflicts_with_known(self, disease_id: str) -> List[str]:
        disease = self._diseases.get(disease_id)
        if disease is None:
            raise HereditaryDiseaseError(f"unknown disease_id: {disease_id}")
        compatible = set(self.compatible_modes(disease_id))
        known = set(disease.known_modes)
        if not known:
            return []
        return sorted(known - compatible)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "pedigrees": sum(1 for f in self._pedigrees.values() if f),
            "individuals": sum(len(f) for f in self._pedigrees.values()),
        }


def self_test() -> bool:
    analyzer = HereditaryDiseaseAnalyzer()
    analyzer.register_disease(HereditaryDisease(
        "D_cf", "Cystic fibrosis",
        known_modes=["autosomal_recessive"], candidate_genes=["CFTR"]))
    analyzer.add_individual("D_cf", Individual("I1", "M", "unaffected"))
    analyzer.add_individual("D_cf", Individual("I2", "F", "unaffected"))
    analyzer.add_individual("D_cf", Individual(
        "I3", "M", "affected", father_id="I1", mother_id="I2"))
    modes = analyzer.compatible_modes("D_cf")
    assert "autosomal_recessive" in modes
    assert analyzer.conflicts_with_known("D_cf") == []
    assert analyzer.stats()["individuals"] == 3
    print("hereditary_disease_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
