from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.application.results.classification import (
    ClassificationResult,
)
from personal_data_governance.domain.entities.observation import Observation


@dataclass(frozen=True, slots=True)
class ClassificationContext:
    classifier_version: str

    def __post_init__(self) -> None:
        if not self.classifier_version.strip():
            raise ValueError(
                "Classifier version must not be empty."
            )


class EvidenceClassifier(Protocol):

    def classify(
        self,
        observation: Observation,
        context: ClassificationContext,
    ) -> ClassificationResult:
        ...
