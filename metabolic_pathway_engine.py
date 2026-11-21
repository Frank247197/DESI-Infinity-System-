# DESI∞ INFINITY SYSTEM — Metabolic Pathway Engine
# Version: 6.2.0
# Module: metabolic_pathway_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Metabolic Pathway Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def pathway_flux(
    reaction_rates: dict[str, float],
    stoichiometry: dict[str, dict[str, float]]
) -> dict:
    """Aggregate species production/consumption from reaction rates and coefficients."""
    if set(reaction_rates) - set(stoichiometry):
        raise ValueError("Every reaction rate needs stoichiometry.")
    net = {}
    for reaction, rate in reaction_rates.items():
        if rate < 0:
            raise ValueError("Reaction rates must be non-negative.")
        for species, coefficient in stoichiometry[reaction].items():
            net[species] = net.get(species, 0.0) + float(coefficient) * float(rate)
    return {
        "net_species_flux": net,
        "balanced": all(abs(v) < 1e-9 for v in net.values())
    }
