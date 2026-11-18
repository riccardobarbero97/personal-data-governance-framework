import sqlite3
from importlib.resources import files
from typing import Final


SCHEMA_NAME: Final[str] = (
    "personal_data_governance"
)

SCHEMA_VERSION: Final[int] = 3

SCHEMA_V1_RESOURCE_NAME: Final[str] = (
    "schema_v1.sql"
)

SCHEMA_V2_RESOURCE_NAME: Final[str] = (
    "schema_v2.sql"
)

SCHEMA_V3_RESOURCE_NAME: Final[str] = (
    "schema_v3.sql"
)


def read_schema_v1() -> str:
    return _read_schema_resource(
        SCHEMA_V1_RESOURCE_NAME
    )


def read_schema_v2() -> str:
    return _read_schema_resource(
        SCHEMA_V2_RESOURCE_NAME
    )


def read_schema_v3() -> str:
    return _read_schema_resource(
        SCHEMA_V3_RESOURCE_NAME
    )


def _read_schema_resource(
    resource_name: str,
) -> str:
    schema_resource = (
        files(
            "personal_data_governance"
            ".infrastructure"
            ".persistence"
            ".sqlite"
        )
        .joinpath(
            resource_name
        )
    )

    schema_sql = schema_resource.read_text(
        encoding="utf-8"
    )

    if not schema_sql.strip():
        raise ValueError(
            "SQLite schema resource "
            "must not be empty: "
            f"{resource_name}"
        )

    return schema_sql


def create_schema_v1(
    connection: sqlite3.Connection,
) -> None:
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.executescript(
        read_schema_v1()
    )

    connection.commit()


def get_schema_version(
    connection: sqlite3.Connection,
) -> int | None:
    table_exists = connection.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE
            type = 'table'
            AND name = 'schema_metadata'
        """
    ).fetchone()

    if table_exists is None:
        return None

    row = connection.execute(
        """
        SELECT schema_version
        FROM schema_metadata
        WHERE schema_name = ?
        """,
        (
            SCHEMA_NAME,
        ),
    ).fetchone()

    if row is None:
        return None

    return int(
        row[0]
    )


def list_schema_tables(
    connection: sqlite3.Connection,
) -> tuple[str, ...]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE
            type = 'table'
            AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()

    return tuple(
        str(
            row[0]
        )
        for row in rows
    )
