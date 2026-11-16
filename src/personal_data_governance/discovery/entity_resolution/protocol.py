from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.application.results.resolution import (
    ResolutionResult,
)
from personal_data_governance.domain.values.identifiers import ObservationId
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


@dataclass(frozen=True, slots=True)
class ResolutionContext:
    resolver_version: str
    registry_version: str

    def __post_init__(self) -> None:
        if not self.resolver_version.strip():
            raise ValueError(
                "Resolver version must not be empty."
            )

        if not self.registry_version.strip():
            raise ValueError(
                "Registry version must not be empty."
            )


@dataclass(frozen=True, slots=True)
class ResolutionRequest:
    observation_id: ObservationId
    service_identifiers: tuple[ServiceIdentifier, ...]
    context: ResolutionContext

    def __post_init__(self) -> None:
        if not self.service_identifiers:
            raise ValueError(
                "ResolutionRequest requires at least "
                "one ServiceIdentifier."
            )


class EntityResolver(Protocol):

    def resolve(
        self,
        request: ResolutionRequest,
    ) -> ResolutionResult:
        ...
