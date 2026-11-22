"""DESI Infinity System - Drug Repurposing Research (v6.2.0).

Research store for repurposing hypotheses linking existing drugs to new
disease indications with structured evidence. All links are labelled as
hypotheses; NO clinical recommendation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

EVIDENCE_TYPES = ("genetic", "transcriptomic", "proteomic", "network",
                  "clinical_observation", "literature", "predicted")
HYPOTHESIS_STATUS = ("proposed", "under_investigation", "supported",
                     "refuted", "unknown")
SOURCES = ("curated", "literature", "predicted")


class RepurposingError(Exception):
    """Base repurposing error."""


@dataclass
class RepurposingHypothesis:
    hypothesis_id: str
    drug_name: str
    original_indication: str
    proposed_indication: str
    evidence_types: List[str] = field(default_factory=list)
    confidence: float = 0.5
    status: str = "proposed"
    rationale: str = ""
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.hypothesis_id or not isinstance(self.hypothesis_id, str):
            raise RepurposingError("hypothesis_id required")
        if not self.drug_name or not isinstance(self.drug_name, str):
            raise RepurposingError("drug_name required")
        if not self.original_indication or not isinstance(self.original_indication, str):
            raise RepurposingError("original_indication required")
        if not self.proposed_indication or not isinstance(self.proposed_indication, str):
            raise RepurposingError("proposed_indication required")
        if self.status not in HYPOTHESIS_STATUS:
            raise RepurposingError(f"invalid status: {self.status!r}")
        if self.source not in SOURCES:
            raise RepurposingError(f"invalid source: {self.source!r}")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise RepurposingError("confidence must be in [0, 1]")
        for et in self.evidence_types:
            if et not in EVIDENCE_TYPES:
                raise RepurposingError(f"invalid evidence_type: {et!r}")

    def is_prediction(self) -> bool:
        return self.source == "predicted" or "predicted" in self.evidence_types


class DrugRepurposingResearch:
    """Hypothesis store with drug / indication / status queries."""

    def __init__(self) -> None:
        self._hypotheses: Dict[str, RepurposingHypothesis] = {}
        self._drug_index: Dict[str, List[str]] = {}
        self._indication_index: Dict[str, List[str]] = {}

    def add(self, hyp: RepurposingHypothesis) -> RepurposingHypothesis:
        if hyp.hypothesis_id in self._hypotheses:
            raise RepurposingError(f"duplicate hypothesis_id: {hyp.hypothesis_id}")
        self._hypotheses[hyp.hypothesis_id] = hyp
        self._drug_index.setdefault(hyp.drug_name, []).append(hyp.hypothesis_id)
        self._indication_index.setdefault(hyp.proposed_indication, []).append(
            hyp.hypothesis_id)
        return hyp

    def get(self, hypothesis_id: str) -> RepurposingHypothesis:
        try:
            return self._hypotheses[hypothesis_id]
        except KeyError as exc:
            raise RepurposingError(
                f"unknown hypothesis_id: {hypothesis_id}") from exc

    def for_drug(self, drug_name: str) -> List[RepurposingHypothesis]:
        return [self.get(h) for h in self._drug_index.get(drug_name, [])]

    def for_indication(self, indication: str) -> List[RepurposingHypothesis]:
        return [self.get(h) for h in self._indication_index.get(indication, [])]

    def by_status(self, status: str) -> List[RepurposingHypothesis]:
        if status not in HYPOTHESIS_STATUS:
            raise RepurposingError(f"invalid status: {status!r}")
        return [h for h in self._hypotheses.values() if h.status == status]

    def supported(self) -> List[RepurposingHypothesis]:
        return self.by_status("supported")

    def high_confidence(self, threshold: float = 0.7) -> List[RepurposingHypothesis]:
        return [h for h in self._hypotheses.values() if h.confidence >= threshold]

    def predictions(self) -> List[RepurposingHypothesis]:
        return [h for h in self._hypotheses.values() if h.is_prediction()]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "hypotheses": len(self._hypotheses),
            "drugs": len(self._drug_index),
            "indications": len(self._indication_index),
            "supported": len(self.supported()),
        }


def self_test() -> bool:
    research = DrugRepurposingResearch()
    research.add(RepurposingHypothesis(
        "H1", "Metformin", "D_t2d", "D_long_covid",
        evidence_types=["transcriptomic", "clinical_observation"],
        confidence=0.55, status="under_investigation"))
    research.add(RepurposingHypothesis(
        "H2", "Rapamycin", "D_transplant_rejection", "D_aging",
        evidence_types=["genetic", "network"],
        confidence=0.4, status="proposed"))
    research.add(RepurposingHypothesis(
        "H3", "Propranolol", "D_hypertension", "D_hemangioma",
        evidence_types=["clinical_observation"],
        confidence=0.85, status="supported"))
    assert len(research.for_drug("Metformin")) == 1
    assert len(research.for_indication("D_hemangioma")) == 1
    assert len(research.by_status("proposed")) == 1
    assert len(research.supported()) == 1
    assert len(research.high_confidence(0.7)) == 1
    assert len(research.predictions()) == 0
    print("drug_repurposing_research: OK")
    return True


if __name__ == "__main__":
    self_test()
