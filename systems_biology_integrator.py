"""DESI Infinity System - Systems Biology Integrator (v6.2.0).

Integrates multi-omics layers (genomics, transcriptomics, proteomics,
metabolomics) at the gene/feature level using a structured join model.
NO inference across layers is fabricated; missing data is reported as
missing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)

OMICS_LAYERS = ("genomics", "transcriptomics", "proteomics",
                "metabolomics", "epigenomics", "other")
SOURCES = ("curated", "literature", "predicted")


class SystemsBiologyError(Exception):
    """Base systems biology error."""


@dataclass
class OmicsLayerData:
    layer: str
    feature_id: str
    value: float
    unit: str = ""
    sample_group: str = "control"
    source: str = "curated"
    evidence_ids: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.layer not in OMICS_LAYERS:
            raise SystemsBiologyError(f"invalid layer: {self.layer!r}")
        if not self.feature_id or not isinstance(self.feature_id, str):
            raise SystemsBiologyError("feature_id required")
        if not isinstance(self.value, (int, float)):
            raise SystemsBiologyError("value must be numeric")
        if self.source not in SOURCES:
            raise SystemsBiologyError(f"invalid source: {self.source!r}")


class SystemsBiologyIntegrator:
    """Multi-omics integration with per-feature joins."""

    def __init__(self) -> None:
        self._data: Dict[str, List[OmicsLayerData]] = {}
        self._by_layer: Dict[str, List[OmicsLayerData]] = {}

    def add(self, record: OmicsLayerData) -> None:
        self._data.setdefault(record.feature_id, []).append(record)
        self._by_layer.setdefault(record.layer, []).append(record)

    def for_feature(self, feature_id: str) -> Dict[str, List[OmicsLayerData]]:
        out: Dict[str, List[OmicsLayerData]] = {}
        for rec in self._data.get(feature_id, []):
            out.setdefault(rec.layer, []).append(rec)
        return out

    def by_layer(self, layer: str) -> List[OmicsLayerData]:
        if layer not in OMICS_LAYERS:
            raise SystemsBiologyError(f"invalid layer: {layer!r}")
        return list(self._by_layer.get(layer, []))

    def integrated_view(self, feature_id: str) -> Dict[str, object]:
        per_layer = self.for_feature(feature_id)
        view: Dict[str, object] = {"feature_id": feature_id}
        for layer in OMICS_LAYERS:
            recs = per_layer.get(layer, [])
            if not recs:
                view[layer] = {"status": "missing"}
                continue
            values = [r.value for r in recs]
            view[layer] = {
                "status": "present",
                "n": len(values),
                "mean": round(sum(values) / len(values), 4),
                "min": min(values),
                "max": max(values),
            }
        return view

    def features_with_all_layers(self, required_layers: List[str]
                                 ) -> List[str]:
        for layer in required_layers:
            if layer not in OMICS_LAYERS:
                raise SystemsBiologyError(f"invalid layer: {layer!r}")
        out: List[str] = []
        for fid in self._data:
            layers = {r.layer for r in self._data[fid]}
            if all(layer in layers for layer in required_layers):
                out.append(fid)
        return sorted(out)

    def layer_coverage(self) -> Dict[str, int]:
        return {layer: len(self._by_layer.get(layer, []))
                for layer in OMICS_LAYERS}

    def stats(self) -> Dict[str, int]:
        return {
            "version": VERSION,
            "features": len(self._data),
            "records": sum(len(v) for v in self._data.values()),
            "layers": len(self._by_layer),
        }


def self_test() -> bool:
    integrator = SystemsBiologyIntegrator()
    integrator.add(OmicsLayerData("genomics", "TP53", 1.0, "variant_count"))
    integrator.add(OmicsLayerData("transcriptomics", "TP53", 8.5, "log2_tpm"))
    integrator.add(OmicsLayerData("transcriptomics", "TP53", 7.9, "log2_tpm"))
    integrator.add(OmicsLayerData("proteomics", "TP53", 620.0, "abundance"))
    integrator.add(OmicsLayerData("genomics", "BRCA1", 1.0, "variant_count"))
    view = integrator.integrated_view("TP53")
    assert view["genomics"]["status"] == "present"
    assert view["transcriptomics"]["n"] == 2
    assert view["metabolomics"]["status"] == "missing"
    assert integrator.features_with_all_layers(
        ["genomics", "transcriptomics", "proteomics"]) == ["TP53"]
    assert len(integrator.by_layer("genomics")) == 2
    print("systems_biology_integrator: OK")
    return True


if __name__ == "__main__":
    self_test()
