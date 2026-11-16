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
