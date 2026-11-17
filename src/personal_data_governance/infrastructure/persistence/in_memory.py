from dataclasses import replace

from personal_data_governance.application.ports.repositories import (
    ConnectedSourceRepository,
    EvidenceLifecycleProvenance,
    EvidenceRepository,
    ObservationRepository,
    RelationshipRepository,
)
from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.entities.relationship import Relationship
from personal_data_governance.domain.enums.evidence import EvidenceStatus
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    ObservationId,
    RelationshipId,
    ServiceId,
    UserId,
)
from personal_data_governance.domain.values.references import SourceReference


class InMemoryConnectedSourceRepository(
    ConnectedSourceRepository,
):
    def __init__(self) -> None:
        self._sources: dict[
            ConnectedSourceId,
            ConnectedSource,
        ] = {}

    def save(
        self,
        connected_source: ConnectedSource,
    ) -> None:
        self._sources[connected_source.id] = connected_source

    def get(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> ConnectedSource | None:
        return self._sources.get(connected_source_id)

    def find_by_user(
        self,
        user_id: UserId,
    ) -> tuple[ConnectedSource, ...]:
        return tuple(
            source
            for source in self._sources.values()
            if source.user_id == user_id
        )


class InMemoryObservationRepository(
    ObservationRepository,
):
    def __init__(self) -> None:
        self._observations: dict[
            ObservationId,
            Observation,
        ] = {}

    def save(
        self,
        observation: Observation,
    ) -> None:
        self._observations[observation.id] = observation

    def get(
        self,
        observation_id: ObservationId,
    ) -> Observation | None:
        return self._observations.get(observation_id)

    def find_by_source_reference(
        self,
        connected_source_id: ConnectedSourceId,
        source_reference: SourceReference,
    ) -> Observation | None:
        for observation in self._observations.values():
            if (
                observation.connected_source_id
                == connected_source_id
                and observation.source_reference
                == source_reference
            ):
                return observation

        return None


class InMemoryEvidenceRepository(
    EvidenceRepository,
):
    def __init__(self) -> None:
        self._evidence: dict[
            EvidenceId,
            Evidence,
        ] = {}

        self._lifecycle_history: dict[
            EvidenceId,
            list[EvidenceLifecycleProvenance],
        ] = {}

    def save(
        self,
        evidence: Evidence,
    ) -> None:
        self._evidence[evidence.id] = evidence

    def get(
        self,
        evidence_id: EvidenceId,
    ) -> Evidence | None:
        return self._evidence.get(evidence_id)

    def find_by_observation(
        self,
        observation_id: ObservationId,
    ) -> tuple[Evidence, ...]:
        return tuple(
            evidence
            for evidence in self._evidence.values()
            if observation_id in evidence.observation_ids
        )

    def find_active_by_service(
        self,
        service_id: ServiceId,
    ) -> tuple[Evidence, ...]:
        return tuple(
            evidence
            for evidence in self._evidence.values()
            if (
                evidence.service_id == service_id
                and evidence.evidence_status
                == EvidenceStatus.ACTIVE
            )
        )

    def change_status(
        self,
        evidence_id: EvidenceId,
        new_status: EvidenceStatus,
        provenance: EvidenceLifecycleProvenance,
    ) -> None:
        evidence = self._evidence.get(evidence_id)

        if evidence is None:
            raise KeyError(
                f"Evidence not found: {evidence_id.value}"
            )

        if evidence.evidence_status == new_status:
            return

        if evidence.evidence_status != EvidenceStatus.ACTIVE:
            raise ValueError(
                "Only ACTIVE Evidence may transition "
                "in the initial lifecycle model."
            )

        if new_status not in {
            EvidenceStatus.SUPERSEDED,
            EvidenceStatus.REJECTED,
        }:
            raise ValueError(
                "ACTIVE Evidence may only transition to "
                "SUPERSEDED or REJECTED."
            )

        updated_evidence = replace(
               evidence,
            evidence_status=new_status,
        )

        self._evidence[evidence_id] = updated_evidence

        self._lifecycle_history.setdefault(
            evidence_id,
            [],
        ).append(provenance)

    def get_lifecycle_history(
        self,
        evidence_id: EvidenceId,
    ) -> tuple[EvidenceLifecycleProvenance, ...\]:
        return tuple(
            self._lifecycle_history.get(
                evidence_id,
                [],
            )
        )


class InMemoryRelationshipRepository(
    RelationshipRepository,
):
    def __init__(self) -> None:
        self._relationships: dict[
            RelationshipId,
            Relationship,
        ] = {}

    def save(
        self,
        relationship: Relationship,
    ) -> None:
        existing = self.get_by_user_and_service(
            relationship.user_id,
            relationship.service_id,
        )
     if (
            existing is not None
            and existing.id != relationship.id
        ):
            del self._relationships[existing.id]

        self._relationships[
            relationship.id
        ] = relationship

    def get(
        self,
        relationship_id: RelationshipId,
    ) -> Relationship | None:
        return self._relationships.get(
            relationship_id
        )

    def get_by_user_and_service(
        self,
        user_id: UserId,
        service_id: ServiceId,
    ) -> Relationship | None:
        for relationship in self._relationships.values():
            if (
                relationship.user_id == user_id
                and relationship.service_id == service_id
            ):
                return relationship

        return None
