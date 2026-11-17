import re
from pathlib import Path

from personal_data_governance.application.results.configuration_validation import (
    ConfigurationSectionValidation,
    ConfigurationValidationResult,
)
from personal_data_governance.config.loaders import (
    DEFAULT_EMAIL_SUBJECT_RULES_FILE,
    DEFAULT_RELATIONSHIP_POLICY_FILE,
    DEFAULT_SERVICE_REGISTRY_FILE,
    load_classification_rules,
    load_relationship_policy,
    load_service_registry,
)


class ConfigurationValidator:
    def validate(
        self,
        service_registry_file: Path = (
            DEFAULT_SERVICE_REGISTRY_FILE
        ),
        classification_rules_file: Path = (
            DEFAULT_EMAIL_SUBJECT_RULES_FILE
        ),
        relationship_policy_file: Path = (
            DEFAULT_RELATIONSHIP_POLICY_FILE
        ),
    ) -> ConfigurationValidationResult:
        registry_result = (
            self._validate_service_registry(
                service_registry_file
            )
        )

        rules_result = (
            self._validate_classification_rules(
                classification_rules_file
            )
        )

        policy_result = (
            self._validate_relationship_policy(
                relationship_policy_file
            )
        )

        sections = (
            registry_result,
            rules_result,
            policy_result,
        )

        return ConfigurationValidationResult(
            valid=all(
                section.valid
                for section in sections
            ),
            sections=sections,
        )

    @staticmethod
    def _validate_service_registry(
        file_path: Path,
    ) -> ConfigurationSectionValidation:
        try:
            loaded = load_service_registry(
                file_path
            )
        except Exception as error:
            return ConfigurationSectionValidation(
                name="Service Registry",
                version=None,
                valid=False,
                metrics=(),
                errors=(
                    ConfigurationValidator
                    ._format_error(
                        error
                    ),
                ),
                warnings=(),
            )

        services = (
            loaded.registry
            .all_services()
        )

        identifier_count = sum(
            len(
                loaded.registry
                .identifiers_for_service(
                    service.id
                )
            )
            for service in services
        )

        warnings: list[str] = []

        if len(services) < 5:
            warnings.append(
                "SERVICE_REGISTRY_IS_SMALL"
            )

        return ConfigurationSectionValidation(
            name="Service Registry",
            version=loaded.registry_version,
            valid=True,
            metrics=(
                (
                    "services",
                    len(services),
                ),
                (
                    "identifiers",
                    identifier_count,
                ),
            ),
            errors=(),
            warnings=tuple(
                warnings
            ),
        )

    @staticmethod
    def _validate_classification_rules(
        file_path: Path,
    ) -> ConfigurationSectionValidation:
        try:
            loaded = load_classification_rules(
                file_path
            )
        except Exception as error:
            return ConfigurationSectionValidation(
                name="Classification Rules",
                version=None,
                valid=False,
                metrics=(),
                errors=(
                    ConfigurationValidator
                    ._format_error(
                        error
                    ),
                ),
                warnings=(),
            )

        regex_errors: list[str] = []

        pattern_count = 0

        for rule in loaded.rules:
            pattern_count += len(
                rule.patterns
            )

            for pattern in rule.patterns:
                try:
                    re.compile(
                        pattern,
                        flags=re.IGNORECASE,
                    )
                except re.error as error:
                    regex_errors.append(
                        "INVALID_REGEX:"
                        f"{rule.rule_id}:"
                        f"{error}"
                    )

        warnings: list[str] = []

        priorities = [
            rule.priority
            for rule in loaded.rules
        ]

        if (
            len(priorities)
            != len(set(priorities))
        ):
            warnings.append(
                "DUPLICATE_RULE_PRIORITIES"
            )

        return ConfigurationSectionValidation(
            name="Classification Rules",
            version=(
                loaded.rule_set_version
            ),
            valid=not regex_errors,
            metrics=(
                (
                    "rules",
                    len(
                        loaded.rules
                    ),
                ),
                (
                    "patterns",
                    pattern_count,
                ),
            ),
            errors=tuple(
                regex_errors
            ),
            warnings=tuple(
                warnings
            ),
        )

    @staticmethod
    def _validate_relationship_policy(
        file_path: Path,
    ) -> ConfigurationSectionValidation:
        try:
            policy = load_relationship_policy(
                file_path
            )
        except Exception as error:
            return ConfigurationSectionValidation(
                name="Relationship Policy",
                version=None,
                valid=False,
                metrics=(),
                errors=(
                    ConfigurationValidator
                    ._format_error(
                        error
                    ),
                ),
                warnings=(),
            )

        errors: list[str] = []
        warnings: list[str] = []

        overlap = (
            policy.establishment_evidence_types
            & policy.observed_communication_evidence_types
        )

        if overlap:
            overlapping_values = ",".join(
                sorted(
                    evidence_type.value
                    for evidence_type in overlap
                )
            )

            errors.append(
                "RELATIONSHIP_STATUS_POLICY_OVERLAP:"
                f"{overlapping_values}"
            )

        if (
            policy.deletion_evidence_type
            not in policy.establishment_evidence_types
        ):
            errors.append(
                "DELETION_EVIDENCE_MUST_ESTABLISH_RELATIONSHIP"
            )

        if (
            policy.deletion_evidence_type
            in policy.ongoing_activity_evidence_types
        ):
            errors.append(
                "DELETION_EVIDENCE_CANNOT_BE_ONGOING_ACTIVITY"
            )

        if (
            policy.currently_observed_window_days
            > 3650
        ):
            warnings.append(
                "CURRENTLY_OBSERVED_WINDOW_EXCEEDS_TEN_YEARS"
            )

        return ConfigurationSectionValidation(
            name="Relationship Policy",
            version=policy.policy_version,
            valid=not errors,
            metrics=(
                (
                    "current_window_days",
                    policy.currently_observed_window_days,
                ),
                (
                    "establishment_types",
                    len(
                        policy.establishment_evidence_types
                    ),
                ),
                (
                    "communication_types",
                    len(
                        policy.observed_communication_evidence_types
                    ),
                ),
                (
                    "ongoing_activity_types",
                    len(
                        policy.ongoing_activity_evidence_types
                    ),
                ),
            ),
            errors=tuple(
                errors
            ),
            warnings=tuple(
                warnings
            ),
        )

    @staticmethod
    def _format_error(
        error: Exception,
    ) -> str:
        return (
            f"{type(error).__name__}: "
            f"{error}"
        )
