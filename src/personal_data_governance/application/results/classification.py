from dataclasses import dataclass

from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.processing import (
    ClassificationMethod,
    ClassificationStatus,
    ProcessingStatus,
)
from personal_data_governance.domain.values.identifiers import ObservationId


@dataclass(frozen=True, slots=True)
class EvidenceCandidate:
    evidence_type: EvidenceType
    observation_ids: tuple[ObservationId, ...]
    method: ClassificationMethod
    reason_codes: tuple[str, ...]
    classifier_version: str

    def __post_init__(self) -> None:
        if not self.observation_ids:
            raise ValueError(
                "EvidenceCandidate requires at least "
                "one Observation."
            )

        if not self.classifier_version.strip():
            raise ValueError(
                "Classifier version must not be empty."
            )

        if not self.reason_codes:
            raise ValueError(
                "EvidenceCandidate requires at least "
                "one reason code."
            )


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    observation_id: ObservationId
    processing_status: ProcessingStatus
    classification_status: ClassificationStatus | None
    evidence_candidates: tuple[EvidenceCandidate, ...]
    method: ClassificationMethod | None
    reason_codes: tuple[str, ...]
    classifier_version: str

    def __post_init__(self) -> None:
        if not self.classifier_version.strip():
            raise ValueError(
                "Classifier version must not be empty."
            )

        if (
            self.processing_status == ProcessingStatus.SUCCESS
            and self.classification_status is None
        ):
            raise ValueError(
                "Successful classification requires "
                "a classification status."
            )

        if (
            self.processing_status != ProcessingStatus.SUCCESS
            and self.classification_status is not None
        ):
            raise ValueError(
                "A failed or unsupported classification "
                "must not contain ClassificationStatus."
            )

        if (
            self.processing_status == ProcessingStatus.SUCCESS
            and self.method is None
        ):
            raise ValueError(
                "Successful classification requires "
                "ClassificationMethod."
            )

        if (
            self.classification_status
            == ClassificationStatus.CLASSIFIED
            and not self.evidence_candidates
        ):
            raise ValueError(
                "CLASSIFIED requires at least one "
                "EvidenceCandidate."
            )

        if (
            self.classification_status
            == ClassificationStatus.UNKNOWN
            and self.evidence_candidates
        ):
            raise ValueError(
                "UNKNOWN must not contain "
                "EvidenceCandidates."
            )

        if (
            self.processing_status != ProcessingStatus.SUCCESS
            and self.evidence_candidates
        ):
            raise ValueError(
                "A failed or unsupported classification "
                "must not contain EvidenceCandidates."
            )
