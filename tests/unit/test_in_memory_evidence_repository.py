from datetime import datetime, timezone

import pytest

from personal_data_governance.application.ports.repositories import (
    EvidenceLifecycleProvenance,
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
    ObservationId,
    ServiceId,
)
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryEvidenceRepository,
)


def build_active_evidence(
    evidence_id: str = "evidence_001",
) -> Evidence:
    return Evidence(
        id=EvidenceId(evidence_id),
        evidence_type=EvidenceType.MARKETING,
        evidence_status=EvidenceStatus.ACTIVE,
        observation_ids=(
            ObservationId("observation_001"),
        ),
        service_id=ServiceId("service_spotify"),
        identity_seed_ids=(),
        classification_method=ClassificationMethod.RULE,
        classifier_version="1",
        reason_codes=(
            "EXACT_SUBJECT_PATTERN",
        ),
    )


def test_evidence_can_be_saved_and_loaded() -> None:
    repository = InMemoryEvidenceRepository()

    evidence = build_active_evidence()

    repository.save(evidence)

    stored = repository.get(evidence.id)

    assert stored == evidence


def test_evidence_can_be_found_by_observation() -> None:
    repository = InMemoryEvidenceRepository()

    evidence = build_active_evidence()

    repository.save(evidence)

    stored = repository.find_by_observation(
        ObservationId("observation_001")
    )

    assert stored == (evidence,)


def test_only_active_evidence_is_returned_by_service() -> None:
    repository = InMemoryEvidenceRepository()

    active_evidence = build_active_evidence(
        "evidence_active"
    )

    rejected_evidence = Evidence(
        id=EvidenceId("evidence_rejected"),
        evidence_type=EvidenceType.NEWSLETTER,
        evidence_status=EvidenceStatus.REJECTED,
        observation_ids=(
            ObservationId("observation_002"),
        ),
        service_id=ServiceId("service_spotify"),
        identity_seed_ids=(),
        classification_method=ClassificationMethod.RULE,
        classifier_version="1",
        reason_codes=(
            "USER_CORRECTION",
        ),
    )

    repository.save(active_evidence)
    repository.save(rejected_evidence)

    stored = repository.find_active_by_service(
        ServiceId("service_spotify")
    )

    assert stored == (active_evidence,)


def test_active_evidence_can_be_superseded() -> None:
    repository = InMemoryEvidenceRepository()

    evidence = build_active_evidence()

    repository.save(evidence)

    provenance = EvidenceLifecycleProvenance(
        changed_at=datetime.now(timezone.utc),
        reason_code="RECLASSIFIED",
        actor="classifier_v2",
        superseded_by=EvidenceId("evidence_002"),
    )

    repository.change_status(
        evidence_id=evidence.id,
        new_status=EvidenceStatus.SUPERSEDED,
        provenance=provenance,
    )

    stored = repository.get(evidence.id)

    assert stored is not None
    assert (
        stored.evidence_status
        == EvidenceStatus.SUPERSEDED
    )

    history = repository.get_lifecycle_history(
        evidence.id
    )

    assert len(history) == 1
    assert history[0] == provenance


def test_active_evidence_can_be_rejected() -> None:
    repository = InMemoryEvidenceRepository()

    evidence = build_active_evidence()

    repository.save(evidence)

    provenance = EvidenceLifecycleProvenance(
        changed_at=datetime.now(timezone.utc),
        reason_code="USER_REJECTED",
        actor="user",
    )

    repository.change_status(
        evidence_id=evidence.id,
        new_status=EvidenceStatus.REJECTED,
        provenance=provenance,
    )

    stored = repository.get(evidence.id)

    assert stored is not None
    assert (
        stored.evidence_status
        == EvidenceStatus.REJECTED
    )


def test_superseded_evidence_cannot_transition_again() -> None:
    repository = InMemoryEvidenceRepository()

    evidence = build_active_evidence()

    repository.save(evidence)

    first_provenance = EvidenceLifecycleProvenance(
        changed_at=datetime.now(timezone.utc),
        reason_code="RECLASSIFIED",
        actor="classifier_v2",
        superseded_by=EvidenceId("evidence_002"),
    )

    repository.change_status(
        evidence_id=evidence.id,
        new_status=EvidenceStatus.SUPERSEDED,
        provenance=first_provenance,
    )

    second_provenance = EvidenceLifecycleProvenance(
        changed_at=datetime.now(timezone.utc),
        reason_code="USER_REJECTED",
        actor="user",
    )

    with pytest.raises(ValueError):
        repository.change_status(
            evidence_id=evidence.id,
            new_status=EvidenceStatus.REJECTED,
            provenance=second_provenance,
        )
