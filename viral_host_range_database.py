"""DESI Infinity System - Viral Host Range Database (v6.2.0).

Structured host-range records: virus -> host species, evidence type
(natural / experimental / predicted), and reservoir status.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

EVIDENCE_TYPES = ("natural_infection", "experimental_infection",
                  "in_vitro", "predicted_receptor", "serology", "unknown")
RESERVOIR = ("primary_reservoir", "secondary_reservoir",
             "incidental_host", "dead_end_host", "unknown")
SOURCES = ("curated", "literature", "predicted")


class HostRangeError(Exception):
    """Base host range error."""


@dataclass
class HostRangeRecord:
    record_id: str
    virus_id: str
    host_species: str
    host_kingdom: str = "animalia"
    evidence_type: str = "unknown"
    reservoir_status: str = "unknown"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.record_id or not isinstance(self.record_id, str):
            raise HostRangeError("record_id required")
        if not self.virus_id or not isinstance(self.virus_id, str):
            raise HostRangeError("virus_id required")
        if not self.host_species or not isinstance(self.host_species, str):
            raise HostRangeError("host_species required")
        if self.evidence_type not in EVIDENCE_TYPES:
            raise HostRangeError(f"invalid evidence_type: {self.evidence_type!r}")
        if self.reservoir_status not in RESERVOIR:
            raise HostRangeError(
                f"invalid reservoir_status: {self.reservoir_status!r}")
        if self.source not in SOURCES:
            raise HostRangeError(f"invalid source: {self.source!r}")


class ViralHostRangeDatabase:
    """Host-range registry with virus/host/evidence queries."""

    def __init__(self) -> None:
        self._records: Dict[str, HostRangeRecord] = {}
        self._virus_index: Dict[str, List[str]] = {}
        self._host_index: Dict[str, List[str]] = {}

    def add(self, record: HostRangeRecord) -> HostRangeRecord:
        if record.record_id in self._records:
            raise HostRangeError(f"duplicate record_id: {record.record_id}")
        self._records[record.record_id] = record
        self._virus_index.setdefault(record.virus_id, []).append(record.record_id)
        self._host_index.setdefault(record.host_species, []).append(record.record_id)
        return record

    def get(self, record_id: str) -> HostRangeRecord:
        try:
            return self._records[record_id]
        except KeyError as exc:
            raise HostRangeError(f"unknown record_id: {record_id}") from exc

    def for_virus(self, virus_id: str) -> List[HostRangeRecord]:
        return [self.get(r) for r in self._virus_index.get(virus_id, [])]

    def for_host(self, host_species: str) -> List[HostRangeRecord]:
        return [self.get(r) for r in self._host_index.get(host_species, [])]

    def reservoir_hosts(self, virus_id: str) -> List[str]:
        return sorted({r.host_species for r in self.for_virus(virus_id)
                       if r.reservoir_status == "primary_reservoir"})

    def natural_hosts(self, virus_id: str) -> List[str]:
        return sorted({r.host_species for r in self.for_virus(virus_id)
                       if r.evidence_type == "natural_infection"})

    def by_evidence(self, evidence_type: str) -> List[HostRangeRecord]:
        if evidence_type not in EVIDENCE_TYPES:
            raise HostRangeError(f"invalid evidence_type: {evidence_type!r}")
        return [r for r in self._records.values()
                if r.evidence_type == evidence_type]

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "records": len(self._records),
            "viruses": len(self._virus_index),
            "hosts": len(self._host_index),
        }


def self_test() -> bool:
    db = ViralHostRangeDatabase()
    db.add(HostRangeRecord(
        "HR1", "VS_sars2", "Homo sapiens", evidence_type="natural_infection",
        reservoir_status="dead_end_host"))
    db.add(HostRangeRecord(
        "HR2", "VS_sars2", "Rhinolophus affinis",
        evidence_type="natural_infection",
        reservoir_status="primary_reservoir"))
    db.add(HostRangeRecord(
        "HR3", "VS_sars2", "Mustela putorius furo",
        evidence_type="experimental_infection",
        reservoir_status="incidental_host"))
    db.add(HostRangeRecord(
        "HR4", "VS_flu_a", "Gallus gallus", evidence_type="natural_infection",
        reservoir_status="primary_reservoir"))
    assert len(db.for_virus("VS_sars2")) == 3
    assert len(db.for_host("Homo sapiens")) == 1
    assert db.reservoir_hosts("VS_sars2") == ["Rhinolophus affinis"]
    assert "Homo sapiens" in db.natural_hosts("VS_sars2")
    assert len(db.by_evidence("experimental_infection")) == 1
    print("viral_host_range_database: OK")
    return True


if __name__ == "__main__":
    self_test()
