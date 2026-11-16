from dataclasses import dataclass

from personal_data_governance.domain.enums.processing import (
    CandidateIdentifierType,
)


@dataclass(frozen=True, slots=True)
class CandidateIdentifier:
    type: CandidateIdentifierType
    value: str
    source_attribute: str | None = None

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError(
                "CandidateIdentifier value must not be empty."
            )
