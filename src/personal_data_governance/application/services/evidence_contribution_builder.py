from personal_data_governance.application.ports.repositories import (
    ConnectedSourceRepository,
    ObservationRepository,
)
from personal_data_governance.application.values.evidence_contribution import (
    EvidenceContribution,
)
from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.temporal import TemporalValue


class EvidenceContributionBuilder:
    def __init__(
        self,
        observation_repository: ObservationRepository,
        connected_source_repository: ConnectedSourceRepository,
    ) -> None:
        self._observation_repository = observation_repository
        self._connected_source_repository = connected_source_repository

    def build(
        self,
        evidence: Evidence,
    ) -> EvidenceContribution:
        connected_source_ids: dict[
            str,
            ConnectedSourceId,
        ] = {}

        providers: dict[
            str,
            Provider,
        ] = {}

        source_types = {}
        temporal_values: list[TemporalValue] = []

        for observation_id in evidence.observation_ids:
            observation = self._observation_repository.get(
                observation_id
            )

            if observation is None:
                raise KeyError(
                    "Observation not found: "
                    f"{observation_id.value}"
                )

            connected_source = (
                self._connected_source_repository.get(
                    observation.connected_source_id
                )
            )

            if connected_source is None:
                raise KeyError(
                    "ConnectedSource not found: "
                    f"{observation.connected_source_id.value}"
                )

            connected_source_ids[
                connected_source.id.value
            ] = connected_source.id

            source_types[
                connected_source.source_type.value
            ] = connected_source.source_type

            providers[
                connected_source.provider.id
            ] = connected_source.provider

            if observation.observed_at is not None:
                temporal_values.append(
                    observation.observed_at
                )

        return EvidenceContribution(
            evidence=evidence,
            connected_source_ids=tuple(
                connected_source_ids[key]
                for key in sorted(
                    connected_source_ids
                )
            ),
            source_types=tuple(
                source_types[key]
                for key in sorted(
                    source_types
                )
            ),
            providers=tuple(
                providers[key]
                for key in sorted(
                    providers
                )
            ),
            temporal_values=tuple(
                temporal_values
            ),
        )
