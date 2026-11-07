import hashlib
import json

def generate_data_hash(data_dict):
    """Generates a SHA-256 hash to guarantee data integrity."""
    data_string = json.dumps(data_dict, sort_keys=True).encode()
    return hashlib.sha256(data_string).hexdigest()

def verify_data_hash(data_dict, original_hash):
    """Verifies if the data has been altered."""
    return generate_data_hash(data_dict) == original_hash
