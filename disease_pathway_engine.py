"""
DESI∞ INFINITY SYSTEM
Disease Pathway Engine
Version: 6.2.0
"""

from __future__ import annotations

import json
import logging
import uuid

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("DESI.Pathways")


class PathwayError(Exception):
    pass


@dataclass
class PathwayRecord:
    pathway_id: str
    pathway_name: str
    organism: str
    biological_process: str
    participating_genes: list[str]
    participating_proteins: list[str]
    associated_diseases: list[str]
    evidence_references: list[str]
    evidence_level: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PathwayComparison:
    first_pathway: str
    second_pathway: str
    shared_genes: list[str]
    unique_first_genes: list[str]
    unique_second_genes: list[str]
    shared_proteins: list[str]
    generated_at: str


class DiseasePathwayEngine:

    VALID_EVIDENCE = {
        "unassessed",
        "computational",
        "experimental",
        "observational",
        "clinical",
        "curated"
    }

    def __init__(self):
        self.pathways: dict[str, PathwayRecord] = {}

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def validate_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise PathwayError(f"{field_name} must be text.")

        cleaned = value.strip()

        if not cleaned:
            raise PathwayError(f"{field_name} is required.")

        if len(cleaned) > 10000:
            raise PathwayError(f"{field_name} is too long.")

        return cleaned

    def validate_list(
        self,
        values: list[str],
        field_name: str
    ) -> list[str]:

        if not isinstance(values, list):
            raise PathwayError(f"{field_name} must be a list.")

        result = []

        for value in values:
            cleaned = self.validate_text(value, field_name)
            result.append(cleaned)

        return sorted(set(result), key=str.lower)

    def register_pathway(
        self,
        pathway_name: str,
        organism: str,
        biological_process: str,
        participating_genes: list[str] | None = None,
        participating_proteins: list[str] | None = None,
        associated_diseases: list[str] | None = None,
        evidence_references: list[str] | None = None,
        evidence_level: str = "unassessed",
        metadata: dict[str, Any] | None = None
    ) -> PathwayRecord:

        pathway_name = self.validate_text(
            pathway_name, "Pathway name"
        )

        organism = self.validate_text(organism, "Organism")
        biological_process = self.validate_text(
            biological_process, "Biological process"
        )

        evidence_level = self.validate_text(
            evidence_level, "Evidence level"
        ).lower()

        if evidence_level not in self.VALID_EVIDENCE:
            raise PathwayError("Unsupported evidence level.")

        genes = self.validate_list(
            participating_genes or [], "Gene"
        )

        proteins = self.validate_list(
            participating_proteins or [], "Protein"
        )

        diseases = self.validate_list(
            associated_diseases or [], "Disease"
        )

        references = self.validate_list(
            evidence_references or [], "Reference"
        )

        existing = self.search_pathway(pathway_name)

        if existing:
            raise PathwayError("Pathway already registered.")

        record = PathwayRecord(
            pathway_id=str(uuid.uuid4()),
            pathway_name=pathway_name,
            organism=organism,
            biological_process=biological_process,
            participating_genes=genes,
            participating_proteins=proteins,
            associated_diseases=diseases,
            evidence_references=references,
            evidence_level=evidence_level,
            created_at=self.timestamp(),
            metadata=metadata or {}
        )

        self.pathways[record.pathway_id] = record

        logger.info("Registered pathway: %s", pathway_name)

        return record

    def get_pathway(
        self,
        pathway_id: str
    ) -> PathwayRecord | None:

        return self.pathways.get(pathway_id)

    def search_pathway(
        self,
        pathway_name: str
    ) -> list[PathwayRecord]:

        query = self.validate_text(
            pathway_name, "Pathway search"
        ).lower()

        return [
            record
            for record in self.pathways.values()
            if query in record.pathway_name.lower()
        ]

    def search_by_gene(
        self,
        gene_symbol: str
    ) -> list[PathwayRecord]:

        query = self.validate_text(
            gene_symbol, "Gene symbol"
        ).upper()

        return [
            record
            for record in self.pathways.values()
            if query in [
                gene.upper()
                for gene in record.participating_genes
            ]
        ]

    def search_by_protein(
        self,
        protein_name: str
    ) -> list[PathwayRecord]:

        query = self.validate_text(
            protein_name, "Protein name"
        ).lower()

        return [
            record
            for record in self.pathways.values()
            if any(
                query in protein.lower()
                for protein in record.participating_proteins
            )
        ]

    def search_by_disease(
        self,
        disease_name: str
    ) -> list[PathwayRecord]:

        query = self.validate_text(
            disease_name, "Disease name"
        ).lower()

        return [
            record
            for record in self.pathways.values()
            if any(
                query in disease.lower()
                for disease in record.associated_diseases
            )
        ]

    def compare_pathways(
        self,
        first_id: str,
        second_id: str
    ) -> PathwayComparison:

        first = self.get_pathway(first_id)
        second = self.get_pathway(second_id)

        if first is None or second is None:
            raise PathwayError("Pathway record not found.")

        first_genes = {
            gene.upper() for gene in first.participating_genes
        }

        second_genes = {
            gene.upper() for gene in second.participating_genes
        }

        first_proteins = {
            protein.lower()
            for protein in first.participating_proteins
        }

        second_proteins = {
            protein.lower()
            for protein in second.participating_proteins
        }

        return PathwayComparison(
            first_pathway=first.pathway_name,
            second_pathway=second.pathway_name,
            shared_genes=sorted(first_genes & second_genes),
            unique_first_genes=sorted(first_genes - second_genes),
            unique_second_genes=sorted(second_genes - first_genes),
            shared_proteins=sorted(first_proteins & second_proteins),
            generated_at=self.timestamp()
        )

    def update_pathway(
        self,
        pathway_id: str,
        updates: dict[str, Any]
    ) -> PathwayRecord:

        record = self.get_pathway(pathway_id)

        if record is None:
            raise PathwayError("Pathway not found.")

        allowed = {
            "biological_process",
            "participating_genes",
            "participating_proteins",
            "associated_diseases",
            "evidence_references",
            "evidence_level",
            "metadata"
        }

        for key, value in updates.items():
            if key not in allowed:
                raise PathwayError(f"Field cannot be updated: {key}")

            if key in {
                "participating_genes",
                "participating_proteins",
                "associated_diseases",
                "evidence_references"
            }:
                value = self.validate_list(value, key)

            if key == "evidence_level":
                if value not in self.VALID_EVIDENCE:
                    raise PathwayError("Invalid evidence level.")

            setattr(record, key, value)

        logger.info("Updated pathway: %s", record.pathway_name)

        return record

    def remove_pathway(self, pathway_id: str) -> bool:
        return self.pathways.pop(pathway_id, None) is not None

    def statistics(self) -> dict[str, Any]:
        evidence_counts = {
            level: 0 for level in self.VALID_EVIDENCE
        }

        for record in self.pathways.values():
            evidence_counts[record.evidence_level] += 1

        return {
            "version": VERSION,
            "total_pathways": len(self.pathways),
            "evidence_distribution": evidence_counts
        }

    def export_records(self) -> list[dict[str, Any]]:
        return [
            asdict(record)
            for record in self.pathways.values()
        ]

    def export_json(self) -> str:
        return json.dumps(
            self.export_records(),
            indent=4,
            ensure_ascii=False
        )


def initialize_pathway_engine() -> DiseasePathwayEngine:
    logger.info("DESI∞ Pathway Engine initialized: %s", VERSION)
    return DiseasePathwayEngine()


if __name__ == "__main__":
    engine = initialize_pathway_engine()
    print(json.dumps(engine.statistics(), indent=4))
