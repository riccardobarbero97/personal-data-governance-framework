from datetime import datetime, timezone

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
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.enums.processing import (
    AggregationStatus,
    ResolutionStatus,
)
from personal_data_governance.domain.enums.relationship import (
    RelationshipStatus,
    TemporalStatus,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    EvidenceId,
    IdentitySeedId,
    ObservationId,
    RelationshipId,
    ServiceId,
    UserId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import TemporalValue
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryConnectedSourceRepository,
    InMemoryEvidenceRepository,
    InMemoryObservationRepository,
    InMemoryRelationshipRepository,
)


ASSESSED_AT = datetime(
    2026,
    11,
    16,
    18,
    0,
    tzinfo=timezone.utc,
)


class SequentialEvidenceIdFactory:
    def __init__(self) -> None:
        self._counter = 0

    def __call__(self) -> EvidenceId:
        self._counter += 1

        return EvidenceId(
            f"evidence_{self._counter:03d}"
        )


class SequentialRelationshipIdFactory:
    def __init__(self) -> None:
        self._counter = 0

    def __call__(self) -> RelationshipId:
        self._counter += 1

        return RelationshipId(
            f"relationship_{self._counter:03d}"
        )


def build_context() -> DiscoveryProcessingContext:
    loaded_registry = (
        build_initial_service_registry()
    )

    loaded_rules = (
        load_classification_rules()
    )

    relationship_policy = (
        load_relationship_policy()
    )

    return DiscoveryProcessingContext(
        candidate_detection=(
            CandidateDetectionContext(
                detector_version="1",
            )
        ),
        resolution=ResolutionContext(
            resolver_version="1",
            registry_version=(
                loaded_registry.registry_version
            ),
        ),
        classification=(
            ClassificationContext(
                classifier_version=(
                    loaded_rules.rule_set_version
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
                    relationship_policy.policy_version
                ),
                assessed_at=ASSESSED_AT,
                currently_observed_window_days=(
                    relationship_policy
                    .currently_observed_window_days
                ),
            )
        ),
    )


def build_connected_source(
    user_id: UserId,
) -> ConnectedSource:
    return ConnectedSource(
        id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        user_id=user_id,
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="google",
            display_name="Google",
        ),
        connector_id="gmail",
        display_name="Personal Gmail",
        external_account_reference=(
            "user@example.com"
        ),
        connection_state=(
            ConnectionState.CONNECTED
        ),
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )


def build_observation(
    observation_id: str,
    source_reference: str,
    subject: str,
    observed_at: datetime,
) -> Observation:
    return Observation(
        id=ObservationId(
            observation_id
        ),
        connected_source_id=(
            ConnectedSourceId(
                "source_gmail_personal"
            )
        ),
        observation_type=(
            ObservationType.EMAIL_MESSAGE_METADATA
        ),
        schema_version=SchemaVersion(
            1
        ),
        source_reference=SourceReference(
            source_reference
        ),
        observed_at=TemporalValue(
            timestamp=observed_at,
            semantics=(
                TemporalSemantics.MESSAGE_TIME
            ),
        ),
        collected_at=ASSESSED_AT,
        payload=EmailMessageMetadataV1(
            sender=(
                "Spotify "
                "<no-reply@spotify.com>"
            ),
            recipients=(
                "user@example.com",
            ),
            subject=subject,
            thread_reference=(
                f"thread_{observation_id}"
            ),
            labels=(),
        ),
    )


def build_discovery_service(
    connected_source_repository: (
        InMemoryConnectedSourceRepository
    ),
    observation_repository: (
        InMemoryObservationRepository
    ),
    evidence_repository: (
        InMemoryEvidenceRepository
    ),
    relationship_repository: (
        InMemoryRelationshipRepository
    ),
) -> DiscoveryService:
    loaded_registry = (
        build_initial_service_registry()
    )

    loaded_rules = (
        load_classification_rules()
    )

    relationship_policy = (
        load_relationship_policy()
    )

    return DiscoveryService(
        candidate_detector=(
            DeterministicEmailCandidateDetector()
        ),
        entity_resolver=(
            DeterministicEntityResolver(
                service_registry=(
                    loaded_registry.registry
                )
            )
        ),
        evidence_classifier=(
            DeterministicEmailEvidenceClassifier(
                rules=loaded_rules.rules
            )
        ),
        evidence_materializer=(
            EvidenceMaterializer(
                evidence_repository=(
                    evidence_repository
                ),
                evidence_id_factory=(
                    SequentialEvidenceIdFactory()
                ),
            )
        ),
        evidence_repository=(
            evidence_repository
        ),
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
                ),
                relationship_id_factory=(
                    SequentialRelationshipIdFactory()
                ),
            )
        ),
    )


def test_new_evidence_reassesses_complete_service_history() -> None:
    user_id = UserId(
        "user_001"
    )

    identity_seed_id = IdentitySeedId(
        "identity_email"
    )

    spotify_service_id = ServiceId(
        "service_spotify"
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
        build_connected_source(
            user_id
        )
    )

    discovery_service = (
        build_discovery_service(
            connected_source_repository=(
                connected_source_repository
            ),
            observation_repository=(
                observation_repository
            ),
            evidence_repository=(
                evidence_repository
            ),
            relationship_repository=(
                relationship_repository
            ),
        )
    )

    verification_observation = (
        build_observation(
            observation_id=(
                "observation_001"
            ),
            source_reference=(
                "gmail_message_001"
            ),
            subject=(
                "Verify your email address"
            ),
            observed_at=datetime(
                2026,
                1,
                1,
                10,
                0,
                tzinfo=timezone.utc,
            ),
        )
    )

    observation_repository.save(
        verification_observation
    )

    first_outcome = (
        discovery_service.process_observation(
            user_id=user_id,
            observation=(
                verification_observation
            ),
            identity_seed_ids=(
                identity_seed_id,
            ),
            context=build_context(),
        )
    )

    assert (
        first_outcome.resolution_result
        is not None
    )

    assert (
        first_outcome.resolution_result
        .resolution_status
        == ResolutionStatus.RESOLVED
    )

    assert (
        first_outcome.resolution_result
        .resolved_service_id
        == spotify_service_id
    )

    assert (
        first_outcome.relationship_id
        == RelationshipId(
            "relationship_001"
        )
    )

    assert (
        first_outcome.assessment_result
        is not None
    )

    assert (
        first_outcome.assessment_result
        .relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        first_outcome.assessment_result
        .evidence_ids
        == (
            EvidenceId(
                "evidence_001"
            ),
        )
    )

    payment_observation = (
        build_observation(
            observation_id=(
                "observation_002"
            ),
            source_reference=(
                "gmail_message_002"
            ),
            subject=(
                "Your payment was successful"
            ),
            observed_at=datetime(
                2026,
                11,
                10,
                9,
                0,
                tzinfo=timezone.utc,
            ),
        )
    )

    observation_repository.save(
        payment_observation
    )

    second_outcome = (
        discovery_service.process_observation(
            user_id=user_id,
            observation=payment_observation,
            identity_seed_ids=(
                identity_seed_id,
            ),
            context=build_context(),
        )
    )

    assert second_outcome.evidence_ids == (
        EvidenceId(
            "evidence_002"
        ),
    )

    assert (
        second_outcome.aggregation_result
        is not None
    )

    assert (
        second_outcome.aggregation_result
        .aggregation_status
        == AggregationStatus.AGGREGATED
    )

    assert (
        second_outcome.aggregation_result
        .aggregate
        is not None
    )

    aggregate = (
        second_outcome
        .aggregation_result
        .aggregate
    )

    assert aggregate.evidence_ids == (
        EvidenceId(
            "evidence_001"
        ),
        EvidenceId(
            "evidence_002"
        ),
    )

    assert (
        aggregate.evidence_summary
        .total_evidence_count
        == 2
    )

    assert (
        aggregate.evidence_summary
        .evidence_count_by_type[
            EvidenceType.ACCOUNT_VERIFICATION
        ]
        == 1
    )

    assert (
        aggregate.evidence_summary
        .evidence_count_by_type[
            EvidenceType.PAYMENT
        ]
        == 1
    )

    assert (
        second_outcome.assessment_result
        is not None
    )

    assert (
        second_outcome.assessment_result
        .evidence_ids
        == (
            EvidenceId(
                "evidence_001"
            ),
            EvidenceId(
                "evidence_002"
            ),
        )
    )

    assert (
        second_outcome.assessment_result
        .relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        second_outcome.assessment_result
        .temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )

    assert (
        second_outcome.relationship_id
        == RelationshipId(
            "relationship_001"
        )
    )

    current_relationship = (
        relationship_repository
        .get_by_user_and_service(
            user_id=user_id,
            service_id=(
                spotify_service_id
            ),
        )
    )

    assert (
        current_relationship
        is not None
    )

    assert (
        current_relationship.id
        == RelationshipId(
            "relationship_001"
        )
    )

    assert (
        current_relationship.evidence_ids
        == (
            EvidenceId(
                "evidence_001"
            ),
            EvidenceId(
                "evidence_002"
            ),
        )
    )

    assert (
        current_relationship
        .relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        current_relationship
        .temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )


def test_cumulative_reassessment_keeps_one_relationship_per_user_service() -> None:
    user_id = UserId(
        "user_001"
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
        build_connected_source(
            user_id
        )
    )

    discovery_service = (
        build_discovery_service(
            connected_source_repository=(
                connected_source_repository
            ),
            observation_repository=(
                observation_repository
            ),
            evidence_repository=(
                evidence_repository
            ),
            relationship_repository=(
                relationship_repository
            ),
        )
    )

    observations = (
        build_observation(
            observation_id=(
                "observation_001"
            ),
            source_reference=(
                "gmail_message_001"
            ),
            subject=(
                "Verify your email address"
            ),
            observed_at=datetime(
                2026,
                10,
                1,
                tzinfo=timezone.utc,
            ),
        ),
        build_observation(
            observation_id=(
                "observation_002"
            ),
            source_reference=(
                "gmail_message_002"
            ),
            subject=(
                "Your payment was successful"
            ),
            observed_at=datetime(
                2026,
                11,
                1,
                tzinfo=timezone.utc,
            ),
        ),
    )

    relationship_ids = []

    for observation in observations:
        observation_repository.save(
            observation
        )

        outcome = (
            discovery_service.process_observation(
                user_id=user_id,
                observation=observation,
                identity_seed_ids=(
                    IdentitySeedId(
                        "identity_email"
                    ),
                ),
                context=build_context(),
            )
        )

        relationship_ids.append(
            outcome.relationship_id
        )

    assert relationship_ids == [
        RelationshipId(
            "relationship_001"
        ),
        RelationshipId(
            "relationship_001"
        ),
    ]

    relationship = (
        relationship_repository
        .get_by_user_and_service(
            user_id=user_id,
            service_id=ServiceId(
                "service_spotify"
            ),
        )
    )

    assert relationship is not None

    assert relationship.evidence_ids == (
        EvidenceId(
            "evidence_001"
        ),
        EvidenceId(
            "evidence_002"
        ),
    )
