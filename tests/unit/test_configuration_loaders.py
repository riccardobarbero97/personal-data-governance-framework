import json
from pathlib import Path

from personal_data_governance.config.loaders import (
    load_classification_rules,
    load_relationship_policy,
    load_service_registry,
)
from personal_data_governance.domain.enums.evidence import (
    EvidenceType,
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


def test_default_service_registry_is_loaded() -> None:
    loaded = load_service_registry()

    spotify = loaded.registry.get(
        ServiceId("service_spotify")
    )

    assert spotify is not None
    assert spotify.canonical_name == "Spotify"

    matches = loaded.registry.resolve(
        ServiceIdentifier(
            type=(
                ServiceIdentifierType.EMAIL_DOMAIN
            ),
            original_value="spotify.com",
            observation_id=ObservationId(
                "observation_001"
            ),
        )
    )

    assert matches == (
        spotify,
    )

    assert (
        loaded.registry_version
        == "initial-1"
    )


def test_default_classification_rules_are_loaded() -> None:
    loaded = load_classification_rules()

    assert (
        loaded.rule_set_version
        == "email-subject-rules-1"
    )

    payment_rules = tuple(
        rule
        for rule in loaded.rules
        if rule.evidence_type
        == EvidenceType.PAYMENT
    )

    assert len(
        payment_rules
    ) == 1

    assert (
        payment_rules[0].rule_id
        == "PAYMENT_SUBJECT"
    )


def test_default_relationship_policy_is_loaded() -> None:
    policy = load_relationship_policy()

    assert (
        policy.policy_version
        == "relationship-policy-1"
    )

    assert (
        policy.currently_observed_window_days
        == 365
    )

    assert (
        EvidenceType.ACCOUNT_VERIFICATION
        in policy.establishment_evidence_types
    )

    assert (
        EvidenceType.MARKETING
        in policy
        .observed_communication_evidence_types
    )


def test_invalid_schema_version_is_rejected(
    tmp_path: Path,
) -> None:
    config_file = (
        tmp_path
        / "services.json"
    )

    config_file.write_text(
        json.dumps(
            {
                "schema_version": 999,
                "registry_version": "test",
                "services": []
            }
        ),
        encoding="utf-8",
    )

    try:
        load_service_registry(
            config_file
        )
    except ValueError as error:
        assert "schema version" in str(
            error
        ).lower()
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )


def test_duplicate_service_id_is_rejected(
    tmp_path: Path,
) -> None:
    config_file = (
        tmp_path
        / "services.json"
    )

    service = {
        "service_id": "service_duplicate",
        "canonical_name": "Duplicate",
        "identifiers": [
            {
                "type": "DOMAIN",
                "value": "example.com"
            }
        ]
    }

    config_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registry_version": "test",
                "services": [
                    service,
                    service
                ]
            }
        ),
        encoding="utf-8",
    )

    try:
        load_service_registry(
            config_file
        )
    except ValueError as error:
        assert "Duplicate ServiceId" in str(
            error
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
