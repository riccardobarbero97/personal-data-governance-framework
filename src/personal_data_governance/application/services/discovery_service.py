from dataclasses import dataclass

from personal_data_governance.application.results.discovery import (
    DiscoveryOutcome,
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
from personal_data_governance.application.services.service_identifier_materializer import (
    materialize_service_identifiers,
)
from personal_data_governance.discovery.candidate_detection.protocol import (
    CandidateDetectionContext,
    ServiceCandidateDetector,
)
from personal_data_governance.discovery.entity_resolution.protocol import (
    EntityResolver,
    ResolutionContext,
    ResolutionRequest,
)
from personal_data_governance.discovery.evidence_aggregation.protocol import (
    AggregationContext,
    AggregationRequest,
    EvidenceAggregator,
)
from personal_data_governance.discovery.evidence_classification.protocol import (
    ClassificationContext,
    EvidenceClassifier,
)
from personal_data_governance.discovery.relationship_assessment.protocol import (
    RelationshipAssessmentContext,
    RelationshipAssessor,
)
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.processing import (
    AggregationScope,
    AggregationStatus,
    CandidateStatus,
    ClassificationStatus,
    ProcessingStatus,
    ResolutionStatus,
)
from personal_data_governance.domain.values.identifiers import (
    IdentitySeedId,
    ServiceId,
    UserId,
)


@dataclass(frozen=True, slots=True)
class DiscoveryProcessingContext:
    candidate_detection: CandidateDetectionContext
    resolution: ResolutionContext
    classification: ClassificationContext
    aggregation: AggregationContext
    assessment: RelationshipAssessmentContext


class DiscoveryService:
    def __init__(
        self,
        candidate_detector: ServiceCandidateDetector,
        entity_resolver: EntityResolver,
        evidence_classifier: EvidenceClassifier,
        evidence_materializer: EvidenceMaterializer,
        evidence_contribution_builder: EvidenceContributionBuilder,
        evidence_aggregator: EvidenceAggregator,
        relationship_assessor: RelationshipAssessor,
        relationship_materializer: RelationshipMaterializer,
    ) -> None:
        self._candidate_detector = candidate_detector
        self._entity_resolver = entity_resolver
        self._evidence_classifier = evidence_classifier
        self._evidence_materializer = evidence_materializer
        self._evidence_contribution_builder = (
            evidence_contribution_builder
        )
        self._evidence_aggregator = evidence_aggregator
        self._relationship_assessor = relationship_assessor
        self._relationship_materializer = (
            relationship_materializer
        )

    def process_observation(
        self,
        user_id: UserId,
        observation: Observation,
        identity_seed_ids: tuple[IdentitySeedId, ...],
        context: DiscoveryProcessingContext,
    ) -> DiscoveryOutcome:
        candidate_result = self._candidate_detector.detect(
            observation=observation,
            context=context.candidate_detection,
        )

        classification_result = (
            self._evidence_classifier.classify(
                observation=observation,
                context=context.classification,
            )
        )

        resolution_result = None
        service_identifiers = ()
        resolved_service_id: ServiceId | None = None

        if (
            candidate_result.processing_status
            == ProcessingStatus.SUCCESS
            and candidate_result.candidate_status
            == CandidateStatus.CANDIDATE
        ):
            service_identifiers = (
                materialize_service_identifiers(
                    candidate_identifiers=(
                        candidate_result.candidate_identifiers
                    ),
                    observation_id=observation.id,
                )
            )

            if service_identifiers:
                resolution_request = ResolutionRequest(
                    observation_id=observation.id,
                    service_identifiers=service_identifiers,
                    context=context.resolution,
                )

                resolution_result = (
                    self._entity_resolver.resolve(
                        resolution_request
                    )
                )

                if (
                    resolution_result.processing_status
                    == ProcessingStatus.SUCCESS
                    and resolution_result.resolution_status
                    == ResolutionStatus.RESOLVED
                ):
                    resolved_service_id = (
                        resolution_result.resolved_service_id
                    )

        materialized_evidence = ()

        if (
            classification_result.processing_status
            == ProcessingStatus.SUCCESS
            and classification_result.classification_status
            == ClassificationStatus.CLASSIFIED
        ):
            materialized_evidence = (
                self._evidence_materializer.materialize(
                    observation_id=observation.id,
                    evidence_candidates=(
                        classification_result.evidence_candidates
                    ),
                    service_id=resolved_service_id,
                    identity_seed_ids=identity_seed_ids,
                    lifecycle_actor=(
                        classification_result.classifier_version
                    ),
                    changed_at=(
                        context.assessment.assessed_at
                    ),
                )
            )

        evidence_ids = tuple(
            evidence.id
            for evidence in materialized_evidence
        )

        if (
            not materialized_evidence
            or resolution_result is None
            or not service_identifiers
        ):
            return DiscoveryOutcome(
                observation_id=observation.id,
                candidate_result=candidate_result,
                resolution_result=resolution_result,
                classification_result=classification_result,
                aggregation_result=None,
                assessment_result=None,
                evidence_ids=evidence_ids,
                relationship_id=None,
            )

        aggregation_scope = self._determine_aggregation_scope(
            resolution_result
        )

        if aggregation_scope is None:
            return DiscoveryOutcome(
                observation_id=observation.id,
                candidate_result=candidate_result,
                resolution_result=resolution_result,
                classification_result=classification_result,
                aggregation_result=None,
                assessment_result=None,
                evidence_ids=evidence_ids,
                relationship_id=None,
            )

        contributions = tuple(
            self._evidence_contribution_builder.build(
                evidence
            )
            for evidence in materialized_evidence
        )

        unresolved_identifiers = ()
        alternative_service_ids = ()

        if (
            aggregation_scope
            == AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
        ):
            unresolved_identifiers = (
                resolution_result.normalized_identifiers
            )

        if (
            aggregation_scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
        ):
            unresolved_identifiers = (
                resolution_result.normalized_identifiers
            )

            alternative_service_ids = (
                resolution_result.alternative_service_ids
            )

        aggregation_request = AggregationRequest(
            scope=aggregation_scope,
            service_id=resolved_service_id,
            unresolved_identifiers=(
                unresolved_identifiers
            ),
            alternative_service_ids=(
                alternative_service_ids
            ),
            identity_seed_ids=identity_seed_ids,
            contributions=contributions,
            context=context.aggregation,
        )

        aggregation_result = (
            self._evidence_aggregator.aggregate(
                aggregation_request
            )
        )

        if (
            aggregation_result.processing_status
            != ProcessingStatus.SUCCESS
            or aggregation_result.aggregation_status
            != AggregationStatus.AGGREGATED
            or aggregation_result.aggregate is None
        ):
            return DiscoveryOutcome(
                observation_id=observation.id,
                candidate_result=candidate_result,
                resolution_result=resolution_result,
                classification_result=classification_result,
                aggregation_result=aggregation_result,
                assessment_result=None,
                evidence_ids=evidence_ids,
                relationship_id=None,
            )

        assessment_result = (
            self._relationship_assessor.assess(
                aggregate=aggregation_result.aggregate,
                context=context.assessment,
            )
        )

        relationship_id = None

        if (
            assessment_result.processing_status
            == ProcessingStatus.SUCCESS
            and assessment_result.service_id is not None
            and assessment_result.evidence_ids
        ):
            relationship = (
                self._relationship_materializer.materialize(
                    user_id=user_id,
                    assessment_result=assessment_result,
                    assessed_at=(
                        context.assessment.assessed_at
                    ),
                )
            )

            relationship_id = relationship.id

        return DiscoveryOutcome(
            observation_id=observation.id,
            candidate_result=candidate_result,
            resolution_result=resolution_result,
            classification_result=classification_result,
            aggregation_result=aggregation_result,
            assessment_result=assessment_result,
            evidence_ids=evidence_ids,
            relationship_id=relationship_id,
        )

    @staticmethod
    def _determine_aggregation_scope(
        resolution_result,
    ) -> AggregationScope | None:
        if (
            resolution_result.processing_status
            != ProcessingStatus.SUCCESS
        ):
            return None

        if (
            resolution_result.resolution_status
            == ResolutionStatus.RESOLVED
        ):
            return AggregationScope.SERVICE

        if (
            resolution_result.resolution_status
            == ResolutionStatus.UNRESOLVED
        ):
            return (
                AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
            )

        if (
            resolution_result.resolution_status
            == ResolutionStatus.AMBIGUOUS
        ):
            return (
                AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            )

        return None
