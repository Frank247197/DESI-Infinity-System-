"""DESI Infinity System - Viral Recombination Research (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class RecombinantLineage:
    recombinant_id: str
    virus_id: str
    name: str
    parent_a: str
    parent_b: str
    breakpoints: List[int] = field(default_factory=list)
    detection_date: str = ""

    def __post_init__(self) -> None:
        if not self.recombinant_id or not self.virus_id:
            raise ValueError("IDs required")
        if not self.parent_a or not self.parent_b:
            raise ValueError("Both parents required")
        if self.parent_a == self.parent_b:
            raise ValueError("Parents must be different")

class RecombinationResearch:
    def __init__(self) -> None:
        self._recombinants: Dict[str, RecombinantLineage] = {}

    def add(self, rec: RecombinantLineage) -> None:
        if rec.recombinant_id in self._recombinants:
            raise ValueError(f"duplicate recombinant_id: {rec.recombinant_id}")
        self._recombinants[rec.recombinant_id] = rec

    def by_parent(self, virus_id: str, parent_lineage: str) -> List[RecombinantLineage]:
        return [r for r in self._recombinants.values() 
                if r.virus_id == virus_id and parent_lineage in (r.parent_a, r.parent_b)]

    def multi_breakpoint(self, virus_id: str) -> List[RecombinantLineage]:
        return [r for r in self._recombinants.values() if r.virus_id == virus_id and len(r.breakpoints) > 1]

def self_test() -> bool:
    research = RecombinationResearch()
    research.add(RecombinantLineage("R1", "VS_sars2", "XBB", "BJ.1", "BM.1.1.1", [1000, 5000]))
    research.add(RecombinantLineage("R2", "VS_sars2", "XD", "Delta", "Omicron", [3500]))
    
    assert len(research.by_parent("VS_sars2", "BJ.1")) == 1
    assert len(research.multi_breakpoint("VS_sars2")) == 1
    assert research.multi_breakpoint("VS_sars2")[0].name == "XBB"
    print("viral_recombination_research: OK")
    return True

if __name__ == "__main__":
    self_test()
