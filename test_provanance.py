import unittest
from provenance import (
    generate_data_hash,
    verify_data_hash,
)

class TestResearchProvenance(unittest.TestCase):
    def test_hash_is_deterministic(self):
        data = {"patient_id": "DESI-001", "dna_sequence": "ATGC"}
        self.assertEqual(generate_data_hash(data), generate_data_hash(data))

    def test_original_data_verifies(self):
        data = {"patient_id": "DESI-001", "dna_sequence": "ATGC"}
        original_hash = generate_data_hash(data)
        self.assertTrue(verify_data_hash(data, original_hash))

    def test_modified_data_fails_verification(self):
        data = {"patient_id": "DESI-001", "dna_sequence": "ATGC"}
        original_hash = generate_data_hash(data)
        modified_data = {"patient_id": "DESI-001", "dna_sequence": "ATGG"}
        self.assertFalse(verify_data_hash(modified_data, original_hash))

    def test_different_data_has_different_hash(self):
        first = {"sequence": "ATGC"}
        second = {"sequence": "ATGG"}
        self.assertNotEqual(generate_data_hash(first), generate_data_hash(second))

if __name__ == "__main__":
    unittest.main()
