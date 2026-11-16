from datetime import datetime, timezone

from personal_data_governance.application.services.evidence_contribution_builder import (
    EvidenceContributionBuilder,
)
from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.evidence import (
    EvidenceStatus,
    EvidenceType,
)
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.enums.processing import (
    ClassificationMethod,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    ObservationId,
    ServiceId,
    UserId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import TemporalValue
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryConnectedSourceRepository,
    InMemoryObservationRepository,
)


def test_builder_resolves_source_and_temporal_provenance() -> None:
    observation_repository = InMemoryObservationRepository()
    source_repository = InMemoryConnectedSourceRepository()

    connected_source = ConnectedSource(
        id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        user_id=UserId("user_001"),
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="google",
            display_name="Google",
        ),
        connector_id="gmail",
        display_name="Personal Gmail",
        external_account_reference=(
            "user@example.com"
        ),
        connection_state=ConnectionState.CONNECTED,
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )

    source_repository.save(
        connected_source
    )

    observed_at = TemporalValue(
        timestamp=datetime(
            2026,
            1,
            1,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        semantics=TemporalSemantics.MESSAGE_TIME,
    )

    observation = Observation(
        id=ObservationId("observation_001"),
        connected_source_id=connected_source.id,
        observation_type=(
            ObservationType.EMAIL_MESSAGE_METADATA
        ),
        schema_version=SchemaVersion(1),
        source_reference=SourceReference(
            "gmail_message_123"
        ),
        observed_at=observed_at,
        collected_at=datetime.now(
            timezone.utc
        ),
        payload=EmailMessageMetadataV1(
            sender="no-reply@spotify.com",
            recipients=(
                "user@example.com",
            ),
            subject="Verify your email address",
            thread_reference="thread_001",
            labels=(),
        ),
    )

    observation_repository.save(
        observation
    )

    evidence = Evidence(
        id=EvidenceId("evidence_001"),
        evidence_type=(
            EvidenceType.ACCOUNT_VERIFICATION
        ),
        evidence_status=EvidenceStatus.ACTIVE,
        observation_ids=(
            observation.id,
        ),
        service_id=ServiceId(
            "service_spotify"
        ),
        identity_seed_ids=(),
        classification_method=(
            ClassificationMethod.RULE
        ),
        classifier_version="1",
        reason_codes=(
            "ACCOUNT_VERIFICATION_SUBJECT",
        ),
    )

    builder = EvidenceContributionBuilder(
        observation_repository=(
            observation_repository
        ),
        connected_source_repository=(
            source_repository
        ),
    )

    contribution = builder.build(
        evidence
    )

    assert contribution.evidence == evidence

    assert contribution.connected_source_ids == (
        connected_source.id,
    )

    assert contribution.source_types == (
        SourceType.EMAIL,
    )

    assert contribution.providers == (
        Provider(
            id="google",
            display_name="Google",
        ),
    )

    assert contribution.temporal_values == (
        observed_at,
    )

def test_missing_observation_raises_error() -> None:
    observation_repository = InMemoryObservationRepository()
    source_repository = InMemoryConnectedSourceRepository()

    evidence = Evidence(
        id=EvidenceId("evidence_001"),
        evidence_type=EvidenceType.PAYMENT,
        evidence_status=EvidenceStatus.ACTIVE,
        observation_ids=(
            ObservationId("missing_observation"),
        ),
        service_id=None,
        identity_seed_ids=(),
        classification_method=ClassificationMethod.RULE,
        classifier_version="1",
        reason_codes=(
            "PAYMENT_SUBJECT",
        ),
    )

    builder = EvidenceContributionBuilder(
        observation_repository=(
            observation_repository
        ),
        connected_source_repository=(
            source_repository
        ),
    )

    try:
        builder.build(evidence)
    except KeyError as error:
        assert "Observation not found" in str(error)
    else:
        raise AssertionError(
            "Expected KeyError was not raised."
        )
