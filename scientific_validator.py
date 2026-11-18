# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - SCIENTIFIC VALIDATION FRAMEWORK
# Mathematical Assumptions, Boundary Checking & Digital Twin Guard
# ============================================================

import math
from typing import Dict, Any, Callable, Tuple

class ScientificValidator:
    """
    [CALC / SIM] Validates input parameters, verifies expected output ranges,
    and enforces rigorous scientific provenance tracking for DESI-Infinity modules.
    """
    def __init__(self, module_name: str, classification: str):
        valid_classifications = {"CALC_VALIDATED", "SIMULATION_MODEL", "THEORETICAL_APPROXIMATION"}
        if classification not in valid_classifications:
            raise ValueError(f"Invalid classification. Must be one of: {valid_classifications}")
        
        self.module_name = module_name
        self.classification = classification

    def validate_and_execute(
        self,
        func: Callable,
        inputs: Dict[str, float],
        bounds: Dict[str, Tuple[float, float]],
        output_bounds: Tuple[float, float]
    ) -> Dict[str, Any]:
        """
        Validates input boundaries, executes the scientific computation/simulation,
        and ensures the resulting output lies within safe physical limits.
        """
        # 1. Input Boundary Validation
        for param, val in inputs.items():
            if param in bounds:
                min_val, max_val = bounds[param]
                if not (min_val <= val <= max_val):
                    raise ValueError(
                        f"Input validation failed for '{param}': value {val} "
                        f"is out of bounds [{min_val}, {max_val}]."
                    )

        # 2. Execution
        raw_output = func(**inputs)

        # 3. Output Range Verification
        out_min, out_max = output_bounds
        if not (out_min <= raw_output <= out_max):
            raise ArithmeticError(
                f"Output validation failed in {self.module_name}: result {raw_output} "
                f"violates expected physiological/physical range [{out_min}, {out_max}]."
            )

        return {
            "module": self.module_name,
            "classification": self.classification,
            "inputs": inputs,
            "result": float(raw_output),
            "status": "VALIDATION_PASSED"
        }


if __name__ == "__main__":
    print("=" * 60)
    print("DESI∞ SCIENTIFIC VALIDATOR VERIFICATION [CALC/SIM]")
    print("=" * 60)

    # Example: Simulating blood-brain barrier solute permeability flux
    validator = ScientificValidator(
        module_name="BBB_FLUX_SIMULATOR",
        classification="SIMULATION_MODEL"
    )

    def calculate_solute_flux(concentration_gradient: g_gradient, permeability: p_coeff) -> float:
        # Fick's first law approximation: Flux = P * dC
        return permeability * concentration_gradient

    # Input bounds check
    input_params = {"concentration_gradient": 5.0, "permeability": 1.2e-6}
    param_bounds = {
        "concentration_gradient": (0.0, 100.0),
        "permeability": (1e-9, 1e-4)
    }
    # Expected output safe range (mol/s*m^2)
    safe_output_range = (0.0, 1.0)

    try:
        report = validator.validate_and_execute(
            func=lambda concentration_gradient, permeability: permeability * concentration_gradient,
            inputs=input_params,
            bounds=param_bounds,
            output_bounds=safe_output_range
        )
        print(f"\n[1] Scientific Validation Successful:")
        print(f"  Module         : {report['module']}")
        print(f"  Classification : {report['classification']}")
        print(f"  Computed Flux  : {report['result']:.8e}")
        print(f"  Status         : {report['status']}")
    except Exception as e:
        print(f"Validation Error: {e}")
