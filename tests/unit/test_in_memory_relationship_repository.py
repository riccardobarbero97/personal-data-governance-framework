from datetime import datetime, timezone

from personal_data_governance.domain.entities.relationship import (
    Relationship,
)
from personal_data_governance.domain.enums.processing import (
    AssessmentMethod,
)
from personal_data_governance.domain.enums.relationship import (
    RelationshipStatus,
    TemporalStatus,
)
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    RelationshipId,
    ServiceId,
    UserId,
)
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryRelationshipRepository,
)


def build_relationship(
    relationship_id: str,
    relationship_status: RelationshipStatus,
) -> Relationship:
    return Relationship(
        id=RelationshipId(relationship_id),
        user_id=UserId("user_001"),
        service_id=ServiceId("service_spotify"),
        relationship_status=relationship_status,
        temporal_status=TemporalStatus.UNKNOWN,
        identity_seed_ids=(),
        evidence_ids=(
            EvidenceId("evidence_001"),
        ),
        reason_codes=(
            "ACCOUNT_RELATED_EVIDENCE",
        ),
        warnings=(),
        assessment_method=AssessmentMethod.RULE,
        assessor_version="1",
        assessment_policy_version="1",
        assessed_at=datetime.now(timezone.utc),
    )


def test_relationship_can_be_saved_and_loaded() -> None:
    repository = InMemoryRelationshipRepository()

    relationship = build_relationship(
        relationship_id="relationship_001",
        relationship_status=RelationshipStatus.OBSERVED,
    )

    repository.save(relationship)

    stored = repository.get(relationship.id)

    assert stored == relationship


def test_relationship_can_be_found_by_user_and_service() -> None:
    repository = InMemoryRelationshipRepository()

    relationship = build_relationship(
        relationship_id="relationship_001",
        relationship_status=RelationshipStatus.OBSERVED,
    )

    repository.save(relationship)

    stored = repository.get_by_user_and_service(
        user_id=UserId("user_001"),
        service_id=ServiceId("service_spotify"),
    )

    assert stored == relationship


def test_only_one_current_relationship_exists_per_user_service() -> None:
    repository = InMemoryRelationshipRepository()

    first_relationship = build_relationship(
        relationship_id="relationship_001",
        relationship_status=RelationshipStatus.OBSERVED,
    )

    second_relationship = build_relationship(
        relationship_id="relationship_002",
        relationship_status=RelationshipStatus.ESTABLISHED,
    )

    repository.save(first_relationship)
    repository.save(second_relationship)

    stored = repository.get_by_user_and_service(
        user_id=UserId("user_001"),
        service_id=ServiceId("service_spotify"),
    )

    assert stored == second_relationship
    assert repository.get(
        first_relationship.id
    ) is None
