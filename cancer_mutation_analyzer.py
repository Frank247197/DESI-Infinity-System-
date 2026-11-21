"""DESI Infinity System - Cancer Mutation Analyzer (v6.2.0).

Analyzes somatic and germline cancer mutations with functional-effect
annotations, oncogenicity labels (curated), and VAF statistics. Research
annotations only — no clinical interpretation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MUTATION_ORIGINS = ("somatic", "germline", "unknown")
FUNCTIONAL_EFFECTS = ("gain_of_function", "loss_of_function",
                      "dominant_negative", "neutral", "unknown")
ONCOGENICITY = ("oncogenic", "likely_oncogenic", "uncertain",
                "likely_benign", "benign", "unknown")
SOURCES = ("curated", "literature", "predicted")


class CancerMutationError(Exception):
    """Base cancer mutation error."""


@dataclass
class CancerMutation:
    mutation_id: str
    cancer_id: str
    gene_symbol: str
    origin: str = "unknown"
    functional_effect: str = "unknown"
    oncogenicity: str = "unknown"
    vaf: Optional[float] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.mutation_id or not isinstance(self.mutation_id, str):
            raise CancerMutationError("mutation_id required")
        if not self.cancer_id or not isinstance(self.cancer_id, str):
            raise CancerMutationError("cancer_id required")
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise CancerMutationError("gene_symbol required")
        if self.origin not in MUTATION_ORIGINS:
            raise CancerMutationError(f"invalid origin: {self.origin!r}")
        if self.functional_effect not in FUNCTIONAL_EFFECTS:
            raise CancerMutationError(f"invalid functional_effect: {self.functional_effect!r}")
        if self.oncogenicity not in ONCOGENICITY:
            raise CancerMutationError(f"invalid oncogenicity: {self.oncogenicity!r}")
        if self.source not in SOURCES:
            raise CancerMutationError(f"invalid source: {self.source!r}")
        if self.vaf is not None:
            if not isinstance(self.vaf, (int, float)) or not 0.0 <= float(self.vaf) <= 1.0:
                raise CancerMutationError("vaf must be in [0, 1] or None")


class CancerMutationAnalyzer:
    """Registry + analysis of cancer mutations."""

    def __init__(self) -> None:
        self._mutations: Dict[str, CancerMutation] = {}
        self._gene_index: Dict[str, List[str]] = {}
        self._cancer_index: Dict[str, List[str]] = {}

    def add(self, mutation: CancerMutation) -> CancerMutation:
        if mutation.mutation_id in self._mutations:
            raise CancerMutationError(f"duplicate mutation_id: {mutation.mutation_id}")
        self._mutations[mutation.mutation_id] = mutation
        self._gene_index.setdefault(mutation.gene_symbol, []).append(mutation.mutation_id)
        self._cancer_index.setdefault(mutation.cancer_id, []).append(mutation.mutation_id)
        return mutation

    def get(self, mutation_id: str) -> CancerMutation:
        try:
            return self._mutations[mutation_id]
        except KeyError as exc:
            raise CancerMutationError(f"unknown mutation_id: {mutation_id}") from exc

    def by_gene(self, gene_symbol: str) -> List[CancerMutation]:
        return [self.get(mid) for mid in self._gene_index.get(gene_symbol, [])]

    def for_cancer(self, cancer_id: str) -> List[CancerMutation]:
        return [self.get(mid) for mid in self._cancer_index.get(cancer_id, [])]

    def oncogenic(self) -> List[CancerMutation]:
        return [m for m in self._mutations.values()
                if m.oncogenicity in ("oncogenic", "likely_oncogenic")]

    def somatic_only(self) -> List[CancerMutation]:
        return [m for m in self._mutations.values() if m.origin == "somatic"]

    def high_vaf(self, threshold: float = 0.2) -> List[CancerMutation]:
        return [m for m in self._mutations.values()
                if m.vaf is not None and m.vaf >= threshold]

    def gene_landscape(self, cancer_id: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for m in self.for_cancer(cancer_id):
            counts[m.gene_symbol] = counts.get(m.gene_symbol, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "mutations": len(self._mutations),
            "genes": len(self._gene_index),
            "cancers": len(self._cancer_index),
            "oncogenic": len(self.oncogenic()),
        }


def self_test() -> bool:
    analyzer = CancerMutationAnalyzer()
    analyzer.add(CancerMutation("M1", "C_luad", "EGFR", "somatic",
                                "gain_of_function", "oncogenic", vaf=0.35))
    analyzer.add(CancerMutation("M2", "C_luad", "TP53", "somatic",
                                "loss_of_function", "likely_oncogenic", vaf=0.45))
    analyzer.add(CancerMutation("M3", "C_luad", "EGFR", "somatic",
                                "gain_of_function", "oncogenic", vaf=0.15))
    assert len(analyzer.by_gene("EGFR")) == 2
    assert len(analyzer.for_cancer("C_luad")) == 3
    assert len(analyzer.oncogenic()) == 2
    assert len(analyzer.high_vaf(0.2)) == 2
    assert analyzer.gene_landscape("C_luad")["EGFR"] == 2
    print("cancer_mutation_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
