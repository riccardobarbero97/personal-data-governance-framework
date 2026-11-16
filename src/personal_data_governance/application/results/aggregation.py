from dataclasses import dataclass

from personal_data_governance.domain.enums.processing import (
    AggregationStatus,
    ProcessingStatus,
)
from personal_data_governance.domain.views.evidence_aggregate import (
    EvidenceAggregate,
)


@dataclass(frozen=True, slots=True)
class AggregationResult:
    processing_status: ProcessingStatus
    aggregation_status: AggregationStatus | None
    aggregate: EvidenceAggregate | None
    aggregator_version: str

    def __post_init__(self) -> None:
        if not self.aggregator_version.strip():
            raise ValueError(
                "Aggregator version must not be empty."
            )

        if (
            self.processing_status == ProcessingStatus.SUCCESS
            and self.aggregation_status is None
        ):
            raise ValueError(
                "Successful aggregation requires "
                "an aggregation status."
            )

        if (
            self.aggregation_status
            == AggregationStatus.AGGREGATED
            and self.aggregate is None
        ):
            raise ValueError(
                "AGGREGATED requires an EvidenceAggregate."
            )

        if (
            self.aggregation_status
            == AggregationStatus.EMPTY
            and self.aggregate is not None
        ):
            raise ValueError(
                "EMPTY must not contain "
                "an EvidenceAggregate."
            )
