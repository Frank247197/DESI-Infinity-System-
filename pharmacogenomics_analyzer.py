"""DESI Infinity System - Pharmacogenomics Analyzer (v6.2.0).

Research-level pharmacogenomic associations: gene-drug pairs, variant
effects on drug metabolism, and CPIC-style research phenotypes. NO
dosing guidance or treatment recommendations.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

METABOLIZER_STATUS = ("poor", "intermediate", "normal", "rapid",
                      "ultrarapid", "unknown")
EFFECT_TYPES = ("efficacy", "toxicity", "metabolism", "transport",
                "target_binding", "unknown")
SOURCES = ("curated", "literature", "predicted")


class PharmacogenomicsError(Exception):
    """Base pharmacogenomics error."""


@dataclass
class PharmacogenomicAssociation:
    association_id: str
    gene_symbol: str
    drug_name: str
    variant_ids: List[str] = field(default_factory=list)
    effect_type: str = "unknown"
    metabolizer_status: str = "unknown"
    population: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.association_id or not isinstance(self.association_id, str):
            raise PharmacogenomicsError("association_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise PharmacogenomicsError("gene_symbol required")
        if not self.drug_name or not isinstance(self.drug_name, str):
            raise PharmacogenomicsError("drug_name required")
        if self.effect_type not in EFFECT_TYPES:
            raise PharmacogenomicsError(f"invalid effect_type: {self.effect_type!r}")
        if self.metabolizer_status not in METABOLIZER_STATUS:
            raise PharmacogenomicsError(
                f"invalid metabolizer_status: {self.metabolizer_status!r}")
        if self.source not in SOURCES:
            raise PharmacogenomicsError(f"invalid source: {self.source!r}")


class PharmacogenomicsAnalyzer:
    """Association registry with gene / drug / variant queries."""

    def __init__(self) -> None:
        self._assocs: Dict[str, PharmacogenomicAssociation] = {}
        self._gene_index: Dict[str, List[str]] = {}
        self._drug_index: Dict[str, List[str]] = {}
        self._variant_index: Dict[str, List[str]] = {}

    def add(self, assoc: PharmacogenomicAssociation) -> PharmacogenomicAssociation:
        if assoc.association_id in self._assocs:
            raise PharmacogenomicsError(f"duplicate association_id: {assoc.association_id}")
        self._assocs[assoc.association_id] = assoc
        self._gene_index.setdefault(assoc.gene_symbol, []).append(assoc.association_id)
        self._drug_index.setdefault(assoc.drug_name, []).append(assoc.association_id)
        for v in assoc.variant_ids:
            self._variant_index.setdefault(v, []).append(assoc.association_id)
        return assoc

    def get(self, association_id: str) -> PharmacogenomicAssociation:
        try:
            return self._assocs[association_id]
        except KeyError as exc:
            raise PharmacogenomicsError(
                f"unknown association_id: {association_id}") from exc

    def by_gene(self, gene_symbol: str) -> List[PharmacogenomicAssociation]:
        return [self.get(a) for a in self._gene_index.get(gene_symbol, [])]

    def by_drug(self, drug_name: str) -> List[PharmacogenomicAssociation]:
        return [self.get(a) for a in self._drug_index.get(drug_name, [])]

    def by_variant(self, variant_id: str) -> List[PharmacogenomicAssociation]:
        return [self.get(a) for a in self._variant_index.get(variant_id, [])]

    def by_effect(self, effect_type: str) -> List[PharmacogenomicAssociation]:
        if effect_type not in EFFECT_TYPES:
            raise PharmacogenomicsError(f"invalid effect_type: {effect_type!r}")
        return [a for a in self._assocs.values() if a.effect_type == effect_type]

    def poor_metabolizers(self) -> List[PharmacogenomicAssociation]:
        return [a for a in self._assocs.values()
                if a.metabolizer_status == "poor"]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "associations": len(self._assocs),
            "genes": len(self._gene_index),
            "drugs": len(self._drug_index),
            "poor_metabolizers": len(self.poor_metabolizers()),
        }


def self_test() -> bool:
    analyzer = PharmacogenomicsAnalyzer()
    analyzer.add(PharmacogenomicAssociation(
        "PG1", "CYP2D6", "codeine", ["rs3892097"],
        effect_type="metabolism", metabolizer_status="poor"))
    analyzer.add(PharmacogenomicAssociation(
        "PG2", "CYP2C19", "clopidogrel", ["rs4244285"],
        effect_type="efficacy", metabolizer_status="poor"))
    analyzer.add(PharmacogenomicAssociation(
        "PG3", "TPMT", "azathioprine", ["rs1800462"],
        effect_type="toxicity", metabolizer_status="intermediate"))
    assert len(analyzer.by_gene("CYP2D6")) == 1
    assert analyzer.by_drug("codeine")[0].association_id == "PG1"
    assert analyzer.by_variant("rs4244285")[0].association_id == "PG2"
    assert len(analyzer.by_effect("toxicity")) == 1
    assert len(analyzer.poor_metabolizers()) == 2
    print("pharmacogenomics_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
