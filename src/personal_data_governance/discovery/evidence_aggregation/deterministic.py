from collections import Counter

from personal_data_governance.application.results.aggregation import (
    AggregationResult,
)
from personal_data_governance.application.values.evidence_contribution import (
    EvidenceContribution,
)
from personal_data_governance.discovery.evidence_aggregation.protocol import (
    AggregationRequest,
    EvidenceAggregator,
)
from personal_data_governance.domain.enums.evidence import EvidenceStatus
from personal_data_governance.domain.enums.processing import (
    AggregationStatus,
    ProcessingStatus,
)
from personal_data_governance.domain.enums.source import SourceType
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    IdentitySeedId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.temporal import TemporalValue
from personal_data_governance.domain.views.evidence_aggregate import (
    ConflictSummary,
    EvidenceAggregate,
    EvidenceSummary,
    SourceSummary,
    TemporalSummary,
)


class DeterministicEvidenceAggregator(
    EvidenceAggregator,
):
    def aggregate(
        self,
        request: AggregationRequest,
    ) -> AggregationResult:
        active_contributions = tuple(
            contribution
            for contribution in request.contributions
            if (
                contribution.evidence.evidence_status
                == EvidenceStatus.ACTIVE
            )
        )

        if not active_contributions:
            return AggregationResult(
                processing_status=ProcessingStatus.SUCCESS,
                aggregation_status=AggregationStatus.EMPTY,
                aggregate=None,
                aggregator_version=(
                    request.context.aggregator_version
                ),
            )

        evidence_ids = self._collect_evidence_ids(
            active_contributions
        )

        identity_seed_ids = (
            self._collect_identity_seed_ids(
                request=request,
                contributions=active_contributions,
            )
        )

        evidence_summary = self._build_evidence_summary(
            active_contributions
        )

        source_summary = self._build_source_summary(
            active_contributions
        )

        temporal_summary = self._build_temporal_summary(
            active_contributions
        )

        conflict_summary = self._build_conflict_summary(
            active_contributions
        )

        aggregate = EvidenceAggregate(
            scope=request.scope,
            service_id=request.service_id,
            unresolved_identifiers=(
                request.unresolved_identifiers
            ),
            alternative_service_ids=(
                request.alternative_service_ids
            ),
            identity_seed_ids=identity_seed_ids,
            evidence_ids=evidence_ids,
            evidence_summary=evidence_summary,
            source_summary=source_summary,
            temporal_summary=temporal_summary,
            conflict_summary=conflict_summary,
            coverage_summary=None,
            aggregator_version=(
                request.context.aggregator_version
            ),
        )

        return AggregationResult(
            processing_status=ProcessingStatus.SUCCESS,
            aggregation_status=AggregationStatus.AGGREGATED,
            aggregate=aggregate,
            aggregator_version=(
                request.context.aggregator_version
            ),
        )

    @staticmethod
    def _collect_evidence_ids(
        contributions: tuple[
            EvidenceContribution,
            ...,
        ],
    ) -> tuple[EvidenceId, ...]:
        evidence_by_id = {
            contribution.evidence.id.value: (
                contribution.evidence.id
            )
            for contribution in contributions
        }

        return tuple(
            evidence_by_id[key]
            for key in sorted(
                evidence_by_id
            )
        )

    @staticmethod
    def _collect_identity_seed_ids(
        request: AggregationRequest,
        contributions: tuple[
            EvidenceContribution,
            ...,
        ],
    ) -> tuple[IdentitySeedId, ...]:
        identity_seed_ids: dict[
            str,
            IdentitySeedId,
        ] = {
            identity_seed_id.value: identity_seed_id
            for identity_seed_id
            in request.identity_seed_ids
        }

        for contribution in contributions:
            for identity_seed_id in (
                contribution.evidence.identity_seed_ids
            ):
                identity_seed_ids[
                    identity_seed_id.value
                ] = identity_seed_id

        return tuple(
            identity_seed_ids[key]
            for key in sorted(
                identity_seed_ids
            )
        )

    @staticmethod
    def _build_evidence_summary(
        contributions: tuple[
            EvidenceContribution,
            ...,
        ],
    ) -> EvidenceSummary:
        evidence_count_by_type = Counter(
            contribution.evidence.evidence_type
            for contribution in contributions
        )

        active_evidence_types = tuple(
            sorted(
                evidence_count_by_type.keys(),
                key=lambda evidence_type: (
                    evidence_type.value
                ),
            )
        )

        return EvidenceSummary(
            total_evidence_count=len(
                contributions
            ),
            evidence_count_by_type=dict(
                evidence_count_by_type
            ),
            active_evidence_types=active_evidence_types,
        )

    @staticmethod
    def _build_source_summary(
        contributions: tuple[
            EvidenceContribution,
            ...,
        ],
    ) -> SourceSummary:
        connected_sources: dict[
            str,
            ConnectedSourceId,
        ] = {}

        source_types: dict[
            str,
            SourceType,
        ] = {}

        providers: dict[
            str,
            Provider,
        ] = {}

        evidence_count_by_connected_source: Counter[
            ConnectedSourceId
        ] = Counter()

        evidence_count_by_source_type: Counter[
            SourceType
        ] = Counter()

        for contribution in contributions:
            for connected_source_id in (
                contribution.connected_source_ids
            ):
                connected_sources[
                    connected_source_id.value
                ] = connected_source_id

                evidence_count_by_connected_source[
                    connected_source_id
                ] += 1

            for source_type in contribution.source_types:
                source_types[
                    source_type.value
                ] = source_type

                evidence_count_by_source_type[
                    source_type
                ] += 1

            for provider in contribution.providers:
                providers[
                    provider.id
                ] = provider

        return SourceSummary(
            connected_source_count=len(
                connected_sources
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
            evidence_count_by_connected_source=dict(
                evidence_count_by_connected_source
            ),
            evidence_count_by_source_type=dict(
                evidence_count_by_source_type
            ),
        )

    @staticmethod
    def _build_temporal_summary(
        contributions: tuple[
            EvidenceContribution,
            ...,
        ],
    ) -> TemporalSummary:
        temporal_values: list[
            TemporalValue
        ] = []

        for contribution in contributions:
            temporal_values.extend(
                contribution.temporal_values
            )

        ordered_values = tuple(
            sorted(
                temporal_values,
                key=lambda temporal_value: (
                    temporal_value.timestamp
                ),
            )
        )

        first_observed = (
            ordered_values[0]
            if ordered_values
            else None
        )

        last_observed = (
            ordered_values[-1]
            if ordered_values
            else None
        )

        return TemporalSummary(
            first_observed=first_observed,
            last_observed=last_observed,
            typed_temporal_values=ordered_values,
        )

    @staticmethod
    def _build_conflict_summary(
        contributions: tuple[
            EvidenceContribution,
            ...,
        ],
    ) -> ConflictSummary:
        return ConflictSummary(
            has_potential_conflicts=False,
            conflict_types=(),
            involved_evidence_ids=(),
        )
