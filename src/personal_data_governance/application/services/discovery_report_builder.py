from collections import Counter
from datetime import datetime, timezone

from personal_data_governance.application.results.discovery import (
    DiscoveryOutcome,
)
from personal_data_governance.application.results.discovery_report import (
    DiscoveryRelationship,
    DiscoveryRelationshipEvidence,
    DiscoveryReport,
    DiscoveryReportEntry,
    DiscoveryReportEvidence,
    DiscoveryReportSummary,
    UnresolvedDiscovery,
)
from personal_data_governance.config.service_registry import (
    build_initial_service_registry,
)
from personal_data_governance.domain.enums.processing import (
    CandidateStatus,
    ClassificationStatus,
    ResolutionStatus,
)
from personal_data_governance.domain.values.identifiers import (
    ServiceId,
)


class DiscoveryReportBuilder:
    def build(
        self,
        outcomes: tuple[
            DiscoveryOutcome,
            ...,
        ],
        source_mode: str,
        synthetic_data: bool,
        generated_at: datetime | None = None,
    ) -> DiscoveryReport:
        effective_generated_at = (
            generated_at
            if generated_at is not None
            else datetime.now(
                timezone.utc
            )
        )

        if (
            effective_generated_at.tzinfo
            is None
            or effective_generated_at
            .utcoffset()
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

        return DiscoveryReport(
            schema_version=2,
            generated_at=(
                effective_generated_at
                .astimezone(
                    timezone.utc
                )
                .isoformat()
            ),
            source_mode=source_mode,
            synthetic_data=synthetic_data,
            summary=self._build_summary(
                outcomes
            ),
            relationships=(
                self._build_relationships(
                    outcomes
                )
            ),
            unresolved_discoveries=(
                self._build_unresolved_discoveries(
                    outcomes
                )
            ),
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
                    candidate
                    .evidence_type
                    .value
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

        reason_codes = (
            DiscoveryReportBuilder
            ._deduplicate(
                outcome.candidate_result
                .reason_codes
                + resolution_reason_codes
                + outcome.classification_result
                .reason_codes
                + assessment_reason_codes
            )
        )

        return DiscoveryReportEntry(
            observation_id=(
                outcome.observation_id.value
            ),
            candidate_status=(
                candidate_status.value
                if candidate_status
                is not None
                else None
            ),
            candidate_identifiers=(
                candidate_identifiers
            ),
            resolution_status=(
                resolution_status
            ),
            resolved_service_id=(
                resolved_service_id
            ),
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
            temporal_status=(
                temporal_status
            ),
            relationship_id=(
                relationship_id
            ),
            reason_codes=(
                reason_codes
            ),
            warnings=(
                warnings
            ),
        )

    @staticmethod
    def _build_relationships(
        outcomes: tuple[
            DiscoveryOutcome,
            ...,
        ],
    ) -> tuple[
        DiscoveryRelationship,
        ...,
    ]:
        loaded_registry = (
            build_initial_service_registry()
        )

        latest_by_service: dict[
            str,
            DiscoveryOutcome,
        ] = {}

        observation_ids_by_service: dict[
            str,
            list[str],
        ] = {}

        evidence_types_by_service: dict[
            str,
            Counter[str],
        ] = {}

        evidence_ids_by_service: dict[
            str,
            set[str],
        ] = {}

        for outcome in outcomes:
            if outcome.resolution_result is None:
                continue

            service_id = (
                outcome.resolution_result
                .resolved_service_id
            )

            if service_id is None:
                continue

            service_id_value = (
                service_id.value
            )

            observation_ids_by_service.setdefault(
                service_id_value,
                [],
            ).append(
                outcome.observation_id.value
            )

            evidence_types = (
                evidence_types_by_service
                .setdefault(
                    service_id_value,
                    Counter(),
                )
            )

            for candidate in (
                outcome.classification_result
                .evidence_candidates
            ):
                evidence_types[
                    candidate.evidence_type.value
                ] += 1

            service_evidence_ids = (
                evidence_ids_by_service
                .setdefault(
                    service_id_value,
                    set(),
                )
            )

            for evidence_id in (
                outcome.evidence_ids
            ):
                service_evidence_ids.add(
                    evidence_id.value
                )

            if (
                outcome.relationship_id
                is not None
                and outcome.assessment_result
                is not None
            ):
                latest_by_service[
                    service_id_value
                ] = outcome

        relationships: list[
            DiscoveryRelationship
        ] = []

        for service_id_value in sorted(
            latest_by_service
        ):
            outcome = latest_by_service[
                service_id_value
            ]

            assessment = (
                outcome.assessment_result
            )

            relationship_id = (
                outcome.relationship_id
            )

            if (
                assessment is None
                or relationship_id is None
            ):
                continue

            service = (
                loaded_registry.registry.get(
                    ServiceId(
                        service_id_value
                    )
                )
            )

            service_name = (
                service.canonical_name
                if service is not None
                else service_id_value
            )

            evidence_counter = (
                evidence_types_by_service.get(
                    service_id_value,
                    Counter(),
                )
            )

            evidence = tuple(
                DiscoveryRelationshipEvidence(
                    evidence_type=(
                        evidence_type
                    ),
                    evidence_count=(
                        evidence_counter[
                            evidence_type
                        ]
                    ),
                )
                for evidence_type in sorted(
                    evidence_counter
                )
            )

            relationships.append(
                DiscoveryRelationship(
                    service_id=(
                        service_id_value
                    ),
                    service_name=(
                        service_name
                    ),
                    relationship_id=(
                        relationship_id.value
                    ),
                    relationship_status=(
                        assessment
                        .relationship_status
                        .value
                    ),
                    temporal_status=(
                        assessment
                        .temporal_status
                        .value
                    ),
                    evidence_count=len(
                        evidence_ids_by_service.get(
                            service_id_value,
                            set(),
                        )
                    ),
                    evidence=evidence,
                    observation_ids=tuple(
                        dict.fromkeys(
                            observation_ids_by_service
                            .get(
                                service_id_value,
                                [],
                            )
                        )
                    ),
                    reason_codes=(
                        assessment.reason_codes
                    ),
                    warnings=(
                        assessment.warnings
                    ),
                )
            )

        return tuple(
            relationships
        )

    @staticmethod
    def _build_unresolved_discoveries(
        outcomes: tuple[
            DiscoveryOutcome,
            ...,
        ],
    ) -> tuple[
        UnresolvedDiscovery,
        ...,
    ]:
        grouped: dict[
            tuple[str, ...],
            dict[str, object],
        ] = {}

        for outcome in outcomes:
            resolution = (
                outcome.resolution_result
            )

            if resolution is None:
                continue

            if (
                resolution.resolution_status
                != ResolutionStatus.UNRESOLVED
            ):
                continue

            identifiers = tuple(
                sorted(
                    {
                        identifier.normalized_value
                        or identifier.original_value
                        for identifier in (
                            resolution
                            .normalized_identifiers
                        )
                    }
                )
            )

            if not identifiers:
                identifiers = tuple(
                    sorted(
                        {
                            candidate.value
                            for candidate in (
                                outcome
                                .candidate_result
                                .candidate_identifiers
                            )
                        }
                    )
                )

            group = grouped.setdefault(
                identifiers,
                {
                    "evidence_types": set(),
                    "observation_ids": [],
                    "reason_codes": [],
                    "warnings": [],
                },
            )

            evidence_types = group[
                "evidence_types"
            ]

            observation_ids = group[
                "observation_ids"
            ]

            reason_codes = group[
                "reason_codes"
            ]

            warnings = group[
                "warnings"
            ]

            assert isinstance(
                evidence_types,
                set,
            )

            assert isinstance(
                observation_ids,
                list,
            )

            assert isinstance(
                reason_codes,
                list,
            )

            assert isinstance(
                warnings,
                list,
            )

            for candidate in (
                outcome.classification_result
                .evidence_candidates
            ):
                evidence_types.add(
                    candidate.evidence_type.value
                )

            observation_ids.append(
                outcome.observation_id.value
            )

            reason_codes.extend(
                resolution.reason_codes
            )

            if outcome.assessment_result is not None:
                reason_codes.extend(
                    outcome.assessment_result
                    .reason_codes
                )

                warnings.extend(
                    outcome.assessment_result
                    .warnings
                )

        unresolved: list[
            UnresolvedDiscovery
        ] = []

        for identifiers in sorted(
            grouped
        ):
            group = grouped[
                identifiers
            ]

            evidence_types = group[
                "evidence_types"
            ]

            observation_ids = group[
                "observation_ids"
            ]

            reason_codes = group[
                "reason_codes"
            ]

            warnings = group[
                "warnings"
            ]

            assert isinstance(
                evidence_types,
                set,
            )

            assert isinstance(
                observation_ids,
                list,
            )

            assert isinstance(
                reason_codes,
                list,
            )

            assert isinstance(
                warnings,
                list,
            )

            unresolved.append(
                UnresolvedDiscovery(
                    identifiers=identifiers,
                    evidence_types=tuple(
                        sorted(
                            evidence_types
                        )
                    ),
                    observation_ids=tuple(
                        dict.fromkeys(
                            observation_ids
                        )
                    ),
                    reason_codes=(
                        DiscoveryReportBuilder
                        ._deduplicate(
                            tuple(
                                reason_codes
                            )
                        )
                    ),
                    warnings=(
                        DiscoveryReportBuilder
                        ._deduplicate(
                            tuple(
                                warnings
                            )
                        )
                    ),
                )
            )

        return tuple(
            unresolved
        )

    @staticmethod
    def _build_summary(
        outcomes: tuple[
            DiscoveryOutcome,
            ...,
        ],
    ) -> DiscoveryReportSummary:
        candidate_count = 0
        resolved_count = 0
        unresolved_count = 0
        ambiguous_count = 0
        classified_count = 0
        unknown_count = 0

        relationship_ids: set[
            str
        ] = set()

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

            status = (
                outcome.classification_result
                .classification_status
            )

            if (
                status
                == ClassificationStatus.CLASSIFIED
            ):
                classified_count += 1

            elif (
                status
                == ClassificationStatus.UNKNOWN
            ):
                unknown_count += 1

            if outcome.relationship_id is not None:
                relationship_ids.add(
                    outcome.relationship_id.value
                )

        return DiscoveryReportSummary(
            observation_count=len(
                outcomes
            ),
            candidate_count=(
                candidate_count
            ),
            resolved_count=(
                resolved_count
            ),
            unresolved_count=(
                unresolved_count
            ),
            ambiguous_count=(
                ambiguous_count
            ),
            classified_count=(
                classified_count
            ),
            unknown_classification_count=(
                unknown_count
            ),
            materialized_relationship_count=len(
                relationship_ids
            ),
        )

    @staticmethod
    def _deduplicate(
        values: tuple[
            str,
            ...,
        ],
    ) -> tuple[
        str,
        ...,
    ]:
        return tuple(
            dict.fromkeys(
                values
            )
        )
