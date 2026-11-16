from datetime import datetime, timezone

from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import TemporalValue
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryObservationRepository,
)


def test_observation_can_be_saved_and_loaded() -> None:
    repository = InMemoryObservationRepository()

    observation = Observation(
        id=ObservationId("observation_001"),
        connected_source_id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        observation_type=ObservationType.EMAIL_MESSAGE_METADATA,
        schema_version=SchemaVersion(1),
        source_reference=SourceReference(
            "gmail_message_123"
        ),
        observed_at=TemporalValue(
            timestamp=datetime(
                2026,
                1,
                1,
                10,
                30,
                tzinfo=timezone.utc,
            ),
            semantics=TemporalSemantics.MESSAGE_TIME,
        ),
        collected_at=datetime.now(timezone.utc),
        payload=EmailMessageMetadataV1(
            sender="no-reply@spotify.com",
            recipients=(
                "user@example.com",
            ),
            subject="Verify your email address",
            thread_reference="gmail_thread_001",
            labels=(),
        ),
    )

    repository.save(observation)

    stored = repository.get(observation.id)

    assert stored == observation


def test_observation_can_be_found_by_source_reference() -> None:
    repository = InMemoryObservationRepository()

    connected_source_id = ConnectedSourceId(
        "source_gmail_personal"
    )

    source_reference = SourceReference(
        "gmail_message_123"
    )

    observation = Observation(
        id=ObservationId("observation_001"),
        connected_source_id=connected_source_id,
        observation_type=ObservationType.EMAIL_MESSAGE_METADATA,
        schema_version=SchemaVersion(1),
        source_reference=source_reference,
        observed_at=TemporalValue(
            timestamp=datetime(
                2026,
                1,
                1,
                10,
                30,
                tzinfo=timezone.utc,
            ),
            semantics=TemporalSemantics.MESSAGE_TIME,
        ),
        collected_at=datetime.now(timezone.utc),
        payload=EmailMessageMetadataV1(
            sender="no-reply@spotify.com",
            recipients=(
                "user@example.com",
            ),
            subject="Verify your email address",
            thread_reference="gmail_thread_001",
            labels=(),
        ),
    )

    repository.save(observation)

    stored = repository.find_by_source_reference(
        connected_source_id=connected_source_id,
        source_reference=source_reference,
    )

    assert stored == observation


def test_source_reference_is_scoped_by_connected_source() -> None:
    repository = InMemoryObservationRepository()

    source_reference = SourceReference(
        "provider_message_123"
    )

    source_one = ConnectedSourceId("source_001")
    source_two = ConnectedSourceId("source_002")

    observation = Observation(
        id=ObservationId("observation_001"),
        connected_source_id=source_one,
        observation_type=ObservationType.EMAIL_MESSAGE_METADATA,
        schema_version=SchemaVersion(1),
        source_reference=source_reference,
        observed_at=None,
        collected_at=datetime.now(timezone.utc),
        payload=EmailMessageMetadataV1(
            sender="no-reply@spotify.com",
            recipients=(),
            subject="Verify your email address",
            thread_reference=None,
            labels=(),
        ),
    )

    repository.save(observation)

    found_from_source_one = (
        repository.find_by_source_reference(
            connected_source_id=source_one,
            source_reference=source_reference,
        )
    )

    found_from_source_two = (
        repository.find_by_source_reference(
            connected_source_id=source_two,
            source_reference=source_reference,
        )
    )

    assert found_from_source_one == observation
    assert found_from_source_two is None
