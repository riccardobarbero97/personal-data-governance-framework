from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.application.results.classification import (
    EvidenceCandidate,
)
from personal_data_governance.application.services.evidence_materializer import (
    EvidenceMaterializer,
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
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)
from personal_data_governance.infrastructure.persistence.sqlite.evidence_repository import (
    SQLiteEvidenceRepository,
)


OBSERVATION_ID = ObservationId(
    "observation_001"
)

SERVICE_ID = ServiceId(
    "service_spotify"
)

IDENTITY_SEED_ID = IdentitySeedId(
    "identity_email"
)

CHANGED_AT = datetime(
    2026,
    12,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)


class SequentialEvidenceIdFactory:
    def __init__(
        self,
        starting_value: int = 0,
    ) -> None:
        self._counter = starting_value

    def __call__(
        self,
    ) -> EvidenceId:
        self._counter += 1

        return EvidenceId(
            f"evidence_{self._counter:03d}"
        )


def initialize_database(
    database_file: Path,
) -> SQLiteDatabase:
    database = SQLiteDatabase(
        database_file
    )

    database.initialize()

    with database.transaction() as connection:
        existing_source = connection.execute(
            """
            SELECT connected_source_id
            FROM connected_sources
            WHERE connected_source_id = ?
            """,
            (
                "source_gmail",
            ),
        ).fetchone()

        if existing_source is None:
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

        existing_observation = connection.execute(
            """
            SELECT observation_id
            FROM observations
            WHERE observation_id = ?
            """,
            (
                OBSERVATION_ID.value,
            ),
        ).fetchone()

        if existing_observation is None:
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
                    OBSERVATION_ID.value,
                    "source_gmail",
                    "EMAIL_MESSAGE_METADATA",
                    1,
                    "gmail_message_001",
                    (
                        "2026-11-15"
                        "T08:00:00+00:00"
                    ),
                    "MESSAGE_TIME",
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

    return database


def build_candidate(
    evidence_type: EvidenceType = (
        EvidenceType.ACCOUNT_VERIFICATION
    ),
    classifier_version: str = "rules-1",
    reason_codes: tuple[
        str,
        ...,
    ] = (
        "ACCOUNT_VERIFICATION_SUBJECT",
    ),
) -> EvidenceCandidate:
    return EvidenceCandidate(
        evidence_type=evidence_type,
        observation_ids=(
            OBSERVATION_ID,
        ),
        method=(
            ClassificationMethod.RULE
        ),
        classifier_version=(
            classifier_version
        ),
        reason_codes=reason_codes,
    )


def test_materializer_reuses_evidence_after_database_restart(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    first_database = (
        initialize_database(
            database_file
        )
    )

    first_repository = (
        SQLiteEvidenceRepository(
            first_database
        )
    )

    first_materializer = (
        EvidenceMaterializer(
            evidence_repository=(
                first_repository
            ),
            evidence_id_factory=(
                SequentialEvidenceIdFactory()
            ),
        )
    )

    candidate = build_candidate()

    first_result = (
        first_materializer.materialize(
            observation_id=(
                OBSERVATION_ID
            ),
            evidence_candidates=(
                candidate,
            ),
            service_id=(
                SERVICE_ID
            ),
            identity_seed_ids=(
                IDENTITY_SEED_ID,
            ),
            changed_at=(
                CHANGED_AT
            ),
        )
    )

    assert len(
        first_result
    ) == 1

    assert (
        first_result[0].id
        == EvidenceId(
            "evidence_001"
        )
    )

    assert (
        first_result[0].evidence_status
        == EvidenceStatus.ACTIVE
    )

    assert (
        len(
            first_repository.list_all()
        )
        == 1
    )

    second_database = SQLiteDatabase(
        database_file
    )

    migration_result = (
        second_database.initialize()
    )

    assert (
        migration_result.initial_version
        == 2
    )

    assert (
        migration_result.final_version
        == 2
    )

    assert (
        migration_result.applied_versions
        == ()
    )

    second_repository = (
        SQLiteEvidenceRepository(
            second_database
        )
    )

    second_id_factory = (
        SequentialEvidenceIdFactory(
            starting_value=1
        )
    )

    second_materializer = (
        EvidenceMaterializer(
            evidence_repository=(
                second_repository
            ),
            evidence_id_factory=(
                second_id_factory
            ),
        )
    )

    second_result = (
        second_materializer.materialize(
            observation_id=(
                OBSERVATION_ID
            ),
            evidence_candidates=(
                candidate,
            ),
            service_id=(
                SERVICE_ID
            ),
            identity_seed_ids=(
                IDENTITY_SEED_ID,
            ),
            changed_at=(
                CHANGED_AT
            ),
        )
    )

    assert len(
        second_result
    ) == 1

    assert (
        second_result[0]
        == first_result[0]
    )

    assert (
        second_result[0].id
        == EvidenceId(
            "evidence_001"
        )
    )

    persisted_evidence = (
        second_repository.list_all()
    )

    assert (
        persisted_evidence
        == (
            first_result[0],
        )
    )

    assert (
        second_repository
        .get_lifecycle_history(
            EvidenceId(
                "evidence_001"
            )
        )
        == ()
    )


def test_materializer_supersedes_stale_evidence_after_restart(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    first_database = (
        initialize_database(
            database_file
        )
    )

    first_repository = (
        SQLiteEvidenceRepository(
            first_database
        )
    )

    first_materializer = (
        EvidenceMaterializer(
            evidence_repository=(
                first_repository
            ),
            evidence_id_factory=(
                SequentialEvidenceIdFactory()
            ),
        )
    )

    original_candidate = build_candidate(
        evidence_type=(
            EvidenceType.ACCOUNT_VERIFICATION
        ),
        classifier_version=(
            "rules-1"
        ),
        reason_codes=(
            "ACCOUNT_VERIFICATION_SUBJECT",
        ),
    )

    original_result = (
        first_materializer.materialize(
            observation_id=(
                OBSERVATION_ID
            ),
            evidence_candidates=(
                original_candidate,
            ),
            service_id=(
                SERVICE_ID
            ),
            identity_seed_ids=(
                IDENTITY_SEED_ID,
            ),
            changed_at=(
                CHANGED_AT
            ),
        )
    )

    assert (
        original_result[0].id
        == EvidenceId(
            "evidence_001"
        )
    )

    second_database = SQLiteDatabase(
        database_file
    )

    second_database.initialize()

    second_repository = (
        SQLiteEvidenceRepository(
            second_database
        )
    )

    second_materializer = (
        EvidenceMaterializer(
            evidence_repository=(
                second_repository
            ),
            evidence_id_factory=(
                SequentialEvidenceIdFactory(
                    starting_value=1
                )
            ),
        )
    )

    replacement_candidate = (
        build_candidate(
            evidence_type=(
                EvidenceType.PAYMENT
            ),
            classifier_version=(
                "rules-2"
            ),
            reason_codes=(
                "PAYMENT_SUBJECT",
            ),
        )
    )

    replacement_result = (
        second_materializer.materialize(
            observation_id=(
                OBSERVATION_ID
            ),
            evidence_candidates=(
                replacement_candidate,
            ),
            service_id=(
                SERVICE_ID
            ),
            identity_seed_ids=(
                IDENTITY_SEED_ID,
            ),
            lifecycle_actor=(
                "classifier_rules_2"
            ),
            changed_at=(
                CHANGED_AT
            ),
        )
    )

    assert len(
        replacement_result
    ) == 1

    assert (
        replacement_result[0].id
        == EvidenceId(
            "evidence_002"
        )
    )

    original_evidence = (
        second_repository.get(
            EvidenceId(
                "evidence_001"
            )
        )
    )

    assert original_evidence is not None

    assert (
        original_evidence.evidence_status
        == EvidenceStatus.SUPERSEDED
    )

    replacement_evidence = (
        second_repository.get(
            EvidenceId(
                "evidence_002"
            )
        )
    )

    assert replacement_evidence is not None

    assert (
        replacement_evidence
        .evidence_status
        == EvidenceStatus.ACTIVE
    )

    history = (
        second_repository
        .get_lifecycle_history(
            EvidenceId(
                "evidence_001"
            )
        )
    )

    assert len(
        history
    ) == 1

    assert (
        history[0].reason_code
        == "CLASSIFICATION_REPLACED"
    )

    assert (
        history[0].actor
        == "classifier_rules_2"
    )

    assert (
        history[0].superseded_by
        == EvidenceId(
            "evidence_002"
        )
    )

    assert (
        history[0].changed_at
        == CHANGED_AT
    )


def test_materializer_rejection_survives_restart(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    first_database = (
        initialize_database(
            database_file
        )
    )

    first_repository = (
        SQLiteEvidenceRepository(
            first_database
        )
    )

    first_materializer = (
        EvidenceMaterializer(
            evidence_repository=(
                first_repository
            ),
            evidence_id_factory=(
                SequentialEvidenceIdFactory()
            ),
        )
    )

    candidate = build_candidate()

    result = (
        first_materializer.materialize(
            observation_id=(
                OBSERVATION_ID
            ),
            evidence_candidates=(
                candidate,
            ),
            service_id=(
                SERVICE_ID
            ),
            identity_seed_ids=(
                IDENTITY_SEED_ID,
            ),
            changed_at=(
                CHANGED_AT
            ),
        )
    )

    evidence_id = result[
        0
    ].id

    first_materializer.reject(
        evidence_id=evidence_id,
        reason_code=(
            "USER_REJECTED"
        ),
        actor="user",
        changed_at=(
            CHANGED_AT
        ),
    )

    second_database = SQLiteDatabase(
        database_file
    )

    second_database.initialize()

    second_repository = (
        SQLiteEvidenceRepository(
            second_database
        )
    )

    rejected_evidence = (
        second_repository.get(
            evidence_id
        )
    )

    assert rejected_evidence is not None

    assert (
        rejected_evidence.evidence_status
        == EvidenceStatus.REJECTED
    )

    assert (
        second_repository
        .find_active_by_service(
            SERVICE_ID
        )
        == ()
    )

    history = (
        second_repository
        .get_lifecycle_history(
            evidence_id
        )
    )

    assert len(
        history
    ) == 1

    assert (
        history[0].reason_code
        == "USER_REJECTED"
    )

    assert (
        history[0].actor
        == "user"
    )

    assert (
        history[0].changed_at
        == CHANGED_AT
    )
