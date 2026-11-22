"""DESI Infinity System - Disease Intelligence Orchestrator (v6.2.0).

Top-level orchestrator that composes the Disease Intelligence subsystem.
Registers available engines, tracks their versions, exposes a consistent
`execute()` dispatch interface, and performs subsystem health checks.

The orchestrator NEVER diagnoses, prescribes, or guarantees outcomes.
It is a research coordination layer.
"""
from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
logger = logging.getLogger(__name__)


class OrchestratorError(Exception):
    """Base orchestrator error."""


# Registry of expected modules. The orchestrator attempts to import each
# and records whether it is present. Missing modules are reported, not
# fabricated.
EXPECTED_MODULES: List[str] = [
    "disease_registry_engine",
    "disease_classification_engine",
    "disease_biology_engine",
    "disease_gene_association_engine",
    "disease_pathway_engine",
    "disease_protein_association_engine",
    "disease_ontology_engine",
    "disease_database_connector",
    "disease_symptom_analyzer",
    "disease_risk_factor_engine",
    "disease_prevalence_analyzer",
    "disease_incidence_tracker",
    "disease_epidemiology_engine",
    "disease_progression_model",
    "disease_severity_analyzer",
    "disease_subtype_classifier",
    "rare_disease_analyzer",
    "genetic_disorder_engine",
    "infectious_disease_engine",
    "autoimmune_disease_engine",
    "metabolic_disease_engine",
    "cardiovascular_disease_engine",
    "neurological_disease_engine",
    "respiratory_disease_engine",
    "gastrointestinal_disease_engine",
    "endocrine_disease_engine",
    "renal_disease_engine",
    "musculoskeletal_disease_engine",
    "dermatological_disease_engine",
    "hematological_disease_engine",
    "reproductive_disease_engine",
    "pediatric_disease_engine",
    "cancer_intelligence_engine",
    "tumor_biology_analyzer",
    "cancer_genomics_engine",
    "cancer_mutation_analyzer",
    "cancer_pathway_analyzer",
    "tumor_microenvironment_engine",
    "metastasis_research_engine",
    "pathogen_registry_engine",
    "virus_intelligence_engine",
    "viral_genome_analyzer",
    "viral_sequence_analyzer",
    "bacterial_genome_analyzer",
    "fungal_pathogen_analyzer",
    "parasite_intelligence_engine",
    "pathogen_mutation_tracker",
    "pathogen_evolution_engine",
    "pathogen_host_interaction",
    "host_pathogen_response_engine",
    "immune_system_analyzer",
    "immune_cell_intelligence",
    "antibody_research_engine",
    "cytokine_network_analyzer",
    "inflammation_pathway_engine",
    "autoimmune_mechanism_analyzer",
    "human_genome_analyzer",
    "genome_sequence_processor",
    "genomic_variant_analyzer",
    "variant_pathogenicity_engine",
    "mutation_effect_predictor",
    "genome_annotation_engine",
    "gene_function_analyzer",
    "gene_regulation_engine",
    "gene_expression_analyzer",
    "transcriptomics_engine",
    "epigenetics_analyzer",
    "epigenomic_data_engine",
    "hereditary_disease_analyzer",
    "population_genomics_engine",
    "pharmacogenomics_analyzer",
    "proteomics_engine",
    "protein_structure_analyzer",
    "protein_function_predictor",
    "protein_interaction_network",
    "protein_pathogenicity_engine",
    "molecular_biology_engine",
    "molecular_interaction_analyzer",
    "molecular_docking_research",
    "molecular_dynamics_analyzer",
    "cellular_mechanism_engine",
    "cell_signaling_analyzer",
    "cell_cycle_research_engine",
    "apoptosis_mechanism_analyzer",
    "autophagy_research_engine",
    "stem_cell_research_engine",
    "tissue_pathology_analyzer",
    "organ_pathology_engine",
    "disease_biomarker_engine",
    "biomarker_discovery_analyzer",
    "diagnostic_biomarker_validator",
    "laboratory_research_analyzer",
    "medical_imaging_research_engine",
    "histopathology_image_analyzer",
    "clinical_research_database",
    "scientific_literature_engine",
    "biomedical_publication_search",
    "research_evidence_extractor",
    "scientific_evidence_grader",
    "clinical_trial_research_analyzer",
    "treatment_research_registry",
    "therapeutic_strategy_analyzer",
    "drug_mechanism_analyzer",
    "drug_target_discovery_engine",
    "drug_repurposing_research",
    "drug_resistance_analyzer",
    "therapeutic_pathway_comparator",
    "treatment_evidence_comparator",
    "combination_therapy_research",
    "personalized_medicine_engine",
    "precision_medicine_analyzer",
    "disease_modeling_engine",
    "disease_simulation_engine",
    "biological_network_analyzer",
    "systems_biology_integrator",
    "disease_gene_network_engine",
    "disease_protein_network_engine",
    "disease_pathway_integrator",
    "disease_knowledge_graph",
]


@dataclass
class ModuleRecord:
    name: str
    loaded: bool
    version: str = ""
    error: str = ""


class DiseaseIntelligenceOrchestrator:
    """Composes Disease Intelligence modules with consistent interfaces."""

    VERSION = VERSION
    SYSTEM = SYSTEM_NAME

    def __init__(self) -> None:
        self._modules: Dict[str, ModuleRecord] = {}

    def discover(self, strict_version: bool = True) -> Dict[str, int]:
        summary = {"loaded": 0, "missing": 0, "version_mismatch": 0}
        for name in EXPECTED_MODULES:
            try:
                module = importlib.import_module(name)
                version = getattr(module, "VERSION", "")
                mismatch = strict_version and version and version != VERSION
                self._modules[name] = ModuleRecord(
                    name=name, loaded=True, version=version,
                    error="version_mismatch" if mismatch else "")
                summary["loaded"] += 1
                if mismatch:
                    summary["version_mismatch"] += 1
            except Exception as exc:  # missing or import error
                self._modules[name] = ModuleRecord(
                    name=name, loaded=False, error=str(exc))
                summary["missing"] += 1
        return summary

    def execute(self, module_name: str, function_name: str,
                *args: Any, **kwargs: Any) -> Any:
        if module_name not in self._modules:
            raise OrchestratorError(
                f"module {module_name!r} not discovered; call discover() first")
        record = self._modules[module_name]
        if not record.loaded:
            raise OrchestratorError(
                f"module {module_name!r} unavailable: {record.error}")
        module = importlib.import_module(module_name)
        fn: Optional[Callable[..., Any]] = getattr(module, function_name, None)
        if fn is None:
            raise OrchestratorError(
                f"function {function_name!r} not found in {module_name!r}")
        return fn(*args, **kwargs)

    def run_self_tests(self) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for name, record in self._modules.items():
            if not record.loaded:
                results[name] = "skipped (module not loaded)"
                continue
            module = importlib.import_module(name)
            fn = getattr(module, "self_test", None)
            if not callable(fn):
                results[name] = "no self_test"
                continue
            try:
                ok = fn()
                results[name] = "ok" if ok else "failed"
            except Exception as exc:
                results[name] = f"error: {exc}"
        return results

    def health(self) -> Dict[str, Any]:
        loaded = [r for r in self._modules.values() if r.loaded]
        missing = [r for r in self._modules.values() if not r.loaded]
        mismatched = [r for r in loaded if r.error == "version_mismatch"]
        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "expected_modules": len(EXPECTED_MODULES),
            "loaded": len(loaded),
            "missing": len(missing),
            "version_mismatch": len(mismatched),
            "missing_modules": [r.name for r in missing],
            "mismatched_modules": [r.name for r in mismatched],
        }

    def module_record(self, module_name: str) -> ModuleRecord:
        try:
            return self._modules[module_name]
        except KeyError as exc:
            raise OrchestratorError(f"unknown module: {module_name}") from exc


def self_test() -> bool:
    orch = DiseaseIntelligenceOrchestrator()
    assert orch.VERSION == VERSION
    assert orch.SYSTEM == SYSTEM_NAME
    assert len(EXPECTED_MODULES) == 114
    # Not all modules may be importable in isolation; only check structure.
    assert "disease_knowledge_graph" in EXPECTED_MODULES
    assert "disease_intelligence_orchestrator" not in EXPECTED_MODULES
    # Health before discover()
    assert orch.health()["loaded"] == 0
    record = ModuleRecord(name="disease_knowledge_graph", loaded=True,
                          version=VERSION)
    assert record.loaded is True
    print("disease_intelligence_orchestrator: OK")
    return True


if __name__ == "__main__":
    self_test()
