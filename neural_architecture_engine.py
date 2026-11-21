# DESI∞ INFINITY SYSTEM — Neural Architecture Research
# Version: 6.2.0
# Module: neural_architecture_engine.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Neural Architecture Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def parameter_count(
    layer_widths: list[int],
    include_bias: bool = True
) -> int:
    if (
        len(layer_widths) < 2
        or any(
            isinstance(x, bool) or not isinstance(x, int) or x < 1
            for x in layer_widths
        )
    ):
        raise ValueError("Provide at least two positive integer layer widths.")
    return sum(
        a * b + (b if include_bias else 0)
        for a, b in zip(layer_widths, layer_widths[1:])
    )

def memory_bytes(
    parameters: int,
    bytes_per_parameter: int = 4
) -> int:
    if parameters < 0 or bytes_per_parameter < 1:
        raise ValueError("Invalid memory inputs.")
    return parameters * bytes_per_parameter
