"""DESI Infinity System - Viral Host Association Engine (v6.2.0).

Models virus-host associations at the molecular interface: which host
receptors/co-receptors are used, which host tissues express them, and
which host restriction factors block entry. Research data only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

INTERACTION_TYPES = ("receptor_binding", "co_receptor_binding",
                     "entry_factor", "restriction_factor",
                     "post_entry_factor", "other")
EVIDENCE_CLASSES = ("experimental", "structural", "computational",
                    "predicted", "unknown")
SOURCES = ("curated", "literature", "predicted")


class HostAssociationError(Exception):
    """Base host association error."""


@dataclass
class HostAssociation:
    association_id: str
    virus_id: str
    host_factor: str
    interaction_type: str
    evidence_class: str = "unknown"
    host_tissues: List[str] = field(default_factory=list)
    host_species: str = "Homo sapiens"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.association_id or not isinstance(self.association_id, str):
            raise HostAssociationError("association_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise HostAssociationError("virus_id required")
        if not self.host_factor or not isinstance(self.host_factor, str):
            raise HostAssociationError("host_factor required")
        if self.interaction_type not in INTERACTION_TYPES:
            raise HostAssociationError(
                f"invalid interaction_type: {self.interaction_type!r}")
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise HostAssociationError(
                f"invalid evidence_class: {self.evidence_class!r}")
        if self.source not in SOURCES:
            raise HostAssociationError(f"invalid source: {self.source!r}")


class ViralHostAssociationEngine:
    """Association store with virus/host-factor/type queries."""

    def __init__(self) -> None:
        self._associations: Dict[str, HostAssociation] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._factor_index: Dict[str, List[str]] = {}

    def add(self, assoc: HostAssociation) -> HostAssociation:
        if assoc.association_id in self._associations:
            raise HostAssociationError(
                f"duplicate association_id: {assoc.association_id}")
        self._associations[assoc.association_id] = assoc
        self._virus_index.setdefault(assoc.virus_id, []).append(assoc.association_id)
        self._factor_index.setdefault(assoc.host_factor, []).append(
            assoc.association_id)
        return assoc

    def get(self, association_id: str) -> HostAssociation:
        try:
            return self._associations[association_id]
        except KeyError as exc:
            raise HostAssociationError(
                f"unknown association_id: {association_id}") from exc

    def for_virus(self, virus_id: str) -> List[HostAssociation]:
        return [self.get(a) for a in self._virus_index.get(virus_id, [])]

    def for_host_factor(self, host_factor: str) -> List[HostAssociation]:
        return [self.get(a) for a in self._factor_index.get(host_factor, [])]

    def by_interaction_type(self, interaction_type: str) -> List[HostAssociation]:
        if interaction_type not in INTERACTION_TYPES:
            raise HostAssociationError(
                f"invalid interaction_type: {interaction_type!r}")
        return [a for a in self._associations.values()
                if a.interaction_type == interaction_type]

    def receptors_for(self, virus_id: str) -> List[str]:
        return sorted({a.host_factor for a in self.for_virus(virus_id)
                       if a.interaction_type in ("receptor_binding",
                                                 "co_receptor_binding")})

    def restriction_factors_for(self, virus_id: str) -> List[str]:
        return sorted({a.host_factor for a in self.for_virus(virus_id)
                       if a.interaction_type == "restriction_factor"})

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "associations": len(self._associations),
            "viruses": len(self._virus_index),
            "host_factors": len(self._factor_index),
        }


def self_test() -> bool:
    engine = ViralHostAssociationEngine()
    engine.add(HostAssociation(
        "HA1", "VS_sars2", "ACE2", "receptor_binding",
        "experimental", ["respiratory_epithelium", "intestinal_epithelium"]))
    engine.add(HostAssociation(
        "HA2", "VS_sars2", "TMPRSS2", "entry_factor", "experimental",
        ["respiratory_epithelium"]))
    engine.add(HostAssociation(
        "HA3", "VS_sars2", "IFITM3", "restriction_factor", "experimental"))
    engine.add(HostAssociation(
        "HA4", "VS_hiv1", "CD4", "receptor_binding", "experimental",
        ["cd4_t_cell"]))
    engine.add(HostAssociation(
        "HA5", "VS_hiv1", "CCR5", "co_receptor_binding", "experimental"))
    assert len(engine.for_virus("VS_sars2")) == 3
    assert len(engine.for_host_factor("ACE2")) == 1
    assert len(engine.by_interaction_type("restriction_factor")) == 1
    assert engine.receptors_for("VS_hiv1") == ["CCR5", "CD4"]
    assert engine.restriction_factors_for("VS_sars2") == ["IFITM3"]
    print("viral_host_association_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
