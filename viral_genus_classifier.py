"""DESI Infinity System - Viral Genus Classifier (v6.2.0).

Deterministic classifier: given structured genus features (genome type,
envelope, host kingdom, family), matches against curated genus profiles.
Returns "unknown" if no match. This is a research classifier, NOT a
taxonomic authority.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

GENOME_TYPES = ("dsDNA", "ssDNA", "dsRNA", "positive_ssRNA",
                "negative_ssRNA", "reverse_transcribing", "unknown")
ENVELOPE = ("enveloped", "non_enveloped", "unknown")
HOST_KINGDOMS = ("animalia", "plantae", "fungi", "bacteria", "archaea",
                 "protista", "unknown")


class GenusClassifierError(Exception):
    """Base genus classifier error."""


@dataclass
class GenusProfile:
    genus_id: str
    name: str
    family_id: str
    genome_type: str
    envelope: str
    host_kingdoms: List[str] = field(default_factory=list)
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.genus_id or not isinstance(self.genus_id, str):
            raise GenusClassifierError("genus_id required")
        if self.genome_type not in GENOME_TYPES:
            raise GenusClassifierError(f"invalid genome_type: {self.genome_type!r}")
        if self.envelope not in ENVELOPE:
            raise GenusClassifierError(f"invalid envelope: {self.envelope!r}")
        for k in self.host_kingdoms:
            if k not in HOST_KINGDOMS:
                raise GenusClassifierError(f"invalid host_kingdom: {k!r}")


@dataclass
class ClassificationInput:
    genome_type: str
    envelope: str
    host_kingdom: str
    family_id: str = ""

    def __post_init__(self) -> None:
        if self.genome_type not in GENOME_TYPES:
            raise GenusClassifierError(f"invalid genome_type: {self.genome_type!r}")
        if self.envelope not in ENVELOPE:
            raise GenusClassifierError(f"invalid envelope: {self.envelope!r}")
        if self.host_kingdom not in HOST_KINGDOMS:
            raise GenusClassifierError(
                f"invalid host_kingdom: {self.host_kingdom!r}")


class ViralGenusClassifier:
    """Rule-based classifier over curated genus profiles."""

    def __init__(self) -> None:
        self._profiles: Dict[str, GenusProfile] = {}

    def add(self, profile: GenusProfile) -> GenusProfile:
        if profile.genus_id in self._profiles:
            raise GenusClassifierError(
                f"duplicate genus_id: {profile.genus_id}")
        self._profiles[profile.genus_id] = profile
        return profile

    def get(self, genus_id: str) -> GenusProfile:
        try:
            return self._profiles[genus_id]
        except KeyError as exc:
            raise GenusClassifierError(f"unknown genus_id: {genus_id}") from exc

    def classify(self, inp: ClassificationInput) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for p in self._profiles.values():
            score = 0
            if p.genome_type == inp.genome_type:
                score += 2
            if p.envelope == inp.envelope:
                score += 1
            if inp.host_kingdom in p.host_kingdoms:
                score += 1
            if inp.family_id and p.family_id == inp.family_id:
                score += 2
            if score > 0:
                results.append({"genus_id": p.genus_id, "name": p.name,
                                "score": score, "family_id": p.family_id})
        results.sort(key=lambda r: r["score"], reverse=True)  # type: ignore
        return results

    def best_match(self, inp: ClassificationInput) -> str:
        ranked = self.classify(inp)
        if not ranked:
            return "unknown"
        return ranked[0]["genus_id"]  # type: ignore[return-value]

    def stats(self) -> Dict[str, int]:
        return {"version": VERSION, "profiles": len(self._profiles)}


def self_test() -> bool:
    clf = ViralGenusClassifier()
    clf.add(GenusProfile(
        "Alphainfluenzavirus", "Alphainfluenzavirus", "VF_ortho",
        "negative_ssRNA", "enveloped", ["animalia"]))
    clf.add(GenusProfile(
        "Betacoronavirus", "Betacoronavirus", "VF_corona",
        "positive_ssRNA", "enveloped", ["animalia"]))
    clf.add(GenusProfile(
        "Parvovirus", "Parvovirus", "VF_parvo",
        "ssDNA", "non_enveloped", ["animalia"]))

    inp = ClassificationInput(
        "negative_ssRNA", "enveloped", "animalia", "VF_ortho")
    assert clf.best_match(inp) == "Alphainfluenzavirus"

    inp2 = ClassificationInput("positive_ssRNA", "enveloped", "animalia")
    assert clf.best_match(inp2) == "Betacoronavirus"

    inp3 = ClassificationInput("dsDNA", "non_enveloped", "bacteria")
    assert clf.best_match(inp3) == "unknown"

    ranked = clf.classify(inp)
    assert ranked[0]["score"] >= 4
    assert clf.stats()["profiles"] == 3
    print("viral_genus_classifier: OK")
    return True


if __name__ == "__main__":
    self_test()
