"""DESI Infinity System - Viral Genome Annotation (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class ViralGene:
    gene_id: str
    virus_id: str
    name: str
    start: int
    end: int
    strand: str = "+"

    def __post_init__(self) -> None:
        if not self.gene_id or not self.virus_id:
            raise ValueError("gene_id and virus_id required")
        if self.start < 0 or self.end <= self.start:
            raise ValueError("invalid genomic coordinates")
        if self.strand not in ("+", "-", "."):
            raise ValueError("strand must be +, -, or .")

    def length(self) -> int:
        return self.end - self.start

class ViralAnnotationEngine:
    def __init__(self) -> None:
        self._genes: Dict[str, List[ViralGene]] = {}

    def add(self, gene: ViralGene) -> None:
        if any(g.gene_id == gene.gene_id for g in self._genes.get(gene.virus_id, [])):
            raise ValueError(f"duplicate gene_id {gene.gene_id} for virus {gene.virus_id}")
        self._genes.setdefault(gene.virus_id, []).append(gene)

    def get_genes(self, virus_id: str) -> List[ViralGene]:
        return sorted(self._genes.get(virus_id, []), key=lambda g: g.start)

    def find_overlaps(self, virus_id: str) -> List[tuple[str, str]]:
        genes = self.get_genes(virus_id)
        overlaps = []
        for i in range(len(genes)):
            for j in range(i + 1, len(genes)):
                if genes[i].end > genes[j].start:
                    overlaps.append((genes[i].gene_id, genes[j].gene_id))
        return overlaps

    def total_coding_length(self, virus_id: str) -> int:
        return sum(g.length() for g in self.get_genes(virus_id))

def self_test() -> bool:
    engine = ViralAnnotationEngine()
    engine.add(ViralGene("G1", "VS_sars2", "ORF1a", 0, 13000, "+"))
    engine.add(ViralGene("G2", "VS_sars2", "S", 21000, 25000, "+"))
    engine.add(ViralGene("G3", "VS_sars2", "ORF1b_overlap", 12900, 21500, "+"))
    
    assert len(engine.get_genes("VS_sars2")) == 3
    assert engine.get_genes("VS_sars2")[0].name == "ORF1a"
    assert ("G1", "G3") in engine.find_overlaps("VS_sars2")
    assert engine.total_coding_length("VS_sars2") > 20000
    print("viral_genome_annotation: OK")
    return True

if __name__ == "__main__":
    self_test()
