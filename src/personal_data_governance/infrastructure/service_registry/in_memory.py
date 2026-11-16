from personal_data_governance.application.ports.service_registry import (
    ServiceRegistry,
)
from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.processing import (
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import ServiceId
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


class InMemoryServiceRegistry(ServiceRegistry):
    def __init__(self) -> None:
        self._services: dict[
            ServiceId,
            Service,
        ] = {}

        self._identifier_index: dict[
            tuple[ServiceIdentifierType, str],
            set[ServiceId],
        ] = {}

    def register_service(
        self,
        service: Service,
    ) -> None:
        self._services[service.id] = service

    def register_identifier(
        self,
        service_id: ServiceId,
        identifier_type: ServiceIdentifierType,
        identifier_value: str,
    ) -> None:
        if service_id not in self._services:
            raise KeyError(
                f"Service not found: {service_id.value}"
            )

        normalized_value = self._normalize_registry_value(
            identifier_value
        )

        key = (
            identifier_type,
            normalized_value,
        )

        self._identifier_index.setdefault(
            key,
            set(),
        ).add(service_id)

    def resolve(
        self,
        identifier: ServiceIdentifier,
    ) -> tuple[Service, ...]:
        lookup_value = (
            identifier.normalized_value
            if identifier.normalized_value is not None
            else identifier.original_value
        )

        normalized_lookup_value = (
            self._normalize_registry_value(
                lookup_value
            )
        )

        key = (
            identifier.type,
            normalized_lookup_value,
        )

        service_ids = self._identifier_index.get(
            key,
            set(),
        )

        services = tuple(
            self._services[service_id]
            for service_id in sorted(
                service_ids,
                key=lambda item: item.value,
            )
        )

        return services

    def get(
        self,
        service_id: ServiceId,
    ) -> Service | None:
        return self._services.get(service_id)

    @staticmethod
    def _normalize_registry_value(
        value: str,
    ) -> str:
        normalized = value.strip().lower()

        if not normalized:
            raise ValueError(
                "Service identifier value must not be empty."
            )

        return normalized
