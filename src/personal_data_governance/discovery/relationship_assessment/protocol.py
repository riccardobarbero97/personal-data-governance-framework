from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.application.results.assessment import (
    RelationshipAssessmentResult,
)
from personal_data_governance.domain.views.evidence_aggregate import (
    EvidenceAggregate,
)


@dataclass(frozen=True, slots=True)
class RelationshipAssessmentContext:
    assessor_version: str
    assessment_policy_version: str

    def __post_init__(self) -> None:
        if not self.assessor_version.strip():
            raise ValueError(
                "Assessor version must not be empty."
            )

        if not self.assessment_policy_version.strip():
            raise ValueError(
                "Assessment policy version "
                "must not be empty."
            )


class RelationshipAssessor(Protocol):

    def assess(
        self,
        aggregate: EvidenceAggregate,
        context: RelationshipAssessmentContext,
    ) -> RelationshipAssessmentResult:
        ...
