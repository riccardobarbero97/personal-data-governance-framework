from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from personal_data_governance.domain.entities.observation import (
    Observation,
)
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import (
    TemporalValue,
)
from personal_data_governance.infrastructure.persistence.sqlite.codecs import (
    deserialize_datetime,
    deserialize_observation_payload,
    serialize_datetime,
    serialize_observation_payload,
)
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)


class SQLiteObservationRepository:
    def __init__(
        self,
        database: SQLiteDatabase,
    ) -> None:
        self._database = database

    def save(
        self,
        observation: Observation,
    ) -> None:
        (
            payload_type,
            payload_json,
        ) = serialize_observation_payload(
            observation.payload
        )

        observed_at_timestamp = None
        observed_at_semantics = None

        if observation.observed_at is not None:
            observed_at_timestamp = (
                serialize_datetime(
                    observation
                    .observed_at
                    .timestamp
                )
            )

            observed_at_semantics = (
                observation
                .observed_at
                .semantics
                .value
            )

        source_reference_value = (
            observation.source_reference.value
            if observation.source_reference
            is not None
            else None
        )

        created_at = serialize_datetime(
            datetime.now(
                timezone.utc
            )
        )

        try:
            with self._database.transaction() as connection:
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
                    ON CONFLICT (
                        observation_id
                    )
                    DO NOTHING
                    """,
                    (
                        observation.id.value,
                        (
                            observation
                            .connected_source_id
                            .value
                        ),
                        (
                            observation
                            .observation_type
                            .value
                        ),
                        (
                            observation
                            .schema_version
                            .value
                        ),
                        source_reference_value,
                        observed_at_timestamp,
                        observed_at_semantics,
                        serialize_datetime(
                            observation.collected_at
                        ),
                        payload_type,
                        payload_json,
                        created_at,
                    ),
                )

        except sqlite3.IntegrityError as error:
            if (
                source_reference_value
                is not None
                and self.find_by_source_reference(
                    connected_source_id=(
                        observation
                        .connected_source_id
                    ),
                    source_reference=(
                        observation
                        .source_reference
                    ),
                )
                is not None
            ):
                return

            raise error

    def get(
        self,
        observation_id: ObservationId,
    ) -> Observation | None:
        with self._database.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    observation_id,
                    connected_source_id,
                    observation_type,
                    schema_version,
                    source_reference_value,
                    observed_at_timestamp,
                    observed_at_semantics,
                    collected_at,
                    payload_type,
                    payload_json
                FROM observations
                WHERE observation_id = ?
                """,
                (
                    observation_id.value,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._map_row(
            row
        )

    def find_by_source_reference(
        self,
        connected_source_id: ConnectedSourceId,
        source_reference: SourceReference,
    ) -> Observation | None:
        with self._database.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    observation_id,
                    connected_source_id,
                    observation_type,
                    schema_version,
                    source_reference_value,
                    observed_at_timestamp,
                    observed_at_semantics,
                    collected_at,
                    payload_type,
                    payload_json
                FROM observations
                WHERE
                    connected_source_id = ?
                    AND source_reference_value = ?
                """,
                (
                    connected_source_id.value,
                    source_reference.value,
                ),
            ).fetchone()

        if row is None:
            return None

        return self._map_row(
            row
        )

    def list_by_connected_source(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> tuple[
        Observation,
        ...,
    ]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    observation_id,
                    connected_source_id,
                    observation_type,
                    schema_version,
                    source_reference_value,
                    observed_at_timestamp,
                    observed_at_semantics,
                    collected_at,
                    payload_type,
                    payload_json
                FROM observations
                WHERE connected_source_id = ?
                ORDER BY
                    collected_at,
                    observation_id
                """,
                (
                    connected_source_id.value,
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
    ) -> Observation:
        source_reference_value = row[
            "source_reference_value"
        ]

        observed_at_timestamp = row[
            "observed_at_timestamp"
        ]

        observed_at_semantics = row[
            "observed_at_semantics"
        ]

        source_reference = (
            SourceReference(
                source_reference_value
            )
            if source_reference_value
            is not None
            else None
        )

        observed_at = None

        if observed_at_timestamp is not None:
            if observed_at_semantics is None:
                raise ValueError(
                    "Persisted Observation has "
                    "a timestamp without temporal "
                    "semantics."
                )

            observed_at = TemporalValue(
                timestamp=(
                    deserialize_datetime(
                        observed_at_timestamp
                    )
                ),
                semantics=TemporalSemantics(
                    observed_at_semantics
                ),
            )

        return Observation(
            id=ObservationId(
                row[
                    "observation_id"
                ]
            ),
            connected_source_id=(
                ConnectedSourceId(
                    row[
                        "connected_source_id"
                    ]
                )
            ),
            observation_type=ObservationType(
                row[
                    "observation_type"
                ]
            ),
            schema_version=SchemaVersion(
                int(
                    row[
                        "schema_version"
                    ]
                )
            ),
            source_reference=(
                source_reference
            ),
            observed_at=observed_at,
            collected_at=(
                deserialize_datetime(
                    row[
                        "collected_at"
                    ]
                )
            ),
            payload=(
                deserialize_observation_payload(
                    payload_type=row[
                        "payload_type"
                    ],
                    payload_json=row[
                        "payload_json"
                    ],
                )
            ),
        )
