# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - NANOMEDICINE MODULE
# Computational Nanotechnology & Molecular Engineering
# ============================================================

import math

class Nanomedicine:
    def __init__(self):
        self.name = "NANOMEDICINE"
        self.version = "6.1"
        # Boltzmann constant (J/K)
        self.k_B = 1.380649e-23

    def calculate_diffusion_coefficient(self, temperature_k, viscosity_pas, radius_m):
        """
        Calculates the diffusion coefficient using the Stokes-Einstein equation:
        D = (k_B * T) / (6 * pi * eta * r)
        """
        if temperature_k <= 0:
            raise ValueError("Temperature must be greater than 0 Kelvin.")
        if viscosity_pas <= 0:
            raise ValueError("Viscosity must be positive.")
        if radius_m <= 0:
            raise ValueError("Particle radius must be positive.")

        D = (self.k_B * temperature_k) / (6 * math.pi * viscosity_pas * radius_m)
        return D

    def estimate_diffusion_time(self, distance_m, diffusion_coefficient):
        """
        Estimates the time required for a particle to diffuse across a distance.
        Using 3D diffusion relation: t = L^2 / (6 * D)
        """
        if distance_m <= 0:
            raise ValueError("Distance must be positive.")
        if diffusion_coefficient <= 0:
            raise ValueError("Diffusion coefficient must be positive.")

        time_seconds = (distance_m ** 2) / (6 * diffusion_coefficient)
        return time_seconds

    def convert_concentration_to_molar(self, value, unit):
        """
        Converts molar concentration units (M, mM, uM, nM) into standard Molar (M).
        """
        factors = {
            "M": 1.0,
            "mM": 1e-3,
            "uM": 1e-6,
            "nM": 1e-9
        }
        if unit not in factors:
            raise ValueError(f"Unsupported concentration unit: {unit}")
        if value < 0:
            raise ValueError("Concentration cannot be negative.")
        
        molar_value = value * factors[unit]
        return round(molar_value, 9)

# ============================================================
# DEMONSTRATION
# ============================================================
if __name__ == "__main__":
    nano = Nanomedicine()
    print("="*50)
    print(f"DESI∞ {nano.name} v{nano.version} Initialized")
    print("="*50)
    
    # 1. Nanoparticle Diffusion
    print("\n[1] Stokes-Einstein Diffusion Model:")
    temp = 310.15      # Body temp in Kelvin (37 C)
    viscosity = 0.0007 # Blood plasma viscosity (Pa·s)
    radius = 5e-9      # 10 nm diameter particle (5 nm radius)
    
    D = nano.calculate_diffusion_coefficient(temp, viscosity, radius)
    print(f"  Temperature: {temp} K")
    print(f"  Particle Radius: {radius} m (10 nm)")
    print(f"  Diffusion Coefficient (D): {D:.4e} m^2/s")

    # 2. Diffusion Time
    print("\n[2] Diffusion Time Estimate:")
    distance = 0.01 # 1 centimeter
    time_sec = nano.estimate_diffusion_time(distance, D)
    days = time_sec / (60 * 60 * 24)
    print(f"  Time to travel 1 cm: {time_sec:.2f} seconds")
    print(f"  Equivalent to: {days:.2f} days")

    # 3. Concentration Conversion
    print("\n[3] Concentration Conversion:")
    print(f"  5 mM -> {nano.convert_concentration_to_molar(5, 'mM')} M")
    print(f"  250 nM -> {nano.convert_concentration_to_molar(250, 'nM')} M")
