# ==========================================================
# DESI∞ INFINITY SYSTEM - PHYSICS ENERGY MODULE
# ==========================================================

class PhysicsEnergy:
    def __init__(self):
        self.name = "PHYSICS_ENERGY"
        self.version = "6.1"

    def compute_conduction(self, k, area, delta_t, length):
        """Calculates 1D steady-state heat conduction (Q = k * A * Delta T / L)."""
        if length <= 0:
            raise ValueError("Length must be greater than zero.")
        return (k * area * delta_t) / length

