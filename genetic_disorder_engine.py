"""DESI Infinity System - Genetic Disorder Engine (v6.2.0).

Stores genetic disorders with inheritance mode, penetrance, gene linkage,
and known variant-class patterns. Supports carrier-risk research
calculations (Mendelian probability) — explicitly NOT clinical counseling.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INHERITANCE_MODES = ("autosomal_dominant", "autosomal_recessive", "x_linked_dominant",
                     "x_linked_recessive", "mitochondrial", "de_novo", "complex")
SOURCES = ("curated", "literature", "predicted")


class GeneticDisorderError(Exception):
    """Base genetic disorder error."""


@dataclass
class GeneticDisorder:
    disorder_id: str
    name: str
    inheritance_mode: str
    causative_genes: List[str] = field(default_factory=list)
    penetrance: Optional[float] = None
    prevalence_per_100k: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disorder_id or not isinstance(self.disorder_id, str):
            raise GeneticDisorderError("disorder_id required")
        if self.inheritance_mode not in INHERITANCE_MODES:
            raise GeneticDisorderError(f"invalid inheritance_mode: {self.inheritance_mode!r}")
        if self.source not in SOURCES:
            raise GeneticDisorderError(f"invalid source: {self.source!r}")
        if self.penetrance is not None:
            if not isinstance(self.penetrance, (int, float)) or not 0.0 <= self.penetrance <= 1.0:
                raise GeneticDisorderError("penetrance must be in [0, 1] or None")


class GeneticDisorderEngine:
    """Registry + Mendelian carrier-probability research helper."""

    def __init__(self) -> None:
        self._disorders: Dict[str, GeneticDisorder] = {}
        self._gene_index: Dict[str, List[str]] = {}

    def add(self, disorder: GeneticDisorder) -> GeneticDisorder:
        if disorder.disorder_id in self._disorders:
            raise GeneticDisorderError(f"duplicate disorder_id: {disorder.disorder_id}")
        self._disorders[disorder.disorder_id] = disorder
        for g in disorder.causative_genes:
            self._gene_index.setdefault(g, []).append(disorder.disorder_id)
        return disorder

    def get(self, disorder_id: str) -> GeneticDisorder:
        try:
            return self._disorders[disorder_id]
        except KeyError as exc:
            raise GeneticDisorderError(f"unknown disorder_id: {disorder_id}") from exc

    def by_gene(self, gene_symbol: str) -> List[GeneticDisorder]:
        return [self.get(did) for did in self._gene_index.get(gene_symbol, [])]

    def by_inheritance(self, mode: str) -> List[GeneticDisorder]:
        if mode not in INHERITANCE_MODES:
            raise GeneticDisorderError(f"invalid inheritance_mode: {mode!r}")
        return [d for d in self._disorders.values() if d.inheritance_mode == mode]

    def carrier_carrier_recurrence(self, disorder_id: str) -> Dict[str, float]:
        """Mendelian probability for two carrier parents (autosomal recessive).

        Returns proportions: affected, carrier, unaffected.
        Research-only; NOT clinical counseling.
        """
        d = self.get(disorder_id)
        if d.inheritance_mode != "autosomal_recessive":
            return {"applicable": 0.0, "reason": 1.0}
        pen = d.penetrance if d.penetrance is not None else 1.0
        return {
            "affected": round(0.25 * pen, 4),
            "carrier": 0.5,
            "unaffected": round(1.0 - 0.25 * pen, 4),
        }

    def high_penetrance(self, threshold: float = 0.8) -> List[GeneticDisorder]:
        return [d for d in self._disorders.values()
                if d.penetrance is not None and d.penetrance >= threshold]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "disorders": len(self._disorders),
            "genes": len(self._gene_index),
            "high_penetrance": len(self.high_penetrance()),
        }


def self_test() -> bool:
    engine = GeneticDisorderEngine()
    engine.add(GeneticDisorder("GD_cf", "Cystic fibrosis", "autosomal_recessive",
                               causative_genes=["CFTR"], penetrance=1.0))
    engine.add(GeneticDisorder("GD_hd", "Huntington", "autosomal_dominant",
                               causative_genes=["HTT"], penetrance=0.95))
    assert engine.by_gene("CFTR")[0].disorder_id == "GD_cf"
    rec = engine.carrier_carrier_recurrence("GD_cf")
    assert rec["affected"] == 0.25
    assert len(engine.by_inheritance("autosomal_dominant")) == 1
    assert len(engine.high_penetrance(0.9)) == 2
    print("018 genetic_disorder_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
