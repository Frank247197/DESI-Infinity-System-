"""DESI Infinity System - Cancer Pathway Analyzer (v6.2.0).

Analyzes pathway-level dysregulation in cancer using structured alteration
evidence and pathway dependency scoring. Research only — no therapeutic
recommendation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

HALLMARK_PATHWAYS = ("RTK_RAS", "PI3K_AKT_MTOR", "p53", "cell_cycle",
                     "WNT", "NOTCH", "Hedgehog", "TGF_beta",
                     "DNA_damage_repair", "apoptosis", "other")
ALTERATION_TYPES = ("mutation", "amplification", "deletion", "fusion",
                    "methylation", "overexpression", "unknown")
SOURCES = ("curated", "literature", "predicted")


class CancerPathwayError(Exception):
    """Base cancer pathway error."""


@dataclass
class PathwayAlteration:
    cancer_id: str
    pathway_id: str
    alteration_type: str
    gene_symbols: List[str] = field(default_factory=list)
    frequency: float = 0.0
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.cancer_id or not isinstance(self.cancer_id, str):
            raise CancerPathwayError("cancer_id required")
        if not self.pathway_id or not isinstance(self.pathway_id, str):
            raise CancerPathwayError("pathway_id required")
        if self.alteration_type not in ALTERATION_TYPES:
            raise CancerPathwayError(f"invalid alteration_type: {self.alteration_type!r}")
        if self.source not in SOURCES:
            raise CancerPathwayError(f"invalid source: {self.source!r}")
        if not 0.0 <= float(self.frequency) <= 1.0:
            raise CancerPathwayError("frequency must be in [0, 1]")


class CancerPathwayAnalyzer:
    """Pathway alteration aggregation and ranking by cancer."""

    def __init__(self) -> None:
        self._alterations: List[PathwayAlteration] = []
        self._by_cancer: Dict[str, List[int]] = {}
        self._by_pathway: Dict[str, List[int]] = {}

    def add(self, alteration: PathwayAlteration) -> None:
        idx = len(self._alterations)
        self._alterations.append(alteration)
        self._by_cancer.setdefault(alteration.cancer_id, []).append(idx)
        self._by_pathway.setdefault(alteration.pathway_id, []).append(idx)

    def for_cancer(self, cancer_id: str) -> List[PathwayAlteration]:
        return [self._alterations[i] for i in self._by_cancer.get(cancer_id, [])]

    def for_pathway(self, pathway_id: str) -> List[PathwayAlteration]:
        return [self._alterations[i] for i in self._by_pathway.get(pathway_id, [])]

    def rank_pathways(self, cancer_id: str) -> List[Dict[str, object]]:
        agg: Dict[str, float] = {}
        for a in self.for_cancer(cancer_id):
            agg[a.pathway_id] = agg.get(a.pathway_id, 0.0) + a.frequency
        rows = [{"pathway_id": k, "score": round(v, 4)} for k, v in agg.items()]
        rows.sort(key=lambda r: r["score"], reverse=True)  # type: ignore
        return rows

    def shared_pathways(self, cancer_a: str, cancer_b: str) -> List[str]:
        pa = {a.pathway_id for a in self.for_cancer(cancer_a)}
        pb = {a.pathway_id for a in self.for_cancer(cancer_b)}
        return sorted(pa & pb)

    def alteration_types(self, pathway_id: str) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for a in self.for_pathway(pathway_id):
            counts[a.alteration_type] = counts.get(a.alteration_type, 0) + 1
        return counts

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "alterations": len(self._alterations),
            "cancers": len(self._by_cancer),
            "pathways": len(self._by_pathway),
        }


def self_test() -> bool:
    analyzer = CancerPathwayAnalyzer()
    analyzer.add(PathwayAlteration("C_luad", "RTK_RAS", "mutation",
                                   ["EGFR", "KRAS"], 0.6))
    analyzer.add(PathwayAlteration("C_luad", "p53", "mutation",
                                   ["TP53"], 0.5))
    analyzer.add(PathwayAlteration("C_colorectal", "WNT", "mutation",
                                   ["APC"], 0.8))
    analyzer.add(PathwayAlteration("C_colorectal", "p53", "mutation",
                                   ["TP53"], 0.7))
    assert analyzer.rank_pathways("C_luad")[0]["pathway_id"] == "RTK_RAS"
    assert "p53" in analyzer.shared_pathways("C_luad", "C_colorectal")
    assert analyzer.alteration_types("p53")["mutation"] == 2
    assert analyzer.stats()["pathways"] == 3
    print("cancer_pathway_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
