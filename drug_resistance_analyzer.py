"""DESI Infinity System - Drug Resistance Analyzer (v6.2.0).

Structured store of documented resistance mechanisms at pathogen, tumor,
or disease level. Includes mechanism class, drug classes affected,
frequency annotations. Research record-keeping only.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

RESISTANCE_MECHANISMS = ("target_mutation", "efflux_pump",
                         "enzyme_inactivation", "bypass_pathway",
                         "epigenetic_silencing", "amplification",
                         "drug_inactivation", "reduced_uptake",
                         "immune_escape", "unknown")
ORGANISM_TYPES = ("pathogen", "tumor", "other")
SOURCES = ("curated", "literature", "predicted")


class DrugResistanceError(Exception):
    """Base drug resistance error."""


@dataclass
class ResistanceRecord:
    record_id: str
    entity_id: str
    entity_type: str
    drug_classes: List[str] = field(default_factory=list)
    mechanism: str = "unknown"
    gene_symbols: List[str] = field(default_factory=list)
    frequency: float = 0.0
    evidence_class: str = "curated"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not isinstance(self.record_id, str):
            raise DrugResistanceError("record_id required")
        if not self.entity_id or not isinstance(self.entity_id, str):
            raise DrugResistanceError("entity_id required")
        if self.entity_type not in ORGANISM_TYPES:
            raise DrugResistanceError(f"invalid entity_type: {self.entity_type!r}")
        if self.mechanism not in RESISTANCE_MECHANISMS:
            raise DrugResistanceError(f"invalid mechanism: {self.mechanism!r}")
        if self.source not in SOURCES:
            raise DrugResistanceError(f"invalid source: {self.source!r}")
        if not 0.0 <= float(self.frequency) <= 1.0:
            raise DrugResistanceError("frequency must be in [0, 1]")


class DrugResistanceAnalyzer:
    """Record store with mechanism / entity / drug-class queries."""

    def __init__(self) -> None:
        self._records: Dict[str, ResistanceRecord] = {}
        self._entity_index: Dict[str, List[str]] = {}
        self._mechanism_index: Dict[str, List[str]] = {}

    def add(self, record: ResistanceRecord) -> ResistanceRecord:
        if record.record_id in self._records:
            raise DrugResistanceError(f"duplicate record_id: {record.record_id}")
        self._records[record.record_id] = record
        self._entity_index.setdefault(record.entity_id, []).append(record.record_id)
        self._mechanism_index.setdefault(record.mechanism, []).append(record.record_id)
        return record

    def get(self, record_id: str) -> ResistanceRecord:
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise DrugResistanceError(f"unknown record_id: {record_id}") from exc

    def for_entity(self, entity_id: str) -> List[ResistanceRecord]:
        return [self.get(r) for r in self._entity_index.get(entity_id, [])]

    def by_mechanism(self, mechanism: str) -> List[ResistanceRecord]:
        if mechanism not in RESISTANCE_MECHANISMS:
            raise DrugResistanceError(f"invalid mechanism: {mechanism!r}")
        return [self.get(r) for r in self._mechanism_index.get(mechanism, [])]

    def for_drug_class(self, drug_class: str) -> List[ResistanceRecord]:
        return [r for r in self._records.values() if drug_class in r.drug_classes]

    def high_frequency(self, threshold: float = 0.5) -> List[ResistanceRecord]:
        return [r for r in self._records.values() if r.frequency >= threshold]

    def entity_mechanisms(self, entity_id: str) -> List[str]:
        return sorted({r.mechanism for r in self.for_entity(entity_id)})

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "entities": len(self._entity_index),
            "mechanisms": len(self._mechanism_index),
        }


def self_test() -> bool:
    analyzer = DrugResistanceAnalyzer()
    analyzer.add(ResistanceRecord(
        "RR1", "Mtb_H37Rv", "pathogen",
        drug_classes=["rifamycin"], mechanism="target_mutation",
        gene_symbols=["rpoB"], frequency=0.6))
    analyzer.add(ResistanceRecord(
        "RR2", "Mtb_H37Rv", "pathogen",
        drug_classes=["isoniazid"], mechanism="enzyme_inactivation",
        gene_symbols=["katG"], frequency=0.4))
    analyzer.add(ResistanceRecord(
        "RR3", "CML_K562", "tumor",
        drug_classes=["BCR-ABL_inhibitor"], mechanism="target_mutation",
        gene_symbols=["ABL1"], frequency=0.3))
    assert len(analyzer.for_entity("Mtb_H37Rv")) == 2
    assert len(analyzer.by_mechanism("target_mutation")) == 2
    assert len(analyzer.for_drug_class("rifamycin")) == 1
    assert len(analyzer.high_frequency(0.5)) == 1
    assert analyzer.entity_mechanisms("Mtb_H37Rv") == [
        "enzyme_inactivation", "target_mutation"]
    print("drug_resistance_analyzer: OK")
    return True


if __name__ == "__main__":
    self_test()
