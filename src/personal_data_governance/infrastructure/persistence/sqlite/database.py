from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from personal_data_governance.infrastructure.persistence.sqlite.migrations import (
    SQLiteMigrationResult,
    SQLiteMigrator,
)


DEFAULT_BUSY_TIMEOUT_MILLISECONDS = 5000


class SQLiteDatabase:
    def __init__(
        self,
        database_file: Path,
        migrator: SQLiteMigrator | None = None,
        busy_timeout_milliseconds: int = (
            DEFAULT_BUSY_TIMEOUT_MILLISECONDS
        ),
    ) -> None:
        if (
            busy_timeout_milliseconds
            < 0
        ):
            raise ValueError(
                "SQLite busy timeout "
                "must not be negative."
            )

        self._database_file = (
            database_file
        )

        self._migrator = (
            migrator
            if migrator is not None
            else SQLiteMigrator()
        )

        self._busy_timeout_milliseconds = (
            busy_timeout_milliseconds
        )

    @property
    def database_file(
        self,
    ) -> Path:
        return self._database_file

    def initialize(
        self,
    ) -> SQLiteMigrationResult:
        self._database_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.connection() as connection:
            return self._migrator.migrate(
                connection
            )

    @contextmanager
    def connection(
        self,
    ) -> Iterator[
        sqlite3.Connection
    ]:
        connection = self._open_connection()

        try:
            yield connection

        finally:
            connection.close()

    @contextmanager
    def transaction(
        self,
    ) -> Iterator[
        sqlite3.Connection
    ]:
        connection = self._open_connection()

        try:
            connection.execute(
                "BEGIN IMMEDIATE"
            )

            yield connection

            connection.commit()

        except Exception:
            if connection.in_transaction:
                connection.rollback()

            raise

        finally:
            connection.close()

    def _open_connection(
        self,
    ) -> sqlite3.Connection:
        self._database_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        connection = sqlite3.connect(
            self._database_file,
            timeout=(
                self._busy_timeout_milliseconds
                / 1000
            ),
        )

        connection.row_factory = (
            sqlite3.Row
        )

        try:
            connection.execute(
                "PRAGMA foreign_keys = ON"
            )

            connection.execute(
                "PRAGMA busy_timeout = "
                f"{self._busy_timeout_milliseconds}"
            )

            foreign_keys = connection.execute(
                "PRAGMA foreign_keys"
            ).fetchone()

            if (
                foreign_keys is None
                or foreign_keys[0] != 1
            ):
                raise RuntimeError(
                    "SQLite foreign keys "
                    "could not be enabled."
                )

            busy_timeout = connection.execute(
                "PRAGMA busy_timeout"
            ).fetchone()

            if (
                busy_timeout is None
                or busy_timeout[0]
                != self._busy_timeout_milliseconds
            ):
                raise RuntimeError(
                    "SQLite busy timeout "
                    "could not be configured."
                )

            return connection

        except Exception:
            connection.close()
            raise
