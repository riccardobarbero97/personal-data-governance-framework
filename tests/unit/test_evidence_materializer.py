from datetime import datetime, timezone

from personal_data_governance.application.results.classification import (
    EvidenceCandidate,
)
from personal_data_governance.application.services.evidence_materializer import (
    EvidenceMaterializer,
)
from personal_data_governance.domain.entities.evidence import Evidence
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
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryEvidenceRepository,
)


class SequentialEvidenceIdFactory:
    def __init__(self) -> None:
        self._counter = 0

    def __call__(self) -> EvidenceId:
        self._counter += 1

        return EvidenceId(
            f"evidence_{self._counter:03d}"
        )


def build_candidate(
    evidence_type: EvidenceType,
    observation_id: ObservationId | None = None,
    classifier_version: str = "1",
    reason_code: str = "SUBJECT_RULE_MATCH",
) -> EvidenceCandidate:
    effective_observation_id = (
        observation_id
        if observation_id is not None
        else ObservationId("observation_001")
    )

    return EvidenceCandidate(
        evidence_type=evidence_type,
        observation_ids=(
            effective_observation_id,
        ),
        method=ClassificationMethod.RULE,
        reason_codes=(
            reason_code,
        ),
        classifier_version=classifier_version,
    )


def build_materializer(
    repository: InMemoryEvidenceRepository,
) -> EvidenceMaterializer:
    return EvidenceMaterializer(
        evidence_repository=repository,
        evidence_id_factory=SequentialEvidenceIdFactory(),
    )


def test_candidate_is_materialized_as_active_evidence() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    candidate = build_candidate(
        EvidenceType.ACCOUNT_VERIFICATION
    )

    materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
        identity_seed_ids=(
            IdentitySeedId("identity_email"),
        ),
    )

    assert len(materialized) == 1

    evidence = materialized[0]

    assert evidence.id == EvidenceId("evidence_001")

    assert (
        evidence.evidence_type
        == EvidenceType.ACCOUNT_VERIFICATION
    )

    assert evidence.evidence_status == EvidenceStatus.ACTIVE

    assert evidence.observation_ids == (
        observation_id,
    )

    assert (
        evidence.service_id
        == ServiceId("service_spotify")
    )

    assert evidence.identity_seed_ids == (
        IdentitySeedId("identity_email"),
    )

    assert (
        evidence.classification_method
        == ClassificationMethod.RULE
    )

    assert evidence.classifier_version == "1"

    assert evidence.reason_codes == (
        "SUBJECT_RULE_MATCH",
    )

    assert repository.get(evidence.id) == evidence


def test_evidence_can_be_materialized_without_service() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    candidate = build_candidate(
        EvidenceType.PAYMENT
    )

    materialized = materializer.materialize(
        observation_id=ObservationId(
            "observation_001"
        ),
        evidence_candidates=(
            candidate,
        ),
        service_id=None,
    )

    assert len(materialized) == 1
    assert materialized[0].service_id is None

    assert (
        materialized[0].evidence_status
        == EvidenceStatus.ACTIVE
    )


def test_identical_active_evidence_is_reused() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    candidate = build_candidate(
        EvidenceType.ACCOUNT_VERIFICATION
    )

    first_result = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    second_result = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    assert first_result == second_result

    assert first_result[0].id == EvidenceId(
        "evidence_001"
    )

    stored = repository.find_by_observation(
        observation_id
    )

    assert len(stored) == 1


def test_reclassification_supersedes_previous_evidence() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    old_candidate = build_candidate(
        EvidenceType.MARKETING,
        reason_code="MARKETING_SUBJECT",
    )

    old_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            old_candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    old_evidence = old_materialized[0]

    changed_at = datetime(
        2026,
        11,
        16,
        12,
        0,
        tzinfo=timezone.utc,
    )

    new_candidate = build_candidate(
        EvidenceType.PRIVACY_NOTICE,
        classifier_version="2",
        reason_code="PRIVACY_NOTICE_SUBJECT",
    )

    new_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            new_candidate,
        ),
        service_id=ServiceId("service_spotify"),
        lifecycle_actor="classifier_v2",
        changed_at=changed_at,
    )

    new_evidence = new_materialized[0]

    stored_old_evidence = repository.get(
        old_evidence.id
    )

    assert stored_old_evidence is not None

    assert (
        stored_old_evidence.evidence_status
        == EvidenceStatus.SUPERSEDED
    )

    assert new_evidence.id == EvidenceId(
        "evidence_002"
    )

    assert (
        new_evidence.evidence_type
        == EvidenceType.PRIVACY_NOTICE
    )

    assert (
        new_evidence.evidence_status
        == EvidenceStatus.ACTIVE
    )

    history = repository.get_lifecycle_history(
        old_evidence.id
    )

    assert len(history) == 1

    provenance = history[0]

    assert provenance.changed_at == changed_at

    assert (
        provenance.reason_code
        == "CLASSIFICATION_REPLACED"
    )

    assert provenance.actor == "classifier_v2"

    assert (
        provenance.superseded_by
        == new_evidence.id
    )


def test_multiple_candidates_create_multiple_active_evidence() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    payment_candidate = build_candidate(
        EvidenceType.PAYMENT,
        reason_code="PAYMENT_SUBJECT",
    )

    invoice_candidate = build_candidate(
        EvidenceType.INVOICE,
        reason_code="INVOICE_SUBJECT",
    )

    materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            payment_candidate,
            invoice_candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    assert len(materialized) == 2

    evidence_types = {
        evidence.evidence_type
        for evidence in materialized
    }

    assert evidence_types == {
        EvidenceType.INVOICE,
        EvidenceType.PAYMENT,
    }

    assert all(
        evidence.evidence_status
        == EvidenceStatus.ACTIVE
        for evidence in materialized
    )


def test_retained_and_new_evidence_can_coexist() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    payment_candidate = build_candidate(
        EvidenceType.PAYMENT,
        reason_code="PAYMENT_SUBJECT",
    )

    first_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            payment_candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    retained_payment = first_materialized[0]

    invoice_candidate = build_candidate(
        EvidenceType.INVOICE,
        reason_code="INVOICE_SUBJECT",
    )

    second_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            payment_candidate,
            invoice_candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    assert len(second_materialized) == 2

    evidence_by_type = {
        evidence.evidence_type: evidence
        for evidence in second_materialized
    }

    assert (
        evidence_by_type[EvidenceType.PAYMENT].id
        == retained_payment.id
    )

    assert (
        evidence_by_type[EvidenceType.INVOICE].id
        == EvidenceId("evidence_002")
    )

    stored_payment = repository.get(
        retained_payment.id
    )

    assert stored_payment is not None

    assert (
        stored_payment.evidence_status
        == EvidenceStatus.ACTIVE
    )


def test_removed_candidate_supersedes_only_stale_evidence() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    payment_candidate = build_candidate(
        EvidenceType.PAYMENT,
        reason_code="PAYMENT_SUBJECT",
    )

    invoice_candidate = build_candidate(
        EvidenceType.INVOICE,
        reason_code="INVOICE_SUBJECT",
    )

    first_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            payment_candidate,
            invoice_candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    evidence_by_type = {
        evidence.evidence_type: evidence
        for evidence in first_materialized
    }

    payment_evidence = evidence_by_type[
        EvidenceType.PAYMENT
    ]

    invoice_evidence = evidence_by_type[
        EvidenceType.INVOICE
    ]

    second_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            payment_candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    assert second_materialized == (
        payment_evidence,
    )

    stored_payment = repository.get(
        payment_evidence.id
    )

    stored_invoice = repository.get(
        invoice_evidence.id
    )

    assert stored_payment is not None
    assert stored_invoice is not None

    assert (
        stored_payment.evidence_status
        == EvidenceStatus.ACTIVE
    )

    assert (
        stored_invoice.evidence_status
        == EvidenceStatus.SUPERSEDED
    )


def test_empty_candidate_set_supersedes_existing_active_evidence() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    candidate = build_candidate(
        EvidenceType.MARKETING
    )

    first_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    existing_evidence = first_materialized[0]

    second_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(),
        service_id=ServiceId("service_spotify"),
    )

    assert second_materialized == ()

    stored = repository.get(
        existing_evidence.id
    )

    assert stored is not None

    assert (
        stored.evidence_status
        == EvidenceStatus.SUPERSEDED
    )


def test_candidate_must_reference_materialized_observation() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    candidate = build_candidate(
        EvidenceType.PAYMENT,
        observation_id=ObservationId(
            "different_observation"
        ),
    )

    try:
        materializer.materialize(
            observation_id=ObservationId(
                "observation_001"
            ),
            evidence_candidates=(
                candidate,
            ),
            service_id=None,
        )
    except ValueError as error:
        assert str(error) == (
            "Every EvidenceCandidate must reference "
            "the materialized Observation."
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )


def test_identity_seed_ids_are_deduplicated() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    candidate = build_candidate(
        EvidenceType.ACCOUNT_VERIFICATION
    )

    materialized = materializer.materialize(
        observation_id=ObservationId(
            "observation_001"
        ),
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
        identity_seed_ids=(
            IdentitySeedId("identity_b"),
            IdentitySeedId("identity_a"),
            IdentitySeedId("identity_b"),
        ),
    )

    assert materialized[0].identity_seed_ids == (
        IdentitySeedId("identity_a"),
        IdentitySeedId("identity_b"),
    )


def test_service_change_creates_new_evidence_interpretation() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    observation_id = ObservationId("observation_001")

    candidate = build_candidate(
        EvidenceType.ACCOUNT_VERIFICATION
    )

    first_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            candidate,
        ),
        service_id=None,
    )

    unresolved_evidence = first_materialized[0]

    second_materialized = materializer.materialize(
        observation_id=observation_id,
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    resolved_evidence = second_materialized[0]

    assert resolved_evidence.id == EvidenceId(
        "evidence_002"
    )

    assert (
        resolved_evidence.service_id
        == ServiceId("service_spotify")
    )

    stored_unresolved = repository.get(
        unresolved_evidence.id
    )

    assert stored_unresolved is not None

    assert (
        stored_unresolved.evidence_status
        == EvidenceStatus.SUPERSEDED
    )


def test_active_evidence_can_be_rejected() -> None:
    repository = InMemoryEvidenceRepository()

    materializer = build_materializer(repository)

    candidate = build_candidate(
        EvidenceType.MARKETING
    )

    materialized = materializer.materialize(
        observation_id=ObservationId(
            "observation_001"
        ),
        evidence_candidates=(
            candidate,
        ),
        service_id=ServiceId("service_spotify"),
    )

    evidence = materialized[0]

    changed_at = datetime(
        2026,
        11,
        16,
        13,
        0,
        tzinfo=timezone.utc,
    )

    materializer.reject(
        evidence_id=evidence.id,
        reason_code="USER_REJECTED",
        actor="user",
        changed_at=changed_at,
    )

    stored = repository.get(evidence.id)

    assert stored is not None

    assert (
        stored.evidence_status
        == EvidenceStatus.REJECTED
    )

    history = repository.get_lifecycle_history(
        evidence.id
    )

    assert len(history) == 1
    assert history[0].changed_at == changed_at
    assert history[0].reason_code == "USER_REJECTED"
    assert history[0].actor == "user"
    assert history[0].superseded_by is None
