"""DESI Infinity System - Viral Replication Research Model (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Dict, List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class ReplicationModel:
    model_id: str
    virus_id: str
    r0: float
    generation_time_days: float
    target_cells: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.model_id or not self.virus_id:
            raise ValueError("model_id and virus_id required")
        if self.r0 < 0 or self.generation_time_days <= 0:
            raise ValueError("r0 must be >= 0 and generation_time must be > 0")

    def simulate_growth(self, days: int, initial_cells: int = 1) -> List[int]:
        """Simulates viral load growth over time using a basic exponential model."""
        if days <= 0 or initial_cells <= 0:
            raise ValueError("days and initial_cells must be positive")
        growth_rate = self.r0 / self.generation_time_days
        return [int(initial_cells * (2.718 ** (growth_rate * d))) for d in range(days)]

class ReplicationEngine:
    def __init__(self) -> None:
        self._models: Dict[str, ReplicationModel] = {}

    def add(self, model: ReplicationModel) -> None:
        if model.model_id in self._models:
            raise ValueError(f"duplicate model_id: {model.model_id}")
        self._models[model.model_id] = model

    def get(self, model_id: str) -> ReplicationModel:
        if model_id not in self._models:
            raise ValueError(f"unknown model_id: {model_id}")
        return self._models[model_id]

    def for_virus(self, virus_id: str) -> List[ReplicationModel]:
        return [m for m in self._models.values() if m.virus_id == virus_id]

    def high_replication_viruses(self, threshold: float = 2.0) -> List[str]:
        return list({m.virus_id for m in self._models.values() if m.r0 >= threshold})

def self_test() -> bool:
    engine = ReplicationEngine()
    engine.add(ReplicationModel("M1", "VS_sars2", r0=3.5, generation_time_days=5.0))
    engine.add(ReplicationModel("M2", "VS_flu", r0=1.5, generation_time_days=2.0))
    
    assert len(engine.for_virus("VS_sars2")) == 1
    assert len(engine.high_replication_viruses(2.0)) == 1
    
    sim = engine.get("M1").simulate_growth(5, 100)
    assert len(sim) == 5 and sim[-1] > sim[0]
    print("viral_replication_research_model: OK")
    return True

if __name__ == "__main__":
    self_test()
