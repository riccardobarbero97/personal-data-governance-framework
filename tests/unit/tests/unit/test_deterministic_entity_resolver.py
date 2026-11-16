from personal_data_governance.discovery.entity_resolution.deterministic import (
    DeterministicEntityResolver,
)
from personal_data_governance.discovery.entity_resolution.protocol import (
    ResolutionContext,
    ResolutionRequest,
)
from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.processing import (
    ProcessingStatus,
    ResolutionMethod,
    ResolutionStatus,
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


def build_context() -> ResolutionContext:
    return ResolutionContext(
        resolver_version="1",
        registry_version="1",
    )


def build_spotify_service() -> Service:
    return Service(
        id=ServiceId("service_spotify"),
        canonical_name="Spotify",
    )


def build_registry_with_spotify() -> InMemoryServiceRegistry:
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
        identifier_type=ServiceIdentifierType.DOMAIN,
        identifier_value="spotify.com",
    )

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.HOSTNAME,
        identifier_value="accounts.spotify.com",
    )

    return registry


def test_exact_identifier_match_is_resolved() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="spotify.com",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.resolution_status == ResolutionStatus.RESOLVED

    assert (
        result.resolved_service_id
        == ServiceId("service_spotify")
    )

    assert result.alternative_service_ids == ()

    assert (
        result.method
        == ResolutionMethod.EXACT_IDENTIFIER_MATCH
    )

    assert result.reason_codes == (
        "EXACT_IDENTIFIER_MATCH",
    )

    assert len(result.normalized_identifiers) == 1

    normalized_identifier = (
        result.normalized_identifiers[0]
    )

    assert (
        normalized_identifier.normalized_value
        == "spotify.com"
    )


def test_unknown_identifier_is_unresolved() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="unknown.example",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert (
        result.resolution_status
        == ResolutionStatus.UNRESOLVED
    )

    assert result.resolved_service_id is None
    assert result.alternative_service_ids == ()
    assert result.method is None

    assert result.reason_codes == (
        "NO_MATCH",
    )


def test_case_and_whitespace_normalization_can_resolve() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="  SPOTIFY.COM  ",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.resolution_status == ResolutionStatus.RESOLVED

    assert (
        result.resolved_service_id
        == ServiceId("service_spotify")
    )

    assert (
        result.method
        == ResolutionMethod.DOMAIN_NORMALIZATION
    )

    assert result.reason_codes == (
        "NORMALIZED_IDENTIFIER_MATCH",
    )

    assert (
        result.normalized_identifiers[0].normalized_value
        == "spotify.com"
    )

    assert (
        result.normalized_identifiers[0].original_value
        == "  SPOTIFY.COM  "
    )


def test_provided_normalized_value_is_used() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="accounts.spotify.com",
        normalized_value="spotify.com",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.resolution_status == ResolutionStatus.RESOLVED

    assert (
        result.resolved_service_id
        == ServiceId("service_spotify")
    )

    assert (
        result.method
        == ResolutionMethod.DOMAIN_NORMALIZATION
    )

    assert (
        result.normalized_identifiers[0].original_value
        == "accounts.spotify.com"
    )

    assert (
        result.normalized_identifiers[0].normalized_value
        == "spotify.com"
    )


def test_multiple_matches_are_ambiguous() -> None:
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

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="shared.example",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.processing_status == ProcessingStatus.SUCCESS

    assert (
        result.resolution_status
        == ResolutionStatus.AMBIGUOUS
    )

    assert result.resolved_service_id is None

    assert result.alternative_service_ids == (
        ServiceId("service_a"),
        ServiceId("service_b"),
    )

    assert result.method is None

    assert result.reason_codes == (
        "MULTIPLE_MATCHES",
    )


def test_duplicate_matches_are_collapsed() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    email_domain_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="spotify.com",
        observation_id=observation_id,
    )

    domain_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="spotify.com",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            email_domain_identifier,
            domain_identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.resolution_status == ResolutionStatus.RESOLVED

    assert (
        result.resolved_service_id
        == ServiceId("service_spotify")
    )

    assert result.alternative_service_ids == ()


def test_conflicting_identifiers_are_ambiguous() -> None:
    registry = InMemoryServiceRegistry()

    spotify = Service(
        id=ServiceId("service_spotify"),
        canonical_name="Spotify",
    )

    netflix = Service(
        id=ServiceId("service_netflix"),
        canonical_name="Netflix",
    )

    registry.register_service(spotify)
    registry.register_service(netflix)

    registry.register_identifier(
        service_id=spotify.id,
        identifier_type=ServiceIdentifierType.DOMAIN,
        identifier_value="spotify.com",
    )

    registry.register_identifier(
        service_id=netflix.id,
        identifier_type=ServiceIdentifierType.DOMAIN,
        identifier_value="netflix.com",
    )

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    spotify_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="spotify.com",
        observation_id=observation_id,
    )

    netflix_identifier = ServiceIdentifier(
        type=ServiceIdentifierType.DOMAIN,
        original_value="netflix.com",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            spotify_identifier,
            netflix_identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    assert result.resolution_status == ResolutionStatus.AMBIGUOUS

    assert result.alternative_service_ids == (
        ServiceId("service_netflix"),
        ServiceId("service_spotify"),
    )

    assert result.reason_codes == (
        "MULTIPLE_MATCHES",
    )


def test_original_identifier_is_preserved_after_normalization() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="  SPOTIFY.COM  ",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=build_context(),
    )

    result = resolver.resolve(request)

    normalized_identifier = result.normalized_identifiers[0]

    assert (
        normalized_identifier.original_value
        == "  SPOTIFY.COM  "
    )

    assert (
        normalized_identifier.normalized_value
        == "spotify.com"
    )


def test_resolver_version_is_preserved() -> None:
    registry = build_registry_with_spotify()

    resolver = DeterministicEntityResolver(
        service_registry=registry
    )

    observation_id = ObservationId("observation_001")

    identifier = ServiceIdentifier(
        type=ServiceIdentifierType.EMAIL_DOMAIN,
        original_value="spotify.com",
        observation_id=observation_id,
    )

    request = ResolutionRequest(
        observation_id=observation_id,
        service_identifiers=(
            identifier,
        ),
        context=ResolutionContext(
            resolver_version="resolver_1.0",
            registry_version="registry_1.0",
        ),
    )

    result = resolver.resolve(request)

    assert result.resolver_version == "resolver_1.0"
