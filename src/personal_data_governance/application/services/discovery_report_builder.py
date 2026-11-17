from datetime import datetime, timezone

from personal_data_governance.application.results.discovery import (
    DiscoveryOutcome,
)
from personal_data_governance.application.results.discovery_report import (
    DiscoveryReport,
    DiscoveryReportEntry,
    DiscoveryReportEvidence,
    DiscoveryReportSummary,
)
from personal_data_governance.domain.enums.processing import (
    CandidateStatus,
    ClassificationStatus,
    ResolutionStatus,
)


class DiscoveryReportBuilder:
    def build(
        self,
        outcomes: tuple[DiscoveryOutcome, ...],
        source_mode: str,
        synthetic_data: bool,
        generated_at: datetime | None = None,
    ) -> DiscoveryReport:
        effective_generated_at = (
            generated_at
            if generated_at is not None
            else datetime.now(timezone.utc)
        )

        if (
            effective_generated_at.tzinfo
            is None
            or effective_generated_at.utcoffset()
            is None
        ):
            raise ValueError(
                "Report generation time must be "
                "timezone-aware."
            )

        entries = tuple(
            self._build_entry(
                outcome
            )
            for outcome in outcomes
        )

        summary = self._build_summary(
            outcomes
        )

        return DiscoveryReport(
            schema_version=1,
            generated_at=(
                effective_generated_at
                .astimezone(timezone.utc)
                .isoformat()
            ),
            source_mode=source_mode,
            synthetic_data=synthetic_data,
            summary=summary,
            entries=entries,
        )

    @staticmethod
    def _build_entry(
        outcome: DiscoveryOutcome,
    ) -> DiscoveryReportEntry:
        candidate_status = (
            outcome.candidate_result
            .candidate_status
        )

        candidate_identifiers = tuple(
            identifier.value
            for identifier in (
                outcome.candidate_result
                .candidate_identifiers
            )
        )

        resolution_status = None
        resolved_service_id = None
        alternative_service_ids: tuple[
            str,
            ...,
        ] = ()

        resolution_reason_codes: tuple[
            str,
            ...,
        ] = ()

        if outcome.resolution_result is not None:
            resolution_status_value = (
                outcome.resolution_result
                .resolution_status
            )

            if resolution_status_value is not None:
                resolution_status = (
                    resolution_status_value.value
                )

            if (
                outcome.resolution_result
                .resolved_service_id
                is not None
            ):
                resolved_service_id = (
                    outcome.resolution_result
                    .resolved_service_id
                    .value
                )

            alternative_service_ids = tuple(
                service_id.value
                for service_id in (
                    outcome.resolution_result
                    .alternative_service_ids
                )
            )

            resolution_reason_codes = (
                outcome.resolution_result
                .reason_codes
            )

        classification_status_value = (
            outcome.classification_result
            .classification_status
        )

        classification_status = (
            classification_status_value.value
            if classification_status_value
            is not None
            else None
        )

        evidence = tuple(
            DiscoveryReportEvidence(
                evidence_type=(
                    candidate.evidence_type.value
                ),
                evidence_ids=tuple(
                    evidence_id.value
                    for evidence_id
                    in outcome.evidence_ids
                ),
            )
            for candidate in (
                outcome.classification_result
                .evidence_candidates
            )
        )

        relationship_status = None
        temporal_status = None
        assessment_reason_codes: tuple[
            str,
            ...,
        ] = ()
        warnings: tuple[
            str,
            ...,
        ] = ()

        if outcome.assessment_result is not None:
            if (
                outcome.assessment_result
                .relationship_status
                is not None
            ):
                relationship_status = (
                    outcome.assessment_result
                    .relationship_status
                    .value
                )

            if (
                outcome.assessment_result
                .temporal_status
                is not None
            ):
                temporal_status = (
                    outcome.assessment_result
                    .temporal_status
                    .value
                )

            assessment_reason_codes = (
                outcome.assessment_result
                .reason_codes
            )

            warnings = (
                outcome.assessment_result
                .warnings
            )

        relationship_id = (
            outcome.relationship_id.value
            if outcome.relationship_id
            is not None
            else None
        )

        reason_codes = tuple(
            dict.fromkeys(
                outcome.candidate_result.reason_codes
                + resolution_reason_codes
                + outcome.classification_result.reason_codes
                + assessment_reason_codes
            )
        )

        return DiscoveryReportEntry(
            observation_id=(
                outcome.observation_id.value
            ),
            candidate_status=(
                candidate_status.value
                if candidate_status is not None
                else None
            ),
            candidate_identifiers=(
                candidate_identifiers
            ),
            resolution_status=resolution_status,
            resolved_service_id=resolved_service_id,
            alternative_service_ids=(
                alternative_service_ids
            ),
            classification_status=(
                classification_status
            ),
            evidence=evidence,
            relationship_status=(
                relationship_status
            ),
            temporal_status=temporal_status,
            relationship_id=relationship_id,
            reason_codes=reason_codes,
            warnings=warnings,
        )

    @staticmethod
    def _build_summary(
        outcomes: tuple[DiscoveryOutcome, ...],
    ) -> DiscoveryReportSummary:
        candidate_count = 0
        resolved_count = 0
        unresolved_count = 0
        ambiguous_count = 0
        classified_count = 0
        unknown_classification_count = 0

        relationship_ids: set[str] = set()

        for outcome in outcomes:
            if (
                outcome.candidate_result
                .candidate_status
                == CandidateStatus.CANDIDATE
            ):
                candidate_count += 1

            if outcome.resolution_result is not None:
                resolution_status = (
                    outcome.resolution_result
                    .resolution_status
                )

                if (
                    resolution_status
                    == ResolutionStatus.RESOLVED
                ):
                    resolved_count += 1

                elif (
                    resolution_status
                    == ResolutionStatus.UNRESOLVED
                ):
                    unresolved_count += 1

                elif (
                    resolution_status
                    == ResolutionStatus.AMBIGUOUS
                ):
                    ambiguous_count += 1

            classification_status = (
                outcome.classification_result
                .classification_status
            )

            if (
                classification_status
                == ClassificationStatus.CLASSIFIED
            ):
                classified_count += 1

            elif (
                classification_status
                == ClassificationStatus.UNKNOWN
            ):
                unknown_classification_count += 1

            if outcome.relationship_id is not None:
                relationship_ids.add(
                    outcome.relationship_id.value
                )

        return DiscoveryReportSummary(
            observation_count=len(
                outcomes
            ),
            candidate_count=candidate_count,
            resolved_count=resolved_count,
            unresolved_count=unresolved_count,
            ambiguous_count=ambiguous_count,
            classified_count=classified_count,
            unknown_classification_count=(
                unknown_classification_count
            ),
            materialized_relationship_count=len(
                relationship_ids
            ),
        )
