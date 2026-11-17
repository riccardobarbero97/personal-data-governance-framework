from personal_data_governance.application.ports.service_registry import (
    ServiceRegistry,
)
from personal_data_governance.application.results.resolution import (
    ResolutionResult,
)
from personal_data_governance.discovery.entity_resolution.protocol import (
    EntityResolver,
    ResolutionRequest,
)
from personal_data_governance.domain.entities.service import Service
from personal_data_governance.domain.enums.processing import (
    ProcessingStatus,
    ResolutionMethod,
    ResolutionStatus,
)
from personal_data_governance.domain.values.identifiers import ServiceId
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


class DeterministicEntityResolver(EntityResolver):
    def __init__(
        self,
        service_registry: ServiceRegistry,
    ) -> None:
        self._service_registry = service_registry

    def resolve(
        self,
        request: ResolutionRequest,
    ) -> ResolutionResult:
        normalized_identifiers = tuple(
            self._normalize_identifier(identifier)
            for identifier in request.service_identifiers
        )

        matched_services = self._collect_unique_matches(
            normalized_identifiers
        )

        if not matched_services:
            return ResolutionResult(
                observation_id=request.observation_id,
                input_identifiers=request.service_identifiers,
                normalized_identifiers=normalized_identifiers,
                processing_status=ProcessingStatus.SUCCESS,
                resolution_status=ResolutionStatus.UNRESOLVED,
                resolved_service_id=None,
                alternative_service_ids=(),
                method=None,
                reason_codes=(
                    "NO_MATCH",
                ),
                resolver_version=request.context.resolver_version,
            )

        if len(matched_services) == 1:
            resolved_service = matched_services[0]

            resolution_method = self._determine_resolution_method(
                input_identifiers=request.service_identifiers,
                normalized_identifiers=normalized_identifiers,
            )

            return ResolutionResult(
                observation_id=request.observation_id,
                input_identifiers=request.service_identifiers,
                normalized_identifiers=normalized_identifiers,
                processing_status=ProcessingStatus.SUCCESS,
                resolution_status=ResolutionStatus.RESOLVED,
                resolved_service_id=resolved_service.id,
                alternative_service_ids=(),
                method=resolution_method,
                reason_codes=(
                    self._resolved_reason_code(
                        resolution_method
                    ),
                ),
                resolver_version=request.context.resolver_version,
            )

        alternative_service_ids = tuple(
            service.id
            for service in matched_services
        )

        return ResolutionResult(
            observation_id=request.observation_id,
            input_identifiers=request.service_identifiers,
            normalized_identifiers=normalized_identifiers,
            processing_status=ProcessingStatus.SUCCESS,
            resolution_status=ResolutionStatus.AMBIGUOUS,
            resolved_service_id=None,
            alternative_service_ids=alternative_service_ids,
            method=None,
            reason_codes=(
                "MULTIPLE_MATCHES",
            ),
            resolver_version=request.context.resolver_version,
        )

    def _collect_unique_matches(
        self,
        identifiers: tuple[ServiceIdentifier, ...],
    ) -> tuple[Service, ...]:
        services_by_id: dict[ServiceId, Service] = {}

        for identifier in identifiers:
            matches = self._service_registry.resolve(
                identifier
            )

            for service in matches:
                services_by_id[service.id] = service

        return tuple(
            services_by_id[service_id]
            for service_id in sorted(
                services_by_id,
                key=lambda item: item.value,
            )
        )

    @staticmethod
    def _normalize_identifier(
        identifier: ServiceIdentifier,
    ) -> ServiceIdentifier:
        normalized_original_value = (
            identifier.original_value.strip().lower()
        )

        if identifier.normalized_value is not None:
            normalized_value = (
                identifier.normalized_value.strip().lower()
            )
        else:
            normalized_value = normalized_original_value

        return ServiceIdentifier(
            type=identifier.type,
            original_value=identifier.original_value,
            normalized_value=normalized_value,
            observation_id=identifier.observation_id,
        )

    @staticmethod
    def _determine_resolution_method(
        input_identifiers: tuple[ServiceIdentifier, ...],
        normalized_identifiers: tuple[ServiceIdentifier, ...],
    ) -> ResolutionMethod:
        normalization_changed_value = any(
            (
                input_identifier.normalized_value is not None
                and (
                    input_identifier.normalized_value
                    != input_identifier.original_value
                )
            )
            or (
                normalized_identifier.normalized_value
                != input_identifier.original_value
            )
            for (
                input_identifier,
                normalized_identifier,
            ) in zip(
                input_identifiers,
                normalized_identifiers,
            )
        )

        if normalization_changed_value:
            return ResolutionMethod.DOMAIN_NORMALIZATION

        return ResolutionMethod.EXACT_IDENTIFIER_MATCH

    @staticmethod
    def _effective_input_value(
        identifier: ServiceIdentifier,
    ) -> str:
        value = (
            identifier.normalized_value
            if identifier.normalized_value is not None
            else identifier.original_value
        )

        return value

    @staticmethod
    def _resolved_reason_code(
        method: ResolutionMethod,
    ) -> str:
        if method == ResolutionMethod.DOMAIN_NORMALIZATION:
            return "NORMALIZED_IDENTIFIER_MATCH"

        return "EXACT_IDENTIFIER_MATCH"
