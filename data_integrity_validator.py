# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - DATA QUALITY & INTEGRITY GUARD
# Automated NaN, Inf, Schema & Biological Unit Verification
# ============================================================

import math
import numpy as np
from typing import Dict, Any, List

class DataIntegrityValidator:
    """
    [CALC] Inspects incoming biological and physical arrays before execution
    to block NaNs, infinite values, empty datasets, and invalid units.
    """
    SUPPORTED_UNITS = {"nm", "um", "mm", "m", "K", "C", "Pa*s", "mol/L", "MW", "ms", "s"}

    def validate_numeric_array(self, data: List[float], unit: str, allow_negative: bool = False) -> Dict[str, Any]:
        if unit not in self.SUPPORTED_UNITS:
            raise ValueError(f"Unsupported scientific unit '{unit}'. Allowed: {sorted(self.SUPPORTED_UNITS)}")
        if not data:
            raise ValueError("Dataset cannot be empty.")

        arr = np.asarray(data, dtype=np.float64)
        if np.isnan(arr).any():
            raise ValueError("Data integrity failure: NaN values detected in dataset.")
        if np.isinf(arr).any():
            raise ValueError("Data integrity failure: Infinite values detected in dataset.")
        if not allow_negative and (arr < 0).any():
            raise ValueError(f"Data integrity failure: Negative values detected for non-negative unit '{unit}'.")

        return {
            "count": int(arr.size),
            "unit": unit,
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "integrity_status": "PASSED"
        }

if __name__ == "__main__":
    validator = DataIntegrityValidator()
    report = validator.validate_numeric_array([10.5, 25.0, 50.2], unit="nm", allow_negative=False)
    print("Data Integrity Report:", report)
