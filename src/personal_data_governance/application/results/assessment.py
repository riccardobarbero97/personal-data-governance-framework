from dataclasses import dataclass

from personal_data_governance.domain.enums.processing import (
    AssessmentMethod,
    ProcessingStatus,
)
from personal_data_governance.domain.enums.relationship import (
    RelationshipStatus,
    TemporalStatus,
)
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    IdentitySeedId,
    ServiceId,
)


@dataclass(frozen=True, slots=True)
class RelationshipAssessmentResult:
    processing_status: ProcessingStatus
    service_id: ServiceId | None
    relationship_status: RelationshipStatus | None
    temporal_status: TemporalStatus | None
    identity_seed_ids: tuple[IdentitySeedId, ...]
    evidence_ids: tuple[EvidenceId, ...]
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    method: AssessmentMethod | None
    assessor_version: str
    assessment_policy_version: str

    def __post_init__(self) -> None:
        if not self.assessor_version.strip():
            raise ValueError(
                "Assessor version must not be empty."
            )

        if not self.assessment_policy_version.strip():
            raise ValueError(
                "Assessment policy version "
                "must not be empty."
            )

        if self.processing_status == ProcessingStatus.SUCCESS:
            if self.relationship_status is None:
                raise ValueError(
                    "Successful assessment requires "
                    "RelationshipStatus."
                )

            if self.temporal_status is None:
                raise ValueError(
                    "Successful assessment requires "
                    "TemporalStatus."
                )

            if self.method is None:
                raise ValueError(
                    "Successful assessment requires "
                    "AssessmentMethod."
                )

        if (
            self.processing_status != ProcessingStatus.SUCCESS
            and self.relationship_status is not None
        ):
            raise ValueError(
                "A failed or unsupported assessment "
                "must not contain RelationshipStatus."
            )

        if (
            self.processing_status != ProcessingStatus.SUCCESS
            and self.temporal_status is not None
        ):
            raise ValueError(
                "A failed or unsupported assessment "
                "must not contain TemporalStatus."
            )

        if (
            self.processing_status != ProcessingStatus.SUCCESS
            and self.method is not None
        ):
            raise ValueError(
                "A failed or unsupported assessment "
                "must not contain AssessmentMethod."
            )
