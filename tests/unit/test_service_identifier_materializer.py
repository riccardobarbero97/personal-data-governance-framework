from personal_data_governance.application.services.service_identifier_materializer import (
    materialize_service_identifier,
    materialize_service_identifiers,
)
from personal_data_governance.application.values.candidate_identifier import (
    CandidateIdentifier,
)
from personal_data_governance.domain.enums.processing import (
    CandidateIdentifierType,
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import ObservationId


def test_email_domain_candidate_is_materialized() -> None:
    candidate = CandidateIdentifier(
        type=CandidateIdentifierType.EMAIL_DOMAIN,
        value="spotify.com",
        source_attribute="sender",
    )

    observation_id = ObservationId("observation_001")

    identifier = materialize_service_identifier(
        candidate_identifier=candidate,
        observation_id=observation_id,
    )

    assert (
        identifier.type
        == ServiceIdentifierType.EMAIL_DOMAIN
    )

    assert identifier.original_value == "spotify.com"

    assert identifier.normalized_value is None

    assert identifier.observation_id == observation_id


def test_domain_candidate_is_materialized() -> None:
    candidate = CandidateIdentifier(
        type=CandidateIdentifierType.DOMAIN,
        value="spotify.com",
        source_attribute="domain",
    )

    observation_id = ObservationId("observation_001")

    identifier = materialize_service_identifier(
        candidate_identifier=candidate,
        observation_id=observation_id,
    )

    assert identifier.type == ServiceIdentifierType.DOMAIN
    assert identifier.original_value == "spotify.com"
    assert identifier.observation_id == observation_id


def test_hostname_candidate_is_materialized() -> None:
    candidate = CandidateIdentifier(
        type=CandidateIdentifierType.HOSTNAME,
        value="accounts.spotify.com",
        source_attribute="hostname",
    )

    observation_id = ObservationId("observation_001")

    identifier = materialize_service_identifier(
        candidate_identifier=candidate,
        observation_id=observation_id,
    )

    assert (
        identifier.type
        == ServiceIdentifierType.HOSTNAME
    )

    assert (
        identifier.original_value
        == "accounts.spotify.com"
    )

    assert identifier.normalized_value is None

    assert identifier.observation_id == observation_id


def test_multiple_candidates_are_materialized() -> None:
    candidates = (
        CandidateIdentifier(
            type=CandidateIdentifierType.EMAIL_DOMAIN,
            value="spotify.com",
            source_attribute="sender",
        ),
        CandidateIdentifier(
            type=CandidateIdentifierType.HOSTNAME,
            value="accounts.spotify.com",
            source_attribute="hostname",
        ),
    )

    observation_id = ObservationId("observation_001")

    identifiers = materialize_service_identifiers(
        candidate_identifiers=candidates,
        observation_id=observation_id,
    )

    assert len(identifiers) == 2

    assert (
        identifiers[0].type
        == ServiceIdentifierType.EMAIL_DOMAIN
    )

    assert identifiers[0].original_value == "spotify.com"

    assert (
        identifiers[1].type
        == ServiceIdentifierType.HOSTNAME
    )

    assert (
        identifiers[1].original_value
        == "accounts.spotify.com"
    )

    assert all(
        identifier.observation_id == observation_id
        for identifier in identifiers
    )


def test_empty_candidate_collection_returns_empty_tuple() -> None:
    identifiers = materialize_service_identifiers(
        candidate_identifiers=(),
        observation_id=ObservationId("observation_001"),
    )

    assert identifiers == ()
