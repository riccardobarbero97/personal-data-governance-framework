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
    candidate_status: CandidateStatus
