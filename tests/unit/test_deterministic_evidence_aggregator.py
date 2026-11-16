from datetime import datetime, timezone

from personal_data_governance.application.values.evidence_contribution import (
    EvidenceContribution,
)
from personal_data_governance.discovery.evidence_aggregation.deterministic import (
    DeterministicEvidenceAggregator,
)
from personal_data_governance.discovery.evidence_aggregation.protocol import (
    AggregationContext,
    AggregationRequest,
)
from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.enums.evidence import (
    EvidenceStatus,
    EvidenceType,
)
from personal_data_governance.domain.enums.observation import (
    TemporalSemantics,
)
from personal_data_governance.domain.enums.processing import (
    AggregationScope,
    AggregationStatus,
    ClassificationMethod,
    ProcessingStatus,
    ServiceIdentifierType,
)
from personal_data_governance.domain.enums.source import SourceType
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    IdentitySeedId,
    ObservationId,
    ServiceId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)
from personal_data_governance.domain.values.temporal import TemporalValue


def build_evidence(
    evidence_id: str,
    evidence_type: EvidenceType,
    status: EvidenceStatus = EvidenceStatus.ACTIVE,
    service_id: ServiceId | None = None,
    identity_seed_ids: tuple[IdentitySeedId, ...] = (),
) -> Evidence:
    return Evidence(
        id=EvidenceId(evidence_id),
        evidence_type=evidence_type,
        evidence_status=status,
        observation_ids=(
            ObservationId(
                f"observation_{evidence_id}"
            ),
        ),
        service_id=service_id,
        identity_seed_ids=identity_seed_ids,
        classification_method=ClassificationMethod.RULE,
        classifier_version="1",
        reason_codes=(
            "TEST_RULE",
        ),
    )


def build_contribution(
    evidence: Evidence,
    source_id: str,
    provider_id: str,
    timestamp: datetime,
) -> EvidenceContribution:
    return EvidenceContribution(
        evidence=evidence,
        connected_source_ids=(
            ConnectedSourceId(source_id),
        ),
        source_types=(
            SourceType.EMAIL,
        ),
        providers=(
            Provider(
                id=provider_id,
                display_name=provider_id.title(),
            ),
        ),
        temporal_values=(
            TemporalValue(
                timestamp=timestamp,
                semantics=(
                    TemporalSemantics.MESSAGE_TIME
                ),
            ),
        ),
    )


def build_context() -> AggregationContext:
    return AggregationContext(
        aggregator_version="1",
    )


def test_service_evidence_is_aggregated() -> None:
    service_id = ServiceId(
        "service_spotify"
    )

    identity_id = IdentitySeedId(
        "identity_email"
    )

    verification = build_evidence(
        evidence_id="evidence_001",
        evidence_type=(
            EvidenceType.ACCOUNT_VERIFICATION
        ),
        service_id=service_id,
        identity_seed_ids=(
            identity_id,
        ),
    )

    payment = build_evidence(
        evidence_id="evidence_002",
        evidence_type=EvidenceType.PAYMENT,
        service_id=service_id,
        identity_seed_ids=(
            identity_id,
        ),
    )

    verification_contribution = (
        build_contribution(
            evidence=verification,
            source_id="source_gmail",
            provider_id="google",
            timestamp=datetime(
                2025,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        )
    )

    payment_contribution = (
        build_contribution(
            evidence=payment,
            source_id="source_gmail",
            provider_id="google",
            timestamp=datetime(
                2026,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        )
    )

    request = AggregationRequest(
        scope=AggregationScope.SERVICE,
        service_id=service_id,
        unresolved_identifiers=(),
        alternative_service_ids=(),
        identity_seed_ids=(
            identity_id,
        ),
        contributions=(
            verification_contribution,
            payment_contribution,
        ),
        context=build_context(),
    )

    aggregator = DeterministicEvidenceAggregator()

    result = aggregator.aggregate(
        request
    )

    assert (
        result.processing_status
        == ProcessingStatus.SUCCESS
    )

    assert (
        result.aggregation_status
        == AggregationStatus.AGGREGATED
    )

    assert result.aggregate is not None

    aggregate = result.aggregate

    assert aggregate.service_id == service_id

    assert aggregate.evidence_ids == (
        EvidenceId("evidence_001"),
        EvidenceId("evidence_002"),
    )

    assert aggregate.identity_seed_ids == (
        identity_id,
    )

    assert (
        aggregate.evidence_summary.total_evidence_count
        == 2
    )

    assert (
        aggregate.evidence_summary.evidence_count_by_type[
            EvidenceType.ACCOUNT_VERIFICATION
        ]
        == 1
    )

    assert (
        aggregate.evidence_summary.evidence_count_by_type[
            EvidenceType.PAYMENT
        ]
        == 1
    )

    assert (
        aggregate.source_summary.connected_source_count
        == 1
    )

    assert aggregate.source_summary.source_types == (
        SourceType.EMAIL,
    )

    assert (
        aggregate.temporal_summary.first_observed
        is not None
    )

    assert (
        aggregate.temporal_summary.first_observed.timestamp
        == datetime(
            2025,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )

    assert (
        aggregate.temporal_summary.last_observed
        is not None
    )

    assert (
        aggregate.temporal_summary.last_observed.timestamp
        == datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        )
    )


def test_non_active_evidence_is_excluded() -> None:
    service_id = ServiceId(
        "service_spotify"
    )

    active_evidence = build_evidence(
        evidence_id="evidence_active",
        evidence_type=EvidenceType.PAYMENT,
        service_id=service_id,
    )

    superseded_evidence = build_evidence(
        evidence_id="evidence_superseded",
        evidence_type=EvidenceType.MARKETING,
        status=EvidenceStatus.SUPERSEDED,
        service_id=service_id,
    )

    rejected_evidence = build_evidence(
        evidence_id="evidence_rejected",
        evidence_type=EvidenceType.NEWSLETTER,
        status=EvidenceStatus.REJECTED,
        service_id=service_id,
    )

    contributions = (
        build_contribution(
            active_evidence,
            "source_001",
            "google",
            datetime(
                2026,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        ),
        build_contribution(
            superseded_evidence,
            "source_001",
            "google",
            datetime(
                2026,
                1,
                2,
                tzinfo=timezone.utc,
            ),
        ),
        build_contribution(
            rejected_evidence,
            "source_001",
            "google",
            datetime(
                2026,
                1,
                3,
                tzinfo=timezone.utc,
            ),
        ),
    )

    request = AggregationRequest(
        scope=AggregationScope.SERVICE,
        service_id=service_id,
        unresolved_identifiers=(),
        alternative_service_ids=(),
        identity_seed_ids=(),
        contributions=contributions,
        context=build_context(),
    )

    result = DeterministicEvidenceAggregator().aggregate(
        request
    )

    assert result.aggregate is not None

    assert (
        result.aggregate.evidence_summary.total_evidence_count
        == 1
    )

    assert result.aggregate.evidence_ids == (
        EvidenceId("evidence_active"),
    )


def test_no_active_evidence_returns_empty() -> None:
    service_id = ServiceId(
        "service_spotify"
    )

    rejected_evidence = build_evidence(
        evidence_id="evidence_rejected",
        evidence_type=EvidenceType.MARKETING,
        status=EvidenceStatus.REJECTED,
        service_id=service_id,
    )

    contribution = build_contribution(
        rejected_evidence,
        "source_001",
        "google",
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    request = AggregationRequest(
        scope=AggregationScope.SERVICE,
        service_id=service_id,
        unresolved_identifiers=(),
        alternative_service_ids=(),
        identity_seed_ids=(),
        contributions=(
            contribution,
        ),
        context=build_context(),
    )

    result = DeterministicEvidenceAggregator().aggregate(
        request
    )

    assert (
        result.processing_status
        == ProcessingStatus.SUCCESS
    )

    assert (
        result.aggregation_status
        == AggregationStatus.EMPTY
    )

    assert result.aggregate is None


def test_unresolved_evidence_is_preserved() -> None:
    unresolved_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="unknown.example",
        observation_id=ObservationId(
            "observation_evidence_001"
        ),
    )

    evidence = build_evidence(
        evidence_id="evidence_001",
        evidence_type=EvidenceType.PAYMENT,
        service_id=None,
    )

    contribution = build_contribution(
        evidence,
        "source_gmail",
        "google",
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    request = AggregationRequest(
        scope=(
            AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
        ),
        service_id=None,
        unresolved_identifiers=(
            unresolved_identifier,
        ),
        alternative_service_ids=(),
        identity_seed_ids=(),
        contributions=(
            contribution,
        ),
        context=build_context(),
    )

    result = DeterministicEvidenceAggregator().aggregate(
        request
    )

    assert result.aggregate is not None

    assert (
        result.aggregate.scope
        == AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
    )

    assert result.aggregate.service_id is None

    assert result.aggregate.unresolved_identifiers == (
        unresolved_identifier,
    )

    assert result.aggregate.evidence_ids == (
        EvidenceId("evidence_001"),
    )


def test_ambiguous_evidence_is_preserved() -> None:
    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="shared.example",
        observation_id=ObservationId(
            "observation_evidence_001"
        ),
    )

    evidence = build_evidence(
        evidence_id="evidence_001",
        evidence_type=EvidenceType.SUBSCRIPTION,
        service_id=None,
    )

    contribution = build_contribution(
        evidence,
        "source_gmail",
        "google",
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    alternatives = (
        ServiceId("service_a"),
        ServiceId("service_b"),
    )

    request = AggregationRequest(
        scope=(
            AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
        ),
        service_id=None,
        unresolved_identifiers=(
            identifier,
        ),
        alternative_service_ids=alternatives,
        identity_seed_ids=(),
        contributions=(
            contribution,
        ),
        context=build_context(),
    )

    result = DeterministicEvidenceAggregator().aggregate(
        request
    )

    assert result.aggregate is not None

    assert (
        result.aggregate.scope
        == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
    )

    assert result.aggregate.service_id is None

    assert (
        result.aggregate.alternative_service_ids
        == alternatives
    )


def test_evidence_from_multiple_sources_preserves_source_diversity() -> None:
    service_id = ServiceId(
        "service_spotify"
    )

    first_evidence = build_evidence(
        evidence_id="evidence_001",
        evidence_type=(
            EvidenceType.ACCOUNT_VERIFICATION
        ),
        service_id=service_id,
    )

    second_evidence = build_evidence(
        evidence_id="evidence_002",
        evidence_type=EvidenceType.PAYMENT,
        service_id=service_id,
    )

    first_contribution = EvidenceContribution(
        evidence=first_evidence,
        connected_source_ids=(
            ConnectedSourceId("source_gmail"),
        ),
        source_types=(
            SourceType.EMAIL,
        ),
        providers=(
            Provider(
                id="google",
                display_name="Google",
            ),
        ),
        temporal_values=(),
    )

    second_contribution = EvidenceContribution(
        evidence=second_evidence,
        connected_source_ids=(
            ConnectedSourceId("source_outlook"),
        ),
        source_types=(
            SourceType.EMAIL,
        ),
        providers=(
            Provider(
                id="microsoft",
                display_name="Microsoft",
            ),
        ),
        temporal_values=(),
    )

    request = AggregationRequest(
        scope=AggregationScope.SERVICE,
        service_id=service_id,
        unresolved_identifiers=(),
        alternative_service_ids=(),
        identity_seed_ids=(),
        contributions=(
            first_contribution,
            second_contribution,
        ),
        context=build_context(),
    )

    result = DeterministicEvidenceAggregator().aggregate(
        request
    )

    assert result.aggregate is not None

    source_summary = result.aggregate.source_summary

    assert source_summary.connected_source_count == 2

    assert source_summary.source_types == (
        SourceType.EMAIL,
    )

    assert len(source_summary.providers) == 2

    assert Provider(
        id="google",
        display_name="Google",
    ) in source_summary.providers

    assert Provider(
        id="microsoft",
        display_name="Microsoft",
    ) in source_summary.providers


def test_identity_references_are_combined_and_deduplicated() -> None:
    service_id = ServiceId(
        "service_spotify"
    )

    identity_a = IdentitySeedId(
        "identity_a"
    )

    identity_b = IdentitySeedId(
        "identity_b"
    )

    evidence = build_evidence(
        evidence_id="evidence_001",
        evidence_type=(
            EvidenceType.ACCOUNT_VERIFICATION
        ),
        service_id=service_id,
        identity_seed_ids=(
            identity_b,
        ),
    )

    contribution = build_contribution(
        evidence,
        "source_gmail",
        "google",
        datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    request = AggregationRequest(
        scope=AggregationScope.SERVICE,
        service_id=service_id,
        unresolved_identifiers=(),
        alternative_service_ids=(),
        identity_seed_ids=(
            identity_a,
            identity_b,
        ),
        contributions=(
            contribution,
        ),
        context=build_context(),
    )

    result = DeterministicEvidenceAggregator().aggregate(
        request
    )

    assert result.aggregate is not None

    assert result.aggregate.identity_seed_ids == (
        identity_a,
        identity_b,
    )
