"""DESI Infinity System - Gene Function Analyzer (v6.2.0).

Structured gene function registry: molecular function, biological process,
cellular component, expression tissues, and disease links. GO-style
categories are opaque strings.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

FUNCTION_CLASSES = ("enzyme", "receptor", "transporter", "channel",
                    "transcription_factor", "structural", "signaling",
                    "chaperone", "regulatory_rna", "other")
SOURCE_TYPES = ("curated", "literature", "predicted")


class GeneFunctionError(Exception):
    """Base gene function error."""


@dataclass
class GeneFunction:
    gene_symbol: str
    name: str
    function_class: str = "other"
    molecular_functions: List[str] = field(default_factory=list)
    biological_processes: List[str] = field(default_factory=list)
    cellular_components: List[str] = field(default_factory=list)
    expression_tissues: List[str] = field(default_factory=list)
    disease_ids: List[str] = field(default_factory=list)
    paralogs: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.gene_symbol or not isinstance(self.gene_symbol, str):
            raise GeneFunctionError("gene_symbol required")
        if not self.name or not isinstance(self.name, str):
            raise GeneFunctionError("name required")
        if self.function_class not in FUNCTION_CLASSES:
            raise GeneFunctionError(f"invalid function_class: {self.function_class!r}")
        if self.source not in SOURCE_TYPES:
            raise GeneFunctionError(f"invalid source: {self.source!r}")


class GeneFunctionAnalyzer:
    """Registry with process/component/tissue/disease queries."""

    def __init__(self) -> None:
        self._genes: Dict[str, GeneFunction] = {}
        self._process_index: Dict[str, List[str]] = {}
        self._tissue_index: Dict[str, List[str]] = {}
        self._disease_index: Dict[str, List[str]] = {}

    def add(self, gene: GeneFunction) -> GeneFunction:
        if gene.gene_symbol in self._genes:
            raise GeneFunctionError(f"duplicate gene_symbol: {gene.gene_symbol}")
        self._genes[gene.gene_symbol] = gene
        for p in gene.biological_processes:
            self._process_index.setdefault(p, []).append(gene.gene_symbol)
        for t in gene.expression_tissues:
            self._tissue_index.setdefault(t, []).append(gene.gene_symbol)
        for did in gene.disease_ids:
            self._disease_index.setdefault(did, []).append(gene.gene_symbol)
        return gene

    def get(self, gene_symbol: str) -> GeneFunction:
        try:
            return self._genes[gene_symbol]
        except KeyError as exc:
            raise GeneFunctionError(f"unknown gene_symbol: {gene_symbol}") from exc

    def by_function_class(self, function_class: str) -> List[GeneFunction]:
        if function_class not in FUNCTION_CLASSES:
            raise GeneFunctionError(f"invalid function_class: {function_class!r}")
        return [g for g in self._genes.values() if g.function_class == function_class]

    def by_process(self, process: str) -> List[GeneFunction]:
        return [self.get(g) for g in self._process_index.get(process, [])]

    def by_tissue(self, tissue: str) -> List[GeneFunction]:
        return [self.get(g) for g in self._tissue_index.get(tissue, [])]

    def for_disease(self, disease_id: str) -> List[GeneFunction]:
        return [self.get(g) for g in self._disease_index.get(disease_id, [])]

    def shared_processes(self, gene_a: str, gene_b: str) -> List[str]:
        a = set(self.get(gene_a).biological_processes)
        b = set(self.get(gene_b).biological_processes)
        return sorted(a & b)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "genes": len(self._genes),
            "processes": len(self._process_index),
            "tissues": len(self._tissue_index),
            "diseases": len(self._disease_index),
        }


def self_test() -> bool:
    analyzer = GeneFunctionAnalyzer()
    analyzer.add(GeneFunction(
        "TP53", "Tumor protein p53", "transcription_factor",
        molecular_functions=["DNA binding", "transcription activation"],
        biological_processes=["DNA damage response", "apoptosis"],
        cellular_components=["nucleus"],
        expression_tissues=["ubiquitous"],
        disease_ids=["D_cancer"],
        paralogs=["TP63", "TP73"]))
    analyzer.add(GeneFunction(
        "BRCA1", "BRCA1 DNA repair associated", "enzyme",
        molecular_functions=["E3 ubiquitin ligase"],
        biological_processes=["DNA damage response", "homologous recombination"],
        cellular_components=["nucleus"],
        expression_tissues=["breast", "ovary"],
        disease_ids=["D_breast_cancer"]))
    assert analyzer.by_function_class("transcription_factor")[0].gene_symbol == "TP53"
    assert len(analyzer.by_process("DNA damage response")) == 2
    assert analyzer.by_tissue("breast")[0].gene_symbol == "BRCA1"
    assert analyzer.for_disease("D_cancer")[0].gene_symbol == "TP53"
    assert analyzer.shared_processes("TP53", "BRCA1") == ["DNA damage response"]
    print("gene_function_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
