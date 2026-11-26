"""DESI Infinity System - Viral Mutation Evidence Analyzer (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

IMPACTS = ("immune_escape", "increased_transmissibility", "drug_resistance", "diagnostic_escape", "neutral")

@dataclass
class MutationEvidence:
    mutation_id: str
    virus_id: str
    gene: str
    aa_change: str
    impacts: List[str]
    evidence_level: str # e.g., "strong", "moderate"

    def __post_init__(self) -> None:
        if not self.mutation_id or not self.virus_id:
            raise ValueError("IDs required")
        for impact in self.impacts:
            if impact not in IMPACTS:
                raise ValueError(f"invalid impact: {impact}")

class MutationAnalyzer:
    def __init__(self) -> None:
        self._mutations: Dict[str, MutationEvidence] = {}

    def add(self, mutation: MutationEvidence) -> None:
        if mutation.mutation_id in self._mutations:
            raise ValueError(f"duplicate mutation_id: {mutation.mutation_id}")
        self._mutations[mutation.mutation_id] = mutation

    def by_impact(self, virus_id: str, impact: str) -> List[MutationEvidence]:
        if impact not in IMPACTS:
            raise ValueError("invalid impact")
        return [m for m in self._mutations.values() if m.virus_id == virus_id and impact in m.impacts]

    def strong_evidence_escape(self, virus_id: str) -> List[MutationEvidence]:
        return [m for m in self.by_impact(virus_id, "immune_escape") if m.evidence_level == "strong"]

def self_test() -> bool:
    analyzer = MutationAnalyzer()
    analyzer.add(MutationEvidence("M1", "VS_sars2", "S", "E484K", ["immune_escape"], "strong"))
    analyzer.add(MutationEvidence("M2", "VS_sars2", "S", "N501Y", ["increased_transmissibility"], "strong"))
    analyzer.add(MutationEvidence("M3", "VS_sars2", "S", "L452R", ["immune_escape", "increased_transmissibility"], "moderate"))
    
    assert len(analyzer.by_impact("VS_sars2", "immune_escape")) == 2
    assert len(analyzer.strong_evidence_escape("VS_sars2")) == 1
    assert analyzer.strong_evidence_escape("VS_sars2")[0].aa_change == "E484K"
    print("viral_mutation_evidence_analyzer: OK")
    return True

if __name__ == "__main__":
    self_test()
