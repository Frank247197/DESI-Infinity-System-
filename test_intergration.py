# ============================================================
# DESI∞ INFINITY SYSTEM 6.1 - INTEGRATION TESTS
# Verifying module interaction through the Master Orchestrator
# ============================================================

import unittest
from orchestrator import DesiOrchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        # Initialize the Master Orchestrator before every test
        self.desi = DesiOrchestrator()

    def test_all_modules_loaded(self):
        modules = self.desi.list_active_modules()
        # Ensure all 5 core modules are registered
        self.assertEqual(len(modules), 5)
        names = [m["name"] for m in modules]
        self.assertIn("GENOMCORE", names)
        self.assertIn("NEURAL_HEART", names)
        self.assertIn("NEURO_LINK", names)
        self.assertIn("NANOMEDICINE", names)
        self.assertIn("PHYSICS_ENERGY", names)

    def test_genomic_pipeline_success(self):
        dna = "ATGGACGAGACCATGAAGGAGTTGAAGGCCTACAAATCGGAAGAGCTGG"
        result = self.desi.execute_genomic_analysis(dna)
        self.assertEqual(result["status"], "success")
        self.assertGreater(result["gc_content"], 0)

    def test_genomic_pipeline_invalid_dna(self):
        # Contains 'X' which is not a valid DNA base
        invalid_dna = "ATGX"
        result = self.desi.execute_genomic_analysis(invalid_dna)
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid DNA sequence", result["message"])

    def test_cardiac_pipeline_success(self):
        # Peaks at 100, 250, 400, 550 -> ~40 BPM
        result = self.desi.execute_cardiac_analysis([100, 250, 400, 550], 100)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["safety_check"]["status"], "BRADYCARDIA_WARNING")

    def test_cardiac_pipeline_invalid_peaks(self):
        # Only 1 peak, cannot calculate interval
        result = self.desi.execute_cardiac_analysis([100], 100)
        self.assertEqual(result["status"], "error")

    def test_nanobot_pipeline_success(self):
        # Standard body temp, viscosity, 10nm particle
        result = self.desi.execute_nanobot_diffusion(310.15, 0.0007, 5e-9)
        self.assertEqual(result["status"], "success")
        # Diffusion time for 1cm should be roughly ~2.98 days
        self.assertAlmostEqual(result["time_1cm_days"], 2.98, places=1)

if __name__ == "__main__":
    unittest.main()
