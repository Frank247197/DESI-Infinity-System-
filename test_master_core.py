import unittest
from desi_master_core import (
    calculate_gc_content, 
    simulate_crispr_mutation, 
    translate_mrna,
    transcribe_dna_to_mrna,
    validate_dna
)

class TestGenomCore(unittest.TestCase):
    def test_gc_content(self):
        self.assertEqual(calculate_gc_content("ATGC"), 50.0)

    def test_mutation_position(self):
        result = simulate_crispr_mutation("ATGC", 1, "C")
        self.assertEqual(result.mutated_sequence, "ACGC")

    def test_transcription(self):
        self.assertEqual(transcribe_dna_to_mrna("ATGGCT"), "AUGGCU")

    def test_translation(self):
        result = translate_mrna("AUGGCUUAA")
        self.assertEqual(result.amino_acids, ("Methionine", "Alanine"))
        self.assertTrue(result.stop_found)

if __name__ == '__main__':
    unittest.main()
