import unittest
import sys
import os

# Add the root directory to path so we can import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research.provenance import generate_data_hash, verify_data_hash

class TestResearchEngines(unittest.TestCase):
    def test_data_integrity(self):
        test_data = {"patient_id": "DESI-001", "dna_sequence": "ATGC"}
        hash_val = generate_data_hash(test_data)
        
        # Should be True
        self.assertTrue(verify_data_hash(test_data, hash_val))
        
        # Alter data and check if it fails
        test_data["dna_sequence"] = "ATGG"
        self.assertFalse(verify_data_hash(test_data, hash_val))

if __name__ == '__main__':
    unittest.main()
