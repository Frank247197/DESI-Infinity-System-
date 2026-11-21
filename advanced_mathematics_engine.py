# DESI∞ INFINITY SYSTEM — Advanced Mathematics Engine
# Version: 6.2.0
# Module: advanced_mathematics_engine.py
# Classification: Computational research / educational software

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Advanced Mathematics Engine"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def matrix_multiply(
    a: list[list[float]],
    b: list[list[float]]
) -> list[list[float]]:
    """Multiply compatible rectangular matrices."""
    if not a or not b or not a[0] or not b[0]:
        raise ValueError("Matrices cannot be empty.")
    if any(len(row) != len(a[0]) for row in a):
        raise ValueError("Matrix A must be rectangular.")
    if any(len(row) != len(b[0]) for row in b):
        raise ValueError("Matrix B must be rectangular.")
    if len(a[0]) != len(b):
        raise ValueError("Matrix dimensions are incompatible.")
    columns = list(zip(*b))
    return [
        [
            sum(x * y for x, y in zip(row, column))
            for column in columns
        ]
        for row in a
    ]

def determinant_2x2(matrix: list[list[float]]) -> float:
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("A 2x2 matrix is required.")
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
