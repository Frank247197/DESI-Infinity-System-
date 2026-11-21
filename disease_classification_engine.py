"""
DESI∞ INFINITY SYSTEM
Disease Classification Engine
Version: 6.2.0
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


SYSTEM_NAME = "DESI_INFINITY"
VERSION = "6.2.0"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("DESI.Classification")


class DiseaseType(Enum):
    INFECTIOUS = "infectious"
    GENETIC = "genetic"
    NEUROLOGICAL = "neurological"
    CARDIOVASCULAR = "cardiovascular"
    METABOLIC = "metabolic"
    AUTOIMMUNE = "autoimmune"
    RESPIRATORY = "respiratory"
    ONCOLOGICAL = "oncological"
    HEMATOLOGICAL = "hematological"
    DERMATOLOGICAL = "dermatological"
    GASTROINTESTINAL = "gastrointestinal"
    RENAL = "renal"
    OTHER = "other"


class ClassificationStatus(Enum):
    CONFIRMED = "confirmed_by_source"
    PROVISIONAL = "provisional"
    UNCLASSIFIED = "unclassified"
    CONFLICTING = "conflicting_evidence"


@dataclass
class ClassificationResult:
    disease_name: str
    primary_category: str
    secondary_categories: list[str]
    classification_status: str
    supporting_evidence: list[str]
    conflicting_evidence: list[str]
    confidence: float
    source_references: list[str]
    created_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


class ClassificationError(Exception):
    pass


class DiseaseClassifier:

    def __init__(self):
        self.rules = self._load_rules()
        self.results: dict[str, ClassificationResult] = {}

    @staticmethod
    def timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load_rules(self) -> dict[str, list[str]]:
        return {
            "infectious": [
                "virus", "viral", "bacteria", "bacterial",
                "fungus", "fungal", "parasite", "infection"
            ],
            "genetic": [
                "mutation", "inherited", "chromosome",
                "genetic", "gene variant", "hereditary"
            ],
            "neurological": [
                "brain", "neuron", "nervous system",
                "neurodegeneration", "neurological"
            ],
            "cardiovascular": [
                "heart", "artery", "blood vessel",
                "cardiac", "vascular"
            ],
            "metabolic": [
                "metabolism", "glucose", "insulin",
                "metabolic", "hormone"
            ],
            "autoimmune": [
                "autoimmune", "immune attack",
                "immune-mediated", "autoantibody"
            ],
            "respiratory": [
                "lung", "airway", "respiratory",
                "pulmonary", "breathing"
            ],
            "oncological": [
                "cancer", "tumor", "malignant",
                "neoplasm", "oncological"
            ],
            "hematological": [
                "blood disorder", "anemia",
                "hemoglobin", "hematological"
            ],
            "dermatological": [
                "skin disease", "dermatological",
                "epidermis", "dermis"
            ],
            "gastrointestinal": [
                "intestine", "stomach", "digestive",
                "gastrointestinal", "bowel"
            ],
            "renal": [
                "kidney", "renal", "nephron",
                "urinary system"
            ]
        }

    @staticmethod
    def normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def validate_input(
        self,
        disease_name: str,
        description: str
    ) -> None:
        if not isinstance(disease_name, str):
            raise ClassificationError("Disease name must be text.")

        if not isinstance(description, str):
            raise ClassificationError("Description must be text.")

        if not disease_name.strip():
            raise ClassificationError("Disease name is required.")

        if not description.strip():
            raise ClassificationError("Description is required.")

        if len(disease_name) > 200:
            raise ClassificationError("Disease name is too long.")

        if len(description) > 20000:
            raise ClassificationError("Description is too long.")

    def identify_categories(
        self,
        description: str
    ) -> dict[str, list[str]]:

        text = self.normalize(description)
        matches: dict[str, list[str]] = {}

        for category, keywords in self.rules.items():
            found = [
                keyword for keyword in keywords
                if keyword in text
            ]

            if found:
                matches[category] = found

        return matches

    def classify(
        self,
        disease_name: str,
        description: str,
        source_references: list[str] | None = None,
        verified_category: str | None = None
    ) -> ClassificationResult:

        self.validate_input(disease_name, description)

        matches = self.identify_categories(description)
        references = source_references or []

        if any(not isinstance(ref, str) or not ref.strip()
               for ref in references):
            raise ClassificationError("Invalid source reference.")

        if verified_category is not None:
            if verified_category not in {
                item.value for item in DiseaseType
            }:
                raise ClassificationError("Invalid verified category.")

        categories = list(matches.keys())
        supporting = [
            f"{category}: {', '.join(keywords)}"
            for category, keywords in matches.items()
        ]

        conflicts: list[str] = []

        if verified_category:
            primary = verified_category
            status = ClassificationStatus.CONFIRMED
        elif len(categories) == 1:
            primary = categories[0]
            status = ClassificationStatus.PROVISIONAL
        elif len(categories) > 1:
            primary = categories[0]
            status = ClassificationStatus.PROVISIONAL
        else:
            primary = DiseaseType.OTHER.value
            status = ClassificationStatus.UNCLASSIFIED

        confidence = min(
            0.95,
            len(supporting) * 0.15
        )

        if verified_category:
            confidence = 1.0

        result = ClassificationResult(
            disease_name=disease_name.strip(),
            primary_category=primary,
            secondary_categories=[
                item for item in categories
                if item != primary
            ],
            classification_status=status.value,
            supporting_evidence=supporting,
            conflicting_evidence=conflicts,
            confidence=round(confidence, 3),
            source_references=references,
            created_at=self.timestamp()
        )

        self.results[self.normalize(disease_name)] = result

        logger.info(
            "Classification completed for %s",
            disease_name
        )

        return result

    def get_result(
        self,
        disease_name: str
    ) -> ClassificationResult | None:
        return self.results.get(self.normalize(disease_name))

    def list_results(self) -> list[ClassificationResult]:
        return list(self.results.values())

    def export_results(self) -> list[dict[str, Any]]:
        return [
            asdict(result)
            for result in self.results.values()
        ]

    def category_statistics(self) -> dict[str, int]:
        statistics = {
            category.value: 0
            for category in DiseaseType
        }

        for result in self.results.values():
            category = result.primary_category
            statistics[category] = statistics.get(category, 0) + 1

        return statistics

    def system_information(self) -> dict[str, Any]:
        return {
            "system": SYSTEM_NAME,
            "version": VERSION,
            "registered_classifications": len(self.results),
            "available_categories": [
                category.value for category in DiseaseType
            ],
            "generated_at": self.timestamp()
        }


def initialize_classifier() -> DiseaseClassifier:
    classifier = DiseaseClassifier()
    logger.info("DESI∞ classifier initialized: %s", VERSION)
    return classifier


if __name__ == "__main__":
    engine = initialize_classifier()

    sample = engine.classify(
        disease_name="Example Research Condition",
        description="A neurological condition involving brain cells.",
        source_references=["RESEARCH-REFERENCE-001"]
    )

    print(asdict(sample))
    print(engine.system_information())
