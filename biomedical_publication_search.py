"""DESI Infinity System - Biomedical Publication Search (v6.2.0).

Local index over Publication records with boolean-style query support
(AND / OR / NOT keywords, disease filter, year range). No network calls —
caller supplies data through `index()`.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)


class PublicationSearchError(Exception):
    """Base publication search error."""


@dataclass
class IndexedDocument:
    doc_id: str
    title: str
    abstract: str = ""
    disease_ids: List[str] = field(default_factory=list)
    year: int = 0
    keywords: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.doc_id or not isinstance(self.doc_id, str):
            raise PublicationSearchError("doc_id required")
        if not self.title or not isinstance(self.title, str):
            raise PublicationSearchError("title required")
        if not isinstance(self.year, int) or self.year < 0:
            raise PublicationSearchError("year must be non-negative int")


class BiomedicalPublicationSearch:
    """In-memory index with tokenized full-text search."""

    def __init__(self) -> None:
        self._docs: Dict[str, IndexedDocument] = {}
        self._inverted: Dict[str, Set[str]] = {}

    def _tokenize(self, text: str) -> List[str]:
        return [t.lower() for t in text.replace(",", " ").replace(".", " ").split()
                if t]

    def index(self, doc: IndexedDocument) -> IndexedDocument:
        if doc.doc_id in self._docs:
            raise PublicationSearchError(f"duplicate doc_id: {doc.doc_id}")
        self._docs[doc.doc_id] = doc
        tokens = set(self._tokenize(doc.title + " " + doc.abstract + " "
                                    + " ".join(doc.keywords)))
        for tok in tokens:
            self._inverted.setdefault(tok, set()).add(doc.doc_id)
        return doc

    def _docs_with(self, token: str) -> Set[str]:
        return self._inverted.get(token.lower(), set())

    def search(self, required: List[str] = None, any_of: List[str] = None,
               excluded: List[str] = None, disease_id: Optional[str] = None,
               year_min: Optional[int] = None, year_max: Optional[int] = None
               ) -> List[IndexedDocument]:
        candidate_ids: Optional[Set[str]] = None
        if required:
            for tok in required:
                ids = self._docs_with(tok)
                candidate_ids = ids if candidate_ids is None else (candidate_ids & ids)
        if any_of:
            any_union: Set[str] = set()
            for tok in any_of:
                any_union |= self._docs_with(tok)
            candidate_ids = any_union if candidate_ids is None else (
                candidate_ids & any_union)
        if candidate_ids is None:
            candidate_ids = set(self._docs.keys())
        if excluded:
            for tok in excluded:
                candidate_ids -= self._docs_with(tok)
        results: List[IndexedDocument] = []
        for did in candidate_ids:
            doc = self._docs[did]
            if disease_id and disease_id not in doc.disease_ids:
                continue
            if year_min is not None and doc.year < year_min:
                continue
            if year_max is not None and doc.year > year_max:
                continue
            results.append(doc)
        results.sort(key=lambda d: (-d.year, d.doc_id))
        return results

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "documents": len(self._docs),
            "tokens": len(self._inverted),
        }


def self_test() -> bool:
    search = BiomedicalPublicationSearch()
    search.index(IndexedDocument(
        "D1", "TP53 and BRCA1 in breast cancer", year=2022,
        disease_ids=["D_breast_cancer"], keywords=["TP53", "BRCA1"]))
    search.index(IndexedDocument(
        "D2", "EGFR mutations in lung adenocarcinoma", year=2021,
        disease_ids=["D_lung_cancer"], keywords=["EGFR"]))
    search.index(IndexedDocument(
        "D3", "TP53 in glioblastoma", year=2023,
        disease_ids=["D_glioma"], keywords=["TP53"]))
    hits = search.search(required=["tp53"])
    assert len(hits) == 2
    hits = search.search(required=["tp53"], excluded=["breast"])
    assert len(hits) == 1 and hits[0].doc_id == "D3"
    hits = search.search(any_of=["egfr", "brca1"])
    assert len(hits) == 2
    hits = search.search(disease_id="D_lung_cancer")
    assert len(hits) == 1
    hits = search.search(year_min=2022)
    assert len(hits) == 2
    print("biomedical_publication_search: OK")
    return True


if __name__ == "__main__":
    self_test()
