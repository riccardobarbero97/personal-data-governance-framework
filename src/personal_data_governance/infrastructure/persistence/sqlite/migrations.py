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
    read_schema_v3,
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


def apply_schema_v3(
    connection: sqlite3.Connection,
) -> None:
    relationship_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM relationships
     *  """
    ).fetchone()

    if rel*tionship_count is None:
        ra*se SQLiteMigrationError(
         *  "Could not inspect the v2 "
    *       "Relationship table."
     *  )

    if int(
        relations*ip_count[0]
    ) > 0:
        rai*e UnsafeMigrationError(
          * "Schema v2 contains persisted "
 *          "Relationship data. Auto*atic "
            "migration to s*hema v3 was "
            "refused*because schema v2 does "
         *  "not preserve assessment_method.*
        )

    _execute_migration*script(
        connection,
      * read_schema_v3(),
    )


def _ex*cute_migration_script(
    connect*on: sqlite3.Connection,
    schema*sql: str,
) -> None:
    script = *\n".join(
        (
            "B*GIN IMMEDIATE;",
            schem*_sql,
            "COMMIT;",
     *  )
    )

    try:
        connec*ion.executescript(
            scr*pt
        )

    except Exception*
        if connection.in_transact*on:
            connection.rollbac*()

        raise


DEFAULT_MIGRAT*ONS = (
    SQLiteMigration(
     *  target_version=1,
        name="*reate_initial_schema",
        app*y=apply_schema_v1,
    ),
    SQLi*eMigration(
        target_version*2,
        name="normalize_evidenc*_persistence",
        apply=apply*schema_v2,
    ),
    SQLiteMigrat*on(
        target_version=3,
    *   name=(
            "add_relatio*ship_assessment_method"
        ),*        apply=apply_schema_v3,
   *),
)


class SQLiteMigrator:
    d*f __init__(
        self,
        *igrations: tuple[
            SQLiteMigration,
            ...,
        ] = DEFAULT_MIGRATIONS,
        *upported_version: int = SCHEMA_VER*ION,
    ) -> None:
        if sup*orted_version < 1:
            rai*e ValueError(
                "Sup*orted schema version "
           *    "must be at least one."
      *     )

        versions = tuple(
*           migration.target_versio*
            for migration in migr*tions
        )

        if len(
 *          versions
        ) != le*(
            set(
               *versions
            )
        ):
*           raise ValueError(
     *          "Migration target versio*s "
                "must be uniqu*."
            )

        if tuple*
            sorted(
             *  versions
            )
        )*!= versions:
            raise Val*eError(
                "Migration* must be ordered "
               *"by target version."
            )*
        self._migrations = migrat*ons
        self._supported_versio* = (
            supported_version*        )

    @property
    def s*pported_version(
        self,
   *) -> int:
        return self._sup*orted_version

    def migrate(
  *     self,
        connection: sql*te3.Connection,
    ) -> SQLiteMig*ationResult:
        connection.ex*cute(
            "PRAGMA foreign_*eys = ON"
        )

        initi*l_version = (
            get_sche*a_version(
                connect*on
            )
        )

      * if initial_version is None:
     *      self._validate_unversioned_d*tabase(
                connection*            )

            current*version = 0

        else:
       *    current_version = (
          *     initial_version
            )*
        if (
            current_*ersion
            > self._support*d_version
        ):
            r*ise UnsupportedSchemaVersionError(*                "Database schema v*rsion "
                f"{current*version} is newer than "
         *      "the maximum supported versi*n "
                f"{self._suppo*ted_version}."
            )

    *   applied_versions: list[int] = []

        while (
            curr*nt_version
            < self._sup*orted_version
        ):
         *  target_version = (
             *  current_version + 1
            *

            migration = self._fi*d_migration(
                targe*_version
            )

          * try:
                migration.ap*ly(
                    connection*                )

            exc*pt UnsafeMigrationError:
         *      raise

            except Ex*eption as error:
                i* connection.in_transaction:
      *             connection.rollback()*
                raise SQLiteMigra*ionError(
                    "SQL*te migration failed: "
           *        f"{migration.name} "
     *              f"(version {target_v*rsion})."
                ) from e*ror

            actual_version = *
                get_schema_versio*(
                    connection
 *              )
            )

   *        if (
                actua*_version
                != target*version
            ):
           *    raise SQLiteMigrationError(
  *                 "Migration did no* record "
                    "the*expected schema version. "
       *            f"Expected {target_ver*ion}, "
                    f"foun* {actual_version}."
              * )

            applied_versions.a*pend(
                target_versi*n
            )

            curre*t_version = (
                targ*t_version
            )

        r*turn SQLiteMigrationResult(
      *     initial_version=(
           *    initial_version
            ),*            final_version=(
      *         current_version
         *  ),
            applied_versions=*uple(
                applied_vers*ons
            ),
        )

    *ef _find_migration(
        self,
*       target_version: int,
    ) *> SQLiteMigration:
        for mig*ation in self._migrations:
       *    if (
                migration*target_version
                == *arget_version
            ):
     *          return migration

      * raise MissingMigrationError(
    *       "No SQLite migration regist*red "
            f"for schema ver*ion {target_version}."
        )

*   @staticmethod
    def _validate*unversioned_database(
        conn*ction: sqlite3.Connection,
    ) -* None:
        rows = connection.e*ecute(
            """
           *SELECT name
            FROM sqlit*_master
            WHERE
        *       type = 'table'
            *   AND name NOT LIKE 'sqlite_%'
  *             AND name != ?
       *    ORDER BY name
            """,*            (
                "sch*ma_metadata",
            ),
     *  ).fetchall()

        existing_t*bles = tuple(
            str(
   *            row[0]
            )
 *          for row in rows
        *

        if not existing_tables:
*           return

        raise U*versionedDatabaseError(
          * "The SQLite database contains "
 *          "application tables but *as no "
            f"{SCHEMA_NAME* schema version. "
            "Au*omatic migration was refused. "
  *         "Existing tables: "
     *      + ", ".join(
               *existing_tables
            )
    *   )
