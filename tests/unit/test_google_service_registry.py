import pytest

from personal_data_governance.config.loaders import (
    load_service_registry,
)
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


GOOGLE_SERVICE_ID = ServiceId(
    "service_google"
)

OBSERVATION_ID = ObservationId(
    "observation_google_001"
)


def build_identifier(
    *,
    identifier_type: ServiceIdentifierType,
    value: str,
) -> ServiceIdentifier:
    return ServiceIdentifier(
        type=identifier_type,
        original_value=value,
        observation_id=OBSERVATION_ID,
    )


def test_google_service_is_loaded() -> None:
    loaded = load_service_registry()

    google = loaded.registry.get(
        GOOGLE_SERVICE_ID
    )

    assert google is not None

    assert (
        google.canonical_name
        == "Google"
    )

    assert (
        loaded.registry_version
        == "initial-2"
    )


@pytest.mark.parametrize(
    (
        "identifier_type",
        "identifier_value",
    ),
    [
        (
            ServiceIdentifierType.EMAIL_DOMAIN,
            "google.com",
        ),
        (
            ServiceIdentifierType.DOMAIN,
            "google.com",
        ),
        (
            ServiceIdentifierType.HOSTNAME,
            "google.com",
        ),
        (
            ServiceIdentifierType.EMAIL_DOMAIN,
            "accounts.google.com",
        ),
        (
            ServiceIdentifierType.HOSTNAME,
            "accounts.google.com",
        ),
    ],
)
def test_google_identifiers_resolve_to_google(
    identifier_type: ServiceIdentifierType,
    identifier_value: str,
) -> None:
    loaded = load_service_registry()

    google = loaded.registry.get(
        GOOGLE_SERVICE_ID
    )

    assert google is not None

    matches = loaded.registry.resolve(
        build_identifier(
            identifier_type=(
                identifier_type
            ),
            value=identifier_value,
        )
    )

    assert matches == (
        google,
    )


@pytest.mark.parametrize(
    "identifier_value",
    [
        "GOOGLE.COM",
        "  google.com  ",
        "ACCOUNTS.GOOGLE.COM",
        "  accounts.google.com  ",
    ],
)
def test_google_email_domains_are_normalized(
    identifier_value: str,
) -> None:
    loaded = load_service_registry()

    google = loaded.registry.get(
        GOOGLE_SERVICE_ID
    )

    assert google is not None

    matches = loaded.registry.resolve(
        build_identifier(
            identifier_type=(
                ServiceIdentifierType
                .EMAIL_DOMAIN
            ),
            value=identifier_value,
        )
    )

    assert matches == (
        google,
    )


def test_unregistered_google_subdomain_is_not_resolved() -> None:
    loaded = load_service_registry()

    matches = loaded.registry.resolve(
        build_identifier(
            identifier_type=(
                ServiceIdentifierType
                .EMAIL_DOMAIN
            ),
            value=(
                "unregistered.google.com"
            ),
        )
    )

    assert matches == ()


def test_google_identifier_does_not_resolve_to_other_services() -> None:
    loaded = load_service_registry()

    matches = loaded.registry.resolve(
        build_identifier(
            identifier_type=(
                ServiceIdentifierType
                .EMAIL_DOMAIN
            ),
            value=(
                "accounts.google.com"
            ),
        )
    )

    assert len(
        matches
    ) == 1

    assert (
        matches[0].id
        == GOOGLE_SERVICE_ID
    )
