# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - STOCHASTIC LANGEVIN DYNAMICS
# Brownian Motion & Thermal Fluctuation Nanoparticle Simulation
# ============================================================

import math
import numpy as np
import torch
from typing import Dict, Any

class LangevinDynamicsSimulator:
    """
    [SIM] Simulates stochastic Brownian motion and thermal fluctuations 
    affecting nanoscale drug carriers using Langevin dynamics equations.
    """
    def __init__(self, temperature_k: float = 310.15, viscosity_pas: float = 0.0007):
        if temperature_k <= 0 or viscosity_pas <= 0:
            raise ValueError("Temperature and viscosity must be positive numbers.")
        self.T = temperature_k
        self.eta = viscosity_pas
        self.k_b = 1.380649e-23  # Boltzmann constant (J/K)

    def simulate_brownian_trajectory(self, radius_nm: float, steps: int = 1000, dt: float = 1e-6, seed: int = 42) -> Dict[str, Any]:
        """
        Simulates 1D Langevin dynamics trajectory for a spherical nanoparticle 
        subject to thermal random forces and drag resistance.
        """
        for val in [radius_nm, steps, dt]:
            if isinstance(val, bool) or not math.isfinite(val) or val <= 0:
                raise ValueError("Simulation parameters must be positive finite numbers.")

        radius_m = radius_nm * 1e-9
        # Stokes drag coefficient: gamma = 6 * pi * eta * r
        gamma = 6.0 * math.pi * self.eta * radius_m
        
        # Diffusion coefficient: D = k_B * T / gamma
        D = (self.k_b * self.T) / gamma

        rng = np.default_rng(seed)
        positions = np.zeros(steps)
        current_pos = 0.0

        # Discretized Langevin stochastic integration
        # dx = sqrt(2 * D * dt) * Normal(0, 1)
        noise_amplitude = math.sqrt(2.0 * D * dt)

        for i in range(1, steps):
            random_force = rng.standard_normal()
            current_pos += noise_amplitude * random_force
            positions[i] = current_pos

        return {
            "radius_nm": radius_nm,
            "diffusion_coefficient_m2_s": float(D),
            "final_displacement_m": float(positions[-1]),
            "max_displacement_m": float(np.max(np.abs(positions))),
            "status": "SIMULATION_ONLY"
        }


if __name__ == "__main__":
    print("=" * 60)
    print("DESI∞ LANGEVIN DYNAMICS VERIFICATION [SIM]")
    print("=" * 60)

    simulator = LangevinDynamicsSimulator(temperature_k=310.15, viscosity_pas=0.0007)
    
    # Simulate 50 nm nanoparticle in physiological fluid
    result = simulator.simulate_brownian_trajectory(radius_nm=50.0, steps=2000, dt=1e-5, seed=123)

    print(f"\n[1] Stochastic Langevin Trajectory Simulated:")
    print(f"  Nanoparticle Radius  : {result['radius_nm']} nm")
    print(f"  Diffusion Coeff (D)  : {result['diffusion_coefficient_m2_s']:.6e} m^2/s")
    print(f"  Max Displacement     : {result['max_displacement_m']:.6e} m")
    print(f"  Execution Status     : {result['status']}")
