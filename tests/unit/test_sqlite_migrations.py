import sqlite3

from personal_data_governance.infrastructure.persistence.sqlite.migrations import (
    MissingMigrationError,
    SQLiteMigration,
    SQLiteMigrationError,
    SQLiteMigrator,
    UnsupportedSchemaVersionError,
    UnversionedDatabaseError,
)
from personal_data_governance.infrastructure.persistence.sqlite.schema import (
    get_schema_version,
    list_schema_tables,
)


CURRENT_SCHEMA_VERSION = 3

EXPECTED_CURRENT_TABLES = (
    "connected_sources",
    "evidence",
    "evidence_lifecycle",
    "evidence_observations",
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


def test_empty_database_is_migrated_to_current_version() -> None:
    connection = build_connection()

    try:
        result = SQLiteMigrator().migrate(
            connection
        )

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

        assert result.changed is True

        assert (
            list_schema_tables(
                connection
            )
            == EXPECTED_CURRENT_TABLES
        )

    finally:
        connection.close()


def test_existing_current_database_is_not_changed() -> None:
    connection = build_connection()

    try:
        migrator = SQLiteMigrator()

        first_result = migrator.migrate(
            connection
        )

        second_result = migrator.migrate(
            connection
        )

        assert first_result.initial_version is None

        assert (
            first_result.final_version
            == CURRENT_SCHEMA_VERSION
        )

        assert (
            first_result.applied_versions
            == (
                1,
                2,
                3,
            )
        )

        assert (
            second_result.initial_version
            == CURRENT_SCHEMA_VERSION
        )

        assert (
            second_result.final_version
            == CURRENT_SCHEMA_VERSION
        )

        assert (
            second_result.applied_versions
            == ()
        )

        assert second_result.changed is False

    finally:
        connection.close()


def test_future_schema_version_is_rejected() -> None:
    connection = build_connection()

    try:
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

        try:
            SQLiteMigrator().migrate(
                connection
            )

        except UnsupportedSchemaVersionError as error:
            assert (
                "newer than"
                in str(error)
            )

        else:
            raise AssertionError(
                "Expected "
                "UnsupportedSchemaVersionError "
                "was not raised."
            )

    finally:
        connection.close()


def test_unversioned_application_database_is_rejected() -> None:
    connection = build_connection()

    try:
        connection.execute(
            """
            CREATE TABLE observations (
                observation_id TEXT PRIMARY KEY
            )
            """
        )

        connection.commit()

        try:
            SQLiteMigrator().migrate(
                connection
            )

        except UnversionedDatabaseError as error:
            assert (
                "observations"
                in str(error)
            )

        else:
            raise AssertionError(
                "Expected "
                "UnversionedDatabaseError "
                "was not raised."
            )

    finally:
        connection.close()


def test_missing_migration_is_reported() -> None:
    connection = build_connection()

    try:
        migrator = SQLiteMigrator(
            migrations=(),
            supported_version=1,
        )

        try:
            migrator.migrate(
                connection
            )

        except MissingMigrationError as error:
            assert (
                "version 1"
                in str(error)
            )

        else:
            raise AssertionError(
                "Expected MissingMigrationError "
                "was not raised."
            )

    finally:
        connection.close()


def test_duplicate_migration_versions_are_rejected() -> None:
    def no_operation(
        connection: sqlite3.Connection,
    ) -> None:
        del connection

    migrations = (
        SQLiteMigration(
            target_version=1,
            name="first",
            apply=no_operation,
        ),
        SQLiteMigration(
            target_version=1,
            name="duplicate",
            apply=no_operation,
        ),
    )

    try:
        SQLiteMigrator(
            migrations=migrations,
            supported_version=1,
        )

    except ValueError as error:
        assert (
            "unique"
            in str(error)
        )

    else:
        raise AssertionError(
            "Expected ValueError "
            "was not raised."
        )


def test_failed_migration_is_rolled_back() -> None:
    connection = build_connection()

    def failing_migration(
        target_connection: sqlite3.Connection,
    ) -> None:
        try:
            target_connection.executescript(
                """
                BEGIN IMMEDIATE;

                CREATE TABLE temporary_test_table (
                    id TEXT PRIMARY KEY
                );

                INSERT INTO missing_table (
                    id
                )
                VALUES (
                    'value'
                );

                COMMIT;
                """
            )

        except Exception:
            if target_connection.in_transaction:
                target_connection.rollback()

            raise

    migrator = SQLiteMigrator(
        migrations=(
            SQLiteMigration(
                target_version=1,
                name="failing",
                apply=failing_migration,
            ),
        ),
        supported_version=1,
    )

    try:
        migrator.migrate(
            connection
        )

    except SQLiteMigrationError:
        pass

    else:
        raise AssertionError(
            "Expected SQLiteMigrationError "
            "was not raised."
        )

    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE
            type = 'table'
            AND name = 'temporary_test_table'
        """
    ).fetchone()

    assert table is None

    assert (
        get_schema_version(
            connection
        )
        is None
    )

    connection.close()
