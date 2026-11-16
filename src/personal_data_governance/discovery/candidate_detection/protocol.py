from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.application.results.candidate_detection import (
    CandidateDetectionResult,
)
from personal_data_governance.domain.entities.observation import Observation


@dataclass(frozen=True, slots=True)
class CandidateDetectionContext:
    detector_version: str

    def __post_init__(self) -> None:
        if not self.detector_version.strip():
            raise ValueError(
                "Detector version must not be empty."
            )


class ServiceCandidateDetector(Protocol):

    def detect(
        self,
        observation: Observation,
        context: CandidateDetectionContext,
    ) -> CandidateDetectionResult:
        ...
