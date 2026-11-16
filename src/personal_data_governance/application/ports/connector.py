from dataclasses import dataclass
from typing import Protocol

from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.source import AuthorizationState
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)
from personal_data_governance.domain.values.provider import Provider


@dataclass(frozen=True, slots=True)
class ConnectorDescriptor:
    connector_id: str
    source_type: str
    provider: Provider
    version: str


@dataclass(frozen=True, slots=True)
class Capability:
    value: str


@dataclass(frozen=True, slots=True)
class CapabilitySet:
    capabilities: tuple[Capability, ...]


@dataclass(frozen=True, slots=True)
class PermissionRequirements:
    capability: Capability
    required_permissions: tuple[str, ...]
    requires_user_authorization: bool


@dataclass(frozen=True, slots=True)
class AuthorizationStatus:
    state: AuthorizationState
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AuthorizationRequest:
    connected_source_id: ConnectedSourceId
    capability: Capability
    required_permissions: tuple[str, ...]
    explanation: str


@dataclass(frozen=True, slots=True)
class CollectionRequest:
    connected_source_id: ConnectedSourceId
    capability: Capability
    continuation: str | None = None
    limit: int | None = None


@dataclass(frozen=True, slots=True)
class CollectionResult:
    observations: tuple[Observation, ...]
    status: str
    continuation: str | None
    warnings: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DisconnectResult:
    success: bool
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()


class Connector(Protocol):

    def get_descriptor(self) -> ConnectorDescriptor:
        ...

    def get_capabilities(
        self,
        connected_source: ConnectedSource,
    ) -> CapabilitySet:
        ...

    def get_authorization_status(
        self,
        connected_source: ConnectedSource,
    ) -> AuthorizationStatus:
        ...

    def get_permission_requirements(
        self,
        connected_source: ConnectedSource,
        capability: Capability,
    ) -> PermissionRequirements:
        ...

    def prepare_authorization(
        self,
        connected_source: ConnectedSource,
        capability: Capability,
    ) -> AuthorizationRequest:
        ...

    def collect(
        self,
        request: CollectionRequest,
    ) -> CollectionResult:
        ...

    def disconnect(
        self,
        connected_source: ConnectedSource,
    ) -> DisconnectResult:
        ...
