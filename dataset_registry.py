# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - SCIENTIFIC DATASET REGISTRY
# Dataset Versioning, Integrity Checksums & Provenance Tracking
# ============================================================

import hashlib
import json
from typing import Dict, Any, List

class ScientificDatasetRegistry:
    """
    [CALC] Registers and tracks scientific datasets with cryptographic
    checksums and full pre-processing pedigree for reproducible research.
    """
    def __init__(self):
        self._registry: Dict[str, Dict[str, Any]] = {}

    def register_dataset(
        self,
        dataset_id: str,
        version: str,
        source: str,
        format_type: str,
        preprocessing_steps: List[str],
        raw_sample_data: str
    ) -> Dict[str, Any]:
        checksum = hashlib.sha256(raw_sample_data.encode("utf-8")).hexdigest()
        key = f"{dataset_id}:{version}"
        record = {
            "dataset_id": dataset_id,
            "version": version,
            "source": source,
            "format_type": format_type,
            "preprocessing_steps": preprocessing_steps,
            "integrity_checksum": checksum
        }
        self._registry[key] = record
        return record

    def verify_dataset_integrity(self, dataset_id: str, version: str, current_sample_data: str) -> bool:
        key = f"{dataset_id}:{version}"
        if key not in self._registry:
            raise KeyError(f"Dataset '{key}' not found in registry.")
        expected_checksum = self._registry[key]["integrity_checksum"]
        current_checksum = hashlib.sha256(current_sample_data.encode("utf-8")).hexdigest()
        return expected_checksum == current_checksum

if __name__ == "__main__":
    registry = ScientificDatasetRegistry()
    ds = registry.register_dataset(
        dataset_id="BBB_CAPILLARY_FLUX",
        version="1.0.0",
        source="In-silico FEM Solver",
        format_type="CSV",
        preprocessing_steps=["normalization", "outlier_removal"],
        raw_sample_data="col1,col2\n1.2,3.4"
    )
    print("Registered Dataset Checksum:", ds["integrity_checksum"])
    print("Integrity Verified:", registry.verify_dataset_integrity("BBB_CAPILLARY_FLUX", "1.0.0", "col1,col2\n1.2,3.4"))
