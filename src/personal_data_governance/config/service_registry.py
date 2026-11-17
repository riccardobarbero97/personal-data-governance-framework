from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.processing import (
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import ServiceId
from personal_data_governance.infrastructure.service_registry.in_memory import (
    InMemoryServiceRegistry,
)


INITIAL_SERVICES = (
    (
        Service(
            id=ServiceId("service_spotify"),
            canonical_name="Spotify",
        ),
        (
            (
                ServiceIdentifierType.EMAIL_DOMAIN,
                "spotify.com",
            ),
        ),
    ),
    (
        Service(
            id=ServiceId("service_netflix"),
            canonical_name="Netflix",
        ),
        (
            (
                ServiceIdentifierType.EMAIL_DOMAIN,
                "netflix.com",
            ),
        ),
    ),
    (
        Service(
            id=ServiceId("service_github"),
            canonical_name="GitHub",
        ),
        (
            (
                ServiceIdentifierType.EMAIL_DOMAIN,
                "github.com",
            ),
        ),
    ),
    (
        Service(
            id=ServiceId("service_linkedin"),
            canonical_name="LinkedIn",
        ),
        (
            (
                ServiceIdentifierType.EMAIL_DOMAIN,
                "linkedin.com",
            ),
        ),
    ),
    (
        Service(
            id=ServiceId("service_dropbox"),
            canonical_name="Dropbox",
        ),
        (
            (
                ServiceIdentifierType.EMAIL_DOMAIN,
                "dropbox.com",
            ),
        ),
    ),
)


def build_initial_service_registry() -> InMemoryServiceRegistry:
    registry = InMemoryServiceRegistry()

    for service, identifiers in INITIAL_SERVICES:
        registry.register_service(
            service
        )

        for (
            identifier_type,
            identifier_value,
        ) in identifiers:
            registry.register_identifier(
                service_id=service.id,
                identifier_type=identifier_type,
                identifier_value=identifier_value,
            )

    return registry
