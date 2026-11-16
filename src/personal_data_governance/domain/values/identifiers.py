from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("UserId must not be empty.")


@dataclass(frozen=True, slots=True)
class IdentitySeedId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("IdentitySeedId must not be empty.")


@dataclass(frozen=True, slots=True)
class ConnectedSourceId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ConnectedSourceId must not be empty.")


@dataclass(frozen=True, slots=True)
class ObservationId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ObservationId must not be empty.")


@dataclass(frozen=True, slots=True)
class ServiceId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("ServiceId must not be empty.")


@dataclass(frozen=True, slots=True)
class EvidenceId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("EvidenceId must not be empty.")


@dataclass(frozen=True, slots=True)
class RelationshipId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("RelationshipId must not be empty.")
