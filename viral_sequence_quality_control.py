"""DESI Infinity System - Viral Sequence Quality Control (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

@dataclass
class QCResult:
    seq_id: str
    length: int
    n_content: float
    is_valid: bool
    issues: list[str]

class SequenceQC:
    VALID_BASES = set("ACGT")

    def __init__(self, min_length: int = 50, max_n_percent: float = 0.05) -> None:
        if min_length < 1:
            raise ValueError("min_length must be >= 1")
        self.min_length = min_length
        self.max_n_percent = max_n_percent

    def evaluate(self, seq_id: str, sequence: str) -> QCResult:
        if not seq_id or not sequence:
            raise ValueError("seq_id and sequence required")
        
        seq = sequence.upper()
        length = len(seq)
        issues = []
        
        if length < self.min_length:
            issues.append(f"Too short (min {self.min_length})")
            
        n_count = seq.count("N")
        n_content = round(n_count / length, 4) if length > 0 else 0.0
        if n_content > self.max_n_percent:
            issues.append(f"High N content ({n_content*100}%)")
            
        invalid_chars = set(seq) - self.VALID_BASES - {"N"}
        if invalid_chars:
            issues.append(f"Invalid characters: {invalid_chars}")

        return QCResult(
            seq_id=seq_id,
            length=length,
            n_content=n_content,
            is_valid=len(issues) == 0,
            issues=issues
        )

    def batch_evaluate(self, sequences: dict[str, str]) -> list[QCResult]:
        return [self.evaluate(sid, seq) for sid, seq in sequences.items()]

def self_test() -> bool:
    qc = SequenceQC(min_length=10, max_n_percent=0.10)
    
    r1 = qc.evaluate("S1", "ACGTACGTACGT") # Valid
    assert r1.is_valid is True and r1.length == 12
    
    r2 = qc.evaluate("S2", "ACGTN") # Too short, high N
    assert r2.is_valid is False and len(r2.issues) == 2
    
    r3 = qc.evaluate("S3", "ACGTXACGTACGT") # Invalid char
    assert r3.is_valid is False and "Invalid characters" in r3.issues[0]
    
    batch = qc.batch_evaluate({"S1": "ACGTACGTACGT", "S4": "N" * 20})
    assert batch[0].is_valid is True and batch[1].is_valid is False
    print("viral_sequence_quality_control: OK")
    return True

if __name__ == "__main__":
    self_test()
