"""DESI Infinity System - Population Genomics Engine (v6.2.0).

Stores allele frequencies per population, Fst-style differentiation
summaries, and stratification metadata. Research-only; no clinical use.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

POPULATION_CODES = ("AFR", "AMR", "EAS", "EUR", "SAS", "OTH")
SOURCES = ("curated", "literature", "predicted")


class PopulationGenomicsError(Exception):
    """Base population genomics error."""


@dataclass
class PopulationFrequency:
    variant_id: str
    population: str
    allele_frequency: float
    sample_size: Optional[int] = None
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.variant_id or not isinstance(self.variant_id, str):
            raise PopulationGenomicsError("variant_id required")
        if self.population not in POPULATION_CODES:
            raise PopulationGenomicsError(f"invalid population: {self.population!r}")
        if not 0.0 <= float(self.allele_frequency) <= 1.0:
            raise PopulationGenomicsError("allele_frequency must be in [0, 1]")
        if self.sample_size is not None:
            if not isinstance(self.sample_size, int) or self.sample_size <= 0:
                raise PopulationGenomicsError("sample_size must be a positive int or None")
        if self.source not in SOURCES:
            raise PopulationGenomicsError(f"invalid source: {self.source!r}")


class PopulationGenomicsEngine:
    """Registry + differentiation analyses."""

    def __init__(self) -> None:
        self._frequencies: List[PopulationFrequency] = []
        self._variant_index: Dict[str, List[int]] = {}

    def add(self, freq: PopulationFrequency) -> None:
        idx = len(self._frequencies)
        self._frequencies.append(freq)
        self._variant_index.setdefault(freq.variant_id, []).append(idx)

    def for_variant(self, variant_id: str) -> List[PopulationFrequency]:
        return [self._frequencies[i] for i in self._variant_index.get(variant_id, [])]

    def for_population(self, population: str) -> List[PopulationFrequency]:
        if population not in POPULATION_CODES:
            raise PopulationGenomicsError(f"invalid population: {population!r}")
        return [f for f in self._frequencies if f.population == population]

    def allele_frequencies(self, variant_id: str) -> Dict[str, float]:
        return {f.population: f.allele_frequency for f in self.for_variant(variant_id)}

    def fst_style_differentiation(self, variant_id: str) -> Optional[float]:
        freqs = [f.allele_frequency for f in self.for_variant(variant_id)]
        if len(freqs) < 2:
            return None
        mean = sum(freqs) / len(freqs)
        if mean == 0.0 or mean == 1.0:
            return 0.0
        variance = sum((p - mean) ** 2 for p in freqs) / len(freqs)
        return round(variance / (mean * (1.0 - mean)), 4)

    def high_differentiation(self, threshold: float = 0.15) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for vid in self._variant_index:
            fst = self.fst_style_differentiation(vid)
            if fst is not None and fst >= threshold:
                results.append({"variant_id": vid, "fst_style": fst})
        results.sort(key=lambda r: r["fst_style"], reverse=True)  # type: ignore
        return results

    def sample_total(self, population: str) -> int:
        return sum(f.sample_size or 0 for f in self.for_population(population))

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "frequencies": len(self._frequencies),
            "variants": len(self._variant_index),
            "populations": len({f.population for f in self._frequencies}),
        }


def self_test() -> bool:
    engine = PopulationGenomicsEngine()
    engine.add(PopulationFrequency("V1", "AFR", 0.25, sample_size=500))
    engine.add(PopulationFrequency("V1", "EUR", 0.05, sample_size=1000))
    engine.add(PopulationFrequency("V1", "EAS", 0.02, sample_size=800))
    engine.add(PopulationFrequency("V2", "AFR", 0.10, sample_size=500))
    engine.add(PopulationFrequency("V2", "EUR", 0.09, sample_size=1000))
    assert engine.allele_frequencies("V1")["AFR"] == 0.25
    fst = engine.fst_style_differentiation("V1")
    assert fst is not None and fst > 0
    assert len(engine.high_differentiation(0.1)) >= 1
    assert engine.sample_total("AFR") == 1000
    assert engine.stats()["variants"] == 2
    print("population_genomics_engine: OK")
    return True


if __name__ == "__main__":
    self_test()
