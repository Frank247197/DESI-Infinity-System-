# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - PYDANTIC VALIDATION SCHEMAS
# Strict Runtime Type Safety & Biophysical Parameter Bounds
# ============================================================

from pydantic import BaseModel, Field, field_validator
import math

class PhysicsSimulationConfig(BaseModel):
    """
    [CALC / SIM] Strict validation schema for physics and thermodynamics 
    simulation inputs across DESI-Infinity modules.
    """
    emissivity: float = Field(..., ge=0.0, le=1.0, description="Surface emissivity (0 to 1)")
    area_m2: float = Field(..., gt=0.0, description="Surface area in square meters")
    temp_hot_k: float = Field(..., gt=0.0, description="Hot body temperature in Kelvin")
    temp_cold_k: float = Field(..., gt=0.0, description="Cold body temperature in Kelvin")

    @field_validator('*')
    @classmethod
    def ensure_finite(cls, v: float) -> float:
        if isinstance(v, bool) or not math.isfinite(v):
            raise ValueError("All parameters must be finite numbers, not booleans or NaNs.")
        return v

    def validate_temperatures(self) -> "PhysicsSimulationConfig":
        if self.temp_hot_k <= self.temp_cold_k:
            raise ValueError("Hot temperature must strictly exceed cold temperature.")
        return self


class NanomedicineTransportConfig(BaseModel):
    """
    [SIM] Validates nanoparticle physical properties and fluid dynamics parameters 
    for blood-brain barrier transport models.
    """
    particle_radius_nm: float = Field(..., gt=0.0, le=1000.0, description="Nanoparticle radius in nanometers")
    diffusion_coefficient: float = Field(..., gt=0.0, description="Diffusion coefficient (m^2/s)")
    blood_velocity_um_s: float = Field(..., ge=0.0, description="Capillary blood flow velocity (um/s)")
    target_concentration_molar: float = Field(..., gt=0.0, description="Target initial molar concentration")

    @field_validator('*')
    @classmethod
    def ensure_finite(cls, v: float) -> float:
        if isinstance(v, bool) or not math.isfinite(v):
            raise ValueError("All nanomedicine parameters must be finite numbers.")
        return v


if __name__ == "__main__":
    print("=" * 60)
    print("DESI∞ PYDANTIC VALIDATION SCHEMAS VERIFICATION [CALC]")
    print("=" * 60)

    try:
        print("\n[1] Testing valid physics configuration...")
        config = PhysicsSimulationConfig(
            emissivity=0.9,
            area_m2=2.5,
            temp_hot_k=310.15,
            temp_cold_k=293.15
        ).validate_temperatures()
        print(f"  Validation Passed Successfully: {config}")

        print("\n[2] Testing invalid out-of-bounds parameter...")
        invalid_config = PhysicsSimulationConfig(
            emissivity=1.5,  # Invalid: > 1.0
            area_m2=2.5,
            temp_hot_k=310.15,
            temp_cold_k=293.15
        )
    except Exception as e:
        print(f"  Caught Expected Validation Error: {e}")
