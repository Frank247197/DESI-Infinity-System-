"""
DESI∞ INFINITY SYSTEM
Disease Biology Engine
Version: 6.2.0
"""

from __future__ import annotations

import logging
import json

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("DESI.DiseaseBiology")


@dataclass
class BiologicalFactor:
    factor_id: str
    name: str
    factor_type: str
    description: str
    biological_role: str
    evidence_references: list[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DiseaseBiologyProfile:
    disease_name: str
    genes: list[BiologicalFactor]
    proteins: list[BiologicalFactor]
    pathways: list[BiologicalFactor]
    cellular_processes: list[BiologicalFactor]
    mechanisms: list[str]
    evidence_quality: str
    generated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


class BiologyEngineError(Exception):
    pass


class DiseaseBiologyEngine:

    def __init__(self):
        self.profiles: dict[str, DiseaseBiologyProfile] = {}
        self.factor_registry: dict[str, BiologicalFactor] = {}

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def validate_text(value: str, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise BiologyEngineError(
                f"{field_name} must contain valid text."
            )

        if len(value) > 10000:
            raise BiologyEngineError(
                f"{field_name} exceeds the permitted length."
            )

        return value.strip()

    @staticmethod
    def validate_confidence(value: float) -> float:
        if not isinstance(value, (int, float)):
            raise BiologyEngineError("Confidence must be numeric.")

        if not 0.0 <= value <= 1.0:
            raise BiologyEngineError(
                "Confidence must be between zero and one."
            )

        return float(value)

    def create_factor(
        self,
        name: str,
        factor_type: str,
        description: str,
        biological_role: str,
        references: list[str] | None = None,
        confidence: float = 0.0
    ) -> BiologicalFactor:

        name = self.validate_text(name, "Factor name")
        factor_type = self.validate_text(factor_type, "Factor type")
        description = self.validate_text(description, "Description")
        biological_role = self.validate_text(
            biological_role,
            "Biological role"
        )

        confidence = self.validate_confidence(confidence)
        references = references or []

        if not isinstance(references, list):
            raise BiologyEngineError("References must be a list.")

        for reference in references:
            self.validate_text(reference, "Reference")

        import uuid

        factor = BiologicalFactor(
            factor_id=str(uuid.uuid4()),
            name=name,
            factor_type=factor_type,
            description=description,
            biological_role=biological_role,
            evidence_references=references,
            confidence=confidence
        )

        self.factor_registry[factor.factor_id] = factor

        logger.info("Registered biological factor: %s", name)

        return factor

    def register_profile(
        self,
        disease_name: str,
        genes: list[BiologicalFactor] | None = None,
        proteins: list[BiologicalFactor] | None = None,
        pathways: list[BiologicalFactor] | None = None,
        cellular_processes: list[BiologicalFactor] | None = None,
        mechanisms: list[str] | None = None,
        evidence_quality: str = "unassessed"
    ) -> DiseaseBiologyProfile:

        disease_name = self.validate_text(
            disease_name,
            "Disease name"
        )

        collections = [
            genes or [],
            proteins or [],
            pathways or [],
            cellular_processes or []
        ]

        for collection in collections:
            if not isinstance(collection, list):
                raise BiologyEngineError("Biological data must be lists.")

            for factor in collection:
                if not isinstance(factor, BiologicalFactor):
                    raise BiologyEngineError(
                        "Invalid biological factor."
                    )

        mechanisms = mechanisms or []

        for mechanism in mechanisms:
            self.validate_text(mechanism, "Mechanism")

        profile = DiseaseBiologyProfile(
            disease_name=disease_name,
            genes=collections[0],
            proteins=collections[1],
            pathways=collections[2],
            cellular_processes=collections[3],
            mechanisms=mechanisms,
            evidence_quality=evidence_quality,
            generated_at=self.timestamp()
        )

        self.profiles[disease_name.lower()] = profile

        logger.info("Biology profile registered: %s", disease_name)

        return profile

    def get_profile(
        self,
        disease_name: str
    ) -> DiseaseBiologyProfile | None:

        return self.profiles.get(disease_name.strip().lower())

    def search_factors(
        self,
        query: str
    ) -> list[BiologicalFactor]:

        query = self.validate_text(query, "Search query").lower()

        return [
            factor
            for factor in self.factor_registry.values()
            if query in factor.name.lower()
            or query in factor.description.lower()
            or query in factor.biological_role.lower()
        ]

    def compare_profiles(
        self,
        first_name: str,
        second_name: str
    ) -> dict[str, Any]:

        first = self.get_profile(first_name)
        second = self.get_profile(second_name)

        if first is None or second is None:
            raise BiologyEngineError("A requested profile is missing.")

        def names(items: list[BiologicalFactor]) -> set[str]:
            return {item.name.lower() for item in items}

        comparison = {}

        for attribute in (
            "genes",
            "proteins",
            "pathways",
            "cellular_processes"
        ):
            first_items = names(getattr(first, attribute))
            second_items = names(getattr(second, attribute))

            comparison[attribute] = {
                "shared": sorted(first_items & second_items),
                "first_only": sorted(first_items - second_items),
                "second_only": sorted(second_items - first_items)
            }

        return comparison

    def profile_statistics(self) -> dict[str, int]:
        return {
            "profiles": len(self.profiles),
            "registered_factors": len(self.factor_registry),
            "genes": sum(
                len(profile.genes)
                for profile in self.profiles.values()
            ),
            "proteins": sum(
                len(profile.proteins)
                for profile in self.profiles.values()
            ),
            "pathways": sum(
                len(profile.pathways)
                for profile in self.profiles.values()
            )
        }

    def export_profile(self, disease_name: str) -> dict[str, Any]:
        profile = self.get_profile(disease_name)

        if profile is None:
            raise BiologyEngineError("Profile not found.")

        return asdict(profile)

    def export_json(self, disease_name: str) -> str:
        return json.dumps(
            self.export_profile(disease_name),
            indent=4,
            ensure_ascii=False
        )

    def system_information(self) -> dict[str, Any]:
        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "statistics": self.profile_statistics(),
            "generated_at": self.timestamp()
        }


def initialize_biology_engine() -> DiseaseBiologyEngine:
    engine = DiseaseBiologyEngine()
    logger.info("Disease Biology Engine initialized: %s", VERSION)
    return engine


if __name__ == "__main__":
    engine = initialize_biology_engine()

    print(json.dumps(
        engine.system_information(),
        indent=4
    ))
