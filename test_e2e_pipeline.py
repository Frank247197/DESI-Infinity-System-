# ============================================================
# DESI∞ INFINITY SYSTEM 6.2 - END-TO-END INTEGRATION SUITE
# Cross-Module Pipeline Verification & V5.0 Backward Compatibility
# ============================================================

import unittest
from plugin_registry import PluginRegistry
from scientific_validator import ScientificValidator
from model_registry import ModelRegistry
from sec_vulnerability_scanner import SecurityGuard
from data_integrity_validator import DataIntegrityValidator
from api_server import api
from telemetry_metrics import TelemetryMonitor
from experiment_tracker import ExperimentTracker
from resource_manager import ResourceManager

# Backward-compatible Version 5.0 public genomics interfaces
def validate_dna(seq: str) -> bool:
    s = seq.upper().strip()
    return len(s) > 0 and all(base in {"A", "T", "C", "G"} for base in s)

def calculate_gc_content(seq: str) -> float:
    if not validate_dna(seq):
        raise ValueError("Invalid DNA sequence.")
    s = seq.upper().strip()
    return round(((s.count("G") + s.count("C")) / len(s)) * 100.0, 2)

class TestDESIEndToEndPipeline(unittest.TestCase):
    def test_v5_backward_compatibility(self):
        self.assertTrue(validate_dna("ATGCGTAC"))
        self.assertFalse(validate_dna("ATXG"))
        self.assertEqual(calculate_gc_content("GGCC"), 100.0)

    def test_full_v62_integration_workflow(self):
        # 1. Data Integrity Check
        div = DataIntegrityValidator()
        data_rep = div.validate_numeric_array([20.0, 40.0, 60.0], unit="nm")
        self.assertEqual(data_rep["integrity_status"], "PASSED")

        # 2. Scientific Boundary Validation
        sv = ScientificValidator("TEST_FLUX", "CALC_VALIDATED")
        sci_rep = sv.validate_and_execute(
            func=lambda x: x * 2.0,
            inputs={"x": 10.0},
            bounds={"x": (0.0, 50.0)},
            output_bounds=(0.0, 100.0)
        )
        self.assertEqual(sci_rep["result"], 20.0)

        # 3. Resource Manager & Telemetry
        rm = ResourceManager("LOW_RESOURCE")
        self.assertGreaterEqual(rm.calculate_safe_batch_size(4096), 1)
        tm = TelemetryMonitor(50.0)
        self.assertEqual(tm.record_power_draw(25.0)["status"], "NOMINAL")

        # 4. API & Security Check
        guard = SecurityGuard()
        self.assertTrue(guard.check_permission("ADMIN", "UPDATE_CONFIG"))
        api_res = api.dispatch("/api/v1/genomics/gc-content", {"sequence": "GCGC"})
        self.assertEqual(api_res["status_code"], 200)

        # 5. Reproducible Experiment Logging
        tracker = ExperimentTracker()
        exp = tracker.log_experiment("E2E_TEST", "test_e2e_pipeline", "DS_V1", {"k": 1}, 42, {"ok": True})
        self.assertEqual(len(exp["experiment_id"]), 16)

if __name__ == "__main__":
    unittest.main()
