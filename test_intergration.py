import unittest
from orchestrator import DesiOrchestrator

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.desi = DesiOrchestrator()

    def test_all_modules_loaded(self):
        modules = self.desi.list_active_modules()
        self.assertEqual(len(modules), 5)

    def test_genomic_pipeline_success(self):
        dna = "ATGGACGAGACCATGAAGGAGTTGAAGGCCTACAAATCGGAAGAGCTGG"
        result = self.desi.execute_genomic_analysis(dna)
        self.assertEqual(result["status"], "success")

    def test_genomic_pipeline_invalid_dna(self):
        # Contains 'X' which is not a valid DNA base
        result = self.desi.execute_genomic_analysis("ATGX")
        # Just check that it failed, don't worry about the exact error text
        self.assertEqual(result["status"], "error")

    def test_cardiac_pipeline_success(self):
        result = self.desi.execute_cardiac_analysis([100, 250, 400, 550], 100)
        self.assertEqual(result["status"], "success")

    def test_nanobot_pipeline_success(self):
        result = self.desi.execute_nanobot_diffusion(310.15, 0.0007, 5e-9)
        self.assertEqual(result["status"], "success")

if __name__ == "__main__":
    unittest.main()
