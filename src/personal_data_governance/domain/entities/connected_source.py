from dataclasses import dataclass

from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    UserId,
)
from personal_data_governance.domain.values.provider import Provider


@dataclass(slots=True)
class ConnectedSource:
    id: ConnectedSourceId
    user_id: UserId
    source_type: SourceType
    provider: Provider
    connector_id: str
    display_name: str
    external_account_reference: str | None
    connection_state: ConnectionState
    authorization_state: AuthorizationState

    def __post_init__(self) -> None:
        if not self.connector_id.strip():
            raise ValueError("Connector id must not be empty.")

        if not self.display_name.strip():
            raise ValueError(
                "ConnectedSource display name must not be empty."
            )

        if (
            self.external_account_reference is not None
            and not self.external_account_reference.strip()
        ):
            raise ValueError(
                "External account reference must not be empty."
            )
