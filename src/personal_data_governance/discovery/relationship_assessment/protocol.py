from dataclasses import dataclass
from datetime import datetime
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
    assessed_at: datetime
    currently_observed_window_days: int = 365
    user_rejected: bool = False

    def __post_init__(self) -> None:
        if not self.assessor_version.strip():
            raise ValueError(
                "Assessor version must not be empty."
            )

        if not self.assessment_policy_version.strip():
            raise ValueError(
                "Assessment policy version must not be empty."
            )

        if self.assessed_at.tzinfo is None:
            raise ValueError(
                "Assessment time must be timezone-aware."
            )

        if self.assessed_at.utcoffset() is None:
            raise ValueError(
                "Assessment time must be timezone-aware."
            )

        if self.currently_observed_window_days < 1:
            raise ValueError(
                "Currently-observed window must be "
                "greater than or equal to one day."
            )


class RelationshipAssessor(Protocol):

    def assess(
        self,
        aggregate: EvidenceAggregate,
        context: RelationshipAssessmentContext,
    ) -> RelationshipAssessmentResult:
        ...
