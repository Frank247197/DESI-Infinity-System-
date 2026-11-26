"""DESI Infinity System - Viral Genome Integrity Checker (v6.2.0)."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import List

VERSION = "6.2.0"
logger = logging.getLogger(__name__)

STOP_CODONS = {"TAA", "TAG", "TGA"}

@dataclass
class IntegrityReport:
    seq_id: str
    length: int
    has_premature_stops: bool
    ambiguous_bases: int
    is_intact: bool
    issues: List[str]

class IntegrityChecker:
    @staticmethod
    def check_orf(seq_id: str, sequence: str, start: int, end: int) -> IntegrityReport:
        """Checks an Open Reading Frame for premature stop codons and ambiguous bases."""
        if not sequence or start < 0 or end > len(sequence) or start >= end:
            raise ValueError("Invalid ORF coordinates")
            
        seq = sequence.upper()[start:end]
        issues = []
        
        # Check for ambiguous bases (N, Y, R, etc.)
        ambiguous = sum(1 for b in seq if b not in "ACGT")
        if ambiguous > 0:
            issues.append(f"{ambiguous} ambiguous bases found")
            
        # Check for premature stops (excluding the very last codon)
        premature_stops = False
        for i in range(0, len(seq) - 3, 3):
            if seq[i:i+3] in STOP_CODONS:
                premature_stops = True
                issues.append(f"Premature stop at codon {i//3}")
                break
                
        return IntegrityReport(
            seq_id=seq_id,
            length=len(seq),
            has_premature_stops=premature_stops,
            ambiguous_bases=ambiguous,
            is_intact=len(issues) == 0,
            issues=issues
        )

def self_test() -> bool:
    checker = IntegrityChecker()
    
    # Valid ORF (no stops inside)
    r1 = checker.check_orf("S1", "ATGAAACCCGGGTTT", 0, 15)
    assert r1.is_intact is True and r1.has_premature_stops is False
    
    # Premature stop
    r2 = checker.check_orf("S2", "ATGTAACCCGGGTTT", 0, 15)
    assert r2.is_intact is False and r2.has_premature_stops is True
    
    # Ambiguous bases
    r3 = checker.check_orf("S3", "ATGAAACCCNNNTTT", 0, 15)
    assert r3.ambiguous_bases == 3 and "ambiguous bases" in r3.issues[0]
    print("viral_genome_integrity_checker: OK")
    return True

if __name__ == "__main__":
    self_test()
