# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - PHYSICS & ENERGY MODULE
# Computational Physics, Thermodynamics & ARC Fusion Research
# ============================================================

import math

class PhysicsEnergy:
    def __init__(self):
        self.name = "PHYSICS_ENERGY"
        self.version = "6.1"
        self.sigma = 5.670374419e-8  # Stefan-Boltzmann constant

    def compute_conduction(self, k: float, area: float, delta_t: float, length: float) -> float:
        """Calculates 1D steady-state heat conduction (Q = k * A * Delta T / L)."""
        for val in [k, area, delta_t, length]:
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError("Inputs must be finite numbers, not booleans.")
        if length <= 0:
            raise ValueError("Length must be greater than zero.")
        if area <= 0:
            raise ValueError("Area must be positive.")
        
        return (k * area * delta_t) / length

    def calculate_thermal_radiation(self, emissivity: float, area_m2: float, temp_hot_k: float, temp_cold_k: float) -> float:
        """Calculates thermal radiation heat transfer via Stefan-Boltzmann law."""
        for val in [emissivity, area_m2, temp_hot_k, temp_cold_k]:
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError("Inputs must be finite numbers, not booleans.")
                
        if not (0 <= emissivity <= 1):
            raise ValueError("Emissivity must be between 0 and 1.")
        if area_m2 <= 0:
            raise ValueError("Area must be positive.")
        if temp_hot_k <= temp_cold_k:
            raise ValueError("Hot temperature must be greater than cold temperature.")
        
        Q = emissivity * self.sigma * area_m2 * ((temp_hot_k ** 4) - (temp_cold_k ** 4))
        return Q

    def arc_fusion_zone_simulation(self, input_energy_mw: float, plasma_efficiency: float) -> dict:
        """Simulates ARC-class fusion energy output and stability metrics."""
        for val in [input_energy_mw, plasma_efficiency]:
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError("Inputs must be finite numbers, not booleans.")
                
        if input_energy_mw <= 0:
            raise ValueError("Input energy must be positive.")
        if not (0 < plasma_efficiency <= 1):
            raise ValueError("Plasma efficiency must be between 0 and 1.")
        
        gross_output_mw = input_energy_mw * plasma_efficiency
        net_output_mw = gross_output_mw - input_energy_mw
        stable = gross_output_mw > input_energy_mw
        
        return {
            "input_energy_mw": input_energy_mw,
            "plasma_efficiency": plasma_efficiency,
            "gross_output_mw": round(gross_output_mw, 2),
            "net_output_mw": round(net_output_mw, 2),
            "simulated_stable": stable,
            "status": "SIMULATION_ONLY"
        }

    def calculate_cryogenic_heat_leak(self, emissivity: float, area_m2: float, temp_ambient_k: float, temp_cryo_k: float) -> float:
        """Calculates continuous environmental heat infiltration into cryogenic vacuum barriers."""
        for val in [emissivity, area_m2, temp_ambient_k, temp_cryo_k]:
            if isinstance(val, bool) or not isinstance(val, (int, float)) or not math.isfinite(val):
                raise ValueError("Inputs must be finite numbers, not booleans.")
                
        if temp_ambient_k <= temp_cryo_k:
            raise ValueError("Ambient temperature must be warmer than cryo temperature.")
        if area_m2 <= 0:
            raise ValueError("Area must be positive.")
        if not (0 <= emissivity <= 1):
            raise ValueError("Emissivity must be between 0 and 1.")

        Q_leak = emissivity * self.sigma * area_m2 * ((temp_ambient_k ** 4) - (temp_cryo_k ** 4))
        return Q_leak

if __name__ == "__main__":
    physics = PhysicsEnergy()
    print("="*60)
    print(f"DESI∞ {physics.name} v{physics.version} Initialized")
    print("="*60)
    
    print("\n[1] 1D Steady-State Heat Conduction:")
    q_cond = physics.compute_conduction(k=0.8, area=2.0, delta_t=50.0, length=0.05)
    print(f"  Conduction Heat Transfer: {q_cond:.2f} W")

    print("\n[2] Thermal Radiation:")
    q_rad = physics.calculate_thermal_radiation(0.9, 2.0, 400.0, 300.0)
    print(f"  Radiation Heat Transfer: {q_rad:.2f} W")

    print("\n[3] ARC Fusion (85% Efficiency):")
    fusion = physics.arc_fusion_zone_simulation(50, 0.85)
    print(f"  Net Output: {fusion['net_output_mw']} MW (Stable: {fusion['simulated_stable']})")

    print("\n[4] Cryogenic Heat Leak:")
    q_leak = physics.calculate_cryogenic_heat_leak(0.05, 10.0, 293.0, 20.0)
    print(f"  Cryogenic Heat Infiltration: {q_leak:.2f} W")


