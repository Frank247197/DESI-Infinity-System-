# DESI∞ INFINITY SYSTEM — Neural Connectome
# Version: 6.2.0
# Module: neural_connectome.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Neural Connectome"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def connectivity_summary(matrix: list[list[float]]) -> dict:
    """Validate a symmetric non-negative adjacency matrix and compute node strengths."""
    import math

    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("Connectivity matrix must be square.")
    for i in range(n):
        for j in range(n):
            x = matrix[i][j]
            if x < 0 or not math.isfinite(x):
                raise ValueError("Weights must be finite and non-negative.")
            if abs(x - matrix[j][i]) > 1e-9:
                raise ValueError("Matrix must be symmetric.")
    strengths = [sum(row) for row in matrix]
    edges = sum(
        matrix[i][j]
        for i in range(n)
        for j in range(i + 1, n)
    )
    return {
        "node_count": n,
        "node_strengths": strengths,
        "total_edge_weight": edges,
        "mean_strength": sum(strengths) / n if n else 0.0
    }
