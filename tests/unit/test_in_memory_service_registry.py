import pytest

from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.processing import (
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import (
    ObservationId,
    ServiceId,
)
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)
from personal_data_governance.infrastructure.service_registry.in_memory import (
    InMemoryServiceRegistry,
)


def build_spotify_service() -> Service:
    return Service(
        id=ServiceId("service_spotify"),
        canonical_name="Spotify",
    )


def test_service_can_be_registered_and_loaded() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    stored = registry.get(spotify.id)

    assert stored == spotify


def test_exact_identifier_resolves_to_registered_service() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
        identifier_value="spotify.com",
    )

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="spotify.com",
        observation_id=ObservationId("observation_001"),
    )

    matches = registry.resolve(identifier)

    assert matches == (spotify,)


def test_unknown_identifier_returns_no_matches() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
        identifier_value="spotify.com",
    )

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="unknown.example",
        observation_id=ObservationId("observation_001"),
    )

    matches = registry.resolve(identifier)

    assert matches == ()


def test_registry_lookup_is_case_insensitive() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
        identifier_value="Spotify.COM",
    )

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="SPOTIFY.com",
        observation_id=ObservationId("observation_001"),
    )

    matches = registry.resolve(identifier)

    assert matches == (spotify,)


def test_registry_lookup_ignores_outer_whitespace() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
        identifier_value="spotify.com",
    )

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="  spotify.com  ",
        observation_id=ObservationId("observation_001"),
    )

    matches = registry.resolve(identifier)

    assert matches == (spotify,)


def test_identifier_for_unknown_service_cannot_be_registered() -> None:
    registry = InMemoryServiceRegistry()

    with pytest.raises(KeyError):
        registry.register_identifier(
            service_id=ServiceId("service_missing"),
            identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
            identifier_value="example.com",
        )


def test_empty_registry_identifier_cannot_be_registered() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    with pytest.raises(ValueError):
        registry.register_identifier(
            service_id=spotify.id,
            identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
            identifier_value="   ",
        )


def test_multiple_identifiers_can_resolve_to_same_service() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
        identifier_value="spotify.com",
    )

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.HOSTNAME,
        identifier_value="accounts.spotify.com",
    )

    email_domain_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="spotify.com",
        observation_id=ObservationId("observation_001"),
    )

    hostname_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.HOSTNAME,
        original_value="accounts.spotify.com",
        observation_id=ObservationId("observation_002"),
    )

    email_domain_matches = registry.resolve(
        email_domain_identifier
    )

    hostname_matches = registry.resolve(
        hostname_identifier
    )

    assert email_domain_matches == (spotify,)
    assert hostname_matches == (spotify,)


def test_identifiers_from_different_observations_can_converge() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.EMAIL_DOMAIN,
        identifier_value="spotify.com",
    )

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.HOSTNAME,
        identifier_value="accounts.spotify.com",
    )

    gmail_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="spotify.com",
        observation_id=ObservationId(
            "observation_from_gmail"
        ),
    )

    password_manager_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.HOSTNAME,
        original_value="accounts.spotify.com",
        observation_id=ObservationId(
            "observation_from_password_manager"
        ),
    )

    gmail_matches = registry.resolve(
        gmail_identifier
    )

    password_manager_matches = registry.resolve(
        password_manager_identifier
    )

    assert gmail_matches == (spotify,)
    assert password_manager_matches == (spotify,)


def test_one_identifier_can_return_multiple_services() -> None:
    registry = InMemoryServiceRegistry()

    service_a = Service(
        id=ServiceId("service_a"),
        canonical_name="Service A",
    )

    service_b = Service(
        id=ServiceId("service_b"),
        canonical_name="Service B",
    )

    registry.register_service(service_a)
    registry.register_service(service_b)

    registry.register_identifier(
        service_id=service_a.id,
        identifier_type=ServiceIdentifierType.DOMAIN,
        identifier_value="shared.example",
    )

    registry.register_identifier(
        service_id=service_b.id,
        identifier_type=ServiceIdentifierType.DOMAIN,
        identifier_value="shared.example",
    )

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="shared.example",
        observation_id=ObservationId("observation_001"),
    )

    matches = registry.resolve(identifier)

    assert len(matches) == 2
    assert service_a in matches
    assert service_b in matches


def test_normalized_identifier_value_is_used_for_lookup() -> None:
    registry = InMemoryServiceRegistry()

    spotify = build_spotify_service()

    registry.register_service(spotify)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.DOMAIN,
        identifier_value="spotify.com",
    )

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="accounts.spotify.com",
        normalized_value="spotify.com",
        observation_id=ObservationId("observation_001"),
    )

    matches = registry.resolve(identifier)

    assert matches == (spotify,)

def test_all_services_returns_registered_services() -> None:
    registry = InMemoryServiceRegistry()

    first_service = Service(
        id=ServiceId(
            "service_b"
        ),
        canonical_name="B",
    )

    second_service = Service(
        id=ServiceId(
            "service_a"
        ),
        canonical_name="A",
    )

    registry.register_service(
        first_service
    )

    registry.register_service(
        second_service
    )

    assert registry.all_services() == (
        second_service,
        first_service,
    )


def test_identifiers_for_service_returns_registered_identifiers() -> None:
    registry = InMemoryServiceRegistry()

    service = Service(
        id=ServiceId(
            "service_example"
        ),
        canonical_name="Example",
    )

    registry.register_service(
        service
    )

    registry.register_identifier(
        service_id=service.id,
        identifier_type=(
            ServiceIdentifierType.DOMAIN
        ),
        identifier_value="example.com",
    )

    registry.register_identifier(
        service_id=service.id,
        identifier_type=(
            ServiceIdentifierType.EMAIL_DOMAIN
        ),
        identifier_value="mail.example.com",
    )

    assert (
        registry.identifiers_for_service(
            service.id
        )
        == (
            (
                ServiceIdentifierType.DOMAIN,
                "example.com",
            ),
            (
                ServiceIdentifierType.EMAIL_DOMAIN,
                "mail.example.com",
            ),
        )
    )
