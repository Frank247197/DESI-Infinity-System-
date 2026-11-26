"""DESI Infinity System - Viral Phylogenetics Engine (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class SequenceNode:
    seq_id: str
    sequence: str

    def __post_init__(self) -> None:
        if not self.seq_id or not self.sequence:
            raise ValueError("seq_id and sequence required")
        self.sequence = self.sequence.upper()

class PhylogeneticsEngine:
    def __init__(self) -> None:
        self._nodes: Dict[str, SequenceNode] = {}

    def add(self, node: SequenceNode) -> None:
        if node.seq_id in self._nodes:
            raise ValueError(f"duplicate seq_id: {node.seq_id}")
        self._nodes[node.seq_id] = node

    def hamming_distance(self, id1: str, id2: str) -> int:
        if id1 not in self._nodes or id2 not in self._nodes:
            raise ValueError("seq_ids not found")
        s1, s2 = self._nodes[id1].sequence, self._nodes[id2].sequence
        if len(s1) != len(s2):
            raise ValueError("Sequences must be aligned")
        return sum(1 for a, b in zip(s1, s2) if a != b)

    def distance_matrix(self) -> Dict[str, Dict[str, int]]:
        ids = list(self._nodes.keys())
        matrix = {i: {} for i in ids}
        for i in range(len(ids)):
            for j in range(i, len(ids)):
                d = self.hamming_distance(ids[i], ids[j])
                matrix[ids[i]][ids[j]] = d
                matrix[ids[j]][ids[i]] = d
        return matrix

def self_test() -> bool:
    engine = PhylogeneticsEngine()
    engine.add(SequenceNode("A", "ACGT"))
    engine.add(SequenceNode("B", "ACGA"))
    engine.add(SequenceNode("C", "TTGT"))
    
    assert engine.hamming_distance("A", "B") == 1
    matrix = engine.distance_matrix()
    assert matrix["A"]["B"] == 1 and matrix["A"]["C"] == 2
    print("viral_phylogenetics_engine: OK")
    return True

if __name__ == "__main__":
    self_test()
