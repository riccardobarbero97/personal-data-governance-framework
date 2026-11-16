from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)


@dataclass(frozen=True, slots=True)
class CredentialMaterial:
    value: str


class CredentialStore(Protocol):

    def load(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> CredentialMaterial | None:
        ...

    def save(
        self,
        connected_source_id: ConnectedSourceId,
        credential: CredentialMaterial,
    ) -> None:
        ...

    def delete(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> None:
        ...
