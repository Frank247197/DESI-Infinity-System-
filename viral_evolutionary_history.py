"""DESI Infinity System - Viral Evolutionary History (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class EvolutionaryEvent:
    event_id: str
    virus_id: str
    lineage: str
    year: int
    substitution_rate: float # subs/site/year
    tmrca_years: float # Time to Most Recent Common Ancestor

    def __post_init__(self) -> None:
        if not self.event_id or not self.virus_id:
            raise ValueError("event_id and virus_id required")
        if self.year < 1900 or self.year > 2100:
            raise ValueError("invalid year")
        if self.substitution_rate < 0 or self.tmrca_years < 0:
            raise ValueError("rates must be positive")

class EvolutionaryHistory:
    def __init__(self) -> None:
        self._events: Dict[str, EvolutionaryEvent] = {}

    def add(self, event: EvolutionaryEvent) -> None:
        if event.event_id in self._events:
            raise ValueError(f"duplicate event_id: {event.event_id}")
        self._events[event.event_id] = event

    def get_timeline(self, virus_id: str) -> list[EvolutionaryEvent]:
        events = [e for e in self._events.values() if e.virus_id == virus_id]
        return sorted(events, key=lambda e: e.year)

    def fastest_evolving(self, virus_id: str) -> EvolutionaryEvent | None:
        events = self.get_timeline(virus_id)
        if not events:
            return None
        return max(events, key=lambda e: e.substitution_rate)

def self_test() -> bool:
    history = EvolutionaryHistory()
    history.add(EvolutionaryEvent("E1", "VS_sars2", "B", 2020, 0.001, 10.0))
    history.add(EvolutionaryEvent("E2", "VS_sars2", "Omicron", 2021, 0.002, 5.0))
    
    timeline = history.get_timeline("VS_sars2")
    assert len(timeline) == 2 and timeline[0].year == 2020
    
    fastest = history.fastest_evolving("VS_sars2")
    assert fastest.lineage == "Omicron"
    print("viral_evolutionary_history: OK")
    return True

if __name__ == "__main__":
    self_test()
