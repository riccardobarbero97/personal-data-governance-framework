from __future__ import annotations

from datetime import datetime, timezone

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
from personal_data_governance.infrastructure.persistence.sqlite.codecs import (
    serialize_datetime,
)
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)


class SQLiteConnectedSourceRepository:
    def __init__(
        self,
        database: SQLiteDatabase,
    ) -> None:
        self._database = database

    def save(
        self,
        connected_source: ConnectedSource,
    ) -> None:
        now = serialize_datetime(
            datetime.now(
                timezone.utc
            )
        )

        with self._database.transaction() as connection:
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
                ON CONFLICT (
                    connected_source_id
                )
                DO UPDATE SET
                    user_id = excluded.user_id,
                    source_type = excluded.source_type,
                    provider_id = excluded.provider_id,
                    provider_display_name = (
                        excluded.provider_display_name
                    ),
                    connector_id = excluded.connector_id,
                    display_name = excluded.display_name,
                    external_account_reference = (
                        excluded.external_account_reference
                    ),
                    connection_state = (
                        excluded.connection_state
                    ),
                    authorization_state = (
                        excluded.authorization_state
                    ),
                    updated_at = excluded.updated_at
                """,
                (
                    connected_source.id.value,
                    connected_source.user_id.value,
                    connected_source.source_type.value,
                    connected_source.provider.id,
                    (
                        connected_source
                        .provider
                        .display_name
                    ),
                    connected_source.connector_id,
                    connected_source.display_name,
                    (
                        connected_source
                        .external_account_reference
                    ),
                    (
                        connected_source
                        .connection_state
                        .value
                    ),
                    (
                        connected_source
                        .authorization_state
                        .value
                    ),
                    now,
                    now,
                ),
            )

    def get(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> ConnectedSource | None:
        with self._database.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    connected_source_id,
                    user_id,
                    source_type,
                    provider_id,
                    provider_display_name,
                    connector_id,
                    display_name,
                    external_account_reference,
                    connection_state,
                    authorization_state
                FROM connected_sources
                WHERE connected_source_id = ?
                """,
                (
                    connected_source_id.value,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._map_row(
            row
        )

    def list_by_user(
        self,
        user_id: UserId,
    ) -> tuple[
        ConnectedSource,
        ...,
    ]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    connected_source_id,
                    user_id,
                    source_type,
                    provider_id,
                    provider_display_name,
                    connector_id,
                    display_name,
                    external_account_reference,
                    connection_state,
                    authorization_state
                FROM connected_sources
                WHERE user_id = ?
                ORDER BY connected_source_id
                """,
                (
                    user_id.value,
                ),
            ).fetchall()

        return tuple(
            self._map_row(
                row
            )
            for row in rows
        )

    @staticmethod
    def _map_row(
        row,
    ) -> ConnectedSource:
        return ConnectedSource(
            id=ConnectedSourceId(
                row[
                    "connected_source_id"
                ]
            ),
            user_id=UserId(
                row[
                    "user_id"
                ]
            ),
            source_type=SourceType(
                row[
                    "source_type"
                ]
            ),
            provider=Provider(
                id=row[
                    "provider_id"
                ],
                display_name=row[
                    "provider_display_name"
                ],
            ),
            connector_id=row[
                "connector_id"
            ],
            display_name=row[
                "display_name"
            ],
            external_account_reference=row[
                "external_account_reference"
            ],
            connection_state=ConnectionState(
                row[
                    "connection_state"
                ]
            ),
            authorization_state=(
                AuthorizationState(
                    row[
                        "authorization_state"
                    ]
                )
            ),
        )
