import hashlib
import json

def generate_data_hash(data_dict):
    """
    Generate a deterministic SHA-256 digest for JSON-compatible research data.
    This detects changes when compared with a previously trusted digest.
    It does not by itself establish the identity of the author.
    """
    if not isinstance(data_dict, dict):
        raise TypeError("Research data must be a dictionary.")
    try:
        canonical_data = json.dumps(
            data_dict, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Data must contain valid JSON-compatible values.") from exc
    encoded_data = canonical_data.encode("utf-8")
    return hashlib.sha256(encoded_data).hexdigest()

def verify_data_hash(data_dict, original_hash):
    """
    Verify data against a previously generated SHA-256 digest.
    """
    if not isinstance(original_hash, str):
        return False
    if len(original_hash) != 64:
        return False
    try:
        calculated_hash = generate_data_hash(data_dict)
    except (TypeError, ValueError):
        return False
    return calculated_hash == original_hash
