from pathlib import Path

import pytest

from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)
from personal_data_governance.infrastructure.persistence.sqlite.migrations import (
    SQLiteMigrator,
    UnsafeMigrationError,
)
from personal_data_governance.infrastructure.persistence.sqlite.schema import (
    SCHEMA_VERSION,
    get_schema_version,
)


def build_v2_database(
    database_file: Path,
) -> SQLiteDatabase:
    database = SQLiteDatabase(
        database_file=database_file,
        migrator=SQLiteMigrator(
            supported_version=2
        ),
    )

    database.initialize()

    return database


def test_current_schema_version_is_three() -> None:
    assert SCHEMA_VERSION == 3


def test_new_database_applies_all_three_migrations(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    result = database.initialize()

    assert result.initial_version is None
    assert result.final_version == 3

    assert (
        result.applied_versions
        == (
            1,
            2,
            3,
        )
    )


def test_schema_v3_contains_assessment_method(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    with database.connection() as connection:
        rows = connection.execute(
            """
            PRAGMA table_info(relationships)
            """
        ).fetchall()

    columns = {
        row[
            "name"
        ]
        for row in rows
    }

    assert (
        "assessment_method"
        in columns
    )


def test_empty_schema_v2_database_migrates_to_v3(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    v2_database = build_v2_database(
        database_file
    )

    with v2_database.connection() as connection:
        assert (
            get_schema_version(
                connection
            )
            == 2
        )

    current_database = SQLiteDatabase(
        database_file
    )

    result = current_database.initialize()

    assert result.initial_version == 2
    assert result.final_version == 3

    assert (
        result.applied_versions
        == (
            3,
        )
    )


def test_v2_relationship_data_blocks_automatic_migration(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    v2_database = build_v2_database(
        database_file
    )

    with v2_database.transaction() as connection:
        connection.execute(
            """
            INSERT INTO relationships (
                relationship_id,
                user_id,
                service_id,
                relationship_status,
                temporal_status,
                identity_seed_ids_json,
                evidence_ids_json,
                reason_codes_json,
                warnings_json,
                assessor_version,
                assessment_policy_version,
                assessed_at,
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
                ?,
                ?,
                ?
            )
            """,
            (
                "relationship_001",
                "user_001",
                "service_spotify",
                "ESTABLISHED",
                "CURRENTLY_OBSERVED",
                '["identity_email"]',
                "[]",
                '["ESTABLISHMENT_EVIDENCE_PRESENT"]',
                "[]",
                "1",
                "relationship-policy-1",
                "2026-12-01T12:00:00+00:00",
                "2026-12-01T12:00:00+00:00",
                "2026-12-01T12:00:00+00:00",
            ),
        )

    current_database = SQLiteDatabase(
        database_file
    )

    with pytest.raises(
        UnsafeMigrationError
    ):
        current_database.initialize()

    with v2_database.connection() as connection:
        assert (
            get_schema_version(
                connection
            )
            == 2
        )

        row = connection.execute(
            """
            SELECT relationship_id
            FROM relationships
            WHERE relationship_id = ?
            """,
            (
                "relationship_001",
            ),
        ).fetchone()

        assert row is not None
