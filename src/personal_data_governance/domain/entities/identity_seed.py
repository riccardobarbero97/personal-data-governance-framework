from dataclasses import dataclass

from personal_data_governance.domain.enums.source import (
    IdentitySeedType,
    VerificationStatus,
)
from personal_data_governance.domain.values.identifiers import (
    IdentitySeedId,
    UserId,
)


@dataclass(slots=True)
class IdentitySeed:
    id: IdentitySeedId
    user_id: UserId
    type: IdentitySeedType
    value: str
    verification_status: VerificationStatus

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("IdentitySeed value must not be empty.")
