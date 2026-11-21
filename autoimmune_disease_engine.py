"""DESI Infinity System - Autoimmune Disease Engine (v6.2.0).

Stores autoimmune diseases with autoantigen targets, HLA associations,
and affected tissues/organs. Research data only; no diagnostic claims.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

MECHANISMS = ("autoantibody_mediated", "t_cell_mediated", "mixed", "unknown")
SOURCES = ("curated", "literature", "predicted")


class AutoimmuneError(Exception):
    """Base autoimmune error."""


@dataclass
class AutoimmuneDisease:
    disease_id: str
    name: str
    mechanism: str = "unknown"
    autoantigens: List[str] = field(default_factory=list)
    hla_associations: List[str] = field(default_factory=list)
    affected_tissues: List[str] = field(default_factory=list)
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.disease_id or not isinstance(self.disease_id, str):
            raise AutoimmuneError("disease_id required")
        if self.mechanism not in MECHANISMS:
            raise AutoimmuneError(f"invalid mechanism: {self.mechanism!r}")
        if self.source not in SOURCES:
            raise AutoimmuneError(f"invalid source: {self.source!r}")

    def to_dict(self) -> Dict[str, object]:
        return {
            "disease_id": self.disease_id, "name": self.name,
            "mechanism": self.mechanism,
            "autoantigens": list(self.autoantigens),
            "hla_associations": list(self.hla_associations),
            "affected_tissues": list(self.affected_tissues),
            "source": self.source,
        }


class AutoimmuneDiseaseEngine:
    """Registry with autoantigen / HLA / tissue queries."""

    def __init__(self) -> None:
        self._diseases: Dict[str, AutoimmuneDisease] = {}
        self._antigen_index: Dict[str, List[str]] = {}
        self._hla_index: Dict[str, List[str]] = {}

    def add(self, disease: AutoimmuneDisease) -> AutoimmuneDisease:
        if disease.disease_id in self._diseases:
            raise AutoimmuneError(f"duplicate disease_id: {disease.disease_id}")
        self._diseases[disease.disease_id] = disease
        for a in disease.autoantigens:
            self._antigen_index.setdefault(a, []).append(disease.disease_id)
        for h in disease.hla_associations:
            self._hla_index.setdefault(h, []).append(disease.disease_id)
        return disease

    def get(self, disease_id: str) -> AutoimmuneDisease:
        try:
            return self._diseases[disease_id]
        except KeyError as exc:
            raise AutoimmuneError(f"unknown disease_id: {disease_id}") from exc

    def by_autoantigen(self, antigen: str) -> List[AutoimmuneDisease]:
        return [self.get(did) for did in self._antigen_index.get(antigen, [])]

    def by_hla(self, hla: str) -> List[AutoimmuneDisease]:
        return [self.get(did) for did in self._hla_index.get(hla, [])]

    def by_mechanism(self, mechanism: str) -> List[AutoimmuneDisease]:
        if mechanism not in MECHANISMS:
            raise AutoimmuneError(f"invalid mechanism: {mechanism!r}")
        return [d for d in self._diseases.values() if d.mechanism == mechanism]

    def shared_antigens(self, disease_a: str, disease_b: str) -> List[str]:
        a = set(self.get(disease_a).autoantigens)
        b = set(self.get(disease_b).autoantigens)
        return sorted(a & b)

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "diseases": len(self._diseases),
            "autoantigens": len(self._antigen_index),
            "hla_alleles": len(self._hla_index),
        }


def self_test() -> bool:
    engine = AutoimmuneDiseaseEngine()
    engine.add(AutoimmuneDisease("D_t1d", "Type 1 diabetes", "t_cell_mediated",
                                 autoantigens=["GAD65", "IA-2"],
                                 hla_associations=["HLA-DR3", "HLA-DR4"],
                                 affected_tissues=["pancreatic_beta_cells"]))
    engine.add(AutoimmuneDisease("D_ra", "Rheumatoid arthritis", "mixed",
                                 autoantigens=["RF", "CCP"],
                                 hla_associations=["HLA-DR4"],
                                 affected_tissues=["synovium"]))
    assert engine.by_autoantigen("GAD65")[0].disease_id == "D_t1d"
    assert len(engine.by_hla("HLA-DR4")) == 2
    assert engine.shared_antigens("D_t1d", "D_ra") == []
    assert engine.stats()["autoantigens"] == 4
    print("020 autoimmune_disease_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
