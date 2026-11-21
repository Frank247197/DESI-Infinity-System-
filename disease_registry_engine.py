"""
DESI∞ INFINITY SYSTEM
Disease Registry Engine
Version: 6.2.0

Purpose:
Central registry for structured human disease research.
This module supports scientific information management.
It does not independently diagnose or prescribe treatment.
"""

from __future__ import annotations

import json
import logging
import re
import uuid

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"
DATABASE_FILE = Path("data/disease_registry.json")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("DESI.DiseaseRegistry")


class DiseaseCategory(Enum):
    INFECTIOUS = "infectious"
    GENETIC = "genetic"
    NEUROLOGICAL = "neurological"
    CARDIOVASCULAR = "cardiovascular"
    METABOLIC = "metabolic"
    AUTOIMMUNE = "autoimmune"
    RESPIRATORY = "respiratory"
    CANCER = "cancer"
    OTHER = "other"


class EvidenceLevel(Enum):
    UNKNOWN = "unknown"
    PRELIMINARY = "preliminary"
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    CLINICAL = "clinical"
    REVIEWED = "systematically_reviewed"


@dataclass
class DiseaseRecord:
    disease_id: str
    name: str
    category: str
    description: str
    known_causes: list[str] = field(default_factory=list)
    associated_genes: list[str] = field(default_factory=list)
    associated_pathogens: list[str] = field(default_factory=list)
    biological_pathways: list[str] = field(default_factory=list)
    symptoms_reference: list[str] = field(default_factory=list)
    research_methods: list[str] = field(default_factory=list)
    evidence_level: str = EvidenceLevel.UNKNOWN.value
    references: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class DiseaseRegistryError(Exception):
    """Base exception for registry operations."""


class DiseaseValidationError(DiseaseRegistryError):
    """Raised when a disease record is invalid."""


class DiseaseRegistry:
    def __init__(self, database_path: Path = DATABASE_FILE):
        self.database_path = Path(database_path)
        self.records: dict[str, DiseaseRecord] = {}
        self.load_database()

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def normalize_name(name: str) -> str:
        return re.sub(r"\s+", " ", name.strip()).lower()

    def validate_record(self, record: DiseaseRecord) -> None:
        if not record.name or not record.name.strip():
            raise DiseaseValidationError("Disease name is required.")

        if not record.description.strip():
            raise DiseaseValidationError("Disease description is required.")

        if record.category not in {
            item.value for item in DiseaseCategory
        }:
            raise DiseaseValidationError("Invalid disease category.")

        if record.evidence_level not in {
            item.value for item in EvidenceLevel
        }:
            raise DiseaseValidationError("Invalid evidence level.")

        if len(record.name) > 200:
            raise DiseaseValidationError("Disease name is too long.")

        for item in record.references:
            if not isinstance(item, str) or not item.strip():
                raise DiseaseValidationError("Invalid reference entry.")

    def create_record(
        self,
        name: str,
        category: DiseaseCategory,
        description: str,
        **additional_data: Any
    ) -> DiseaseRecord:

        if not isinstance(category, DiseaseCategory):
            raise DiseaseValidationError("Category must be an enum.")

        now = self.timestamp()

        record = DiseaseRecord(
            disease_id=str(uuid.uuid4()),
            name=name.strip(),
            category=category.value,
            description=description.strip(),
            created_at=now,
            updated_at=now,
            **additional_data
        )

        self.validate_record(record)
        self.add_record(record)

        return record

    def add_record(self, record: DiseaseRecord) -> None:
        self.validate_record(record)

        normalized = self.normalize_name(record.name)

        for existing in self.records.values():
            if self.normalize_name(existing.name) == normalized:
                raise DiseaseRegistryError(
                    f"Disease already exists: {record.name}"
                )

        self.records[record.disease_id] = record
        logger.info("Registered disease: %s", record.name)

    def update_record(
        self,
        disease_id: str,
        updates: dict[str, Any]
    ) -> DiseaseRecord:

        record = self.records.get(disease_id)

        if record is None:
            raise DiseaseRegistryError("Disease record not found.")

        protected = {"disease_id", "created_at"}

        for key, value in updates.items():
            if key in protected:
                raise DiseaseValidationError(
                    f"Cannot modify protected field: {key}"
                )

            if not hasattr(record, key):
                raise DiseaseValidationError(
                    f"Unknown disease field: {key}"
                )

            setattr(record, key, value)

        record.updated_at = self.timestamp()
        self.validate_record(record)

        logger.info("Updated disease: %s", record.name)
        return record

    def remove_record(self, disease_id: str) -> bool:
        if disease_id not in self.records:
            return False

        removed = self.records.pop(disease_id)
        logger.info("Removed registry entry: %s", removed.name)
        return True

    def get_record(self, disease_id: str) -> Optional[DiseaseRecord]:
        return self.records.get(disease_id)

    def search_by_name(self, query: str) -> list[DiseaseRecord]:
        query = self.normalize_name(query)

        if not query:
            return []

        return [
            record for record in self.records.values()
            if query in self.normalize_name(record.name)
        ]

    def filter_by_category(
        self,
        category: DiseaseCategory
    ) -> list[DiseaseRecord]:

        return [
            record for record in self.records.values()
            if record.category == category.value
        ]

    def search_by_gene(self, gene_name: str) -> list[DiseaseRecord]:
        gene_name = gene_name.strip().upper()

        return [
            record for record in self.records.values()
            if gene_name in [
                gene.upper() for gene in record.associated_genes
            ]
        ]

    def search_by_pathogen(self, pathogen: str) -> list[DiseaseRecord]:
        pathogen = pathogen.strip().lower()

        return [
            record for record in self.records.values()
            if any(
                pathogen in item.lower()
                for item in record.associated_pathogens
            )
        ]

    def get_all_records(self) -> list[DiseaseRecord]:
        return list(self.records.values())

    def statistics(self) -> dict[str, Any]:
        category_counts = {}

        for category in DiseaseCategory:
            category_counts[category.value] = len(
                self.filter_by_category(category)
            )

        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "total_records": len(self.records),
            "category_distribution": category_counts,
            "generated_at": self.timestamp()
        }

    def save_database(self) -> None:
        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = [
            asdict(record)
            for record in self.records.values()
        ]

        temporary_file = self.database_path.with_suffix(".tmp")

        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temporary_file.replace(self.database_path)

        logger.info("Disease registry saved successfully.")

    def load_database(self) -> None:
        if not self.database_path.exists():
            logger.info("No existing disease database found.")
            return

        try:
            with self.database_path.open(
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise DiseaseRegistryError(
                    "Database must contain a list."
                )

            for item in data:
                record = DiseaseRecord(**item)
                self.validate_record(record)
                self.records[record.disease_id] = record

            logger.info(
                "Loaded %s disease records.",
                len(self.records)
            )

        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            logger.exception("Database loading failed.")
            raise DiseaseRegistryError(str(error)) from error

    def export_records(self) -> list[dict[str, Any]]:
        return [
            asdict(record)
            for record in self.records.values()
        ]


def initialize_disease_registry() -> DiseaseRegistry:
    registry = DiseaseRegistry()

    logger.info(
        "%s Disease Registry initialized. Version %s",
        SYSTEM_NAME,
        VERSION
    )

    return registry


if __name__ == "__main__":
    disease_registry = initialize_disease_registry()

    print(json.dumps(
        disease_registry.statistics(),
        indent=4
    ))
