from pathlib import Path

from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    UserId,
)
from personal_data_governance.domain.values.provider import (
    Provider,
)
from personal_data_governance.infrastructure.persistence.sqlite.connected_source_repository import (
    SQLiteConnectedSourceRepository,
)
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)


def build_source(
    display_name: str = "Personal Gmail",
    connection_state: ConnectionState = (
        ConnectionState.CONNECTED
    ),
) -> ConnectedSource:
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
        display_name=display_name,
        external_account_reference=(
            "user@example.com"
        ),
        connection_state=(
            connection_state
        ),
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )


def build_repository(
    tmp_path: Path,
) -> SQLiteConnectedSourceRepository:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    return SQLiteConnectedSourceRepository(
        database
    )


def test_connected_source_round_trip(
    tmp_path: Path,
) -> None:
    repository = build_repository(
        tmp_path
    )

    source = build_source()

    repository.save(
        source
    )

    restored = repository.get(
        source.id
    )

    assert restored == source


def test_missing_connected_source_returns_none(
    tmp_path: Path,
) -> None:
    repository = build_repository(
        tmp_path
    )

    assert (
        repository.get(
            ConnectedSourceId(
                "source_missing"
            )
        )
        is None
    )


def test_connected_source_is_updated(
    tmp_path: Path,
) -> None:
    repository = build_repository(
        tmp_path
    )

    repository.save(
        build_source()
    )

    updated = build_source(
        display_name=(
            "Updated Personal Gmail"
        ),
        connection_state=(
            ConnectionState.DISCONNECTED
        ),
    )

    repository.save(
        updated
    )

    restored = repository.get(
        updated.id
    )

    assert restored == updated


def test_list_by_user_is_isolated(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    repository = (
        SQLiteConnectedSourceRepository(
            database
        )
    )

    first = build_source()

    second = ConnectedSource(
        id=ConnectedSourceId(
            "source_other"
        ),
        user_id=UserId(
            "user_002"
        ),
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="microsoft",
            display_name="Microsoft",
        ),
        connector_id="outlook",
        display_name="Outlook",
        external_account_reference=(
            "other@example.com"
        ),
        connection_state=(
            ConnectionState.CONNECTED
        ),
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )

    repository.save(
        first
    )

    repository.save(
        second
    )

    assert (
        repository.list_by_user(
            UserId(
                "user_001"
            )
        )
        == (
            first,
        )
    )


def test_connected_source_survives_database_restart(
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

    first_repository = (
        SQLiteConnectedSourceRepository(
            first_database
        )
    )

    source = build_source()

    first_repository.save(
        source
    )

    second_database = SQLiteDatabase(
        database_file
    )

    second_database.initialize()

    second_repository = (
        SQLiteConnectedSourceRepository(
            second_database
        )
    )

    assert (
        second_repository.get(
            source.id
        )
        == source
    )
