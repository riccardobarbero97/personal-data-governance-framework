from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.entities.observation import (
    Observation,
)
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
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
    ObservationId,
    UserId,
)
from personal_data_governance.domain.values.provider import (
    Provider,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import (
    TemporalValue,
)
from personal_data_governance.infrastructure.persistence.sqlite.connected_source_repository import (
    SQLiteConnectedSourceRepository,
)
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)
from personal_data_governance.infrastructure.persistence.sqlite.observation_repository import (
    SQLiteObservationRepository,
)


COLLECTED_AT = datetime(
    2026,
    12,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)

OBSERVED_AT = datetime(
    2026,
    11,
    15,
    8,
    0,
    tzinfo=timezone.utc,
)


def build_source() -> ConnectedSource:
    return ConnectedSource(
        id=ConnectedSourceId(
            "source_gmail"
        ),
        user_id=UserId(
            "user_001"
        ),
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
        connection_state=(
            ConnectionState.CONNECTED
        ),
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )


def build_observation(
    observation_id: str = (
        "observation_001"
    ),
    source_reference: str = (
        "gmail_message_001"
    ),
) -> Observation:
    return Observation(
        id=ObservationId(
            observation_id
        ),
        connected_source_id=(
            ConnectedSourceId(
                "source_gmail"
            )
        ),
        observation_type=(
            ObservationType.EMAIL_MESSAGE_METADATA
        ),
        schema_version=SchemaVersion(
            1
        ),
        source_reference=SourceReference(
            source_reference
        ),
        observed_at=TemporalValue(
            timestamp=OBSERVED_AT,
            semantics=(
                TemporalSemantics.MESSAGE_TIME
            ),
        ),
        collected_at=COLLECTED_AT,
        payload=EmailMessageMetadataV1(
            sender=(
                "Spotify "
                "<no-reply@spotify.com>"
            ),
            recipients=(
                "user@example.com",
                "secondary@example.com",
            ),
            subject=(
                "Verify your email address"
            ),
            thread_reference=(
                "thread_spotify"
            ),
            labels=(
                "INBOX",
                "CATEGORY_UPDATES",
            ),
        ),
    )


def build_repositories(
    tmp_path: Path,
):
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    source_repository = (
        SQLiteConnectedSourceRepository(
            database
        )
    )

    observation_repository = (
        SQLiteObservationRepository(
            database
        )
    )

    source_repository.save(
        build_source()
    )

    return (
        database,
        source_repository,
        observation_repository,
    )


def test_observation_round_trip(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        repository,
    ) = build_repositories(
        tmp_path
    )

    observation = build_observation()

    repository.save(
        observation
    )

    restored = repository.get(
        observation.id
    )

    assert restored == observation


def test_missing_observation_returns_none(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        repository,
    ) = build_repositories(
        tmp_path
    )

    assert (
        repository.get(
            ObservationId(
                "observation_missing"
            )
        )
        is None
    )


def test_find_by_source_reference(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        repository,
    ) = build_repositories(
        tmp_path
    )

    observation = build_observation()

    repository.save(
        observation
    )

    restored = (
        repository.find_by_source_reference(
            connected_source_id=(
                observation
                .connected_source_id
            ),
            source_reference=(
                observation
                .source_reference
            ),
        )
    )

    assert restored == observation


def test_duplicate_observation_id_is_idempotent(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        repository,
    ) = build_repositories(
        tmp_path
    )

    observation = build_observation()

    repository.save(
        observation
    )

    repository.save(
        observation
    )

    observations = (
        repository
        .list_by_connected_source(
            ConnectedSourceId(
                "source_gmail"
            )
        )
    )

    assert observations == (
        observation,
    )


def test_duplicate_source_reference_is_not_created(
    tmp_path: Path,
) -> None:
    (
        _,
        _,
        repository,
    ) = build_repositories(
        tmp_path
    )

    first = build_observation(
        observation_id=(
            "observation_001"
        ),
        source_reference=(
            "gmail_message_001"
        ),
    )

    duplicate = build_observation(
        observation_id=(
            "observation_002"
        ),
        source_reference=(
            "gmail_message_001"
        ),
    )

    repository.save(
        first
    )

    repository.save(
        duplicate
    )

    observations = (
        repository
        .list_by_connected_source(
            ConnectedSourceId(
                "source_gmail"
            )
        )
    )

    assert observations == (
        first,
    )

    restored = (
        repository.find_by_source_reference(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail"
                )
            ),
            source_reference=(
                SourceReference(
                    "gmail_message_001"
                )
            ),
        )
    )

    assert restored == first


def test_observation_requires_existing_source(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    repository = (
        SQLiteObservationRepository(
            database
        )
    )

    try:
        repository.save(
            build_observation()
        )

    except Exception as error:
        assert (
            "FOREIGN KEY"
            in str(error).upper()
        )

    else:
        raise AssertionError(
            "Expected foreign-key failure "
            "was not raised."
        )


def test_observation_survives_database_restart(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    first_database = SQLiteDatabase(
        database_file
    )

    first_database.initialize()

    first_source_repository = (
        SQLiteConnectedSourceRepository(
            first_database
        )
    )

    first_observation_repository = (
        SQLiteObservationRepository(
            first_database
        )
    )

    source = build_source()
    observation = build_observation()

    first_source_repository.save(
        source
    )

    first_observation_repository.save(
        observation
    )

    second_database = SQLiteDatabase(
        database_file
    )

    second_database.initialize()

    second_source_repository = (
        SQLiteConnectedSourceRepository(
            second_database
        )
    )

    second_observation_repository = (
        SQLiteObservationRepository(
            second_database
        )
    )

    assert (
        second_source_repository.get(
            source.id
        )
        == source
    )

    assert (
        second_observation_repository.get(
            observation.id
        )
        == observation
    )

    assert (
        second_observation_repository
        .find_by_source_reference(
            connected_source_id=(
                source.id
            ),
            source_reference=(
                observation
                .source_reference
            ),
        )
        == observation
    )
