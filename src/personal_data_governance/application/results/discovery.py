from dataclasses import dataclass

from personal_data_governance.application.results.aggregation import (
    AggregationResult,
)
from personal_data_governance.application.results.assessment import (
    RelationshipAssessmentResult,
)
from personal_data_governance.application.results.candidate_detection import (
    CandidateDetectionResult,
)
from personal_data_governance.application.results.classification import (
    ClassificationResult,
)
from personal_data_governance.application.results.resolution import (
    ResolutionResult,
)
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    ObservationId,
    RelationshipId,
)


@dataclass(frozen=True, slots=True)
class DiscoveryOutcome:
    observation_id: ObservationId
    candidate_result: CandidateDetectionResult
    resolution_result: ResolutionResult | None
    classification_result: ClassificationResult
    aggregation_result: AggregationResult | None
    assessment_result: RelationshipAssessmentResult | None
    evidence_ids: tuple[EvidenceId, ...]
    relationship_id: RelationshipId | None
