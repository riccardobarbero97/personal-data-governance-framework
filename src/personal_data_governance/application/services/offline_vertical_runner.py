from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.application.ports.connector import (
    CollectionRequest,
)
from personal_data_governance.application.results.discovery import (
    DiscoveryOutcome,
)
from personal_data_governance.application.services.discovery_service import (
    DiscoveryProcessingContext,
    DiscoveryService,
)
from personal_data_governance.application.services.evidence_contribution_builder import (
    EvidenceContributionBuilder,
)
from personal_data_governance.application.services.evidence_materializer import (
    EvidenceMaterializer,
)
from personal_data_governance.application.services.relationship_materializer import (
    RelationshipMaterializer,
)
from personal_data_governance.config.service_registry import (
    build_initial_service_registry,
)
from personal_data_governance.connectors.gmail.connector import (
    SERVICE_DISCOVERY_METADATA,
    GmailConnector,
)
from personal_data_governance.connectors.gmail.offline_api_client import (
    OfflineGmailApiClient,
)
from personal_data_governance.discovery.candidate_detection.deterministic import (
    DeterministicEmailCandidateDetector,
)
from personal_data_governance.discovery.candidate_detection.protocol import (
    CandidateDetectionContext,
)
from personal_data_governance.discovery.entity_resolution.deterministic import (
    DeterministicEntityResolver,
)
from personal_data_governance.discovery.entity_resolution.protocol import (
    ResolutionContext,
)
from personal_data_governance.discovery.evidence_aggregation.deterministic import (
    DeterministicEvidenceAggregator,
)
from personal_data_governance.discovery.evidence_aggregation.protocol import (
    AggregationContext,
)
from personal_data_governance.discovery.evidence_classification.deterministic import (
    DeterministicEmailEvidenceClassifier,
)
from personal_data_governance.discovery.evidence_classification.protocol import (
    ClassificationContext,
)
from personal_data_governance.discovery.relationship_assessment.deterministic import (
    DeterministicRelationshipAssessor,
)
from personal_data_governance.discovery.relationship_assessment.protocol import (
    RelationshipAssessmentContext,
)
from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    IdentitySeedId,
    UserId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryConnectedSourceRepository,
    InMemoryEvidenceRepository,
    InMemoryObservationRepository,
    InMemoryRelationshipRepository,
)


@dataclass(frozen=True, slots=True)
class OfflineVerticalConfiguration:
    fixture_file: Path
    message_limit: int = 100

    def __post_init__(self) -> None:
        if self.message_limit < 1:
            raise ValueError(
                "Message limit must be at least one."
            )

        if self.message_limit > 500:
            raise ValueError(
                "Message limit must not exceed 500."
            )


@dataclass(frozen=True, slots=True)
class OfflineValidationSummary:
    collected_observations: int
    created_evidence: int
    unique_relationships: int
    candidate_status_counts: tuple[
        tuple[str, int],
        ...,
    ]
    resolution_status_counts: tuple[
        tuple[str, int],
        ...,
    ]
    classification_status_counts: tuple[
        tuple[str, int],
        ...,
    ]
    evidence_type_counts: tuple[
        tuple[str, int],
        ...,
    ]


@dataclass(frozen=True, slots=True)
class OfflineVerticalRunResult:
    collection_status: str
    outcomes: tuple[DiscoveryOutcome, ...]
    summary: OfflineValidationSummary


class OfflineVerticalRunner:
    def __init__(
        self,
        configuration: OfflineVerticalConfiguration,
    ) -> None:
        self._configuration = configuration

    def run(
        self,
    ) -> OfflineVerticalRunResult:
        user_id = UserId(
            "user_offline"
        )

        identity_seed_id = IdentitySeedId(
            "identity_offline_email"
        )

        connected_source_id = ConnectedSourceId(
            "source_offline_gmail"
        )

        api_client = OfflineGmailApiClient(
            fixture_file=(
                self._configuration.fixture_file
            )
        )

        gmail_connector = GmailConnector(
            api_client=api_client
        )

        connected_source = ConnectedSource(
            id=connected_source_id,
            user_id=user_id,
            source_type=SourceType.EMAIL,
            provider=Provider(
                id="google",
                display_name="Google",
            ),
            connector_id="gmail",
            display_name="Synthetic Offline Gmail",
            external_account_reference=(
                "synthetic-user@example.com"
            ),
            connection_state=ConnectionState.CONNECTED,
            authorization_state=(
                AuthorizationState.AUTHORIZED
            ),
        )

        connected_source_repository = (
            InMemoryConnectedSourceRepository()
        )

        observation_repository = (
            InMemoryObservationRepository()
        )

        evidence_repository = (
            InMemoryEvidenceRepository()
        )

        relationship_repository = (
            InMemoryRelationshipRepository()
        )

        connected_source_repository.save(
            connected_source
        )

        service_registry = (
            build_initial_service_registry()
        )

        discovery_service = DiscoveryService(
            candidate_detector=(
                DeterministicEmailCandidateDetector()
            ),
            entity_resolver=(
                DeterministicEntityResolver(
                    service_registry=service_registry
                )
            ),
            evidence_classifier=(
                DeterministicEmailEvidenceClassifier()
            ),
            evidence_materializer=EvidenceMaterializer(
                evidence_repository=(
                    evidence_repository
                )
            ),
            evidence_repository=evidence_repository,
            evidence_contribution_builder=(
                EvidenceContributionBuilder(
                    observation_repository=(
                        observation_repository
                    ),
                    connected_source_repository=(
                        connected_source_repository
                    ),
                )
            ),
            evidence_aggregator=(
                DeterministicEvidenceAggregator()
            ),
            relationship_assessor=(
                DeterministicRelationshipAssessor()
            ),
            relationship_materializer=(
                RelationshipMaterializer(
                    relationship_repository=(
                        relationship_repository
                    )
                )
            ),
        )

        collection_result = gmail_connector.collect(
            CollectionRequest(
                connected_source_id=connected_source_id,
                capability=(
                    SERVICE_DISCOVERY_METADATA
                ),
                continuation=None,
                limit=(
                    self._configuration.message_limit
                ),
            )
        )

        outcomes: list[
            DiscoveryOutcome
        ] = []

        assessed_at = datetime.now(
            timezone.utc
        )

        context = DiscoveryProcessingContext(
            candidate_detection=(
                CandidateDetectionContext(
                    detector_version="1",
                )
            ),
            resolution=ResolutionContext(
                resolver_version="1",
                registry_version="initial-1",
            ),
            classification=ClassificationContext(
                classifier_version="1",
            ),
            aggregation=AggregationContext(
                aggregator_version="1",
            ),
            assessment=(
                RelationshipAssessmentContext(
                    assessor_version="1",
                    assessment_policy_version="1",
                    assessed_at=assessed_at,
                    currently_observed_window_days=365,
                )
            ),
        )

        for observation in (
            collection_result.observations
        ):
            observation_repository.save(
                observation
            )

            outcome = (
                discovery_service.process_observation(
                    user_id=user_id,
                    observation=observation,
                    identity_seed_ids=(
                        identity_seed_id,
                    ),
                    context=context,
                )
            )

            outcomes.append(
                outcome
            )

        result_outcomes = tuple(
            outcomes
        )

        summary = self._build_summary(
            result_outcomes
        )

        return OfflineVerticalRunResult(
            collection_status=(
                collection_result.status
            ),
            outcomes=result_outcomes,
            summary=summary,
        )

    @staticmethod
    def _build_summary(
        outcomes: tuple[DiscoveryOutcome, ...],
    ) -> OfflineValidationSummary:
        candidate_status_counts: Counter[
            str
        ] = Counter()

        resolution_status_counts: Counter[
            str
        ] = Counter()

        classification_status_counts: Counter[
            str
        ] = Counter()

        evidence_type_counts: Counter[
            str
        ] = Counter()

        evidence_ids = set()
        relationship_ids = set()

        for outcome in outcomes:
            candidate_status = (
                outcome.candidate_result
                .candidate_status
            )

            if candidate_status is not None:
                candidate_status_counts[
                    candidate_status.value
                ] += 1

            if outcome.resolution_result is not None:
                resolution_status = (
                    outcome.resolution_result
                    .resolution_status
                )

                if resolution_status is not None:
                    resolution_status_counts[
                        resolution_status.value
                    ] += 1

            classification_status = (
                outcome.classification_result
                .classification_status
            )

            if classification_status is not None:
                classification_status_counts[
                    classification_status.value
                ] += 1

            for candidate in (
                outcome.classification_result
                .evidence_candidates
            ):
                evidence_type_counts[
                    candidate.evidence_type.value
                ] += 1

            for evidence_id in outcome.evidence_ids:
                evidence_ids.add(
                    evidence_id.value
                )

            if outcome.relationship_id is not None:
                relationship_ids.add(
                    outcome.relationship_id.value
                )

        return OfflineValidationSummary(
            collected_observations=len(
                outcomes
            ),
            created_evidence=len(
                evidence_ids
            ),
            unique_relationships=len(
                relationship_ids
            ),
            candidate_status_counts=(
                OfflineVerticalRunner
                ._ordered_counts(
                    candidate_status_counts
                )
            ),
            resolution_status_counts=(
                OfflineVerticalRunner
                ._ordered_counts(
                    resolution_status_counts
                )
            ),
            classification_status_counts=(
                OfflineVerticalRunner
                ._ordered_counts(
                    classification_status_counts
                )
            ),
            evidence_type_counts=(
                OfflineVerticalRunner
                ._ordered_counts(
                    evidence_type_counts
                )
            ),
        )

    @staticmethod
    def _ordered_counts(
        counter: Counter[str],
    ) -> tuple[tuple[str, int], ...]:
        return tuple(
            (
                key,
                counter[key],
            )
            for key in sorted(
                counter
            )
        )
