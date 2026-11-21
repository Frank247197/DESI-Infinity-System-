# DESI∞ INFINITY SYSTEM — Medical Imaging Research
# Version: 6.2.0
# Module: medical_imaging_ai.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Medical Imaging Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def image_statistics(pixels: list[list[float]]) -> dict:
    if (
        not pixels
        or not pixels[0]
        or any(len(row) != len(pixels[0]) for row in pixels)
    ):
        raise ValueError("Image must be a non-empty rectangular matrix.")
    values = [float(x) for row in pixels for x in row]
    if any(not __import__("math").isfinite(x) for x in values):
        raise ValueError("Pixels must be finite.")
    mean = sum(values) / len(values)
    return {
        "width": len(pixels[0]),
        "height": len(pixels),
        "pixel_count": len(values),
        "minimum": min(values),
        "maximum": max(values),
        "mean": mean,
        "variance": sum((x - mean) ** 2 for x in values) / len(values),
        "note": "Descriptive image statistics only; no diagnosis."
    }
