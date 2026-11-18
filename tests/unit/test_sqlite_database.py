import sqlite3
from pathlib import Path

from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)
from personal_data_governance.infrastructure.persistence.sqlite.migrations import (
    UnsupportedSchemaVersionError,
)
from personal_data_governance.infrastructure.persistence.sqlite.schema import (
    get_schema_version,
)


CURRENT_SCHEMA_VERSION = 3


def test_initialize_creates_database_and_schema(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / ".pdgf"
        / "state.db"
    )

    database = SQLiteDatabase(
        database_file
    )

    result = database.initialize()

    assert database_file.exists()

    assert result.initial_version is None

    assert (
        result.final_version
        == CURRENT_SCHEMA_VERSION
    )

    assert (
        result.applied_versions
        == (
            1,
            2,
            3,
        )
    )

    with database.connection() as connection:
        assert (
            get_schema_version(
                connection
            )
            == CURRENT_SCHEMA_VERSION
        )


def test_initialize_existing_database_is_idempotent(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    database = SQLiteDatabase(
        database_file
    )

    first = database.initialize()
    second = database.initialize()

    assert first.initial_version is None

    assert (
        first.final_version
        == CURRENT_SCHEMA_VERSION
    )

    assert (
        first.applied_versions
        == (
            1,
            2,
            3,
        )
    )

    assert (
        second.initial_version
        == CURRENT_SCHEMA_VERSION
    )

    assert (
        second.final_version
        == CURRENT_SCHEMA_VERSION
    )

    assert (
        second.applied_versions
        == ()
    )

    assert second.changed is False


def test_connection_enables_foreign_keys(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    with database.connection() as connection:
        row = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()

        assert row is not None
        assert row[0] == 1


def test_connection_uses_row_factory(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    with database.connection() as connection:
        row = connection.execute(
            """
            SELECT
                schema_name,
                schema_version
            FROM schema_metadata
            """
        ).fetchone()

        assert row is not None

        assert (
            row[
                "schema_name"
            ]
            == "personal_data_governance"
        )

        assert (
            row[
                "schema_version"
            ]
            == CURRENT_SCHEMA_VERSION
        )


def test_transaction_commits_on_success(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    with database.transaction() as connection:
        connection.execute(
            """
            INSERT INTO connected_sources (
                connected_source_id,
                user_id,
                source_type,
                provider_id,
                provider_display_name,
                connector_id,
                display_name,
                external_account_reference,
                connection_state,
                authorization_state,
                created_at,
                updated_at
            )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            (
                "source_gmail",
                "user_001",
                "EMAIL",
                "google",
                "Google",
                "gmail",
                "Personal Gmail",
                "user@example.com",
                "CONNECTED",
                "AUTHORIZED",
                "2026-12-01T12:00:00+00:00",
                "2026-12-01T12:00:00+00:00",
            ),
        )

    with database.connection() as connection:
        row = connection.execute(
            """
            SELECT connected_source_id
            FROM connected_sources
            WHERE connected_source_id = ?
            """,
            (
                "source_gmail",
            ),
        ).fetchone()

        assert row is not None

        assert (
            row[
                "connected_source_id"
            ]
            == "source_gmail"
        )


def test_transaction_rolls_back_on_failure(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    try:
        with database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO connected_sources (
                    connected_source_id,
                    user_id,
                    source_type,
                    provider_id,
                    provider_display_name,
                    connector_id,
                    display_name,
                    external_account_reference,
                    connection_state,
                    authorization_state,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    "source_gmail",
                    "user_001",
                    "EMAIL",
                    "google",
                    "Google",
                    "gmail",
                    "Personal Gmail",
                    "user@example.com",
                    "CONNECTED",
                    "AUTHORIZED",
                    "2026-12-01T12:00:00+00:00",
                    "2026-12-01T12:00:00+00:00",
                ),
            )

            raise RuntimeError(
                "Simulated processing failure."
            )

    except RuntimeError:
        pass

    with database.connection() as connection:
        row = connection.execute(
            """
            SELECT connected_source_id
            FROM connected_sources
            WHERE connected_source_id = ?
            """,
            (
                "source_gmail",
            ),
        ).fetchone()

        assert row is None


def test_future_database_version_is_rejected(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    connection = sqlite3.connect(
        database_file
    )

    connection.execute(
        """
        CREATE TABLE schema_metadata (
            schema_name TEXT PRIMARY KEY,
            schema_version INTEGER NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        INSERT INTO schema_metadata (
            schema_name,
            schema_version,
            applied_at
        )
        VALUES (
            ?,
            ?,
            ?
        )
        """,
        (
            "personal_data_governance",
            99,
            "2026-12-01T12:00:00+00:00",
        ),
    )

    connection.commit()
    connection.close()

    database = SQLiteDatabase(
        database_file
    )

    try:
        database.initialize()

    except UnsupportedSchemaVersionError:
        pass

    else:
        raise AssertionError(
            "Expected "
            "UnsupportedSchemaVersionError "
            "was not raised."
        )


def test_negative_busy_timeout_is_rejected(
    tmp_path: Path,
) -> None:
    try:
        SQLiteDatabase(
            tmp_path
            / "state.db",
            busy_timeout_milliseconds=-1,
        )

    except ValueError as error:
        assert (
            "must not be negative"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError "
            "was not raised."
        )
