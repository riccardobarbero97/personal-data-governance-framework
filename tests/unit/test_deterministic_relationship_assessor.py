from datetime import datetime, timedelta, timezone

from personal_data_governance.discovery.relationship_assessment.deterministic import (
    DeterministicRelationshipAssessor,
)
from personal_data_governance.discovery.relationship_assessment.protocol import (
    RelationshipAssessmentContext,
)
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.observation import (
    TemporalSemantics,
)
from personal_data_governance.domain.enums.processing import (
    AggregationScope,
    AssessmentMethod,
    ProcessingStatus,
)
from personal_data_governance.domain.enums.relationship import (
    RelationshipStatus,
    TemporalStatus,
)
from personal_data_governance.domain.enums.source import SourceType
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    IdentitySeedId,
    ServiceId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.temporal import TemporalValue
from personal_data_governance.domain.views.evidence_aggregate import (
    ConflictSummary,
    CoverageSummary,
    EvidenceAggregate,
    EvidenceSummary,
    SourceSummary,
    TemporalSummary,
)


ASSESSED_AT = datetime(
    2026,
    11,
    16,
    12,
    0,
    tzinfo=timezone.utc,
)


def build_context(
    user_rejected: bool = False,
    window_days: int = 365,
) -> RelationshipAssessmentContext:
    return RelationshipAssessmentContext(
        assessor_version="1",
        assessment_policy_version="1",
        assessed_at=ASSESSED_AT,
        currently_observed_window_days=window_days,
        user_rejected=user_rejected,
    )


def build_aggregate(
    evidence_types: tuple[EvidenceType, ...],
    last_observed: TemporalValue | None,
    service_id: ServiceId | None = None,
    conflict_summary: ConflictSummary | None = None,
    coverage_summary: CoverageSummary | None = None,
) -> EvidenceAggregate:
    effective_service_id = (
        service_id
        if service_id is not None
        else ServiceId("service_spotify")
    )

    evidence_ids = tuple(
        EvidenceId(
            f"evidence_{index:03d}"
        )
        for index, _ in enumerate(
            evidence_types,
            start=1,
        )
    )

    evidence_count_by_type = {
        evidence_type: evidence_types.count(
            evidence_type
        )
        for evidence_type in set(
            evidence_types
        )
    }

    typed_temporal_values = (
        (last_observed,)
        if last_observed is not None
        else ()
    )

    return EvidenceAggregate(
        scope=AggregationScope.SERVICE,
        service_id=effective_service_id,
        unresolved_identifiers=(),
        alternative_service_ids=(),
        identity_seed_ids=(
            IdentitySeedId("identity_email"),
        ),
        evidence_ids=evidence_ids,
        evidence_summary=EvidenceSummary(
            total_evidence_count=len(
                evidence_types
            ),
            evidence_count_by_type=(
                evidence_count_by_type
            ),
            active_evidence_types=tuple(
                sorted(
                    set(evidence_types),
                    key=lambda item: item.value,
                )
            ),
        ),
        source_summary=SourceSummary(
            connected_source_count=1,
            source_types=(
                SourceType.EMAIL,
            ),
            providers=(
                Provider(
                    id="google",
                    display_name="Google",
                ),
            ),
            evidence_count_by_connected_source={
                ConnectedSourceId(
                    "source_gmail"
                ): len(evidence_types)
            },
            evidence_count_by_source_type={
                SourceType.EMAIL: len(
                    evidence_types
                )
            },
        ),
        temporal_summary=TemporalSummary(
            first_observed=last_observed,
            last_observed=last_observed,
            typed_temporal_values=(
                typed_temporal_values
            ),
        ),
        conflict_summary=(
            conflict_summary
            if conflict_summary is not None
            else ConflictSummary(
                has_potential_conflicts=False,
                conflict_types=(),
                involved_evidence_ids=(),
            )
        ),
        coverage_summary=coverage_summary,
        aggregator_version="1",
    )


def recent_temporal_value() -> TemporalValue:
    return TemporalValue(
        timestamp=ASSESSED_AT
        - timedelta(days=10),
        semantics=TemporalSemantics.MESSAGE_TIME,
    )


def old_temporal_value() -> TemporalValue:
    return TemporalValue(
        timestamp=ASSESSED_AT
        - timedelta(days=800),
        semantics=TemporalSemantics.MESSAGE_TIME,
    )


def test_account_verification_establishes_relationship() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
        ),
        last_observed=recent_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS

    assert (
        result.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        result.temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )

    assert result.method == AssessmentMethod.RULE

    assert result.reason_codes == (
        "ESTABLISHMENT_EVIDENCE_PRESENT",
        "RECENT_OBSERVABLE_ACTIVITY",
    )


def test_marketing_only_is_observed() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.MARKETING,
        ),
        last_observed=recent_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.OBSERVED
    )

    assert (
        result.temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )

    assert "COMMUNICATION_ONLY" in result.reason_codes


def test_newsletter_and_privacy_notice_remain_observed() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.NEWSLETTER,
            EvidenceType.PRIVACY_NOTICE,
        ),
        last_observed=recent_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.OBSERVED
    )


def test_account_deletion_without_ongoing_activity_is_historical() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_CREATION,
            EvidenceType.ACCOUNT_DELETION,
        ),
        last_observed=recent_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        result.temporal_status
        == TemporalStatus.HISTORICAL
    )

    assert (
        "ACCOUNT_DELETION_WITHOUT_ONGOING_ACTIVITY"
        in result.reason_codes
    )


def test_deletion_with_authentication_is_not_forced_historical() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_DELETION,
            EvidenceType.AUTHENTICATION,
        ),
        last_observed=recent_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        result.temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )


def test_old_evidence_is_not_automatically_historical() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
        ),
        last_observed=old_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        result.temporal_status
        == TemporalStatus.UNKNOWN
    )

    assert (
        "CURRENT_CONTINUATION_NOT_ESTABLISHED"
        in result.reason_codes
    )


def test_missing_temporal_information_returns_unknown() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
        ),
        last_observed=None,
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        result.temporal_status
        == TemporalStatus.UNKNOWN
    )

    assert (
        "TEMPORAL_EVIDENCE_UNAVAILABLE"
        in result.reason_codes
    )


def test_user_rejection_overrides_automated_relationship_status() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
            EvidenceType.PAYMENT,
        ),
        last_observed=recent_temporal_value(),
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(
            user_rejected=True
        ),
    )

    assert (
        result.relationship_status
        == RelationshipStatus.REJECTED
    )

    assert (
        result.temporal_status
        == TemporalStatus.UNKNOWN
    )

    assert result.reason_codes == (
        "USER_REJECTED",
        "TEMPORAL_STATUS_NOT_ASSESSED_FOR_REJECTED_RELATIONSHIP",
    )


def test_conflict_summary_produces_warning() -> None:
    conflict_summary = ConflictSummary(
        has_potential_conflicts=True,
        conflict_types=(
            "DELETION_FOLLOWED_BY_ACTIVITY",
        ),
        involved_evidence_ids=(
            EvidenceId("evidence_001"),
            EvidenceId("evidence_002"),
        ),
    )

    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_DELETION,
            EvidenceType.AUTHENTICATION,
        ),
        last_observed=recent_temporal_value(),
        conflict_summary=conflict_summary,
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert "CONFLICTING_EVIDENCE" in result.warnings


def test_incomplete_coverage_produces_warning() -> None:
    coverage_summary = CoverageSummary(
        configured_source_ids=(
            ConnectedSourceId("source_gmail"),
            ConnectedSourceId("source_outlook"),
        ),
        completed_source_ids=(
            ConnectedSourceId("source_gmail"),
        ),
        partial_source_ids=(),
        failed_source_ids=(
            ConnectedSourceId("source_outlook"),
        ),
        unavailable_source_ids=(),
    )

    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
        ),
        last_observed=recent_temporal_value(),
        coverage_summary=coverage_summary,
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        "INCOMPLETE_SOURCE_COVERAGE"
        in result.warnings
    )


def test_future_temporal_evidence_returns_unknown_with_warning() -> None:
    future_value = TemporalValue(
        timestamp=ASSESSED_AT
        + timedelta(days=1),
        semantics=TemporalSemantics.MESSAGE_TIME,
    )

    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
        ),
        last_observed=future_value,
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert (
        result.temporal_status
        == TemporalStatus.UNKNOWN
    )

    assert (
        "TEMPORAL_EVIDENCE_IN_FUTURE"
        in result.reason_codes
    )

    assert (
        "FUTURE_TEMPORAL_EVIDENCE"
        in result.warnings
    )


def test_assessment_preserves_service_and_evidence_basis() -> None:
    service_id = ServiceId("service_spotify")

    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
            EvidenceType.PAYMENT,
        ),
        last_observed=recent_temporal_value(),
        service_id=service_id,
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=build_context(),
    )

    assert result.service_id == service_id

    assert result.evidence_ids == (
        EvidenceId("evidence_001"),
        EvidenceId("evidence_002"),
    )

    assert result.identity_seed_ids == (
        IdentitySeedId("identity_email"),
    )


def test_assessor_versions_are_preserved() -> None:
    aggregate = build_aggregate(
        evidence_types=(
            EvidenceType.ACCOUNT_VERIFICATION,
        ),
        last_observed=recent_temporal_value(),
    )

    context = RelationshipAssessmentContext(
        assessor_version="assessor_1.0",
        assessment_policy_version="policy_1.0",
        assessed_at=ASSESSED_AT,
    )

    result = DeterministicRelationshipAssessor().assess(
        aggregate=aggregate,
        context=context,
    )

    assert result.assessor_version == "assessor_1.0"

    assert (
        result.assessment_policy_version
        == "policy_1.0"
    )
