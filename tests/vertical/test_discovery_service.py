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
from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.enums.processing import (
    AggregationStatus,
    CandidateStatus,
    ClassificationStatus,
    ProcessingStatus,
    ResolutionStatus,
    ServiceIdentifierType,
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
from personal_data_governance.infrastructure.service_registry.in_memory import (
    InMemoryServiceRegistry,
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


def build_processing_context() -> DiscoveryProcessingContext:
    return DiscoveryProcessingContext(
        candidate_detection=CandidateDetectionContext(
            detector_version="1",
        ),
        resolution=ResolutionContext(
            resolver_version="1",
            registry_version="1",
        ),
        classification=ClassificationContext(
            classifier_version="1",
        ),
        aggregation=AggregationContext(
            aggregator_version="1",
        ),
        assessment=RelationshipAssessmentContext(
            assessor_version="1",
            assessment_policy_version="1",
            assessed_at=ASSESSED_AT,
            currently_observed_window_days=365,
        ),
    )


def build_discovery_service(
    connected_source_repository: (
        InMemoryConnectedSourceRepository
    ),
    observation_repository: (
        InMemoryObservationRepository
    ),
    evidence_repository: InMemoryEvidenceRepository,
    relationship_repository: (
        InMemoryRelationshipRepository
    ),
    service_registry: InMemoryServiceRegistry,
) -> DiscoveryService:
    candidate_detector = (
        DeterministicEmailCandidateDetector()
    )

    entity_resolver = DeterministicEntityResolver(
        service_registry=service_registry
    )

    evidence_classifier = (
        DeterministicEmailEvidenceClassifier()
    )

    evidence_materializer = EvidenceMaterializer(
        evidence_repository=evidence_repository,
        evidence_id_factory=SequentialEvidenceIdFactory(),
    )

    contribution_builder = EvidenceContributionBuilder(
        observation_repository=observation_repository,
        connected_source_repository=(
            connected_source_repository
        ),
    )

    evidence_aggregator = (
        DeterministicEvidenceAggregator()
    )

    relationship_assessor = (
        DeterministicRelationshipAssessor()
    )

    relationship_materializer = RelationshipMaterializer(
        relationship_repository=relationship_repository,
        relationship_id_factory=(
            SequentialRelationshipIdFactory()
        ),
    )

    return DiscoveryService(
        candidate_detector=candidate_detector,
        entity_resolver=entity_resolver,
        evidence_classifier=evidence_classifier,
        evidence_materializer=evidence_materializer,
        evidence_repository=evidence_repository,
        evidence_contribution_builder=(
            contribution_builder
        ),
        evidence_aggregator=evidence_aggregator,
        relationship_assessor=relationship_assessor,
        relationship_materializer=(
            relationship_materializer
        ),
    )


def build_connected_source() -> ConnectedSource:
    return ConnectedSource(
        id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        user_id=UserId("user_001"),
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
        connection_state=ConnectionState.CONNECTED,
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )


def build_observation(
    sender: str,
    subject: str,
) -> Observation:
    return Observation(
        id=ObservationId("observation_001"),
        connected_source_id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        observation_type=(
            ObservationType.EMAIL_MESSAGE_METADATA
        ),
        schema_version=SchemaVersion(1),
        source_reference=SourceReference(
            "gmail_message_123"
        ),
        observed_at=TemporalValue(
            timestamp=datetime(
                2026,
                11,
                10,
                9,
                0,
                tzinfo=timezone.utc,
            ),
            semantics=TemporalSemantics.MESSAGE_TIME,
        ),
        collected_at=ASSESSED_AT,
        payload=EmailMessageMetadataV1(
            sender=sender,
            recipients=(
                "user@example.com",
            ),
            subject=subject,
            thread_reference="thread_001",
            labels=(),
        ),
    )


def test_spotify_observation_creates_relationship() -> None:
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

    service_registry = InMemoryServiceRegistry()

    connected_source = build_connected_source()

    connected_source_repository.save(
        connected_source
    )

    observation = build_observation(
        sender="Spotify <no-reply@spotify.com>",
        subject="Verify your email address",
    )

    observation_repository.save(
        observation
    )

    spotify = Service(
        id=ServiceId("service_spotify"),
        canonical_name="Spotify",
    )

    service_registry.register_service(
        spotify
    )

    service_registry.register_identifier(
        service_id=spotify.id,
        identifier_type=(
            ServiceIdentifierType.EMAIL_DOMAIN
        ),
        identifier_value="spotify.com",
    )

    discovery_service = build_discovery_service(
        connected_source_repository=(
            connected_source_repository
        ),
        observation_repository=observation_repository,
        evidence_repository=evidence_repository,
        relationship_repository=(
            relationship_repository
        ),
        service_registry=service_registry,
    )

    outcome = discovery_service.process_observation(
        user_id=UserId("user_001"),
        observation=observation,
        identity_seed_ids=(
            IdentitySeedId("identity_email"),
        ),
        context=build_processing_context(),
    )

    assert (
        outcome.candidate_result.processing_status
        == ProcessingStatus.SUCCESS
    )

    assert (
        outcome.candidate_result.candidate_status
        == CandidateStatus.CANDIDATE
    )

    assert outcome.resolution_result is not None

    assert (
        outcome.resolution_result.resolution_status
        == ResolutionStatus.RESOLVED
    )

    assert (
        outcome.resolution_result.resolved_service_id
        == spotify.id
    )

    assert (
        outcome.classification_result.classification_status
        == ClassificationStatus.CLASSIFIED
    )

    assert (
        outcome.classification_result
        .evidence_candidates[0]
        .evidence_type
        == EvidenceType.ACCOUNT_VERIFICATION
    )

    assert outcome.evidence_ids == (
        EvidenceId("evidence_001"),
    )

    assert outcome.aggregation_result is not None

    assert (
        outcome.aggregation_result.aggregation_status
        == AggregationStatus.AGGREGATED
    )

    assert outcome.assessment_result is not None

    assert (
        outcome.assessment_result.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        outcome.assessment_result.temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )

    assert (
        outcome.relationship_id
        == RelationshipId("relationship_001")
    )

    relationship = (
        relationship_repository.get_by_user_and_service(
            user_id=UserId("user_001"),
            service_id=spotify.id,
        )
    )

    assert relationship is not None

    assert (
        relationship.relationship_status
        == RelationshipStatus.ESTABLISHED
    )

    assert (
        relationship.temporal_status
        == TemporalStatus.CURRENTLY_OBSERVED
    )

    assert relationship.evidence_ids == (
        EvidenceId("evidence_001"),
    )


def test_unresolved_service_preserves_evidence_without_relationship() -> None:
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

    service_registry = InMemoryServiceRegistry()

    connected_source = build_connected_source()

    connected_source_repository.save(
        connected_source
    )

    observation = build_observation(
        sender="billing@unknown-service.example",
        subject="Payment successful",
    )

    observation_repository.save(
        observation
    )

    discovery_service = build_discovery_service(
        connected_source_repository=(
            connected_source_repository
        ),
        observation_repository=observation_repository,
        evidence_repository=evidence_repository,
        relationship_repository=(
            relationship_repository
        ),
        service_registry=service_registry,
    )

    outcome = discovery_service.process_observation(
        user_id=UserId("user_001"),
        observation=observation,
        identity_seed_ids=(
            IdentitySeedId("identity_email"),
        ),
        context=build_processing_context(),
    )

    assert outcome.resolution_result is not None

    assert (
        outcome.resolution_result.resolution_status
        == ResolutionStatus.UNRESOLVED
    )

    assert outcome.evidence_ids == (
        EvidenceId("evidence_001"),
    )

    evidence = evidence_repository.get(
        EvidenceId("evidence_001")
    )

    assert evidence is not None
    assert evidence.service_id is None
    assert evidence.evidence_type == EvidenceType.PAYMENT

    assert outcome.aggregation_result is not None
    assert outcome.aggregation_result.aggregate is not None

    assert (
        outcome.aggregation_result.aggregate.scope.value
        == "UNRESOLVED_SERVICE_CANDIDATE"
    )

    assert outcome.assessment_result is not None
    assert outcome.assessment_result.service_id is None

    assert (
        "CANONICAL_SERVICE_UNAVAILABLE"
        in outcome.assessment_result.warnings
    )

    assert outcome.relationship_id is None


def test_unknown_classification_does_not_create_evidence() -> None:
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

    service_registry = InMemoryServiceRegistry()

    connected_source = build_connected_source()

    connected_source_repository.save(
        connected_source
    )

    observation = build_observation(
        sender="no-reply@spotify.com",
        subject="Important information about your account",
    )

    observation_repository.save(
        observation
    )

    spotify = Service(
        id=ServiceId("service_spotify"),
        canonical_name="Spotify",
    )

    service_registry.register_service(
        spotify
    )

    service_registry.register_identifier(
        service_id=spotify.id,
        identifier_type=(
            ServiceIdentifierType.EMAIL_DOMAIN
        ),
        identifier_value="spotify.com",
    )

    discovery_service = build_discovery_service(
        connected_source_repository=(
            connected_source_repository
        ),
        observation_repository=observation_repository,
        evidence_repository=evidence_repository,
        relationship_repository=(
            relationship_repository
        ),
        service_registry=service_registry,
    )

    outcome = discovery_service.process_observation(
        user_id=UserId("user_001"),
        observation=observation,
        identity_seed_ids=(
            IdentitySeedId("identity_email"),
        ),
        context=build_processing_context(),
    )

    assert (
        outcome.classification_result.classification_status
        == ClassificationStatus.UNKNOWN
    )

    assert outcome.evidence_ids == ()
    assert outcome.aggregation_result is None
    assert outcome.assessment_result is None
    assert outcome.relationship_id is None
