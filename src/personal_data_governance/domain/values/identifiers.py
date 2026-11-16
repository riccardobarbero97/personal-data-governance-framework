from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserId:
    value: str


@dataclass(frozen=True, slots=True)
class IdentitySeedId:
    value: str


@dataclass(frozen=True, slots=True)
class ConnectedSourceId:
    value: str


@dataclass(frozen=True, slots=True)
class ObservationId:
    value: str


@dataclass(frozen=True, slots=True)
class ServiceId:
    value: str


@dataclass(frozen=True, slots=True)
class EvidenceId:
    value: str


@dataclass(frozen=True, slots=True)
class RelationshipId:
    value: str
