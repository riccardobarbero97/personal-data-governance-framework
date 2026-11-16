from dataclasses import dataclass

from personal_data_governance.domain.enums.processing import (
    ProcessingStatus,
    ResolutionMethod,
    ResolutionStatus,
)
from personal_data_governance.domain.values.identifiers import (
    ObservationId,
    ServiceId,
)
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    observation_id: ObservationId
    input_identifiers: tuple[ServiceIdentifier, ...]
    normalized_identifiers: tuple[ServiceIdentifier, ...]
    processing_status: ProcessingStatus
    resolution_status: ResolutionStatus | None
    resolved_service_id: ServiceId | None
    alternative_service_ids: tuple[ServiceId, ...]
    method: ResolutionMethod | None
    reason_codes: tuple[str, ...]
    resolver_version: str

    def __post_init__(self) -> None:
        if not self.resolver_version.strip():
            raise ValueError(
                "Resolver version must not be empty."
            )

        if (
            self.processing_status == ProcessingStatus.SUCCESS
            and self.resolution_status is None
        ):
            raise ValueError(
                "Successful resolution requires "
                "a resolution status."
            )

        if (
            self.processing_status != ProcessingStatus.SUCCESS
            and self.resolution_status is not None
        ):
            raise ValueError(
                "A failed or unsupported resolution must not "
                "contain a semantic ResolutionStatus."
            )

        if (
            self.resolution_status == ResolutionStatus.RESOLVED
            and self.resolved_service_id is None
        ):
            raise ValueError(
                "RESOLVED requires a resolved Service."
            )

        if (
            self.resolution_status != ResolutionStatus.RESOLVED
            and self.resolved_service_id is not None
        ):
            raise ValueError(
                "Only RESOLVED may contain "
                "a resolved Service."
            )

        if (
            self.resolution_status == ResolutionStatus.AMBIGUOUS
            and not self.alternative_service_ids
        ):
            raise ValueError(
                "AMBIGUOUS requires at least one "
                "alternative Service."
            )

        if (
            self.resolution_status != ResolutionStatus.AMBIGUOUS
            and self.alternative_service_ids
        ):
            raise ValueError(
                "Alternative Services are only valid "
                "for AMBIGUOUS resolution."
            )
