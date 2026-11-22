"""DESI Infinity System - Disease Knowledge Graph (v6.2.0).

Unified knowledge graph integrating diseases, genes, proteins, pathways,
biomarkers, and treatments via typed relations. Enables consistent
cross-entity traversal used by the orchestrator.
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ENTITY_TYPES = ("disease", "gene", "protein", "pathway", "biomarker",
                "treatment", "publication", "pathogen", "other")
RELATION_TYPES = ("associated_with", "causes", "regulates", "encodes",
                  "part_of", "biomarker_for", "treats", "interacts_with",
                  "related_to")
SOURCES = ("curated", "literature", "predicted")


class KnowledgeGraphError(Exception):
    """Base knowledge graph error."""


@dataclass
class Entity:
    entity_id: str
    entity_type: str
    label: str = ""
    properties: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.entity_id or not isinstance(self.entity_id, str):
            raise KnowledgeGraphError("entity_id required")
        if self.entity_type not in ENTITY_TYPES:
            raise KnowledgeGraphError(f"invalid entity_type: {self.entity_type!r}")


@dataclass
class Relation:
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    evidence_level: str = "unknown"
    source: str = "curated"
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.relation_id or not isinstance(self.relation_id, str):
            raise KnowledgeGraphError("relation_id required")
        if self.source_id == self.target_id:
            raise KnowledgeGraphError("self-relations not allowed")
        if self.relation_type not in RELATION_TYPES:
            raise KnowledgeGraphError(
                f"invalid relation_type: {self.relation_type!r}")
        if self.source not in SOURCES:
            raise KnowledgeGraphError(f"invalid source: {self.source!r}")


class DiseaseKnowledgeGraph:
    """Typed knowledge graph with entity/relation traversal."""

    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}
        self._relations: Dict[str, Relation] = {}
        self._outgoing: Dict[str, Set[str]] = {}
        self._incoming: Dict[str, Set[str]] = {}

    def add_entity(self, entity: Entity) -> Entity:
        if entity.entity_id in self._entities:
            raise KnowledgeGraphError(f"duplicate entity_id: {entity.entity_id}")
        self._entities[entity.entity_id] = entity
        return entity

    def add_relation(self, relation: Relation) -> Relation:
        for eid in (relation.source_id, relation.target_id):
            if eid not in self._entities:
                raise KnowledgeGraphError(f"unknown entity_id: {eid}")
        if relation.relation_id in self._relations:
            raise KnowledgeGraphError(
                f"duplicate relation_id: {relation.relation_id}")
        self._relations[relation.relation_id] = relation
        self._outgoing.setdefault(relation.source_id, set()).add(relation.relation_id)
        self._incoming.setdefault(relation.target_id, set()).add(relation.relation_id)
        return relation

    def get_entity(self, entity_id: str) -> Entity:
        try:
            return self._entities[entity_id]
        except KeyError as exc:
            raise KnowledgeGraphError(f"unknown entity_id: {entity_id}") from exc

    def outgoing(self, entity_id: str, relation_type: Optional[str] = None
                 ) -> List[Relation]:
        self.get_entity(entity_id)
        rels = [self._relations[r] for r in self._outgoing.get(entity_id, set())]
        if relation_type is not None:
            if relation_type not in RELATION_TYPES:
                raise KnowledgeGraphError(
                    f"invalid relation_type: {relation_type!r}")
            rels = [r for r in rels if r.relation_type == relation_type]
        return rels

    def incoming(self, entity_id: str, relation_type: Optional[str] = None
                 ) -> List[Relation]:
        self.get_entity(entity_id)
        rels = [self._relations[r] for r in self._incoming.get(entity_id, set())]
        if relation_type is not None:
            if relation_type not in RELATION_TYPES:
                raise KnowledgeGraphError(
                    f"invalid relation_type: {relation_type!r}")
            rels = [r for r in rels if r.relation_type == relation_type]
        return rels

    def neighbours(self, entity_id: str) -> List[str]:
        out_ids = {r.target_id for r in self.outgoing(entity_id)}
        in_ids = {r.source_id for r in self.incoming(entity_id)}
        return sorted(out_ids | in_ids)

    def expand(self, entity_id: str, max_depth: int = 2) -> Set[str]:
        self.get_entity(entity_id)
        seen: Set[str] = {entity_id}
        frontier = deque([(entity_id, 0)])
        while frontier:
            current, depth = frontier.popleft()
            if depth >= max_depth:
                continue
            for nbr in self.neighbours(current):
                if nbr not in seen:
                    seen.add(nbr)
                    frontier.append((nbr, depth + 1))
        return seen

    def of_type(self, entity_type: str) -> List[Entity]:
        if entity_type not in ENTITY_TYPES:
            raise KnowledgeGraphError(f"invalid entity_type: {entity_type!r}")
        return [e for e in self._entities.values() if e.entity_type == entity_type]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "entities": len(self._entities),
            "relations": len(self._relations),
            "diseases": len(self.of_type("disease")),
        }


def self_test() -> bool:
    kg = DiseaseKnowledgeGraph()
    kg.add_entity(Entity("D_t2d", "disease", "Type 2 diabetes"))
    kg.add_entity(Entity("G_TCF7L2", "gene", "TCF7L2"))
    kg.add_entity(Entity("P_INS", "protein", "Insulin"))
    kg.add_entity(Entity("PW_INS_SIG", "pathway", "Insulin signaling"))
    kg.add_entity(Entity("B_HBA1C", "biomarker", "HbA1c"))
    kg.add_relation(Relation("R1", "G_TCF7L2", "D_t2d", "associated_with",
                             "strong"))
    kg.add_relation(Relation("R2", "PW_INS_SIG", "D_t2d", "associated_with",
                             "strong"))
    kg.add_relation(Relation("R3", "P_INS", "PW_INS_SIG", "part_of"))
    kg.add_relation(Relation("R4", "B_HBA1C", "D_t2d", "biomarker_for"))
    assert len(kg.outgoing("G_TCF7L2")) == 1
    assert "D_t2d" in [r.target_id for r in kg.outgoing("G_TCF7L2")]
    nbrs = kg.neighbours("D_t2d")
    assert set(nbrs) == {"G_TCF7L2", "PW_INS_SIG", "B_HBA1C"}
    expanded = kg.expand("D_t2d", max_depth=2)
    assert "P_INS" in expanded
    assert len(kg.of_type("disease")) == 1
    print("disease_knowledge_graph: OK")
    return True


if __name__ == "__main__":
    self_test()
