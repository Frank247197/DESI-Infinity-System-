"""
DESI∞ INFINITY SYSTEM
Disease Gene Association Engine
Version: 6.2.0
"""

from __future__ import annotations

import logging
import json
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

logger = logging.getLogger("DESI.GeneAssociation")


@dataclass
class GeneAssociation:
    association_id: str
    disease_name: str
    gene_symbol: str
    gene_identifier: str
    association_type: str
    biological_relationship: str
    evidence_sources: list[str]
    evidence_level: str
    confidence: float
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


class GeneAssociationError(Exception):
    pass


class DiseaseGeneAssociationEngine:

    VALID_ASSOCIATIONS = {
        "causal",
        "risk_factor",
        "protective",
        "modifier",
        "correlated",
        "unknown"
    }

    VALID_EVIDENCE = {
        "unknown",
        "computational",
        "experimental",
        "observational",
        "clinical",
        "curated"
    }

    def __init__(self):
        self.associations: dict[str, GeneAssociation] = {}

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def clean(value: str, label: str) -> str:
        if not isinstance(value, str):
            raise GeneAssociationError(f"{label} must be text.")

        value = value.strip()

        if not value:
            raise GeneAssociationError(f"{label} is required.")

        if len(value) > 5000:
            raise GeneAssociationError(f"{label} is too long.")

        return value

    @staticmethod
    def validate_confidence(confidence: float) -> float:
        if not isinstance(confidence, (int, float)):
            raise GeneAssociationError("Confidence must be numeric.")

        if not 0 <= confidence <= 1:
            raise GeneAssociationError("Invalid confidence value.")

        return float(confidence)

    def register_association(
        self,
        disease_name: str,
        gene_symbol: str,
        gene_identifier: str,
        association_type: str,
        biological_relationship: str,
        evidence_sources: list[str],
        evidence_level: str,
        confidence: float,
        metadata: dict[str, Any] | None = None
    ) -> GeneAssociation:

        disease_name = self.clean(disease_name, "Disease name")
        gene_symbol = self.clean(gene_symbol, "Gene symbol").upper()
        gene_identifier = self.clean(
            gene_identifier,
            "Gene identifier"
        )

        association_type = self.clean(
            association_type,
            "Association type"
        ).lower()

        evidence_level = self.clean(
            evidence_level,
            "Evidence level"
        ).lower()

        relationship = self.clean(
            biological_relationship,
            "Biological relationship"
        )

        if association_type not in self.VALID_ASSOCIATIONS:
            raise GeneAssociationError("Unsupported association type.")

        if evidence_level not in self.VALID_EVIDENCE:
            raise GeneAssociationError("Unsupported evidence level.")

        if not isinstance(evidence_sources, list):
            raise GeneAssociationError("Evidence sources must be a list.")

        sources = [
            self.clean(source, "Evidence source")
            for source in evidence_sources
        ]

        confidence = self.validate_confidence(confidence)

        association = GeneAssociation(
            association_id=str(uuid.uuid4()),
            disease_name=disease_name,
            gene_symbol=gene_symbol,
            gene_identifier=gene_identifier,
            association_type=association_type,
            biological_relationship=relationship,
            evidence_sources=sources,
            evidence_level=evidence_level,
            confidence=confidence,
            created_at=self.timestamp(),
            metadata=metadata or {}
        )

        self.associations[association.association_id] = association

        logger.info(
            "Gene association registered: %s / %s",
            disease_name,
            gene_symbol
        )

        return association

    def search_by_disease(
        self,
        disease_name: str
    ) -> list[GeneAssociation]:

        query = self.clean(disease_name, "Disease name").lower()

        return [
            item for item in self.associations.values()
            if item.disease_name.lower() == query
        ]

    def search_by_gene(
        self,
        gene_symbol: str
    ) -> list[GeneAssociation]:

        query = self.clean(gene_symbol, "Gene symbol").upper()

        return [
            item for item in self.associations.values()
            if item.gene_symbol == query
        ]

    def search_by_identifier(
        self,
        gene_identifier: str
    ) -> list[GeneAssociation]:

        query = self.clean(
            gene_identifier,
            "Gene identifier"
        ).lower()

        return [
            item for item in self.associations.values()
            if item.gene_identifier.lower() == query
        ]

    def filter_by_evidence(
        self,
        evidence_level: str
    ) -> list[GeneAssociation]:

        evidence_level = self.clean(
            evidence_level,
            "Evidence level"
        ).lower()

        if evidence_level not in self.VALID_EVIDENCE:
            raise GeneAssociationError("Invalid evidence level.")

        return [
            item for item in self.associations.values()
            if item.evidence_level == evidence_level
        ]

    def compare_disease_genes(
        self,
        first_disease: str,
        second_disease: str
    ) -> dict[str, list[str]]:

        first = {
            item.gene_symbol
            for item in self.search_by_disease(first_disease)
        }

        second = {
            item.gene_symbol
            for item in self.search_by_disease(second_disease)
        }

        return {
            "shared_genes": sorted(first & second),
            "first_disease_only": sorted(first - second),
            "second_disease_only": sorted(second - first)
        }

    def remove_association(self, association_id: str) -> bool:
        return self.associations.pop(association_id, None) is not None

    def get_association(
        self,
        association_id: str
    ) -> GeneAssociation | None:

        return self.associations.get(association_id)

    def statistics(self) -> dict[str, Any]:
        disease_count = len({
            item.disease_name.lower()
            for item in self.associations.values()
        })

        gene_count = len({
            item.gene_symbol
            for item in self.associations.values()
        })

        evidence_distribution = {
            evidence: 0
            for evidence in self.VALID_EVIDENCE
        }

        for item in self.associations.values():
            evidence_distribution[item.evidence_level] += 1

        return {
            "total_associations": len(self.associations),
            "unique_diseases": disease_count,
            "unique_genes": gene_count,
            "evidence_distribution": evidence_distribution
        }

    def export_records(self) -> list[dict[str, Any]]:
        return [
            asdict(item)
            for item in self.associations.values()
        ]

    def export_json(self) -> str:
        return json.dumps(
            self.export_records(),
            indent=4,
            ensure_ascii=False
        )

    def system_information(self) -> dict[str, Any]:
        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "statistics": self.statistics(),
            "generated_at": self.timestamp()
        }


def initialize_gene_association_engine():
    engine = DiseaseGeneAssociationEngine()
    logger.info("Gene Association Engine initialized: %s", VERSION)
    return engine


if __name__ == "__main__":
    engine = initialize_gene_association_engine()

    print(json.dumps(
        engine.system_information(),
        indent=4
    ))
