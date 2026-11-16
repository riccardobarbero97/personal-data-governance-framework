from dataclasses import dataclass

from personal_data_governance.domain.enums.evidence import (
    EvidenceStatus,
    EvidenceType,
)
from personal_data_governance.domain.enums.processing import (
    ClassificationMethod,
)
from personal_data_governance.domain.values.identifiers import (
    EvidenceId,
    IdentitySeedId,
    ObservationId,
    ServiceId,
)


@dataclass(slots=True)
class Evidence:
    id: EvidenceId
    evidence_type: EvidenceType
    evidence_status: EvidenceStatus
    observation_ids: tuple[ObservationId, ...]
    service_id: ServiceId | None
    identity_seed_ids: tuple[IdentitySeedId, ...]
    classification_method: ClassificationMethod
    classifier_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.observation_ids:
            raise ValueError(
                "Evidence must reference at least one Observation."
            )

        if not self.classifier_version.strip():
            raise ValueError(
                "Classifier version must not be empty."
            )
