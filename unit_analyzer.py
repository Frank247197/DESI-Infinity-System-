# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - SCIENTIFIC UNIT & DIMENSIONAL ANALYSIS
# Dimensional Consistency Checking for Physics, Chemistry & Biology
# ============================================================

from typing import Dict, Set, Tuple

class UnitDimensionalAnalyzer:
    """
    [CALC] Enforces strict dimensional compatibility across physical, 
    chemical, and biological parameters (e.g., verifying diffusion or flux calculations).
    """
    UNIT_DIMENSIONS: Dict[str, str] = {
        "nm": "LENGTH",
        "um": "LENGTH",
        "mm": "LENGTH",
        "m": "LENGTH",
        "s": "TIME",
        "ms": "TIME",
        "K": "TEMPERATURE",
        "Pa*s": "VISCOSITY",
        "mol/L": "CONCENTRATION",
        "m^2/s": "DIFFUSION_COEFFICIENT",
        "MW": "POWER"
    }

    def verify_operation(self, unit_a: str, unit_b: str, operation: str) -> bool:
        if unit_a not in self.UNIT_DIMENSIONS or unit_b not in self.UNIT_DIMENSIONS:
            raise ValueError("Unknown or unsupported scientific unit in expression.")
        
        dim_a = self.UNIT_DIMENSIONS[unit_a]
        dim_b = self.UNIT_DIMENSIONS[unit_b]

        if operation in {"+", "-"}:
            return dim_a == dim_b
        elif operation in {"*", "/"}:
            return True  # Permitted dimensional scaling/multiplication
        return False

if __name__ == "__main__":
    analyzer = UnitDimensionalAnalyzer()
    print("Can add nm and m (LENGTH + LENGTH):", analyzer.verify_operation("nm", "m", "+"))
    print("Can add nm and K (LENGTH + TEMP):", analyzer.verify_operation("nm", "K", "+"))
