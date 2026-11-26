"""DESI Infinity System - Viral Genome Comparison (v6.2.0)."""
from __future__ import annotations
import logging
from collections import Counter
from dataclasses import dataclass

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class GenomeProfile:
    genome_id: str
    virus_id: str
    sequence: str

    def __post_init__(self) -> None:
        if not self.genome_id or not self.sequence:
            raise ValueError("genome_id and sequence required")
        self.sequence = self.sequence.upper().replace("U", "T")

class GenomeComparator:
    def __init__(self) -> None:
        self._genomes: dict[str, GenomeProfile] = {}

    def add(self, profile: GenomeProfile) -> None:
        if profile.genome_id in self._genomes:
            raise ValueError(f"duplicate genome_id: {profile.genome_id}")
        self._genomes[profile.genome_id] = profile

    def get(self, genome_id: str) -> GenomeProfile:
        if genome_id not in self._genomes:
            raise ValueError(f"unknown genome_id: {genome_id}")
        return self._genomes[genome_id]

    def snp_distance(self, id1: str, id2: str) -> int:
        """Counts single nucleotide polymorphisms between two sequences."""
        g1, g2 = self.get(id1), self.get(id2)
        if len(g1.sequence) != len(g2.sequence):
            raise ValueError("Genomes must be aligned (same length) for SNP comparison")
        return sum(1 for a, b in zip(g1.sequence, g2.sequence) if a != b)

    def jaccard_similarity(self, id1: str, id2: str, k: int = 3) -> float:
        """Calculates Jaccard similarity using k-mer sets."""
        g1, g2 = self.get(id1), self.get(id2)
        kmers1 = {g1.sequence[i:i+k] for i in range(len(g1.sequence) - k + 1)}
        kmers2 = {g2.sequence[i:i+k] for i in range(len(g2.sequence) - k + 1)}
        if not kmers1 or not kmers2:
            return 0.0
        return round(len(kmers1 & kmers2) / len(kmers1 | kmers2), 4)

def self_test() -> bool:
    comp = GenomeComparator()
    comp.add(GenomeProfile("S1", "VS_flu", "ATGCGTACGT"))
    comp.add(GenomeProfile("S2", "VS_flu", "ATGCGTTCGT"))
    comp.add(GenomeProfile("S3", "VS_flu", "GGGGCCCCAA"))
    
    assert comp.snp_distance("S1", "S2") == 1
    assert comp.snp_distance("S1", "S1") == 0
    assert 0.0 <= comp.jaccard_similarity("S1", "S2", 2) <= 1.0
    assert comp.jaccard_similarity("S1", "S3", 2) < 0.5
    print("viral_genome_comparison: OK")
    return True

if __name__ == "__main__":
    self_test()
