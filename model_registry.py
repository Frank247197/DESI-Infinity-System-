# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - AI/ML MODEL MANAGEMENT REGISTRY
# Model Lifecycle, Evaluation Metrics & Clinical Boundary Guard
# ============================================================

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class ModelRecord:
    model_id: str
    version: str
    architecture: str
    dataset_id: str
    metrics: Dict[str, float]
    limitations: str
    clinically_validated: bool = False
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ModelRegistry:
    """
    [CALC] Manages AI/ML model versions, evaluation metrics, and enforces
    strict separation between experimental research models and clinical validation.
    """
    def __init__(self):
        self._models: Dict[str, ModelRecord] = {}

    def register_model(
        self,
        model_id: str,
        version: str,
        architecture: str,
        dataset_id: str,
        metrics: Dict[str, float],
        limitations: str,
        clinically_validated: bool = False
    ) -> Dict[str, Any]:
        if clinically_validated:
            raise PermissionError(
                "Clinical validation flag requires verified regulatory authorization."
            )
        key = f"{model_id}:{version}"
        record = ModelRecord(
            model_id=model_id,
            version=version,
            architecture=architecture,
            dataset_id=dataset_id,
            metrics=metrics,
            limitations=limitations,
            clinically_validated=False
        )
        self._models[key] = record
        return {"registered": key, "status": "RESEARCH_MODEL_ONLY"}

    def get_model_info(self, model_id: str, version: str) -> Dict[str, Any]:
        key = f"{model_id}:{version}"
        if key not in self._models:
            raise KeyError(f"Model '{key}' not found in registry.")
        rec = self._models[key]
        return {
            "model_id": rec.model_id,
            "version": rec.version,
            "architecture": rec.architecture,
            "dataset_id": rec.dataset_id,
            "metrics": rec.metrics,
            "limitations": rec.limitations,
            "clinically_validated": rec.clinically_validated
        }

if __name__ == "__main__":
    registry = ModelRegistry()
    res = registry.register_model(
        model_id="DESI_GNN_BBB",
        version="1.0.0",
        architecture="GraphConvNet-3Layer",
        dataset_id="BBB_PERMEABILITY_V1",
        metrics={"auroc": 0.89, "rmse": 0.14},
        limitations="Trained on in-silico molecular descriptors; not for clinical dosing."
    )
    print("Model Registry Status:", res)
