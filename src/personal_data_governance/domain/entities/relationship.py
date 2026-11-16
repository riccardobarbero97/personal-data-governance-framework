from dataclasses import dataclass
from datetime import datetime

from personal_data_governance.domain.enums.processing import AssessmentMethod
from personal_data_governance.domain.enums.relationship import (
    RelationshipStatus,
    TemporalStatus,
)
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    IdentitySeedId,
    RelationshipId,
    ServiceId,
    UserId,
)


@dataclass(slots=True)
class Relationship:
    id: RelationshipId
    user_id: UserId
    service_id: ServiceId
    relationship_status: RelationshipStatus
    temporal_status: TemporalStatus
    identity_seed_ids: tuple[IdentitySeedId, ...]
    evidence_ids: tuple[EvidenceId, ...]
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    assessment_method: AssessmentMethod
    assessor_version: str
    assessment_policy_version: str
    assessed_at: datetime

    def __post_init__(self) -> None:
        if not self.evidence_ids:
            raise ValueError(
                "Relationship must reference at least one Evidence item."
            )

        if not self.assessor_version.strip():
            raise ValueError(
                "Assessor version must not be empty."
            )

        if not self.assessment_policy_version.strip():
            raise ValueError(
                "Assessment policy version must not be empty."
            )
