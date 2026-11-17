from personal_data_governance.application.ports.service_registry import (
    ServiceRegistry,
)
from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.processing import (
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import (
    ServiceId,
)
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


class InMemoryServiceRegistry(
    ServiceRegistry,
):
    def __init__(self) -> None:
        self._services: dict[
            ServiceId,
            Service,
        ] = {}

        self._identifier_index: dict[
            tuple[
                ServiceIdentifierType,
                str,
            ],
            set[ServiceId],
        ] = {}

    def register_service(
        self,
        service: Service,
    ) -> None:
        self._services[
            service.id
        ] = service

    def register_identifier(
        self,
        service_id: ServiceId,
        identifier_type: ServiceIdentifierType,
        identifier_value: str,
    ) -> None:
        if service_id not in self._services:
            raise KeyError(
                "Cannot register identifier "
                "for an unknown Service: "
                f"{service_id.value}"
            )

        normalized_value = (
            identifier_value
            .strip()
            .lower()
        )

        if not normalized_value:
            raise ValueError(
                "Service identifier "
                "must not be empty."
            )

        key = (
            identifier_type,
            normalized_value,
        )

        self._identifier_index.setdefault(
            key,
            set(),
        ).add(
            service_id
        )

    def resolve(
        self,
        identifier: ServiceIdentifier,
    ) -> tuple[Service, ...]:
        effective_value = (
            identifier.normalized_value
            if identifier.normalized_value
            is not None
            else identifier.original_value
        )

        normalized_value = (
            effective_value
            .strip()
            .lower()
        )

        key = (
            identifier.type,
            normalized_value,
        )

        service_ids = (
            self._identifier_index.get(
                key,
                set(),
            )
        )

        return tuple(
            self._services[
                service_id
            ]
            for service_id in sorted(
                service_ids,
                key=lambda item: item.value,
            )
        )

    def get(
        self,
        service_id: ServiceId,
    ) -> Service | None:
        return self._services.get(
            service_id
        )

    def all_services(
        self,
    ) -> tuple[Service, ...]:
        return tuple(
            self._services[
                service_id
            ]
            for service_id in sorted(
                self._services,
                key=lambda item: item.value,
            )
        )

    def identifiers_for_service(
        self,
        service_id: ServiceId,
    ) -> tuple[
        tuple[
            ServiceIdentifierType,
            str,
        ],
        ...,
    ]:
        identifiers: list[
            tuple[
                ServiceIdentifierType,
                str,
            ]
        ] = []

        for (
            identifier_type,
            identifier_value,
        ), service_ids in (
            self._identifier_index.items()
        ):
            if service_id in service_ids:
                identifiers.append(
                    (
                        identifier_type,
                        identifier_value,
                    )
                )

        return tuple(
            sorted(
                identifiers,
                key=lambda item: (
                    item[0].value,
                    item[1],
                ),
            )
        )
