from datetime import timedelta

from personal_data_governance.application.results.assessment import (
    RelationshipAssessmentResult,
)
from personal_data_governance.config.loaders import (
    RelationshipPolicyConfiguration,
)
from personal_data_governance.discovery.relationship_assessment.protocol import (
    RelationshipAssessmentContext,
    RelationshipAssessor,
)
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.processing import (
    AssessmentMethod,
    ProcessingStatus,
)
from personal_data_governance.domain.enums.relationship import (
    RelationshipStatus,
    TemporalStatus,
)
from personal_data_governance.domain.views.evidence_aggregate import (
    EvidenceAggregate,
)


class DeterministicRelationshipAssessor(
    RelationshipAssessor,
):
    def __init__(
        self,
        policy: RelationshipPolicyConfiguration,
    ) -> None:
        self._policy = policy

    def assess(
        self,
        aggregate: EvidenceAggregate,
        context: RelationshipAssessmentContext,
    ) -> RelationshipAssessmentResult:
        evidence_types = frozenset(
            aggregate.evidence_summary.active_evidence_types
        )

        relationship_status, relationship_reasons = (
            self._assess_relationship_status(
                evidence_types=evidence_types,
                total_evidence_count=(
                    aggregate.evidence_summary
                    .total_evidence_count
                ),
                user_rejected=(
                    context.user_rejected
                ),
            )
        )

        (
            temporal_status,
            temporal_reasons,
            temporal_warnings,
        ) = self._assess_temporal_status(
            aggregate=aggregate,
            evidence_types=evidence_types,
            context=context,
            relationship_status=relationship_status,
        )

        warnings = self._collect_warnings(
            aggregate=aggregate,
            additional_warnings=(
                temporal_warnings
            ),
        )

        reason_codes = self._deduplicate_strings(
            relationship_reasons
            + temporal_reasons
        )

        return RelationshipAssessmentResult(
            processing_status=ProcessingStatus.SUCCESS,
            service_id=aggregate.service_id,
            relationship_status=relationship_status,
            temporal_status=temporal_status,
            identity_seed_ids=(
                aggregate.identity_seed_ids
            ),
            evidence_ids=aggregate.evidence_ids,
            reason_codes=reason_codes,
            warnings=warnings,
            method=AssessmentMethod.RULE,
            assessor_version=(
                context.assessor_version
            ),
            assessment_policy_version=(
                self._policy.policy_version
            ),
        )

    def _assess_relationship_status(
        self,
        evidence_types: frozenset[EvidenceType],
        total_evidence_count: int,
        user_rejected: bool,
    ) -> tuple[
        RelationshipStatus,
        tuple[str, ...],
    ]:
        if user_rejected:
            return (
                RelationshipStatus.REJECTED,
                (
                    "USER_REJECTED",
                ),
            )

        if total_evidence_count == 0:
            return (
                RelationshipStatus.UNKNOWN,
                (
                    "NO_ELIGIBLE_EVIDENCE",
                ),
            )

        establishment_types = (
            evidence_types
            & self._policy
            .establishment_evidence_types
        )

        if establishment_types:
            return (
                RelationshipStatus.ESTABLISHED,
                (
                    "ESTABLISHMENT_EVIDENCE_PRESENT",
                ),
            )

        observed_types = (
            evidence_types
            & self._policy
            .observed_communication_evidence_types
        )

        if observed_types:
            return (
                RelationshipStatus.OBSERVED,
                (
                    "COMMUNICATION_ONLY",
                ),
            )

        return (
            RelationshipStatus.UNKNOWN,
            (
                "INSUFFICIENT_EVIDENCE",
            ),
        )

    def _assess_temporal_status(
        self,
        aggregate: EvidenceAggregate,
        evidence_types: frozenset[EvidenceType],
        context: RelationshipAssessmentContext,
        relationship_status: RelationshipStatus,
    ) -> tuple[
        TemporalStatus,
        tuple[str, ...],
        tuple[str, ...],
    ]:
        if relationship_status == RelationshipStatus.REJECTED:
            return (
                TemporalStatus.UNKNOWN,
                (
                    "TEMPORAL_STATUS_NOT_ASSESSED_FOR_REJECTED_RELATIONSHIP",
                ),
                (),
            )

        last_observed = (
            aggregate.temporal_summary
            .last_observed
        )

        if last_observed is None:
            return (
                TemporalStatus.UNKNOWN,
                (
                    "TEMPORAL_EVIDENCE_UNAVAILABLE",
                ),
                (),
            )

        if not self._is_timezone_aware(
            last_observed.timestamp
        ):
            return (
                TemporalStatus.UNKNOWN,
                (
                    "TEMPORAL_EVIDENCE_UNUSABLE",
                ),
                (
                    "TEMPORAL_VALUE_WITHOUT_TIMEZONE",
                ),
            )

        if (
            last_observed.timestamp
            > context.assessed_at
        ):
            return (
                TemporalStatus.UNKNOWN,
                (
                    "TEMPORAL_EVIDENCE_IN_FUTURE",
                ),
                (
                    "FUTURE_TEMPORAL_EVIDENCE",
                ),
            )

        has_deletion_evidence = (
            self._policy.deletion_evidence_type
            in evidence_types
        )

        has_ongoing_activity = bool(
            evidence_types
            & self._policy
            .ongoing_activity_evidence_types
        )

        if (
            has_deletion_evidence
            and not has_ongoing_activity
        ):
            return (
                TemporalStatus.HISTORICAL,
                (
                    "ACCOUNT_DELETION_WITHOUT_ONGOING_ACTIVITY",
                ),
                (),
            )

        currently_observed_cutoff = (
            context.assessed_at
            - timedelta(
                days=(
                    self._policy
                    .currently_observed_window_days
                )
            )
        )

        if (
            last_observed.timestamp
            >= currently_observed_cutoff
        ):
            return (
                TemporalStatus.CURRENTLY_OBSERVED,
                (
                    "RECENT_OBSERVABLE_ACTIVITY",
                ),
                (),
            )

        return (
            TemporalStatus.UNKNOWN,
            (
                "CURRENT_CONTINUATION_NOT_ESTABLISHED",
            ),
            (),
        )

    @staticmethod
    def _collect_warnings(
        aggregate: EvidenceAggregate,
        additional_warnings: tuple[str, ...],
    ) -> tuple[str, ...]:
        warnings = list(
            additional_warnings
        )

        if (
            aggregate.conflict_summary
            .has_potential_conflicts
        ):
            warnings.append(
                "CONFLICTING_EVIDENCE"
            )

        coverage_summary = (
            aggregate.coverage_summary
        )

        if coverage_summary is not None:
            if (
                coverage_summary.partial_source_ids
                or coverage_summary.failed_source_ids
                or coverage_summary.unavailable_source_ids
            ):
                warnings.append(
                    "INCOMPLETE_SOURCE_COVERAGE"
                )

        if aggregate.service_id is None:
            warnings.append(
                "CANONICAL_SERVICE_UNAVAILABLE"
            )

        return (
            DeterministicRelationshipAssessor
            ._deduplicate_strings(
                tuple(
                    warnings
                )
            )
        )

    @staticmethod
    def _deduplicate_strings(
        values: tuple[str, ...],
    ) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                values
            )
        )

    @staticmethod
    def _is_timezone_aware(
        value,
    ) -> bool:
        return (
            value.tzinfo is not None
            and value.utcoffset() is not None
        )
