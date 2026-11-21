"""
DESI∞ INFINITY SYSTEM
Disease Protein Association Engine
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

logger = logging.getLogger("DESI.ProteinAssociation")


class ProteinAssociationError(Exception):
    pass


@dataclass
class ProteinRecord:
    protein_id: str
    protein_name: str
    accession_id: str
    organism: str
    protein_function: str
    associated_genes: list[str]
    associated_diseases: list[str]
    cellular_locations: list[str]
    evidence_references: list[str]
    evidence_level: str
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProteinComparison:
    first_protein: str
    second_protein: str
    shared_genes: list[str]
    shared_diseases: list[str]
    shared_locations: list[str]
    generated_at: str


class DiseaseProteinAssociationEngine:

    EVIDENCE_LEVELS = {
        "unassessed",
        "computational",
        "experimental",
        "observational",
        "clinical",
        "curated"
    }

    def __init__(self):
        self.proteins: dict[str, ProteinRecord] = {}

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def validate_text(value: str, field_name: str) -> str:
        if not isinstance(value, str):
            raise ProteinAssociationError(
                f"{field_name} must be text."
            )

        value = value.strip()

        if not value:
            raise ProteinAssociationError(
                f"{field_name} is required."
            )

        if len(value) > 10000:
            raise ProteinAssociationError(
                f"{field_name} is too long."
            )

        return value

    def validate_list(
        self,
        values: list[str],
        field_name: str
    ) -> list[str]:

        if not isinstance(values, list):
            raise ProteinAssociationError(
                f"{field_name} must be a list."
            )

        cleaned = []

        for value in values:
            cleaned.append(
                self.validate_text(value, field_name)
            )

        return sorted(set(cleaned), key=str.lower)

    def register_protein(
        self,
        protein_name: str,
        accession_id: str,
        organism: str,
        protein_function: str,
        associated_genes: list[str] | None = None,
        associated_diseases: list[str] | None = None,
        cellular_locations: list[str] | None = None,
        evidence_references: list[str] | None = None,
        evidence_level: str = "unassessed",
        metadata: dict[str, Any] | None = None
    ) -> ProteinRecord:

        protein_name = self.validate_text(
            protein_name, "Protein name"
        )

        accession_id = self.validate_text(
            accession_id, "Accession identifier"
        )

        organism = self.validate_text(organism, "Organism")

        protein_function = self.validate_text(
            protein_function, "Protein function"
        )

        evidence_level = self.validate_text(
            evidence_level, "Evidence level"
        ).lower()

        if evidence_level not in self.EVIDENCE_LEVELS:
            raise ProteinAssociationError(
                "Unsupported evidence level."
            )

        genes = self.validate_list(
            associated_genes or [], "Gene"
        )

        diseases = self.validate_list(
            associated_diseases or [], "Disease"
        )

        locations = self.validate_list(
            cellular_locations or [], "Cellular location"
        )

        references = self.validate_list(
            evidence_references or [], "Reference"
        )

        if self.search_by_accession(accession_id):
            raise ProteinAssociationError(
                "Accession identifier already registered."
            )

        record = ProteinRecord(
            protein_id=str(uuid.uuid4()),
            protein_name=protein_name,
            accession_id=accession_id,
            organism=organism,
            protein_function=protein_function,
            associated_genes=genes,
            associated_diseases=diseases,
            cellular_locations=locations,
            evidence_references=references,
            evidence_level=evidence_level,
            created_at=self.timestamp(),
            metadata=metadata or {}
        )

        self.proteins[record.protein_id] = record

        logger.info("Registered protein: %s", protein_name)

        return record

    def get_protein(
        self,
        protein_id: str
    ) -> ProteinRecord | None:

        return self.proteins.get(protein_id)

    def search_by_name(
        self,
        protein_name: str
    ) -> list[ProteinRecord]:

        query = self.validate_text(
            protein_name, "Protein name"
        ).lower()

        return [
            record for record in self.proteins.values()
            if query in record.protein_name.lower()
        ]

    def search_by_accession(
        self,
        accession_id: str
    ) -> list[ProteinRecord]:

        query = self.validate_text(
            accession_id, "Accession identifier"
        ).lower()

        return [
            record for record in self.proteins.values()
            if record.accession_id.lower() == query
        ]

    def search_by_gene(
        self,
        gene_symbol: str
    ) -> list[ProteinRecord]:

        query = self.validate_text(
            gene_symbol, "Gene symbol"
        ).upper()

        return [
            record for record in self.proteins.values()
            if query in [
                gene.upper()
                for gene in record.associated_genes
            ]
        ]

    def search_by_disease(
        self,
        disease_name: str
    ) -> list[ProteinRecord]:

        query = self.validate_text(
            disease_name, "Disease name"
        ).lower()

        return [
            record for record in self.proteins.values()
            if any(
                query in disease.lower()
                for disease in record.associated_diseases
            )
        ]

    def search_by_location(
        self,
        location: str
    ) -> list[ProteinRecord]:

        query = self.validate_text(
            location, "Cellular location"
        ).lower()

        return [
            record for record in self.proteins.values()
            if any(
                query in item.lower()
                for item in record.cellular_locations
            )
        ]

    def compare_proteins(
        self,
        first_id: str,
        second_id: str
    ) -> ProteinComparison:

        first = self.get_protein(first_id)
        second = self.get_protein(second_id)

        if first is None or second is None:
            raise ProteinAssociationError(
                "Protein record not found."
            )

        return ProteinComparison(
            first_protein=first.protein_name,
            second_protein=second.protein_name,
            shared_genes=sorted(
                set(first.associated_genes)
                & set(second.associated_genes)
            ),
            shared_diseases=sorted(
                set(first.associated_diseases)
                & set(second.associated_diseases)
            ),
            shared_locations=sorted(
                set(first.cellular_locations)
                & set(second.cellular_locations)
            ),
            generated_at=self.timestamp()
        )

    def update_protein(
        self,
        protein_id: str,
        updates: dict[str, Any]
    ) -> ProteinRecord:

        record = self.get_protein(protein_id)

        if record is None:
            raise ProteinAssociationError("Protein not found.")

        allowed = {
            "protein_function",
            "associated_genes",
            "associated_diseases",
            "cellular_locations",
            "evidence_references",
            "evidence_level",
            "metadata"
        }

        for key, value in updates.items():
            if key not in allowed:
                raise ProteinAssociationError(
                    f"Field cannot be updated: {key}"
                )

            if key in {
                "associated_genes",
                "associated_diseases",
                "cellular_locations",
                "evidence_references"
            }:
                value = self.validate_list(value, key)

            if key == "evidence_level":
                if value not in self.EVIDENCE_LEVELS:
                    raise ProteinAssociationError(
                        "Invalid evidence level."
                    )

            setattr(record, key, value)

        logger.info("Updated protein: %s", record.protein_name)

        return record

    def remove_protein(self, protein_id: str) -> bool:
        return self.proteins.pop(protein_id, None) is not None

    def statistics(self) -> dict[str, Any]:
        disease_count = len({
            disease
            for record in self.proteins.values()
            for disease in record.associated_diseases
        })

        gene_count = len({
            gene
            for record in self.proteins.values()
            for gene in record.associated_genes
        })

        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "registered_proteins": len(self.proteins),
            "associated_diseases": disease_count,
            "associated_genes": gene_count
        }

    def export_records(self) -> list[dict[str, Any]]:
        return [
            asdict(record)
            for record in self.proteins.values()
        ]

    def export_json(self) -> str:
        return json.dumps(
            self.export_records(),
            indent=4,
            ensure_ascii=False
        )


def initialize_protein_engine():
    logger.info("Protein Association Engine initialized: %s", VERSION)
    return DiseaseProteinAssociationEngine()


if __name__ == "__main__":
    engine = initialize_protein_engine()
    print(json.dumps(engine.statistics(), indent=4))
