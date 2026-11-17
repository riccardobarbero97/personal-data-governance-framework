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
from personal_data_governance.config.loaders import (
    load_classification_rules,
    load_relationship_policy,
)
from personal_data_governance.config.service_registry import (
    build_initial_service_registry,
)
from personal_data_governance.connectors.gmail.connector import (
    SERVICE_DISCOVERY_METADATA,
    GmailConnector,
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
from personal_data_governance.infrastructure.credentials.file_store import (
    FileCredentialStore,
)
from personal_data_governance.infrastructure.google.gmail_api_client import (
    GoogleGmailApiClient,
)
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryConnectedSourceRepository,
    InMemoryEvidenceRepository,
    InMemoryObservationRepository,
    InMemoryRelationshipRepository,
)


@dataclass(frozen=True, slots=True)
class GmailVerticalRunnerConfiguration:
    client_secrets_file: Path
    token_directory: Path
    account_reference: str
    message_limit: int = 10

    def __post_init__(self) -> None:
        if not self.account_reference.strip():
            raise ValueError(
                "Gmail account reference must not be empty."
            )

        if self.message_limit < 1:
            raise ValueError(
                "Message limit must be at least one."
            )

        if self.message_limit > 500:
            raise ValueError(
                "Message limit must not exceed 500."
            )


@dataclass(frozen=True, slots=True)
class GmailVerticalRunResult:
    collection_status: str
    collected_observation_count: int
    outcomes: tuple[DiscoveryOutcome, ...]


class GmailVerticalRunner:
    def __init__(
        self,
        configuration: GmailVerticalRunnerConfiguration,
    ) -> None:
        self._configuration = configuration

    def run(
        self,
    ) -> GmailVerticalRunResult:
        user_id = UserId(
            "user_local"
        )

        identity_seed_id = IdentitySeedId(
            "identity_primary_email"
        )

        connected_source_id = ConnectedSourceId(
            "source_gmail_personal"
        )

        credential_store = FileCredentialStore(
            root_directory=(
                self._configuration.token_directory
            )
        )

        api_client = GoogleGmailApiClient(
            connected_source_id=connected_source_id,
            credential_store=credential_store,
            client_secrets_file=(
                self._configuration.client_secrets_file
            ),
        )

        if not api_client.is_authorized():
            api_client.authorize()

        connected_source = ConnectedSource(
            id=connected_source_id,
            user_id=user_id,
            source_type=SourceType.EMAIL,
            provider=Provider(
                id="google",
                display_name="Google",
            ),
            connector_id="gmail",
            display_name="Personal Gmail",
            external_account_reference=(
                self._configuration.account_reference
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

        loaded_registry = (
            build_initial_service_registry()
        )

        service_registry = (
            loaded_registry.registry
        )

        loaded_rules = (
            load_classification_rules()
        )

        relationship_policy = (
            load_relationship_policy()
        )

        gmail_connector = GmailConnector(
            api_client=api_client,
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
                DeterministicEmailEvidenceClassifier(
                    rules=loaded_rules.rules
                )
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
                DeterministicRelationshipAssessor(
                    policy=relationship_policy
                )
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

        for observation in (
            collection_result.observations
        ):
            existing_observation = (
                observation_repository
                .find_by_source_reference(
                    connected_source_id=(
                        observation
                        .connected_source_id
                    ),
                    source_reference=(
                        observation
                        .source_reference
                    ),
                )
            )

            if existing_observation is not None:
                effective_observation = (
                    existing_observation
                )
            else:
                observation_repository.save(
                    observation
                )

                effective_observation = (
                    observation
                )

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
                    registry_version=(
                        loaded_registry
                        .registry_version
                    ),
                ),
                classification=(
                    ClassificationContext(
                        classifier_version=(
                            loaded_rules
                            .rule_set_version
                        ),
                    )
                ),
                aggregation=AggregationContext(
                    aggregator_version="1",
                ),
                assessment=(
                    RelationshipAssessmentContext(
                        assessor_version="1",
                        assessment_policy_version=(
                            relationship_policy
                            .policy_version
                        ),
                        assessed_at=assessed_at,
                        currently_observed_window_days=(
                            relationship_policy
                            .currently_observed_window_days
                        ),
                    )
                ),
            )

            outcome = (
                discovery_service.process_observation(
                    user_id=user_id,
                    observation=effective_observation,
                    identity_seed_ids=(
                        identity_seed_id,
                    ),
                    context=context,
                )
            )

            outcomes.append(
                outcome
            )

        return GmailVerticalRunResult(
            collection_status=(
                collection_result.status
            ),
            collected_observation_count=len(
                collection_result.observations
            ),
            outcomes=tuple(
                outcomes
            ),
        )
