,
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

        
