from personal_data_governance.application.values.candidate_identifier import (
    CandidateIdentifier,
)
from personal_data_governance.domain.enums.processing import (
    CandidateIdentifierType,
    ServiceIdentifierType,
)
from personal_data_governance.domain.values.identifiers import ObservationId
from personal_data_governance.domain.values.service_identifier import (
    ServiceIdentifier,
)


_CANDIDATE_TO_SERVICE_IDENTIFIER_TYPE: dict[
    CandidateIdentifierType,
    ServiceIdentifierType,
] = {
    CandidateIdentifierType.EMAIL_DOMAIN: (
        ServiceIdentifierType.EMAIL_DOMAIN
    ),
    CandidateIdentifierType.DOMAIN: (
        ServiceIdentifierType.DOMAIN
    ),
    CandidateIdentifierType.HOSTNAME: (
        ServiceIdentifierType.HOSTNAME
    ),
}


def materialize_service_identifier(
    candidate_identifier: CandidateIdentifier,
    observation_id: ObservationId,
) -> ServiceIdentifier:
    service_identifier_type = (
        _CANDIDATE_TO_SERVICE_IDENTIFIER_TYPE.get(
            candidate_identifier.type
        )
    )

    if service_identifier_type is None:
        raise ValueError(
            "Unsupported CandidateIdentifierType: "
            f"{candidate_identifier.type}"
        )

    return ServiceIdentifier(
        type=service_identifier_type,
        original_value=candidate_identifier.value,
        observation_id=observation_id,
    )


def materialize_service_identifiers(
    candidate_identifiers: tuple[CandidateIdentifier, ...],
    observation_id: ObservationId,
) -> tuple[ServiceIdentifier, ...]:
    return tuple(
        materialize_service_identifier(
            candidate_identifier=candidate_identifier,
            observation_id=observation_id,
        )
        for candidate_identifier in candidate_identifiers
    )
