"""DESI Infinity System - Disease Ontology Engine (v6.2.0).

Represents ontology terms (disease, symptom, phenotype, anatomy) with
parent-child relationships and synonym resolution. Supports ontology
traversal, ancestor/descendant queries, and term resolution across
vocabularies (MONDO, HPO, DOID, SNOMED-style IDs as opaque strings).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

ONTOLOGY_SCOPES = ("disease", "symptom", "phenotype", "anatomy", "pathogen")


class OntologyError(Exception):
    """Base ontology error."""


class OntologyValidationError(OntologyError):
    """Raised when an ontology term is invalid."""


@dataclass
class OntologyTerm:
    term_id: str
    label: str
    scope: str
    definition: str = ""
    synonyms: List[str] = field(default_factory=list)
    parent_ids: List[str] = field(default_factory=list)
    xrefs: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not self.term_id or not isinstance(self.term_id, str):
            raise OntologyValidationError("term_id must be a non-empty string")
        if not self.label or not isinstance(self.label, str):
            raise OntologyValidationError("label must be a non-empty string")
        if self.scope not in ONTOLOGY_SCOPES:
            raise OntologyValidationError(f"invalid scope: {self.scope!r}")

    def to_dict(self) -> Dict[str, object]:
        return {
            "term_id": self.term_id,
            "label": self.label,
            "scope": self.scope,
            "definition": self.definition,
            "synonyms": list(self.synonyms),
            "parent_ids": list(self.parent_ids),
            "xrefs": list(self.xrefs),
        }


class DiseaseOntologyEngine:
    """In-memory ontology with parent/child traversal."""

    def __init__(self) -> None:
        self._terms: Dict[str, OntologyTerm] = {}
        self._children: Dict[str, Set[str]] = {}

    def add_term(self, term: OntologyTerm) -> OntologyTerm:
        if term.term_id in self._terms:
            raise OntologyValidationError(f"duplicate term_id: {term.term_id}")
        self._terms[term.term_id] = term
        for parent_id in term.parent_ids:
            self._children.setdefault(parent_id, set()).add(term.term_id)
        return term

    def get(self, term_id: str) -> OntologyTerm:
        try:
            return self._terms[term_id]
        except KeyError as exc:
            raise OntologyValidationError(f"unknown term_id: {term_id}") from exc

    def children(self, term_id: str) -> List[OntologyTerm]:
        self.get(term_id)
        return [self._terms[c] for c in sorted(self._children.get(term_id, set()))]

    def ancestors(self, term_id: str, max_depth: int = 32) -> List[OntologyTerm]:
        seen: Set[str] = set()
        frontier = [term_id]
        out: List[OntologyTerm] = []
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: List[str] = []
            for tid in frontier:
                term = self.get(tid)
                for pid in term.parent_ids:
                    if pid not in seen and pid in self._terms:
                        seen.add(pid)
                        out.append(self._terms[pid])
                        next_frontier.append(pid)
            frontier = next_frontier
            depth += 1
        return out

    def descendants(self, term_id: str, max_depth: int = 32) -> List[OntologyTerm]:
        self.get(term_id)
        seen: Set[str] = set()
        frontier = list(self._children.get(term_id, set()))
        out: List[OntologyTerm] = []
        depth = 0
        while frontier and depth < max_depth:
            next_frontier: List[str] = []
            for cid in frontier:
                if cid in seen or cid not in self._terms:
                    continue
                seen.add(cid)
                out.append(self._terms[cid])
                next_frontier.extend(self._children.get(cid, set()))
            frontier = next_frontier
            depth += 1
        return out

    def resolve_synonym(self, synonym: str) -> List[OntologyTerm]:
        if not synonym:
            return []
        target = synonym.lower()
        return [t for t in self._terms.values()
                if target in (s.lower() for s in t.synonyms)]

    def by_scope(self, scope: str) -> List[OntologyTerm]:
        if scope not in ONTOLOGY_SCOPES:
            raise OntologyValidationError(f"invalid scope: {scope!r}")
        return [t for t in self._terms.values() if t.scope == scope]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "terms": len(self._terms),
            "diseases": len(self.by_scope("disease")),
            "phenotypes": len(self.by_scope("phenotype")),
        }


def self_test() -> bool:
    engine = DiseaseOntologyEngine()
    engine.add_term(OntologyTerm(term_id="MONDO:0000001", label="disease", scope="disease"))
    engine.add_term(OntologyTerm(term_id="MONDO:0005148", label="type 2 diabetes",
                                 scope="disease", parent_ids=["MONDO:0000001"],
                                 synonyms=["T2DM"]))
    engine.add_term(OntologyTerm(term_id="MONDO:0005015", label="diabetes mellitus",
                                 scope="disease", parent_ids=["MONDO:0000001"]))
    assert len(engine.children("MONDO:0000001")) == 2
    assert engine.ancestors("MONDO:0005148")[0].term_id == "MONDO:0000001"
    assert engine.resolve_synonym("T2DM")[0].term_id == "MONDO:0005148"
    assert engine.stats()["terms"] == 3
    print("007 disease_ontology_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
