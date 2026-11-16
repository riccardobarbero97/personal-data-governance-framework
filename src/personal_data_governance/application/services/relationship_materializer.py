from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from personal_data_governance.application.ports.repositories import (
    RelationshipRepository,
)
from personal_data_governance.application.results.assessment import (
    RelationshipAssessmentResult,
)
from personal_data_governance.domain.entities.relationship import (
    Relationship,
)
from personal_data_governance.domain.enums.processing import (
    ProcessingStatus,
)
from personal_data_governance.domain.values.identifiers import (
    RelationshipId,
    UserId,
)


RelationshipIdFactory = Callable[[], RelationshipId]


def default_relationship_id_factory() -> RelationshipId:
    return RelationshipId(
        f"relationship_{uuid4().hex}"
    )


class RelationshipMaterializer:
    def __init__(
        self,
        relationship_repository: RelationshipRepository,
        relationship_id_factory: RelationshipIdFactory | None = None,
    ) -> None:
        self._relationship_repository = relationship_repository

        self._relationship_id_factory = (
            relationship_id_factory
            if relationship_id_factory is not None
            else default_relationship_id_factory
        )

    def materialize(
        self,
        user_id: UserId,
        assessment_result: RelationshipAssessmentResult,
        assessed_at: datetime,
    ) -> Relationship:
        if (
            assessment_result.processing_status
            != ProcessingStatus.SUCCESS
        ):
            raise ValueError(
                "Only a successful assessment can be "
                "materialized as a Relationship."
            )

        if assessment_result.service_id is None:
            raise ValueError(
                "Canonical Service is required to "
                "materialize a Relationship."
            )

        if assessment_result.relationship_status is None:
            raise ValueError(
                "RelationshipStatus is required to "
                "materialize a Relationship."
            )

        if assessment_result.temporal_status is None:
            raise ValueError(
                "TemporalStatus is required to "
                "materialize a Relationship."
            )

        if assessment_result.method is None:
            raise ValueError(
                "AssessmentMethod is required to "
                "materialize a Relationship."
            )

        if not assessment_result.evidence_ids:
            raise ValueError(
                "Relationship materialization requires "
                "at least one Evidence item."
            )

        if assessed_at.tzinfo is None:
            raise ValueError(
                "Assessment time must be timezone-aware."
            )

        if assessed_at.utcoffset() is None:
            raise ValueError(
                "Assessment time must be timezone-aware."
            )

        existing_relationship = (
            self._relationship_repository.get_by_user_and_service(
                user_id=user_id,
                service_id=assessment_result.service_id,
            )
        )

        relationship_id = (
            existing_relationship.id
            if existing_relationship is not None
            else self._relationship_id_factory()
        )

        relationship = Relationship(
            id=relationship_id,
            user_id=user_id,
            service_id=assessment_result.service_id,
            relationship_status=(
                assessment_result.relationship_status
            ),
            temporal_status=assessment_result.temporal_status,
            identity_seed_ids=(
                assessment_result.identity_seed_ids
            ),
            evidence_ids=assessment_result.evidence_ids,
            reason_codes=assessment_result.reason_codes,
            warnings=assessment_result.warnings,
            assessment_method=assessment_result.method,
            assessor_version=(
                assessment_result.assessor_version
            ),
            assessment_policy_version=(
                assessment_result.assessment_policy_version
            ),
            assessed_at=assessed_at,
        )

        self._relationship_repository.save(
            relationship
        )

        return relationship
