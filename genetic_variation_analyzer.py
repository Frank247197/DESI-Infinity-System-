# DESI∞ INFINITY SYSTEM — Genetic Variation Analyzer
# Version: 6.2.0
# Module: genetic_variation_analyzer.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Genetic Variation Analyzer"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def summarize_genotypes(genotypes: list[str]) -> dict:
    """Accept diploid calls such as AA, AG, or missing NN; descriptive only."""
    calls = [g.upper() for g in genotypes]
    if any(len(g) != 2 or set(g) - set("ACGTN") for g in calls):
        raise ValueError("Genotypes must be two-character A/C/G/T/N calls.")
    alleles = [a for g in calls for a in g if a != "N"]
    counts = {a: alleles.count(a) for a in "ACGT"}
    total = len(alleles)
    frequencies = {
        a: c / total for a, c in counts.items()
    } if total else {}
    hetero = sum(
        g[0] != g[1] and "N" not in g
        for g in calls
    )
    return {
        "sample_count": len(calls),
        "allele_counts": counts,
        "allele_frequencies": frequencies,
        "observed_heterozygosity": hetero / len(calls) if calls else None
    }
