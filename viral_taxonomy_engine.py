"""DESI Infinity System - Viral Taxonomy Engine (v6.2.0).

Structured viral taxonomy store aligned with ICTV-style hierarchy:
realm -> kingdom -> phylum -> class -> order -> family -> genus -> species.
Opaque ID strings; taxonomy rank validation enforced.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

RANKS = ("realm", "kingdom", "phylum", "class", "order",
         "family", "genus", "species", "strain")
SOURCES = ("curated", "literature", "predicted")


class ViralTaxonomyError(Exception):
    """Base viral taxonomy error."""


@dataclass
class TaxonomyNode:
    taxon_id: str
    name: str
    rank: str
    parent_id: Optional[str] = None
    synonyms: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.taxon_id or not isinstance(self.taxon_id, str):
            raise ViralTaxonomyError("taxon_id required")
        if not self.name or not isinstance(self.name, str):
            raise ViralTaxonomyError("name required")
        if self.rank not in RANKS:
            raise ViralTaxonomyError(f"invalid rank: {self.rank!r}")
        if self.source not in SOURCES:
            raise ViralTaxonomyError(f"invalid source: {self.source!r}")

    def rank_index(self) -> int:
        return RANKS.index(self.rank)


class ViralTaxonomyEngine:
    """Taxonomy hierarchy with child/ancestor traversal."""

    def __init__(self) -> None:
        self._nodes: Dict[str, TaxonomyNode] = {}
        self._children: Dict[str, List[str]] = {}

    def add(self, node: TaxonomyNode) -> TaxonomyNode:
        if node.taxon_id in self._nodes:
            raise ViralTaxonomyError(f"duplicate taxon_id: {node.taxon_id}")
        if node.parent_id is not None:
            if node.parent_id not in self._nodes:
                raise ViralTaxonomyError(f"unknown parent_id: {node.parent_id}")
            parent = self._nodes[node.parent_id]
            if parent.rank_index() >= node.rank_index():
                raise ViralTaxonomyError(
                    f"rank {node.rank!r} must be below parent rank {parent.rank!r}")
        self._nodes[node.taxon_id] = node
        if node.parent_id:
            self._children.setdefault(node.parent_id, []).append(node.taxon_id)
        return node

    def get(self, taxon_id: str) -> TaxonomyNode:
        try:
            return self._nodes[taxon_id]
        except KeyError as exc:
            raise ViralTaxonomyError(f"unknown taxon_id: {taxon_id}") from exc

    def children(self, taxon_id: str) -> List[TaxonomyNode]:
        self.get(taxon_id)
        return [self._nodes[c] for c in self._children.get(taxon_id, [])]

    def ancestors(self, taxon_id: str) -> List[TaxonomyNode]:
        self.get(taxon_id)
        out: List[TaxonomyNode] = []
        current = self._nodes[taxon_id].parent_id
        while current is not None:
            node = self._nodes[current]
            out.append(node)
            current = node.parent_id
        return out

    def descendants(self, taxon_id: str) -> List[TaxonomyNode]:
        self.get(taxon_id)
        out: List[TaxonomyNode] = []
        frontier = list(self._children.get(taxon_id, []))
        seen = set()
        while frontier:
            cid = frontier.pop()
            if cid in seen:
                continue
            seen.add(cid)
            out.append(self._nodes[cid])
            frontier.extend(self._children.get(cid, []))
        return out

    def by_rank(self, rank: str) -> List[TaxonomyNode]:
        if rank not in RANKS:
            raise ViralTaxonomyError(f"invalid rank: {rank!r}")
        return [n for n in self._nodes.values() if n.rank == rank]

    def lineage(self, taxon_id: str) -> List[str]:
        return [n.name for n in reversed(self.ancestors(taxon_id))] + [
            self.get(taxon_id).name]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "nodes": len(self._nodes),
            "families": len(self.by_rank("family")),
            "genera": len(self.by_rank("genus")),
            "species": len(self.by_rank("species")),
        }


def self_test() -> bool:
    engine = ViralTaxonomyEngine()
    engine.add(TaxonomyNode("T_realm_ribo", "Riboviria", "realm"))
    engine.add(TaxonomyNode("T_king_ortho", "Orthornavirae", "kingdom",
                            parent_id="T_realm_ribo"))
    engine.add(TaxonomyNode("T_fam_ortho", "Orthomyxoviridae", "family",
                            parent_id="T_king_ortho"))
    engine.add(TaxonomyNode("T_gen_alpha", "Alphainfluenzavirus", "genus",
                            parent_id="T_fam_ortho"))
    engine.add(TaxonomyNode("T_sp_h1n1", "Influenza A virus H1N1", "species",
                            parent_id="T_gen_alpha"))
    assert engine.get("T_sp_h1n1").rank == "species"
    assert len(engine.children("T_fam_ortho")) == 1
    assert engine.ancestors("T_sp_h1n1")[0].name == "Alphainfluenzavirus"
    assert engine.lineage("T_sp_h1n1") == [
        "Riboviria", "Orthornavirae", "Orthomyxoviridae",
        "Alphainfluenzavirus", "Influenza A virus H1N1"]
    assert len(engine.by_rank("family")) == 1
    assert engine.stats()["species"] == 1
    print("viral_taxonomy_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
