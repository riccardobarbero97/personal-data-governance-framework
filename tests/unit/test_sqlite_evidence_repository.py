import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

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
from personal_data_governance.infrastructure.persistence.sqlite.database import (
    SQLiteDatabase,
)
from personal_data_governance.infrastructure.persistence.sqlite.evidence_repository import (
    SQLiteEvidenceRepository,
)


CHANGED_AT = datetime(
    2026,
    12,
    1,
    12,
    0,
    tzinfo=timezone.utc,
)


def build_database(
    tmp_path: Path,
) -> SQLiteDatabase:
    database = SQLiteDatabase(
        tmp_path
        / "state.db"
    )

    database.initialize()

    with database.transaction() as connection:
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

        for index in range(
            1,
            4,
        ):
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
                    f"observation_{index:03d}",
                    "source_gmail",
                    "EMAIL_MESSAGE_METADATA",
                    1,
                    f"gmail_message_{index:03d}",
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


def build_evidence(
    evidence_id: str = "evidence_001",
    evidence_type: EvidenceType = (
        EvidenceType.ACCOUNT_VERIFICATION
    ),
    evidence_status: EvidenceStatus = (
        EvidenceStatus.ACTIVE
    ),
    observation_ids: tuple[
        ObservationId,
        ...,
    ] = (
        ObservationId(
            "observation_001"
        ),
    ),
    service_id: ServiceId | None = (
        ServiceId(
            "service_spotify"
        )
    ),
    identity_seed_ids: tuple[
        IdentitySeedId,
        ...,
    ] = (
        IdentitySeedId(
            "identity_email"
        ),
    ),
    classification_method: (
        ClassificationMethod
    ) = ClassificationMethod.RULE,
    classifier_version: str = "rules-1",
    reason_codes: tuple[
        str,
        ...,
    ] = (
        "EXACT_SUBJECT_PATTERN",
    ),
) -> Evidence:
    return Evidence(
        id=EvidenceId(
            evidence_id
        ),
        evidence_type=evidence_type,
        evidence_status=evidence_status,
        observation_ids=observation_ids,
        service_id=service_id,
        identity_seed_ids=(
            identity_seed_ids
        ),
        classification_method=(
            classification_method
        ),
        classifier_version=(
            classifier_version
        ),
        reason_codes=reason_codes,
    )


def test_evidence_round_trip(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence()

    repository.save(
        evidence
    )

    assert (
        repository.get(
            evidence.id
        )
        == evidence
    )


def test_evidence_with_multiple_observations_round_trip(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence(
        observation_ids=(
            ObservationId(
                "observation_001"
            ),
            ObservationId(
                "observation_002"
            ),
            ObservationId(
                "observation_003"
            ),
        )
    )

    repository.save(
        evidence
    )

    restored = repository.get(
        evidence.id
    )

    assert restored == evidence


def test_evidence_without_service_round_trip(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence(
        service_id=None
    )

    repository.save(
        evidence
    )

    restored = repository.get(
        evidence.id
    )

    assert restored == evidence

    assert restored is not None
    assert restored.service_id is None


def test_all_classification_methods_round_trip(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    for index, method in enumerate(
        ClassificationMethod,
        start=1,
    ):
        evidence = build_evidence(
            evidence_id=(
                f"evidence_{index:03d}"
            ),
            observation_ids=(
                ObservationId(
                    "observation_001"
                ),
            ),
            classification_method=(
                method
            ),
        )

        repository.save(
            evidence
        )

        restored = repository.get(
            evidence.id
        )

        assert restored is not None

        assert (
            restored.classification_method
            == method
        )


def test_missing_evidence_returns_none(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    assert (
        repository.get(
            EvidenceId(
                "evidence_missing"
            )
        )
        is None
    )


def test_find_by_observation(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    first = build_evidence(
        evidence_id="evidence_001",
        observation_ids=(
            ObservationId(
                "observation_001"
            ),
            ObservationId(
                "observation_002"
            ),
        ),
    )

    second = build_evidence(
        evidence_id="evidence_002",
        evidence_type=EvidenceType.PAYMENT,
        observation_ids=(
            ObservationId(
                "observation_002"
            ),
        ),
    )

    repository.save(
        first
    )

    repository.save(
        second
    )

    assert (
        repository.find_by_observation(
            ObservationId(
                "observation_002"
            )
        )
        == (
            first,
            second,
        )
    )


def test_find_active_by_service_excludes_non_active_evidence(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    active = build_evidence(
        evidence_id=(
            "evidence_active"
        ),
        evidence_status=(
            EvidenceStatus.ACTIVE
        ),
    )

    rejected = build_evidence(
        evidence_id=(
            "evidence_rejected"
        ),
        evidence_type=(
            EvidenceType.MARKETING
        ),
        evidence_status=(
            EvidenceStatus.REJECTED
        ),
        observation_ids=(
            ObservationId(
                "observation_002"
            ),
        ),
    )

    other_service = build_evidence(
        evidence_id=(
            "evidence_other"
        ),
        evidence_type=(
            EvidenceType.PAYMENT
        ),
        observation_ids=(
            ObservationId(
                "observation_003"
            ),
        ),
        service_id=ServiceId(
            "service_netflix"
        ),
    )

    repository.save(
        active
    )

    repository.save(
        rejected
    )

    repository.save(
        other_service
    )

    assert (
        repository.find_active_by_service(
            ServiceId(
                "service_spotify"
            )
        )
        == (
            active,
        )
    )


def test_active_evidence_can_be_superseded(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    original = build_evidence(
        evidence_id=(
            "evidence_original"
        )
    )

    replacement = build_evidence(
        evidence_id=(
            "evidence_replacement"
        ),
        evidence_type=(
            EvidenceType.PAYMENT
        ),
        observation_ids=(
            ObservationId(
                "observation_002"
            ),
        ),
    )

    repository.save(
        original
    )

    repository.save(
        replacement
    )

    provenance = EvidenceLifecycleProvenance(
        changed_at=CHANGED_AT,
        reason_code="RECLASSIFIED",
        actor="classifier_v2",
        superseded_by=(
            replacement.id
        ),
    )

    repository.change_status(
        evidence_id=original.id,
        new_status=(
            EvidenceStatus.SUPERSEDED
        ),
        provenance=provenance,
    )

    stored = repository.get(
        original.id
    )

    assert stored is not None

    assert (
        stored.evidence_status
        == EvidenceStatus.SUPERSEDED
    )

    assert (
        repository
        .get_lifecycle_history(
            original.id
        )
        == (
            provenance,
        )
    )


def test_active_evidence_can_be_rejected(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence()

    repository.save(
        evidence
    )

    provenance = EvidenceLifecycleProvenance(
        changed_at=CHANGED_AT,
        reason_code="USER_REJECTED",
        actor="user",
    )

    repository.change_status(
        evidence_id=evidence.id,
        new_status=(
            EvidenceStatus.REJECTED
        ),
        provenance=provenance,
    )

    stored = repository.get(
        evidence.id
    )

    assert stored is not None

    assert (
        stored.evidence_status
        == EvidenceStatus.REJECTED
    )

    assert (
        repository
        .get_lifecycle_history(
            evidence.id
        )
        == (
            provenance,
        )
    )


def test_same_status_transition_is_idempotent(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence()

    repository.save(
        evidence
    )

    provenance = EvidenceLifecycleProvenance(
        changed_at=CHANGED_AT,
        reason_code="NO_CHANGE",
        actor="test",
    )

    repository.change_status(
        evidence_id=evidence.id,
        new_status=(
            EvidenceStatus.ACTIVE
        ),
        provenance=provenance,
    )

    assert (
        repository.get(
            evidence.id
        )
        == evidence
    )

    assert (
        repository
        .get_lifecycle_history(
            evidence.id
        )
        == ()
    )


def test_non_active_evidence_cannot_transition_again(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence()

    repository.save(
        evidence
    )

    first_provenance = (
        EvidenceLifecycleProvenance(
            changed_at=CHANGED_AT,
            reason_code="USER_REJECTED",
            actor="user",
        )
    )

    repository.change_status(
        evidence_id=evidence.id,
        new_status=(
            EvidenceStatus.REJECTED
        ),
        provenance=first_provenance,
    )

    second_provenance = (
        EvidenceLifecycleProvenance(
            changed_at=CHANGED_AT,
            reason_code="RECLASSIFIED",
            actor="classifier_v2",
        )
    )

    with pytest.raises(
        ValueError
    ):
        repository.change_status(
            evidence_id=evidence.id,
            new_status=(
                EvidenceStatus.SUPERSEDED
            ),
            provenance=second_provenance,
        )


def test_missing_evidence_status_change_raises_key_error(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    provenance = EvidenceLifecycleProvenance(
        changed_at=CHANGED_AT,
        reason_code="USER_REJECTED",
        actor="user",
    )

    with pytest.raises(
        KeyError
    ):
        repository.change_status(
            evidence_id=EvidenceId(
                "evidence_missing"
            ),
            new_status=(
                EvidenceStatus.REJECTED
            ),
            provenance=provenance,
        )


def test_evidence_requires_existing_observations(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    evidence = build_evidence(
        observation_ids=(
            ObservationId(
                "observation_missing"
            ),
        )
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        repository.save(
            evidence
        )

    assert (
        repository.get(
            evidence.id
        )
        is None
    )


def test_failed_mapping_update_rolls_back_existing_evidence(
    tmp_path: Path,
) -> None:
    database = build_database(
        tmp_path
    )

    repository = SQLiteEvidenceRepository(
        database
    )

    original = build_evidence()

    repository.save(
        original
    )

    invalid_update = build_evidence(
        evidence_id=(
            original.id.value
        ),
        evidence_type=(
            EvidenceType.PAYMENT
        ),
        observation_ids=(
            ObservationId(
                "observation_missing"
            ),
        ),
        classifier_version=(
            "rules-2"
        ),
    )

    with pytest.raises(
        sqlite3.IntegrityError
    ):
        repository.save(
            invalid_update
        )

    assert (
        repository.get(
            original.id
        )
        == original
    )


def test_evidence_survives_database_restart(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    first_database = build_database(
        tmp_path
    )

    first_repository = (
        SQLiteEvidenceRepository(
            first_database
        )
    )

    original = build_evidence(
        observation_ids=(
            ObservationId(
                "observation_001"
            ),
            ObservationId(
                "observation_002"
            ),
        ),
        identity_seed_ids=(
            IdentitySeedId(
                "identity_email"
            ),
            IdentitySeedId(
                "identity_alias"
            ),
        ),
        reason_codes=(
            "EXACT_SUBJECT_PATTERN",
            "KNOWN_SERVICE_DOMAIN",
        ),
    )

    first_repository.save(
        original
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

    assert (
        second_repository.get(
            original.id
        )
        == original
    )

    assert (
        second_repository
        .find_by_observation(
            ObservationId(
                "observation_002"
            )
        )
        == (
            original,
        )
    )


def test_lifecycle_survives_database_restart(
    tmp_path: Path,
) -> None:
    database_file = (
        tmp_path
        / "state.db"
    )

    first_database = build_database(
        tmp_path
    )

    first_repository = (
        SQLiteEvidenceRepository(
            first_database
        )
    )

    evidence = build_evidence()

    first_repository.save(
        evidence
    )

    provenance = EvidenceLifecycleProvenance(
        changed_at=CHANGED_AT,
        reason_code="USER_REJECTED",
        actor="user",
    )

    first_repository.change_status(
        evidence_id=evidence.id,
        new_status=(
            EvidenceStatus.REJECTED
        ),
        provenance=provenance,
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

    restored = second_repository.get(
        evidence.id
    )

    assert restored is not None

    assert (
        restored.evidence_status
        == EvidenceStatus.REJECTED
    )

    assert (
        second_repository
        .get_lifecycle_history(
            evidence.id
        )
        == (
            provenance,
        )
    )
