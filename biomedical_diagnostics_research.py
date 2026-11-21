# DESI∞ INFINITY SYSTEM — Biomedical Diagnostics Research
# Version: 6.2.0
# Module: biomedical_diagnostics_research.py

from __future__ import annotations

MODULE_NAME = "DESI∞ INFINITY SYSTEM — Biomedical Diagnostics Research"
MODULE_VERSION = "6.2.0"
SYSTEM_VERSION = "6.2.0"

def evaluate_binary(
    labels: list[int],
    predictions: list[int]
) -> dict:
    if len(labels) != len(predictions) or not labels:
        raise ValueError("Provide equally sized non-empty arrays.")
    if any(x not in (0, 1) for x in labels + predictions):
        raise ValueError("Labels and predictions must be binary.")

    tp = sum(a == 1 and b == 1 for a, b in zip(labels, predictions))
    tn = sum(a == 0 and b == 0 for a, b in zip(labels, predictions))
    fp = sum(a == 0 and b == 1 for a, b in zip(labels, predictions))
    fn = sum(a == 1 and b == 0 for a, b in zip(labels, predictions))

    def div(a, b):
        return a / b if b else None

    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": (tp + tn) / len(labels),
        "sensitivity": div(tp, tp + fn),
        "specificity": div(tn, tn + fp),
        "precision": div(tp, tp + fp),
        "f1": div(2 * tp, 2 * tp + fp + fn),
        "warning": "Research metrics do not establish clinical suitability."
    }
