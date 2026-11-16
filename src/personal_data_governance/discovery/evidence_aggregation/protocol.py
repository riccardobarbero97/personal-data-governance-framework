from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.application.results.aggregation import (
    AggregationResult,
)
from personal_data_governance.application.values.evidence_contribution import (
    EvidenceContribution,
)
from personal_data_governance.domain.enums.processing import AggregationScope
from personal_data_governance.domain.values.identifiers import (
    IdentitySeedId,
    ServiceId,
)
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


@dataclass(frozen=True, slots=True)
class AggregationContext:
    aggregator_version: str

    def __post_init__(self) -> None:
        if not self.aggregator_version.strip():
            raise ValueError(
                "Aggregator version must not be empty."
            )


@dataclass(frozen=True, slots=True)
class AggregationRequest:
    scope: AggregationScope
    service_id: ServiceId | None
    unresolved_identifiers: tuple[ServiceIdentifier, ...]
    alternative_service_ids: tuple[ServiceId, ...]
    identity_seed_ids: tuple[IdentitySeedId, ...]
    contributions: tuple[EvidenceContribution, ...]
    context: AggregationContext

    def __post_init__(self) -> None:
        if (
            self.scope == AggregationScope.SERVICE
            and self.service_id is None
        ):
            raise ValueError(
                "SERVICE aggregation requires a Service."
            )

        if (
            self.scope == AggregationScope.SERVICE
            and self.unresolved_identifiers
        ):
            raise ValueError(
                "SERVICE aggregation must not contain "
                "unresolved identifiers."
            )

        if (
            self.scope == AggregationScope.SERVICE
            and self.alternative_service_ids
        ):
            raise ValueError(
                "SERVICE aggregation must not contain "
                "alternative Services."
            )

        if (
            self.scope
            == AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
            and not self.unresolved_identifiers
        ):
            raise ValueError(
                "UNRESOLVED_SERVICE_CANDIDATE "
                "requires identifiers."
            )

        if (
            self.scope
            == AggregationScope.UNRESOLVED_SERVICE_CANDIDATE
            and self.service_id is not None
        ):
            raise ValueError(
                "UNRESOLVED_SERVICE_CANDIDATE "
                "must not contain a Service."
            )

        if (
            self.scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            and not self.unresolved_identifiers
        ):
            raise ValueError(
                "AMBIGUOUS_SERVICE_CANDIDATE "
                "requires identifiers."
            )

        if (
            self.scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            and not self.alternative_service_ids
        ):
            raise ValueError(
                "AMBIGUOUS_SERVICE_CANDIDATE "
                "requires alternative Services."
            )

        if (
            self.scope
            == AggregationScope.AMBIGUOUS_SERVICE_CANDIDATE
            and self.service_id is not None
        ):
            raise ValueError(
                "AMBIGUOUS_SERVICE_CANDIDATE "
                "must not contain a resolved Service."
            )


class EvidenceAggregator(Protocol):

    def aggregate(
        self,
        request: AggregationRequest,
    ) -> AggregationResult:
        ...
