# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - RESOURCE & LOW-DEVICE MANAGER
# Adaptive Operating Modes & Memory-Constrained Batch Sizing
# ============================================================

from typing import Dict, Any

class ResourceManager:
    """
    [CALC] Adapts DESI-Infinity computational workloads between lightweight
    mobile/edge devices and high-performance workstation/cluster nodes.
    """
    PROFILES = {
        "LOW_RESOURCE": {"max_ram_mb": 512, "max_workers": 1, "precision": "float32"},
        "STANDARD": {"max_ram_mb": 4096, "max_workers": 4, "precision": "float32"},
        "HIGH_PERFORMANCE": {"max_ram_mb": 32768, "max_workers": 16, "precision": "float64"}
    }

    def __init__(self, mode: str = "STANDARD"):
        mode_upper = mode.upper()
        if mode_upper not in self.PROFILES:
            raise ValueError(f"Invalid mode '{mode}'. Choose from: {list(self.PROFILES.keys())}")
        self.mode = mode_upper
        self.config = self.PROFILES[mode_upper]

    def calculate_safe_batch_size(self, sample_size_bytes: int) -> int:
        if sample_size_bytes <= 0:
            raise ValueError("Sample size in bytes must be positive.")
        # Reserve 50% of profile RAM budget for active tensor batch
        budget_bytes = (self.config["max_ram_mb"] * 1024 * 1024) * 0.5
        batch_size = max(1, int(budget_bytes // sample_size_bytes))
        return batch_size

    def get_runtime_profile(self) -> Dict[str, Any]:
        return {"active_mode": self.mode, **self.config}

if __name__ == "__main__":
    rm = ResourceManager(mode="LOW_RESOURCE")
    print("Runtime Profile:", rm.get_runtime_profile())
    print("Safe Batch Size (1 MB samples):", rm.calculate_safe_batch_size(1024 * 1024))
