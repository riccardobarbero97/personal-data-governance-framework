from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone

from personal_data_governance.application.ports.repositories import (
    EvidenceLifecycleProvenance,
)
from personal_data_governance.domain.entities.evidence import (
    Evidence,
)
from personal_data_governance.domain.enums.evidence import (
    EvidenceStatus,
    EvidenceType,
)
from personal_data_governance.domain.enums.processing import (
    ClassificationMethod,
)
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    IdentitySeedId,
    ObservationId,
    ServiceId,
)
from personal_data_governance.infrastructure.persistence.sqlite.codecs import (
    SQLiteDeserializationError,
    deserialize_datetime,
    serialize_datetime,
)
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)


class SQLiteEvidenceRepository:
    def __init__(
        self,
        database: SQLiteDatabase,
    ) -> None:
        self._database = database

    def save(
        self,
        evidence: Evidence,
    ) -> None:
        if not evidence.observation_ids:
            raise ValueError(
                "Evidence must reference "
                "at least one Observation."
            )

        now = serialize_datetime(
            datetime.now(
                timezone.utc
            )
        )

        identity_seed_ids_json = (
            self._serialize_string_values(
                tuple(
                    identity_seed_id.value
                    for identity_seed_id
                    in evidence.identity_seed_ids
                )
            )
        )

        reason_codes_json = (
            self._serialize_string_values(
                evidence.reason_codes
            )
        )

        with self._database.transaction() as connection:
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
                    evidence_id
                )
                DO UPDATE SET
                    service_id = excluded.service_id,
                    evidence_type = excluded.evidence_type,
                    evidence_status = excluded.evidence_status,
                    identity_seed_ids_json = (
                        excluded.identity_seed_ids_json
                    ),
                    classification_method = (
                        excluded.classification_method
                    ),
                    classifier_version = (
                        excluded.classifier_version
                    ),
                    reason_codes_json = (
                        excluded.reason_codes_json
                    ),
                    updated_at = excluded.updated_at
                """,
                (
                    evidence.id.value,
                    (
                        evidence.service_id.value
                        if evidence.service_id
                        is not None
                        else None
                    ),
                    evidence.evidence_type.value,
                    evidence.evidence_status.value,
                    identity_seed_ids_json,
                    (
                        evidence
                        .classification_method
                        .value
                    ),
                    evidence.classifier_version,
                    reason_codes_json,
                    now,
                    now,
                ),
            )

            connection.execute(
                """
                DELETE FROM evidence_observations
                WHERE evidence_id = ?
                """,
                (
                    evidence.id.value,
                ),
            )

            for observation_id in (
                evidence.observation_ids
            ):
                connection.execute(
                    """
                    INSERT INTO evidence_observations (
                        evidence_id,
                        observation_id
                    )
                    VALUES (
                        ?,
                        ?
                    )
                    """,
                    (
                        evidence.id.value,
                        observation_id.value,
                    ),
                )

    def get(
        self,
        evidence_id: EvidenceId,
    ) -> Evidence | None:
        with self._database.connection() as connection:
            row = connection.execute(
                """
                SELECT
                    evidence_id,
                    service_id,
                    evidence_type,
                    evidence_status,
                    identity_seed_ids_json,
                    classification_method,
                    classifier_version,
                    reason_codes_json
                FROM evidence
                WHERE evidence_id = ?
                """,
                (
                    evidence_id.value,
                ),
            ).fetchone()

            if row is None:
                return None

            return self._map_row(
                connection=connection,
                row=row,
            )

    def find_by_observation(
        self,
        observation_id: ObservationId,
    ) -> tuple[
        Evidence,
        ...,
    ]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    evidence.evidence_id,
                    evidence.service_id,
                    evidence.evidence_type,
                    evidence.evidence_status,
                    evidence.identity_seed_ids_json,
                    evidence.classification_method,
                    evidence.classifier_version,
                    evidence.reason_codes_json
                FROM evidence
                INNER JOIN evidence_observations
                    ON evidence_observations.evidence_id
                    = evidence.evidence_id
                WHERE
                    evidence_observations.observation_id
                    = ?
                ORDER BY evidence.evidence_id
                """,
                (
                    observation_id.value,
                ),
            ).fetchall()

            return tuple(
                self._map_row(
                    connection=connection,
                    row=row,
                )
                for row in rows
            )

    def find_active_by_service(
        self,
        service_id: ServiceId,
    ) -> tuple[
        Evidence,
        ...,
    ]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    evidence_id,
                    service_id,
                    evidence_type,
                    evidence_status,
                    identity_seed_ids_json,
                    classification_method,
                    classifier_version,
                    reason_codes_json
                FROM evidence
                WHERE
                    service_id = ?
                    AND evidence_status = ?
                ORDER BY evidence_id
                """,
                (
                    service_id.value,
                    EvidenceStatus.ACTIVE.value,
                ),
            ).fetchall()

            return tuple(
                self._map_row(
                    connection=connection,
                    row=row,
                )
                for row in rows
            )

    def change_status(
        self,
        evidence_id: EvidenceId,
        new_status: EvidenceStatus,
        provenance: EvidenceLifecycleProvenance,
    ) -> None:
        changed_at = serialize_datetime(
            provenance.changed_at
        )

        with self._database.transaction() as connection:
            row = connection.execute(
                """
                SELECT evidence_status
                FROM evidence
                WHERE evidence_id = ?
                """,
                (
                    evidence_id.value,
                ),
            ).fetchone()

            if row is None:
                raise KeyError(
                    "Evidence not found: "
                    f"{evidence_id.value}"
                )

            current_status = EvidenceStatus(
                row[
                    "evidence_status"
                ]
            )

            if current_status == new_status:
                return

            if (
                current_status
                != EvidenceStatus.ACTIVE
            ):
                raise ValueError(
                    "Only ACTIVE Evidence may "
                    "transition in the initial "
                    "lifecycle model."
                )

            if new_status not in {
                EvidenceStatus.SUPERSEDED,
                EvidenceStatus.REJECTED,
            }:
                raise ValueError(
                    "ACTIVE Evidence may only "
                    "transition to SUPERSEDED "
                    "or REJECTED."
                )

            updated_at = serialize_datetime(
                datetime.now(
                    timezone.utc
                )
            )

            connection.execute(
                """
                UPDATE evidence
                SET
                    evidence_status = ?,
                    updated_at = ?
                WHERE evidence_id = ?
                """,
                (
                    new_status.value,
                    updated_at,
                    evidence_id.value,
                ),
            )

            connection.execute(
                """
                INSERT INTO evidence_lifecycle (
                    evidence_id,
                    previous_status,
                    new_status,
                    reason_code,
                    actor,
                    superseded_by_evidence_id,
                    changed_at
                )
                VALUES (
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
                    evidence_id.value,
                    current_status.value,
                    new_status.value,
                    provenance.reason_code,
                    provenance.actor,
                    (
                        provenance
                        .superseded_by
                        .value
                        if provenance
                        .superseded_by
                        is not None
                        else None
                    ),
                    changed_at,
                ),
            )

    def get_lifecycle_history(
        self,
        evidence_id: EvidenceId,
    ) -> tuple[
        EvidenceLifecycleProvenance,
        ...,
    ]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    changed_at,
                    reason_code,
                    actor,
                    superseded_by_evidence_id
                FROM evidence_lifecycle
                WHERE evidence_id = ?
                ORDER BY
                    changed_at,
                    lifecycle_event_id
                """,
                (
                    evidence_id.value,
                ),
            ).fetchall()

        return tuple(
            EvidenceLifecycleProvenance(
                changed_at=deserialize_datetime(
                    row[
                        "changed_at"
                    ]
                ),
                reason_code=row[
                    "reason_code"
                ],
                actor=row[
                    "actor"
                ],
                superseded_by=(
                    EvidenceId(
                        row[
                            "superseded_by_evidence_id"
                        ]
                    )
                    if row[
                        "superseded_by_evidence_id"
                    ]
                    is not None
                    else None
                ),
            )
            for row in rows
        )

    def list_all(
        self,
    ) -> tuple[
        Evidence,
        ...,
    ]:
        with self._database.connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    evidence_id,
                    service_id,
                    evidence_type,
                    evidence_status,
                    identity_seed_ids_json,
                    classification_method,
                    classifier_version,
                    reason_codes_json
                FROM evidence
                ORDER BY evidence_id
                """
            ).fetchall()

            return tuple(
                self._map_row(
                    connection=connection,
                    row=row,
                )
                for row in rows
            )

    @staticmethod
    def _map_row(
        connection: sqlite3.Connection,
        row: sqlite3.Row,
    ) -> Evidence:
        observation_rows = connection.execute(
            """
            SELECT observation_id
            FROM evidence_observations
            WHERE evidence_id = ?
            ORDER BY rowid
            """,
            (
                row[
                    "evidence_id"
                ],
            ),
        ).fetchall()

        observation_ids = tuple(
            ObservationId(
                observation_row[
                    "observation_id"
                ]
            )
            for observation_row
            in observation_rows
        )

        if not observation_ids:
            raise SQLiteDeserializationError(
                "Persisted Evidence must reference "
                "at least one Observation: "
                f"{row['evidence_id']}"
            )

        identity_seed_values = (
            SQLiteEvidenceRepository
            ._deserialize_string_values(
                row[
                    "identity_seed_ids_json"
                ],
                field_name=(
                    "identity_seed_ids_json"
                ),
            )
        )

        reason_codes = (
            SQLiteEvidenceRepository
            ._deserialize_string_values(
                row[
                    "reason_codes_json"
                ],
                field_name=(
                    "reason_codes_json"
                ),
            )
        )

        service_id_value = row[
            "service_id"
        ]

        return Evidence(
            id=EvidenceId(
                row[
                    "evidence_id"
                ]
            ),
            evidence_type=EvidenceType(
                row[
                    "evidence_type"
                ]
            ),
            evidence_status=EvidenceStatus(
                row[
                    "evidence_status"
                ]
            ),
            observation_ids=(
                observation_ids
            ),
            service_id=(
                ServiceId(
                    service_id_value
                )
                if service_id_value
                is not None
                else None
            ),
            identity_seed_ids=tuple(
                IdentitySeedId(
                    value
                )
                for value in (
                    identity_seed_values
                )
            ),
            classification_method=(
                ClassificationMethod(
                    row[
                        "classification_method"
                    ]
                )
            ),
            classifier_version=row[
                "classifier_version"
            ],
            reason_codes=(
                reason_codes
            ),
        )

    @staticmethod
    def _serialize_string_values(
        values: tuple[
            str,
            ...,
        ],
    ) -> str:
        return json.dumps(
            list(
                values
            ),
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

    @staticmethod
    def _deserialize_string_values(
        serialized_value: str,
        field_name: str,
    ) -> tuple[
        str,
        ...,
    ]:
        try:
            values = json.loads(
                serialized_value
            )

        except json.JSONDecodeError as error:
            raise SQLiteDeserializationError(
                "Persisted Evidence field "
                f"{field_name} contains "
                "invalid JSON."
            ) from error

        if (
            not isinstance(
                values,
                list,
            )
            or not all(
                isinstance(
                    value,
                    str,
                )
                for value in values
            )
        ):
            raise SQLiteDeserializationError(
                "Persisted Evidence field "
                f"{field_name} must contain "
                "a JSON list of strings."
            )

        return tuple(
            values
        )
