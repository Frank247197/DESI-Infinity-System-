"""DESI Infinity System - Viral Genome Database (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class GenomeRecord:
    accession: str
    virus_id: str
    sequence: str
    collection_date: Optional[str] = None
    country: str = ""

    def __post_init__(self) -> None:
        if not self.accession or not self.virus_id:
            raise ValueError("accession and virus_id required")
        if not self.sequence:
            raise ValueError("sequence cannot be empty")
        self.sequence = self.sequence.upper().replace("U", "T")

    def gc_content(self) -> float:
        if not self.sequence:
            return 0.0
        gc = self.sequence.count("G") + self.sequence.count("C")
        return round(gc / len(self.sequence), 4)

class ViralGenomeDatabase:
    def __init__(self) -> None:
        self._db: dict[str, GenomeRecord] = {}

    def add(self, record: GenomeRecord) -> None:
        if record.accession in self._db:
            raise ValueError(f"duplicate accession: {record.accession}")
        self._db[record.accession] = record

    def get(self, accession: str) -> GenomeRecord:
        if accession not in self._db:
            raise ValueError(f"unknown accession: {accession}")
        return self._db[accession]

    def search_by_virus(self, virus_id: str) -> list[GenomeRecord]:
        return [r for r in self._db.values() if r.virus_id == virus_id]

    def filter_by_gc(self, min_gc: float, max_gc: float) -> list[GenomeRecord]:
        return [r for r in self._db.values() if min_gc <= r.gc_content() <= max_gc]

    def sequence_length_stats(self, virus_id: str) -> dict[str, float]:
        records = self.search_by_virus(virus_id)
        if not records:
            return {"min": 0, "max": 0, "mean": 0}
        lengths = [len(r.sequence) for r in records]
        return {"min": min(lengths), "max": max(lengths), "mean": sum(lengths) / len(lengths)}

def self_test() -> bool:
    db = ViralGenomeDatabase()
    db.add(GenomeRecord("NC_045512", "VS_sars2", "ATGCGCGCGC", country="CHN"))
    db.add(GenomeRecord("MT020880", "VS_sars2", "ATGCGCGCGCA", country="USA"))
    db.add(GenomeRecord("NC_002200", "VS_flu", "GGGGCCCCAA"))
    
    assert len(db.search_by_virus("VS_sars2")) == 2
    assert db.get("NC_045512").gc_content() == 1.0 # 10 chars, all G/C
    assert len(db.filter_by_gc(0.5, 1.0)) == 3
    stats = db.sequence_length_stats("VS_sars2")
    assert stats["min"] == 10 and stats["max"] == 11
    print("viral_genome_database: OK")
    return True

if __name__ == "__main__":
    self_test()
