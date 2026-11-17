import argparse
from pathlib import Path

from personal_data_governance.application.services.configuration_validator import (
    ConfigurationValidator,
)
from personal_data_governance.config.loaders import (
    DEFAULT_EMAIL_SUBJECT_RULES_FILE,
    DEFAULT_RELATIONSHIP_POLICY_FILE,
    DEFAULT_SERVICE_REGISTRY_FILE,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Personal Data Governance "
            "configuration files."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    validate_parser = (
        subparsers.add_parser(
            "validate",
            help=(
                "Validate Registry, Rules "
                "and Relationship Policy."
            ),
        )
    )

    validate_parser.add_argument(
        "--services",
        type=Path,
        default=(
            DEFAULT_SERVICE_REGISTRY_FILE
        ),
        help=(
            "Path to Service Registry JSON."
        ),
    )

    validate_parser.add_argument(
        "--rules",
        type=Path,
        default=(
            DEFAULT_EMAIL_SUBJECT_RULES_FILE
        ),
        help=(
            "Path to email classification "
            "rules JSON."
        ),
    )

    validate_parser.add_argument(
        "--policy",
        type=Path,
        default=(
            DEFAULT_RELATIONSHIP_POLICY_FILE
        ),
        help=(
            "Path to Relationship Policy JSON."
        ),
    )

    return parser


def print_section(
    section,
) -> None:
    print()
    print(
        section.name
    )
    print(
        "-" * 60
    )

    print(
        "  Version:",
        (
            section.version
            if section.version is not None
            else "N/A"
        ),
    )

    for metric_name, value in (
        section.metrics
    ):
        print(
            f"  {metric_name}: {value}"
        )

    print(
        "  Status:",
        (
            "VALID"
            if section.valid
            else "INVALID"
        ),
    )

    if section.warnings:
        print(
            "  Warnings:"
        )

        for warning in (
            section.warnings
        ):
            print(
                f"    - {warning}"
            )

    if section.errors:
        print(
            "  Errors:"
        )

        for error in (
            section.errors
        ):
            print(
                f"    - {error}"
            )


def main() -> int:
    parser = build_parser()

    arguments = parser.parse_args()

    if arguments.command != "validate":
        parser.error(
            "Unsupported command."
        )

    result = (
        ConfigurationValidator()
        .validate(
            service_registry_file=(
                arguments.services
            ),
            classification_rules_file=(
                arguments.rules
            ),
            relationship_policy_file=(
                arguments.policy
            ),
        )
    )

    print()
    print(
        "Personal Data Governance "
        "Configuration Validation"
    )
    print(
        "=" * 60
    )

    for section in result.sections:
        print_section(
            section
        )

    print()
    print(
        "=" * 60
    )

    print(
        "RESULT:",
        (
            "VALID"
            if result.valid
            else "INVALID"
        ),
    )

    print()

    return (
        0
        if result.valid
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
