from pathlib import Path

from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)
from personal_data_governance.infrastructure.persistence.sqlite.migrations import (
    SQLiteMigrator,
)
from personal_data_governance.infrastructure.persistence.sqlite.schema import (
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


def test_database_can_be_initialized_to_schema_v2(
    tmp_path: Path,
) -> None:
    database = build_v2_database(
        tmp_path
        / "state.db"
    )

    with database.connection() as connection:
        assert (
            get_schema_version(
                connection
            )
            == 2
        )


def test_schema_v2_applies_first_two_migrations(
    tmp_path: Path,
) -> None:
    database = SQLiteDatabase(
        database_file=(
            tmp_path
            / "state.db"
        ),
        migrator=SQLiteMigrator(
            supported_version=2
        ),
    )

    result = database.initialize()

    assert result.initial_version is None
    assert result.final_version == 2

    assert (
        result.applied_versions
        == (
            1,
            2,
        )
    )


def test_schema_v2_contains_evidence_observations_table(
    tmp_path: Path,
) -> None:
    database = build_v2_database(
        tmp_path
        / "state.db"
    )

    with database.connection() as connection:
        row = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE
                type = 'table'
                AND name = 'evidence_observations'
            """
        ).fetchone()

        assert row is not None


def test_evidence_contains_domain_required_columns(
    tmp_path: Path,
) -> None:
    database = build_v2_database(
        tmp_path
        / "state.db"
    )

    with database.connection() as connection:
        rows = connection.execute(
            """
            PRAGMA table_info(evidence)
            """
        ).fetchall()

    columns = {
        row[
            "name"
        ]
        for row in rows
    }

    assert {
        "evidence_id",
        "service_id",
        "evidence_type",
        "evidence_status",
        "identity_seed_ids_json",
        "classification_method",
        "classifier_version",
        "reason_codes_json",
        "created_at",
        "updated_at",
    }.issubset(
        columns
    )

    assert (
        "confidence"
        not in columns
    )

    assert (
        "observation_id"
        not in columns
    )


def test_lifecycle_contains_actor_and_superseded_by(
    tmp_path: Path,
) -> None:
    database = build_v2_database(
        tmp_path
        / "state.db"
    )

    with database.connection() as connection:
        rows = connection.execute(
            """
            PRAGMA table_info(evidence_lifecycle)
            """
        ).fetchall()

    columns = {
        row[
            "name"
        ]
        for row in rows
    }

    assert {
        "evidence_id",
        "previous_status",
        "new_status",
        "reason_code",
        "actor",
        "superseded_by_evidence_id",
        "changed_at",
    }.issubset(
        columns
    )


def test_schema_v2_supports_multiple_observations_per_evidence(
    tmp_path: Path,
) -> None:
    database = build_v2_database(
        tmp_path
        / "state.db"
    )

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
                'source_001',
                'user_001',
                'EMAIL',
                'google',
                'Google',
                'gmail',
                'Gmail',
                NULL,
                'CONNECTED',
                'AUTHORIZED',
                '2026-12-01T12:00:00+00:00',
                '2026-12-01T12:00:00+00:00'
            )
            """
        )

        for observation_id in (
            "observation_001",
            "observation_002",
        ):
            connection.execute(
                """
                INSERT INTO observations (
                    observation_id,
                    connected_source_id,
                    observation_type,
                    schema_version,
                    source_reference_value,
                    observed_at_timestamp,
                    observed_at_semantics,
                    collected_at,
                    payload_type,
                    payload_json,
                    created_at
                )
                VALUES (
                    ?,
                    'source_001',
                    'EMAIL_MESSAGE_METADATA',
                    1,
                    ?,
                    NULL,
                    NULL,
                    '2026-12-01T12:00:00+00:00',
                    'EmailMessageMetadataV1',
                    '{}',
                    '2026-12-01T12:00:00+00:00'
                )
                """,
                (
                    observation_id,
                    f"message_{observation_id}",
                ),
            )

        connection.execute(
            """
            INSERT INTO evidence (
                evidence_id,
                service_id,
                evidence_type,
                evidence_status,
                identity_seed_ids_json,
                classification_method,
                classifier_version,
                reason_codes_json,
                created_at,
                updated_at
            )
            VALUES (
                'evidence_001',
                'service_spotify',
                'ACCOUNT_VERIFICATION',
                'ACTIVE',
                '[]',
                'RULE',
                '1',
                '[]',
                '2026-12-01T12:00:00+00:00',
                '2026-12-01T12:00:00+00:00'
            )
            """
        )

        connection.execute(
            """
            INSERT INTO evidence_observations (
                evidence_id,
                observation_id
            )
            VALUES (
                'evidence_001',
                'observation_001'
            ),
            (
                'evidence_001',
                'observation_002'
            )
            """
        )

    with database.connection() as connection:
        count = connection.execute(
            """
            SELECT COUNT(*)
            FROM evidence_observations
            WHERE evidence_id = 'evidence_001'
            """
        ).fetchone()

    assert count is not None
    assert count[0] == 2
