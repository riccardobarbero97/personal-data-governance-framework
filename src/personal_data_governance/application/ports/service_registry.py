from typing import Protocol

from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.values.identifiers import ServiceId
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


class ServiceRegistry(Protocol):

    def resolve(
        self,
        identifier: ServiceIdentifier,
    ) -> tuple[Service, ...]:
        ...

    def get(
        self,
        service_id: ServiceId,
    ) -> Service | None:
        ...
