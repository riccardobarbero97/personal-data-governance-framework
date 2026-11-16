from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

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


@dataclass(frozen=True, slots=True)
class EvidenceLifecycleProvenance:
    changed_at: datetime
    reason_code: str
    actor: str
    superseded_by: EvidenceId | None = None

    def __post_init__(self) -> None:
        if not self.reason_code.strip():
            raise ValueError(
                "Lifecycle reason code must not be empty."
            )

        if not self.actor.strip():
            raise ValueError(
                "Lifecycle actor must not be empty."
            )


class ConnectedSourceRepository(Protocol):

    def save(
        self,
        connected_source: ConnectedSource,
    ) -> None:
        ...

    def get(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> ConnectedSource | None:
        ...

    def find_by_user(
        self,
        user_id: UserId,
    ) -> tuple[ConnectedSource, ...]:
        ...


class ObservationRepository(Protocol):

    def save(
        self,
        observation: Observation,
    ) -> None:
        ...

    def get(
        self,
        observation_id: ObservationId,
    ) -> Observation | None:
        ...

    def find_by_source_reference(
        self,
        connected_source_id: ConnectedSourceId,
        source_reference: SourceReference,
    ) -> Observation | None:
        ...


class EvidenceRepository(Protocol):

    def save(
        self,
        evidence: Evidence,
    ) -> None:
        ...

    def get(
        self,
        evidence_id: EvidenceId,
    ) -> Evidence | None:
        ...

    def find_by_observation(
        self,
        observation_id: ObservationId,
    ) -> tuple[Evidence, ...]:
        ...

    def find_active_by_service(
        self,
        service_id: ServiceId,
    ) -> tuple[Evidence, ...]:
        ...

    def change_status(
        self,
        evidence_id: EvidenceId,
        new_status: EvidenceStatus,
        provenance: EvidenceLifecycleProvenance,
    ) -> None:
        ...


class RelationshipRepository(Protocol):

    def save(
        self,
        relationship: Relationship,
    ) -> None:
        ...

    def get(
        self,
        relationship_id: RelationshipId,
    ) -> Relationship | None:
        ...

    def get_by_user_and_service(
        self,
        user_id: UserId,
        service_id: ServiceId,
    ) -> Relationship | None:
        ...
