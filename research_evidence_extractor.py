"""DESI Infinity System - Research Evidence Extractor (v6.2.0).

Structured extraction of research evidence claims from publications:
subject, predicate, object, direction, and confidence. AI-extracted
claims are marked `extraction_method` and are never presented as
established facts.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

CLAIM_DIRECTIONS = ("increases", "decreases", "associates_with",
                    "no_association", "causes", "treats", "unknown")
EXTRACTION_METHODS = ("manual_curation", "ai_llm", "rule_based", "unknown")
SOURCES = ("curated", "literature", "predicted")


class EvidenceExtractionError(Exception):
    """Base evidence extraction error."""


@dataclass
class ExtractedClaim:
    claim_id: str
    publication_id: str
    subject: str
    predicate: str
    obj: str
    direction: str = "unknown"
    confidence: float = 0.5
    extraction_method: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.claim_id or not isinstance(self.claim_id, str):
            raise EvidenceExtractionError("claim_id required")
        if not self.publication_id or not isinstance(self.publication_id, str):
            raise EvidenceExtractionError("publication_id required")
        if not self.subject or not isinstance(self.subject, str):
            raise EvidenceExtractionError("subject required")
        if not self.predicate or not isinstance(self.predicate, str):
            raise EvidenceExtractionError("predicate required")
        if not self.obj or not isinstance(self.obj, str):
            raise EvidenceExtractionError("obj required")
        if self.direction not in CLAIM_DIRECTIONS:
            raise EvidenceExtractionError(f"invalid direction: {self.direction!r}")
        if self.extraction_method not in EXTRACTION_METHODS:
            raise EvidenceExtractionError(
                f"invalid extraction_method: {self.extraction_method!r}")
        if self.source not in SOURCES:
            raise EvidenceExtractionError(f"invalid source: {self.source!r}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise EvidenceExtractionError("confidence must be in [0, 1]")

    def is_ai_generated(self) -> bool:
        return self.extraction_method == "ai_llm"


class ResearchEvidenceExtractor:
    """Claim registry with publication / subject / method queries."""

    def __init__(self) -> None:
        self._claims: Dict[str, ExtractedClaim] = {}
        self._pub_index: Dict[str, List[str]] = {}
        self._subject_index: Dict[str, List[str]] = {}

    def add(self, claim: ExtractedClaim) -> ExtractedClaim:
        if claim.claim_id in self._claims:
            raise EvidenceExtractionError(f"duplicate claim_id: {claim.claim_id}")
        self._claims[claim.claim_id] = claim
        self._pub_index.setdefault(claim.publication_id, []).append(claim.claim_id)
        self._subject_index.setdefault(claim.subject.lower(), []).append(claim.claim_id)
        return claim

    def get(self, claim_id: str) -> ExtractedClaim:
        try:
            return self._claims[claim_id]
        except KeyError as exc:
            raise EvidenceExtractionError(f"unknown claim_id: {claim_id}") from exc

    def for_publication(self, publication_id: str) -> List[ExtractedClaim]:
        return [self.get(c) for c in self._pub_index.get(publication_id, [])]

    def for_subject(self, subject: str) -> List[ExtractedClaim]:
        return [self.get(c) for c in self._subject_index.get(subject.lower(), [])]

    def by_direction(self, direction: str) -> List[ExtractedClaim]:
        if direction not in CLAIM_DIRECTIONS:
            raise EvidenceExtractionError(f"invalid direction: {direction!r}")
        return [c for c in self._claims.values() if c.direction == direction]

    def high_confidence(self, threshold: float = 0.7) -> List[ExtractedClaim]:
        return [c for c in self._claims.values() if c.confidence >= threshold]

    def ai_claims(self) -> List[ExtractedClaim]:
        return [c for c in self._claims.values() if c.is_ai_generated()]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "claims": len(self._claims),
            "publications": len(self._pub_index),
            "ai_generated": len(self.ai_claims()),
        }


def self_test() -> bool:
    extractor = ResearchEvidenceExtractor()
    extractor.add(ExtractedClaim(
        "C1", "PUB1", "TP53 mutation", "increases_risk_of", "breast cancer",
        direction="increases", confidence=0.9,
        extraction_method="manual_curation"))
    extractor.add(ExtractedClaim(
        "C2", "PUB1", "BRCA1 mutation", "increases_risk_of", "ovarian cancer",
        direction="increases", confidence=0.85,
        extraction_method="manual_curation"))
    extractor.add(ExtractedClaim(
        "C3", "PUB2", "EGFR inhibitor", "treats", "lung adenocarcinoma",
        direction="treats", confidence=0.6,
        extraction_method="ai_llm", source="predicted"))
    assert len(extractor.for_publication("PUB1")) == 2
    assert len(extractor.for_subject("TP53 mutation")) == 1
    assert len(extractor.by_direction("increases")) == 2
    assert len(extractor.high_confidence(0.85)) == 2
    assert len(extractor.ai_claims()) == 1
    print("research_evidence_extractor: OK")
    return True


if __name__ == "__main__":
    self_test()
