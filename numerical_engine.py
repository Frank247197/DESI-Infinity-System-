# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - NUMERICAL ACCURACY & UNCERTAINTY
# Precision Assessment, Error Propagation & Sensitivity Analysis
# ============================================================

import math
from typing import Dict, Any, Callable

class NumericalReliabilityEngine:
    """
    [CALC] Assesses floating-point precision, estimates measurement 
    uncertainty, and tracks error propagation through scientific formulas.
    """
    def estimate_uncertainty(self, nominal_value: float, absolute_error: float) -> Dict[str, Any]:
        if nominal_value == 0.0:
            relative_error_pct = 0.0
        else:
            relative_error_pct = abs(absolute_error / nominal_value) * 100.0

        return {
            "nominal_value": nominal_value,
            "absolute_error": absolute_error,
            "relative_error_pct": round(relative_error_pct, 4),
            "precision_grade": "HIGH" if relative_error_pct < 1.0 else "MODERATE"
        }

    def sensitivity_analysis(self, func: Callable[[float], float], base_x: float, delta: float = 1e-5) -> Dict[str, Any]:
        """Calculates finite-difference numerical sensitivity dy/dx."""
        y_forward = func(base_x + delta)
        y_backward = func(base_x - delta)
        derivative = (y_forward - y_backward) / (2.0 * delta)
        return {
            "base_x": base_x,
            "sensitivity_derivative": float(derivative),
            "status": "SENSITIVITY_COMPUTED"
        }

if __name__ == "__main__":
    engine = NumericalReliabilityEngine()
    print("Uncertainty Check:", engine.estimate_uncertainty(100.0, 0.25))
    print("Sensitivity Check:", engine.sensitivity_analysis(lambda x: x**2, 4.0))
