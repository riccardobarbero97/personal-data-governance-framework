import sqlite3

from personal_data_governance.infrastructure.persistence.sqlite.schema import (
    SCHEMA_VERSION,
    create_schema_v1,
    get_schema_version,
    list_schema_tables,
    read_schema_v1,
)


EXPECTED_TABLES = (
    "connected_sources",
    "evidence",
    "evidence_lifecycle",
    "observations",
    "relationships",
    "schema_metadata",
)


def build_connection(
) -> sqlite3.Connection:
    connection = sqlite3.connect(
        ":memory:"
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def test_schema_resource_can_be_loaded() -> None:
    schema_sql = read_schema_v1()

    assert schema_sql.strip()

    assert (
        "CREATE TABLE IF NOT EXISTS observations"
        in schema_sql
    )

    assert (
        "CREATE TABLE IF NOT EXISTS evidence"
        in schema_sql
    )

    assert (
        "CREATE TABLE IF NOT EXISTS relationships"
        in schema_sql
    )


def test_schema_v1_creates_expected_tables() -> None:
    connection = build_connection()

    try:
        create_schema_v1(
            connection
        )

        assert (
            list_schema_tables(
                connection
            )
            == EXPECTED_TABLES
        )

    finally:
        connection.close()


def test_schema_version_is_recorded() -> None:
    connection = build_connection()

    try:
        assert (
            get_schema_version(
                connection
            )
            is None
        )

        create_schema_v1(
            connection
        )

        assert (
            get_schema_version(
                connection
            )
            == SCHEMA_VERSION
        )

    finally:
        connection.close()


def test_schema_creation_is_idempotent() -> None:
    connection = build_connection()

    try:
        create_schema_v1(
            connection
        )

        create_schema_v1(
            connection
        )

        assert (
            get_schema_version(
                connection
            )
            == 1
        )

        assert (
            list_schema_tables(
                connection
            )
            == EXPECTED_TABLES
        )

    finally:
        connection.close()


def test_foreign_keys_are_enabled() -> None:
    connection = build_connection()

    try:
        create_schema_v1(
            connection
        )

        row = connection.execute(
            "PRAGMA foreign_keys"
        ).fetchone()

        assert row is not None
        assert row[0] == 1

    finally:
        connection.close()


def test_observation_requires_existing_connected_source() -> None:
    connection = build_connection()

    try:
        create_schema_v1(
            connection
        )

        try:
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
                    "observation_001",
                    "source_missing",
                    "EMAIL_MESSAGE_METADATA",
                    1,
                    "message_001",
                    None,
                    None,
                    (
                        "2026-12-01"
                        "T12:00:00+00:00"
                    ),
                    "EmailMessageMetadataV1",
                    "{}",
                    (
                        "2026-12-01"
                        "T12:00:00+00:00"
                    ),
                ),
            )

        except sqlite3.IntegrityError:
            pass

        else:
            raise AssertionError(
                "Expected foreign-key "
                "IntegrityError was not raised."
            )

    finally:
        connection.close()


def test_source_reference_is_unique_per_connected_source() -> None:
    connection = build_connection()

    try:
        create_schema_v1(
            connection
        )

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
                (
                    "2026-12-01"
                    "T12:00:00+00:00"
                ),
                (
                    "2026-12-01"
                    "T12:00:00+00:00"
                ),
            ),
        )

        observation_values = (
            "source_gmail",
            "EMAIL_MESSAGE_METADATA",
            1,
            "gmail_message_001",
            None,
            None,
            (
                "2026-12-01"
                "T12:00:00+00:00"
            ),
            "EmailMessageMetadataV1",
            "{}",
            (
                "2026-12-01"
                "T12:00:00+00:00"
            ),
        )

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
                "observation_001",
                *observation_values,
            ),
        )

        try:
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
                    "observation_002",
                    *observation_values,
                ),
            )

        except sqlite3.IntegrityError:
            pass

        else:
            raise AssertionError(
                "Expected duplicate source-reference "
                "IntegrityError was not raised."
            )

    finally:
        connection.close()


def test_only_one_relationship_exists_per_user_and_service() -> None:
    connection = build_connection()

    try:
        create_schema_v1(
            connection
        )

        relationship_values = (
            "user_001",
            "service_spotify",
            "ESTABLISHED",
            "CURRENTLY_OBSERVED",
            '["identity_email"]',
            '["evidence_001"]',
            '["ESTABLISHMENT_EVIDENCE_PRESENT"]',
            "[]",
            "1",
            "relationship-policy-1",
            (
                "2026-12-01"
                "T12:00:00+00:00"
            ),
            (
                "2026-12-01"
                "T12:00:00+00:00"
            ),
            (
                "2026-12-01"
                "T12:00:00+00:00"
            ),
        )

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
                *relationship_values,
            ),
        )

        try:
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
                    "relationship_002",
                    *relationship_values,
                ),
            )

        except sqlite3.IntegrityError:
            pass

        else:
            raise AssertionError(
                "Expected duplicate user-service "
                "IntegrityError was not raised."
            )

    finally:
        connection.close()
