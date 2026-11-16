from dataclasses import dataclass

from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.processing import (
    AggregationScope,
)
from personal_data_governance.domain.enums.source import SourceType
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    IdentitySeedId,
    ServiceId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)
from personal_data_governance.domain.values.temporal import TemporalValue


@dataclass(frozen=True, slots=True)
class EvidenceSummary:
    total_evidence_count: int
    evidence_count_by_type: dict[EvidenceType, int]
    active_evidence_types: tuple[EvidenceType, ...]

    def __post_init__(self) -> None:
        if self.total_evidence_count < 0:
            raise ValueError(
                "Total Evidence count must not be negative."
            )

        if any(
            count < 0
            for count in self.evidence_count_by_type.values()
        ):
            raise ValueError(
                "Evidence counts must not be negative."
            )


@dataclass(frozen=True, slots=True)
class SourceSummary:
    connected_source_count: int
    source_types: tuple[SourceType, ...]
    providers: tuple[Provider, ...]
    evidence_count_by_connected_source: dict[
        ConnectedSourceId,
        int,
    ]
    evidence_count_by_source_type: dict[
        SourceType,
        int,
    ]

    def __post_init__(self) -> None:
        if self.connected_source_count < 0:
            raise ValueError(
                "ConnectedSource count must not be negative."
            )

        if any(
            count < 0
            for count
            in self.evidence_count_by_connected_source.values()
        ):
            raise ValueError(
                "Evidence counts by ConnectedSource "
                "must not be negative."
            )

        if any(
            count < 0
            for count
            in self.evidence_count_by_source_type.values()
        ):
            raise ValueError(
                "Evidence counts by SourceType "
                "must not be negative."
            )


@dataclass(frozen=True, slots=True)
class TemporalSummary:
    first_observed: TemporalValue | None
    last_observed: TemporalValue | None
    typed_temporal_values: tuple[TemporalValue, ...]


@dataclass(frozen=True, slots=True)
class ConflictSummary:
    has_potential_conflicts: bool
    conflict_types: tuple[str, ...]
    involved_evidence_ids: tuple[EvidenceId, ...]


@dataclass(frozen=True, slots=True)
class CoverageSummary:
    configured_source_ids: tuple[ConnectedSourceId, ...]
    completed_source_ids: tuple[ConnectedSourceId, ...]
    partial_source_ids: tuple[ConnectedSourceId, ...]
    failed_source_ids: tuple[ConnectedSourceId, ...]
    unavailable_source_ids: tuple[ConnectedSourceId, ...]


@dataclass(frozen=True, slots=True)
class EvidenceAggregate:
    scope: AggregationScope
    service_id: ServiceId | None
    unresolved_identifiers: tuple[ServiceIdentifier, ...]
    alternative_service_ids: tuple[ServiceId, ...]
    identity_seed_ids: tuple[IdentitySeedId, ...]
    evidence_ids: tuple[EvidenceId, ...]
    evidence_summary: EvidenceSummary
    source_summary: SourceSummary
    temporal_summary: TemporalSummary
    conflict_summary: ConflictSummary
    coverage_summary: CoverageSummary | None
    aggregator_version: str

    def __post_init__(self) -> None:
        if not self.aggregator_version.strip():
            raise ValueError(
                "Aggregator version must not be empty."
            )

        if (
            self.scope == AggregationScope.SERVICE
            and self.service_id is None
        ):
            raise ValueError(
                "SERVICE aggregation requires a Service."
            )

        if (
            self.scope == AggregationScope.SERVICE
            and self.unresolved_identifiers
        ):
            raise ValueError(
                "SERVICE aggregation must not contain "
                "unresolved identifiers."
            )

        if (
            self.scope == AggregationScope.SERVICE
            and self.alternative_service_ids
        ):
            raise ValueError(
                "SERVICE aggregation must not contain "
                "alternative Services."
            )

        if (
            self.scope
            == AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
            and not self.unresolved_identifiers
        ):
            raise ValueError(
                "UNRESOLVED_SERVICE_CANDIDATE "
                "requires identifiers."
            )

        if (
            self.scope
            == AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
            and self.service_id is not None
        ):
            raise ValueError(
                "UNRESOLVED_SERVICE_CANDIDATE "
                "must not contain a resolved Service."
            )

        if (
            self.scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            and not self.unresolved_identifiers
        ):
            raise ValueError(
                "AMBIGUOUS_SERVICE_CANDIDATE "
                "requires identifiers."
            )

        if (
            self.scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            and not self.alternative_service_ids
        ):
            raise ValueError(
                "AMBIGUOUS_SERVICE_CANDIDATE "
                "requires alternative Services."
            )

        if (
            self.scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            and self.service_id is not None
        ):
            raise ValueError(
                "AMBIGUOUS_SERVICE_CANDIDATE "
                "must not contain a resolved Service."
            )
