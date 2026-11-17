import json
from pathlib import Path

from personal_data_governance.application.services.configuration_validator import (
    ConfigurationValidator,
)


def test_default_configuration_is_valid() -> None:
    result = (
        ConfigurationValidator()
        .validate()
    )

    assert result.valid is True
    assert result.errors == ()

    assert len(
        result.sections
    ) == 3

    section_names = tuple(
        section.name
        for section in result.sections
    )

    assert section_names == (
        "Service Registry",
        "Classification Rules",
        "Relationship Policy",
    )


def test_invalid_regex_is_reported(
    tmp_path: Path,
) -> None:
    rules_file = (
        tmp_path
        / "rules.json"
    )

    rules_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "rule_set_version": "broken-1",
                "rules": [
                    {
                        "rule_id": "BROKEN",
                        "evidence_type": "PAYMENT",
                        "priority": 10,
                        "patterns": [
                            "[invalid"
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = (
        ConfigurationValidator()
        .validate(
            classification_rules_file=(
                rules_file
            )
        )
    )

    assert result.valid is False

    assert any(
        error.startswith(
            "INVALID_REGEX:BROKEN:"
        )
        for error in result.errors
    )


def test_relationship_policy_overlap_is_rejected(
    tmp_path: Path,
) -> None:
    policy_file = (
        tmp_path
        / "policy.json"
    )

    policy_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_version": "invalid-1",
                "currently_observed_window_days": 365,
                "establishment_evidence_types": [
                    "PAYMENT",
                    "MARKETING"
                ],
                "observed_communication_evidence_types": [
                    "MARKETING"
                ],
                "ongoing_activity_evidence_types": [
                    "PAYMENT"
                ],
                "deletion_evidence_type": "PAYMENT"
            }
        ),
        encoding="utf-8",
    )

    result = (
        ConfigurationValidator()
        .validate(
            relationship_policy_file=(
                policy_file
            )
        )
    )

    assert result.valid is False

    assert any(
        error.startswith(
            "RELATIONSHIP_STATUS_POLICY_OVERLAP:"
        )
        for error in result.errors
    )


def test_invalid_service_identifier_type_is_reported(
    tmp_path: Path,
) -> None:
    service_file = (
        tmp_path
        / "services.json"
    )

    service_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "registry_version": "broken-1",
                "services": [
                    {
                        "service_id": "service_test",
                        "canonical_name": "Test",
                        "identifiers": [
                            {
                                "type": "EMAIL_DOMAN",
                                "value": "example.com"
                            }
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = (
        ConfigurationValidator()
        .validate(
            service_registry_file=(
                service_file
            )
        )
    )

    assert result.valid is False

    assert any(
        "ServiceIdentifierType"
        in error
        for error in result.errors
    )


def test_invalid_evidence_type_is_reported(
    tmp_path: Path,
) -> None:
    rules_file = (
        tmp_path
        / "rules.json"
    )

    rules_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "rule_set_version": "broken-1",
                "rules": [
                    {
                        "rule_id": "BROKEN",
                        "evidence_type": "PASSWORD_RESEET",
                        "priority": 10,
                        "patterns": [
                            "reset"
                        ]
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = (
        ConfigurationValidator()
        .validate(
            classification_rules_file=(
                rules_file
            )
        )
    )

    assert result.valid is False

    assert any(
        "EvidenceType"
        in error
        for error in result.errors
    )
