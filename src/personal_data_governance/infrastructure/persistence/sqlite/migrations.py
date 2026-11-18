from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass

from personal_data_governance.infrastructure.persistence.sqlite.schema import (
    SCHEMA_NAME,
    SCHEMA_VERSION,
    get_schema_version,
    read_schema_v1,
    read_schema_v2,
)


MigrationAction = Callable[
    [sqlite3.Connection],
    None,
]


class SQLiteMigrationError(
    RuntimeError
):
    """Base error for SQLite schema migrations."""


class UnsupportedSchemaVersionError(
    SQLiteMigrationError
):
    """Database schema is newer than the app."""


class UnversionedDatabaseError(
    SQLiteMigrationError
):
    """Application tables exist without metadata."""


class MissingMigrationError(
    SQLiteMigrationError
):
    """No migration path exists."""


class UnsafeMigrationError(
    SQLiteMigrationError
):
    """Migration would risk existing data."""


@dataclass(frozen=True, slots=True)
class SQLiteMigration:
    target_version: int
    name: str
    apply: MigrationAction

    def __post_init__(self) -> None:
        if self.target_version < 1:
            raise ValueError(
                "Migration target version "
                "must be at least one."
            )

        if not self.name.strip():
            raise ValueError(
                "Migration name must not be empty."
            )


@dataclass(frozen=True, slots=True)
class SQLiteMigrationResult:
    initial_version: int | None
    final_version: int
    applied_versions: tuple[int, ...]

    @property
    def changed(
        self,
    ) -> bool:
        return bool(
            self.applied_versions
        )


def apply_schema_v1(
    connection: sqlite3.Connection,
) -> None:
    _execute_migration_script(
        connection,
        read_schema_v1(),
    )


def apply_schema_v2(
    connection: sqlite3.Connection,
) -> None:
    evidence_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM evidence
        """
    ).fetchone()

    lifecycle_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM evidence_lifecycle
        """
    ).fetchone()

    if (
        evidence_count is None
        or lifecycle_count is None
    ):
        raise SQLiteMigrationError(
            "Could not inspect v1 Evidence tables."
        )

    if (
        int(
            evidence_count[0]
        )
        > 0
        or int(
            lifecycle_count[0]
        )
        > 0
    ):
        raise UnsafeMigrationError(
            "Schema v1 contains persisted "
            "Evidence data. Automatic migration "
            "to schema v2 was refused because "
            "schema v1 cannot represent all "
            "fields required by the current "
            "Evidence Domain Model."
        )

    _execute_migration_script(
        connection,
        read_schema_v2(),
    )


def _execute_migration_script(
    connection: sqlite3.Connection,
    schema_sql: str,
) -> None:
    script = "\n".join(
        (
            "BEGIN IMMEDIATE;",
            schema_sql,
            "COMMIT;",
        )
    )

    try:
        connection.executescript(
            script
        )

    except Exception:
        if connection.in_transaction:
            connection.rollback()

        raise


DEFAULT_MIGRATIONS = (
    SQLiteMigration(
        target_version=1,
        name="create_initial_schema",
        apply=apply_schema_v1,
    ),
    SQLiteMigration(
        target_version=2,
        name="normalize_evidence_persistence",
        apply=apply_schema_v2,
    ),
)


class SQLiteMigrator:
    def __init__(
        self,
        migrations: tuple[
            SQLiteMigration,
            ...,
        ] = DEFAULT_MIGRATIONS,
        supported_version: int = SCHEMA_VERSION,
    ) -> None:
        if supported_version < 1:
            raise ValueError(
                "Supported schema version "
                "must be at least one."
            )

        versions = tuple(
            migration.target_version
            for migration in migrations
        )

        if len(
            versions
        ) != len(
            set(
                versions
            )
        ):
            raise ValueError(
                "Migration target versions "
                "must be unique."
            )

        if tuple(
            sorted(
                versions
            )
        ) != versions:
            raise ValueError(
                "Migrations must be ordered "
                "by target version."
            )

        self._migrations = migrations
        self._supported_version = (
            supported_version
        )

    @property
    def supported_version(
        self,
    ) -> int:
        return self._supported_version

    def migrate(
        self,
        connection: sqlite3.Connection,
    ) -> SQLiteMigrationResult:
        connection.execute(
            "PRAGMA foreign_keys = ON"
        )

        initial_version = (
            get_schema_version(
                connection
            )
        )

        if initial_version is None:
            self._validate_unversioned_database(
                connection
            )

            current_version = 0

        else:
            current_version = (
                initial_version
            )

        if (
            current_version
            > self._supported_version
        ):
            raise UnsupportedSchemaVersionError(
                "Database schema version "
                f"{current_version} is newer than "
                "the maximum supported version "
                f"{self._supported_version}."
            )

        applied_versions: list[int] = []

        while (
            current_version
            < self._supported_version
        ):
            target_version = (
                current_version + 1
            )

            migration = self._find_migration(
                target_version
            )

            try:
                migration.apply(
                    connection
                )

            except UnsafeMigrationError:
                raise

            except Exception as error:
                if connection.in_transaction:
                    connection.rollback()

                raise SQLiteMigrationError(
                    "SQLite migration failed: "
                    f"{migration.name} "
                    f"(version {target_version})."
                ) from error

            actual_version = (
                get_schema_version(
                    connection
                )
            )

            if (
                actual_version
                != target_version
            ):
                raise SQLiteMigrationError(
                    "Migration did not record "
                    "the expected schema version. "
                    f"Expected {target_version}, "
                    f"found {actual_version}."
                )

            applied_versions.append(
                target_version
            )

            current_version = (
                target_version
            )

        return SQLiteMigrationResult(
            initial_version=(
                initial_version
            ),
            final_version=(
                current_version
            ),
            applied_versions=tuple(
                applied_versions
            ),
        )

    def _find_migration(
        self,
        target_version: int,
    ) -> SQLiteMigration:
        for migration in self._migrations:
            if (
                migration.target_version
                == target_version
            ):
                return migration

        raise MissingMigrationError(
            "No SQLite migration registered "
            f"for schema version {target_version}."
        )

    @staticmethod
    def _validate_unversioned_database(
        connection: sqlite3.Connection,
    ) -> None:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE
                type = 'table'
                AND name NOT LIKE 'sqlite_%'
                AND name != ?
            ORDER BY name
            """,
            (
                "schema_metadata",
            ),
        ).fetchall()

        existing_tables = tuple(
            str(
                row[0]
            )
            for row in rows
        )

        if not existing_tables:
            return

        raise UnversionedDatabaseError(
            "The SQLite database contains "
            "application tables but has no "
            f"{SCHEMA_NAME} schema version. "
            "Automatic migration was refused. "
            "Existing tables: "
            + ", ".join(
                existing_tables
            )
        )
