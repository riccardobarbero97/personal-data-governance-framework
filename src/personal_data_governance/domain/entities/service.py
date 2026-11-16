from dataclasses import dataclass

from personal_data_governance.domain.values.identifiers import ServiceId


@dataclass(slots=True)
class Service:
    id: ServiceId
    canonical_name: str

    def __post_init__(self) -> None:
        if not self.canonical_name.strip():
            raise ValueError(
                "Service canonical name must not be empty."
            )
