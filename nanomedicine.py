# =====================================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - NANOMEDICINE MODULE
# Computational Nanomedicine & Targeted Delivery Simulation
# =====================================================================

import math

try:
    from version_manifest import SYSTEM_VERSION
except ImportError:
    SYSTEM_VERSION = "6.2.0"

BOLTZMANN_CONSTANT = 1.380649e-23


def _is_real_number(value):
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


class Nanomedicine:
    """Simulates targeted nanocarrier dosing, release kinetics, and safety bounds."""

    def __init__(self):
        self.name = "NANOMEDICINE"
        self.version = SYSTEM_VERSION

    def calculate_diffusion_coefficient(self, temp_k, viscosity, radius):
        """Computes Stokes-Einstein diffusion coefficient (m^2/s)."""
        if not _is_real_number(temp_k) or temp_k <= 0:
            raise ValueError("temp_k must be a positive finite number.")
        if not _is_real_number(viscosity) or viscosity <= 0:
            raise ValueError("viscosity must be a positive finite number.")
        if not _is_real_number(radius) or radius <= 0:
            raise ValueError("radius must be a positive finite number.")

        return (BOLTZMANN_CONSTANT * temp_k) / (6.0 * math.pi * viscosity * radius)

    def estimate_diffusion_time(self, distance_m, diffusion_coefficient):
        """Estimates characteristic diffusion time (seconds) across distance_m."""
        if not _is_real_number(distance_m) or distance_m < 0:
            raise ValueError("distance_m must be a non-negative finite number.")
        if not _is_real_number(diffusion_coefficient) or diffusion_coefficient <= 0:
            raise ValueError(
                "diffusion_coefficient must be a positive finite number."
            )

        return (distance_m ** 2) / (2.0 * diffusion_coefficient)

    def plan_targeted_dose(
        self,
        tissue_mass_kg,
        target_concentration_mg_per_kg,
        encapsulation_efficiency=0.85,
    ):
        """Computes required payload mass and carrier dose for a target tissue."""
        if not _is_real_number(tissue_mass_kg) or tissue_mass_kg <= 0:
            raise ValueError("tissue_mass_kg must be a positive finite number.")
        if (
            not _is_real_number(target_concentration_mg_per_kg)
            or target_concentration_mg_per_kg < 0
        ):
            raise ValueError(
                "target_concentration_mg_per_kg must be a non-negative finite number."
            )
        if (
            not _is_real_number(encapsulation_efficiency)
            or encapsulation_efficiency <= 0
            or encapsulation_efficiency > 1.0
        ):
            raise ValueError(
                "encapsulation_efficiency must be a finite number in (0, 1]."
            )

        required_payload_mg = tissue_mass_kg * target_concentration_mg_per_kg
        carrier_dose_mg = required_payload_mg / encapsulation_efficiency

        return {
            "status": "READY",
            "required_payload_mg": round(required_payload_mg, 4),
            "carrier_dose_mg": round(carrier_dose_mg, 4),
            "encapsulation_efficiency": round(encapsulation_efficiency, 4),
        }

    def simulate_release_kinetics(
        self,
        initial_dose_mg,
        release_rate_per_hr,
        elapsed_hours,
    ):
        """Models first-order cumulative payload release over elapsed time."""
        if not _is_real_number(initial_dose_mg) or initial_dose_mg < 0:
            raise ValueError("initial_dose_mg must be a non-negative finite number.")
        if not _is_real_number(release_rate_per_hr) or release_rate_per_hr < 0:
            raise ValueError(
                "release_rate_per_hr must be a non-negative finite number."
            )
        if not _is_real_number(elapsed_hours) or elapsed_hours < 0:
            raise ValueError("elapsed_hours must be a non-negative finite number.")

        fraction_released = 1.0 - math.exp(-release_rate_per_hr * elapsed_hours)
        released_mg = initial_dose_mg * fraction_released
        remaining_mg = max(0.0, initial_dose_mg - released_mg)

        return {
            "status": "SIMULATED",
            "released_mg": round(released_mg, 4),
            "remaining_mg": round(remaining_mg, 4),
            "fraction_released": round(fraction_released, 4),
        }

    def check_payload_safety(self, dose_mg, max_safe_dose_mg):
        """Checks whether a nanocarrier dose stays within the safe ceiling."""
        if not _is_real_number(dose_mg) or dose_mg < 0:
            raise ValueError("dose_mg must be a non-negative finite number.")
        if not _is_real_number(max_safe_dose_mg) or max_safe_dose_mg <= 0:
            raise ValueError("max_safe_dose_mg must be a positive finite number.")

        if dose_mg > max_safe_dose_mg:
            return {
                "status": "OVER_LIMIT_WARNING",
                "message": "Nanocarrier dose exceeds maximum safe threshold.",
                "utilization_ratio": round(dose_mg / max_safe_dose_mg, 4),
            }

        return {
            "status": "SAFE",
            "message": "Nanocarrier dose is within safe bounds.",
            "utilization_ratio": round(dose_mg / max_safe_dose_mg, 4),
        }


# =====================================================================
# DEMONSTRATION
# =====================================================================

if __name__ == "__main__":
    nano = Nanomedicine()
    print("=" * 50)
    print(f"DESI∞ {nano.name} v{nano.version} Initialized")
    print("=" * 50)

    plan = nano.plan_targeted_dose(
        tissue_mass_kg=1.5,
        target_concentration_mg_per_kg=2.0,
        encapsulation_efficiency=0.8,
    )
    print("\n[1] Targeted Dose Plan:", plan)

    kinetics = nano.simulate_release_kinetics(
        initial_dose_mg=plan["carrier_dose_mg"],
        release_rate_per_hr=0.25,
        elapsed_hours=4.0,
    )
    print("\n[2] Release Kinetics:", kinetics)

    safety = nano.check_payload_safety(
        dose_mg=plan["carrier_dose_mg"],
        max_safe_dose_mg=10.0,
    )
    print("\n[3] Safety Check:", safety)
