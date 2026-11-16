from collections.abc import Callable
from datetime import datetime, timezone
from uuid import uuid4

from personal_data_governance.application.ports.repositories import (
    EvidenceLifecycleProvenance,
    EvidenceRepository,
)
from personal_data_governance.application.results.classification import (
    EvidenceCandidate,
)
from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.enums.evidence import EvidenceStatus
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    IdentitySeedId,
    ObservationId,
    ServiceId,
)


EvidenceIdFactory = Callable[[], EvidenceId]


def default_evidence_id_factory() -> EvidenceId:
    return EvidenceId(
        f"evidence_{uuid4().hex}"
    )


class EvidenceMaterializer:
    def __init__(
        self,
        evidence_repository: EvidenceRepository,
        evidence_id_factory: EvidenceIdFactory | None = None,
    ) -> None:
        self._evidence_repository = evidence_repository

        self._evidence_id_factory = (
            evidence_id_factory
            if evidence_id_factory is not None
            else default_evidence_id_factory
        )

    def materialize(
        self,
        observation_id: ObservationId,
        evidence_candidates: tuple[EvidenceCandidate, ...],
        service_id: ServiceId | None,
        identity_seed_ids: tuple[IdentitySeedId, ...] = (),
        lifecycle_actor: str = "evidence_materializer",
        changed_at: datetime | None = None,
    ) -> tuple[Evidence, ...]:
        self._validate_candidates(
            observation_id=observation_id,
            evidence_candidates=evidence_candidates,
        )

        normalized_identity_seed_ids = self._deduplicate_identity_seed_ids(
            identity_seed_ids
        )

        lifecycle_changed_at = (
            changed_at
            if changed_at is not None
            else datetime.now(timezone.utc)
        )

        existing_evidence = (
            self._evidence_repository.find_by_observation(
                observation_id
            )
        )

        existing_active_evidence = tuple(
            evidence
            for evidence in existing_evidence
            if evidence.evidence_status
            == EvidenceStatus.ACTIVE
        )

        retained_evidence: list[Evidence] = []
        created_evidence: list[Evidence] = []

        matched_existing_ids: set[EvidenceId] = set()

        for candidate in evidence_candidates:
            matching_evidence = self._find_matching_evidence(
                candidate=candidate,
                existing_active_evidence=existing_active_evidence,
                service_id=service_id,
                identity_seed_ids=normalized_identity_seed_ids,
                matched_existing_ids=matched_existing_ids,
            )

            if matching_evidence is not None:
                retained_evidence.append(
                    matching_evidence
                )

                matched_existing_ids.add(
                    matching_evidence.id
                )

                continue

            evidence = self._create_evidence(
                candidate=candidate,
                service_id=service_id,
                identity_seed_ids=normalized_identity_seed_ids,
            )

            self._evidence_repository.save(evidence)

            created_evidence.append(evidence)

        replacement_evidence_ids = tuple(
            evidence.id
            for evidence in created_evidence
        )

        self._supersede_stale_evidence(
            existing_active_evidence=existing_active_evidence,
            matched_existing_ids=matched_existing_ids,
            replacement_evidence_ids=replacement_evidence_ids,
            lifecycle_actor=lifecycle_actor,
            changed_at=lifecycle_changed_at,
        )

        return tuple(
            retained_evidence
            + created_evidence
        )

    def reject(
        self,
        evidence_id: EvidenceId,
        reason_code: str,
        actor: str,
        changed_at: datetime | None = None,
    ) -> None:
        if not reason_code.strip():
            raise ValueError(
                "Rejection reason code must not be empty."
            )

        if not actor.strip():
            raise ValueError(
                "Rejection actor must not be empty."
            )

        lifecycle_changed_at = (
            changed_at
            if changed_at is not None
            else datetime.now(timezone.utc)
        )

        provenance = EvidenceLifecycleProvenance(
            changed_at=lifecycle_changed_at,
            reason_code=reason_code,
            actor=actor,
        )

        self._evidence_repository.change_status(
            evidence_id=evidence_id,
            new_status=EvidenceStatus.REJECTED,
            provenance=provenance,
        )

    def _create_evidence(
        self,
        candidate: EvidenceCandidate,
        service_id: ServiceId | None,
        identity_seed_ids: tuple[IdentitySeedId, ...],
    ) -> Evidence:
        evidence_id = self._evidence_id_factory()

        return Evidence(
            id=evidence_id,
            evidence_type=candidate.evidence_type,
            evidence_status=EvidenceStatus.ACTIVE,
            observation_ids=candidate.observation_ids,
            service_id=service_id,
            identity_seed_ids=identity_seed_ids,
            classification_method=candidate.method,
            classifier_version=candidate.classifier_version,
            reason_codes=candidate.reason_codes,
        )

    def _supersede_stale_evidence(
        self,
        existing_active_evidence: tuple[Evidence, ...],
        matched_existing_ids: set[EvidenceId],
        replacement_evidence_ids: tuple[EvidenceId, ...],
        lifecycle_actor: str,
        changed_at: datetime,
    ) -> None:
        if not lifecycle_actor.strip():
            raise ValueError(
                "Lifecycle actor must not be empty."
            )

        superseded_by = (
            replacement_evidence_ids[0]
            if len(replacement_evidence_ids) == 1
            else None
        )

        for evidence in existing_active_evidence:
            if evidence.id in matched_existing_ids:
                continue

            provenance = EvidenceLifecycleProvenance(
                changed_at=changed_at,
                reason_code="CLASSIFICATION_REPLACED",
                actor=lifecycle_actor,
                superseded_by=superseded_by,
            )

            self._evidence_repository.change_status(
                evidence_id=evidence.id,
                new_status=EvidenceStatus.SUPERSEDED,
                provenance=provenance,
            )

    @staticmethod
    def _find_matching_evidence(
        candidate: EvidenceCandidate,
        existing_active_evidence: tuple[Evidence, ...],
        service_id: ServiceId | None,
        identity_seed_ids: tuple[IdentitySeedId, ...],
        matched_existing_ids: set[EvidenceId],
    ) -> Evidence | None:
        for evidence in existing_active_evidence:
            if evidence.id in matched_existing_ids:
                continue

            if (
                evidence.evidence_type
                != candidate.evidence_type
            ):
                continue

            if (
                evidence.observation_ids
                != candidate.observation_ids
            ):
                continue

            if evidence.service_id != service_id:
                continue

            if (
                evidence.identity_seed_ids
                != identity_seed_ids
            ):
                continue

            if (
                evidence.classification_method
                != candidate.method
            ):
                continue

            if (
                evidence.classifier_version
                != candidate.classifier_version
            ):
                continue

            if (
                evidence.reason_codes
                != candidate.reason_codes
            ):
                continue

            return evidence

        return None

    @staticmethod
    def _validate_candidates(
        observation_id: ObservationId,
        evidence_candidates: tuple[EvidenceCandidate, ...],
    ) -> None:
        for candidate in evidence_candidates:
            if observation_id not in candidate.observation_ids:
                raise ValueError(
                    "Every EvidenceCandidate must reference "
                    "the materialized Observation."
                )

    @staticmethod
    def _deduplicate_identity_seed_ids(
        identity_seed_ids: tuple[IdentitySeedId, ...],
    ) -> tuple[IdentitySeedId, ...]:
        unique_ids = {
            identity_seed_id.value: identity_seed_id
            for identity_seed_id in identity_seed_ids
        }

        return tuple(
            unique_ids[key]
            for key in sorted(unique_ids)
        )
