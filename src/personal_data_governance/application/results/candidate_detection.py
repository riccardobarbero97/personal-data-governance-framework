from dataclasses import dataclass

from personal_data_governance.application.values.candidate_identifier import (
    CandidateIdentifier,
)
from personal_data_governance.domain.enums.processing import (
    CandidateStatus,
    DetectionMethod,
    ProcessingStatus,
)
from personal_data_governance.domain.values.identifiers import ObservationId


@dataclass(frozen=True, slots=True)
class CandidateDetectionResult:
    observation_id: ObservationId
    processing_status: ProcessingStatus
    candidate_status: CandidateStatus | None
    candidate_identifiers: tuple[CandidateIdentifier, ...]
    reason_codes: tuple[str, ...]
    method: DetectionMethod
    detector_version: str

    def __post_init__(self) -> None:
        if not self.detector_version.strip():
            raise ValueError(
                "Detector version must not be empty."
            )

        if (
            self.processing_status == ProcessingStatus.SUCCESS
            and self.candidate_status is None
        ):
            raise ValueError(
                "Successful candidate detection requires "
                "a candidate status."
            )

        if (
            self.candidate_status == CandidateStatus.CANDIDATE
            and not self.candidate_identifiers
        ):
            raise ValueError(
                "CANDIDATE requires at least one "
                "CandidateIdentifier."
            )

        if (
            self.candidate_status == CandidateStatus.NOT_CANDIDATE
            and self.candidate_identifiers
        ):
            raise ValueError(
                "NOT_CANDIDATE must not contain "
                "CandidateIdentifiers."
            )
