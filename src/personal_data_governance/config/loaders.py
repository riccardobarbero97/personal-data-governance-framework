import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from personal_data_governance.discovery.evidence_classification.deterministic import (
    SubjectClassificationRule,
)
from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.processing import (
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import (
    ServiceId,
)
from personal_data_governance.infrastructure.service_registry.in_memory import (
    InMemoryServiceRegistry,
)


CONFIG_ROOT = Path(
    __file__
).resolve().parent

DEFAULT_SERVICE_REGISTRY_FILE = (
    CONFIG_ROOT
    / "services"
    / "initial-services.json"
)

DEFAULT_EMAIL_SUBJECT_RULES_FILE = (
    CONFIG_ROOT
    / "rules"
    / "email-subject-rules.json"
)

DEFAULT_RELATIONSHIP_POLICY_FILE = (
    CONFIG_ROOT
    / "policies"
    / "relationship-policy.json"
)


@dataclass(frozen=True, slots=True)
class LoadedServiceRegistry:
    registry: InMemoryServiceRegistry
    registry_version: str


@dataclass(frozen=True, slots=True)
class LoadedClassificationRules:
    rules: tuple[SubjectClassificationRule, ...]
    rule_set_version: str


@dataclass(frozen=True, slots=True)
class RelationshipPolicyConfiguration:
    policy_version: str
    currently_observed_window_days: int
    establishment_evidence_types: frozenset[EvidenceType]
    observed_communication_evidence_types: frozenset[EvidenceType]
    ongoing_activity_evidence_types: frozenset[EvidenceType]
    deletion_evidence_type: EvidenceType

    def __post_init__(self) -> None:
        if not self.policy_version.strip():
            raise ValueError(
                "Relationship policy version "
                "must not be empty."
            )

        if self.currently_observed_window_days < 1:
            raise ValueError(
                "Currently-observed window "
                "must be at least one day."
            )

        if not self.establishment_evidence_types:
            raise ValueError(
                "Relationship policy requires "
                "establishment EvidenceTypes."
            )


def load_json_object(
    file_path: Path,
) -> dict[str, Any]:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {file_path}"
        )

    try:
        payload = json.loads(
            file_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Configuration file contains "
            f"invalid JSON: {file_path}"
        ) from error

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Configuration root must be "
            f"a JSON object: {file_path}"
        )

    schema_version = payload.get(
        "schema_version"
    )

    if schema_version != 1:
        raise ValueError(
            "Unsupported configuration "
            f"schema version in {file_path}: "
            f"{schema_version}"
        )

    return payload


def require_non_empty_string(
    payload: dict[str, Any],
    field_name: str,
    context: str,
) -> str:
    value = payload.get(
        field_name
    )

    if (
        not isinstance(value, str)
        or not value.strip()
    ):
        raise ValueError(
            f"{context}.{field_name} "
            "must be a non-empty string."
        )

    return value.strip()


def require_list(
    payload: dict[str, Any],
    field_name: str,
    context: str,
) -> list[Any]:
    value = payload.get(
        field_name
    )

    if not isinstance(
        value,
        list,
    ):
        raise ValueError(
            f"{context}.{field_name} "
            "must be a list."
        )

    return value


def load_service_registry(
    file_path: Path = DEFAULT_SERVICE_REGISTRY_FILE,
) -> LoadedServiceRegistry:
    payload = load_json_object(
        file_path
    )

    registry_version = require_non_empty_string(
        payload=payload,
        field_name="registry_version",
        context="service_registry",
    )

    raw_services = require_list(
        payload=payload,
        field_name="services",
        context="service_registry",
    )

    registry = InMemoryServiceRegistry()

    seen_service_ids: set[str] = set()

    for service_index, raw_service in enumerate(
        raw_services
    ):
        context = (
            f"service_registry.services[{service_index}]"
        )

        if not isinstance(
            raw_service,
            dict,
        ):
            raise ValueError(
                f"{context} must be an object."
            )

        service_id_value = require_non_empty_string(
            payload=raw_service,
            field_name="service_id",
            context=context,
        )

        canonical_name = require_non_empty_string(
            payload=raw_service,
            field_name="canonical_name",
            context=context,
        )

        if service_id_value in seen_service_ids:
            raise ValueError(
                "Duplicate ServiceId in configuration: "
                f"{service_id_value}"
            )

        seen_service_ids.add(
            service_id_value
        )

        service = Service(
            id=ServiceId(
                service_id_value
            ),
            canonical_name=canonical_name,
        )

        registry.register_service(
            service
        )

        raw_identifiers = require_list(
            payload=raw_service,
            field_name="identifiers",
            context=context,
        )

        if not raw_identifiers:
            raise ValueError(
                f"{context}.identifiers "
                "must not be empty."
            )

        for identifier_index, raw_identifier in enumerate(
            raw_identifiers
        ):
            identifier_context = (
                f"{context}.identifiers"
                f"[{identifier_index}]"
            )

            if not isinstance(
                raw_identifier,
                dict,
            ):
                raise ValueError(
                    f"{identifier_context} "
                    "must be an object."
                )

            identifier_type_value = (
                require_non_empty_string(
                    payload=raw_identifier,
                    field_name="type",
                    context=identifier_context,
                )
            )

            identifier_value = (
                require_non_empty_string(
                    payload=raw_identifier,
                    field_name="value",
                    context=identifier_context,
                )
            )

            try:
                identifier_type = (
                    ServiceIdentifierType(
                        identifier_type_value
                    )
                )
            except ValueError as error:
                raise ValueError(
                    "Unsupported "
                    "ServiceIdentifierType: "
                    f"{identifier_type_value}"
                ) from error

            registry.register_identifier(
                service_id=service.id,
                identifier_type=identifier_type,
                identifier_value=identifier_value,
            )

    return LoadedServiceRegistry(
        registry=registry,
        registry_version=registry_version,
    )


def load_classification_rules(
    file_path: Path = DEFAULT_EMAIL_SUBJECT_RULES_FILE,
) -> LoadedClassificationRules:
    payload = load_json_object(
        file_path
    )

    rule_set_version = require_non_empty_string(
        payload=payload,
        field_name="rule_set_version",
        context="classification_rules",
    )

    raw_rules = require_list(
        payload=payload,
        field_name="rules",
        context="classification_rules",
    )

    if not raw_rules:
        raise ValueError(
            "Classification rule set "
            "must not be empty."
        )

    rules: list[
        SubjectClassificationRule
    ] = []

    seen_rule_ids: set[str] = set()

    for rule_index, raw_rule in enumerate(
        raw_rules
    ):
        context = (
            f"classification_rules.rules[{rule_index}]"
        )

        if not isinstance(
            raw_rule,
            dict,
        ):
            raise ValueError(
                f"{context} must be an object."
            )

        rule_id = require_non_empty_string(
            payload=raw_rule,
            field_name="rule_id",
            context=context,
        )

        if rule_id in seen_rule_ids:
            raise ValueError(
                "Duplicate classification rule id: "
                f"{rule_id}"
            )

        seen_rule_ids.add(
            rule_id
        )

        evidence_type_value = require_non_empty_string(
            payload=raw_rule,
            field_name="evidence_type",
            context=context,
        )

        try:
            evidence_type = EvidenceType(
                evidence_type_value
            )
        except ValueError as error:
            raise ValueError(
                "Unsupported EvidenceType "
                "in classification rule: "
                f"{evidence_type_value}"
            ) from error

        priority = raw_rule.get(
            "priority"
        )

        if (
            not isinstance(priority, int)
            or isinstance(priority, bool)
        ):
            raise ValueError(
                f"{context}.priority "
                "must be an integer."
            )

        raw_patterns = require_list(
            payload=raw_rule,
            field_name="patterns",
            context=context,
        )

        patterns = tuple(
            pattern
            for pattern in raw_patterns
            if (
                isinstance(pattern, str)
                and pattern.strip()
            )
        )

        if len(patterns) != len(
            raw_patterns
        ):
            raise ValueError(
                f"{context}.patterns must contain "
                "only non-empty strings."
            )

        if not patterns:
            raise ValueError(
                f"{context}.patterns "
                "must not be empty."
            )

        rules.append(
            SubjectClassificationRule(
                rule_id=rule_id,
                evidence_type=evidence_type,
                patterns=patterns,
                priority=priority,
            )
        )

    return LoadedClassificationRules(
        rules=tuple(
            rules
        ),
        rule_set_version=rule_set_version,
    )


def load_relationship_policy(
    file_path: Path = DEFAULT_RELATIONSHIP_POLICY_FILE,
) -> RelationshipPolicyConfiguration:
    payload = load_json_object(
        file_path
    )

    policy_version = require_non_empty_string(
        payload=payload,
        field_name="policy_version",
        context="relationship_policy",
    )

    window_days = payload.get(
        "currently_observed_window_days"
    )

    if (
        not isinstance(window_days, int)
        or isinstance(window_days, bool)
    ):
        raise ValueError(
            "relationship_policy."
            "currently_observed_window_days "
            "must be an integer."
        )

    establishment_types = (
        _load_evidence_type_set(
            payload=payload,
            field_name=(
                "establishment_evidence_types"
            ),
        )
    )

    observed_types = (
        _load_evidence_type_set(
            payload=payload,
            field_name=(
                "observed_communication_evidence_types"
            ),
        )
    )

    ongoing_types = (
        _load_evidence_type_set(
            payload=payload,
            field_name=(
                "ongoing_activity_evidence_types"
            ),
        )
    )

    deletion_type_value = require_non_empty_string(
        payload=payload,
        field_name="deletion_evidence_type",
        context="relationship_policy",
    )

    try:
        deletion_type = EvidenceType(
            deletion_type_value
        )
    except ValueError as error:
        raise ValueError(
            "Unsupported deletion EvidenceType: "
            f"{deletion_type_value}"
        ) from error

    return RelationshipPolicyConfiguration(
        policy_version=policy_version,
        currently_observed_window_days=(
            window_days
        ),
        establishment_evidence_types=(
            establishment_types
        ),
        observed_communication_evidence_types=(
            observed_types
        ),
        ongoing_activity_evidence_types=(
            ongoing_types
        ),
        deletion_evidence_type=deletion_type,
    )


def _load_evidence_type_set(
    payload: dict[str, Any],
    field_name: str,
) -> frozenset[EvidenceType]:
    raw_values = require_list(
        payload=payload,
        field_name=field_name,
        context="relationship_policy",
    )

    if not raw_values:
        raise ValueError(
            ."
            f"{field_name} must not be empty."
        )

    evidence_types: set[
        EvidenceType
    ] = set()

    for raw_value in raw_values:
        if (
            not isinstance(raw_value, str)
            or not raw_value.strip()
        ):
            raise ValueError(
                "relationship_policy."
                f"{field_name} must contain "
                "only non-empty strings."
            )

        try:
            evidence_type = EvidenceType(
                raw_value
            )
        except ValueError as error:
            raise ValueError(
                "Unsupported EvidenceType "
                f"in {field_name}: {raw_value}"
            ) from error

        evidence_types.add(
            evidence_type
        )

    return frozenset(
        evidence_types
    )
