from dataclasses import dataclass

from personal_data_governance.domain.enums.processing import (
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import (
    ObservationId,
)


@dataclass(frozen=True, slots=True)
class ServiceIdentifier:
    type: ServiceIdentifierType
    original_value: str
    observation_id: ObservationId
    normalized_value: str | None = None

    def __post_init__(self) -> None:
        if not self.original_value.strip():
            raise ValueError(
                "ServiceIdentifier original value must not be empty."
            )

        if (
            self.normalized_value is not None
            and not self.normalized_value.strip()
        ):
            raise ValueError(
                "ServiceIdentifier normalized value must not be empty."
            )
