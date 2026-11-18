# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - REPRODUCIBLE EXPERIMENT TRACKER
# Deterministic Parameter Hashing & Scientific Provenance Log
# ============================================================

import json
import hashlib
from typing import Dict, Any
from datetime import datetime, timezone

class ExperimentTracker:
    """
    [CALC] Captures software versions, random seeds, dataset IDs, and hyperparameters
    to generate deterministic SHA-256 experiment fingerprints for exact replication.
    """
    def __init__(self, system_version: str = "6.2.0"):
        self.system_version = system_version
        self._records: Dict[str, Dict[str, Any]] = {}

    def log_experiment(
        self,
        experiment_name: str,
        module_name: str,
        dataset_id: str,
        parameters: Dict[str, Any],
        random_seed: int,
        outputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        canonical_config = json.dumps({
            "system_version": self.system_version,
            "module_name": module_name,
            "dataset_id": dataset_id,
            "parameters": parameters,
            "random_seed": random_seed
        }, sort_keys=True)

        experiment_id = hashlib.sha256(canonical_config.encode("utf-8")).hexdigest()[:16]
        record = {
            "experiment_id": experiment_id,
            "experiment_name": experiment_name,
            "system_version": self.system_version,
            "module_name": module_name,
            "dataset_id": dataset_id,
            "parameters": parameters,
            "random_seed": random_seed,
            "outputs": outputs,
            "timestamp_utc": datetime.now(timezone.utc).isoformat()
        }
        self._records[experiment_id] = record
        return record

if __name__ == "__main__":
    tracker = ExperimentTracker()
    exp = tracker.log_experiment(
        experiment_name="BBB_Nanoparticle_Diffusion_Run1",
        module_name="bbb_advection_diffusion",
        dataset_id="SYNTHETIC_CAPILLARY_MESH_V1",
        parameters={"dt": 1e-4, "radius_nm": 50.0},
        random_seed=42,
        outputs={"max_concentration": 0.842}
    )
    print("Logged Reproducible Experiment ID:", exp["experiment_id"])
