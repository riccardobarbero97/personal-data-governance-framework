from collections.abc import Callable
from datetime import datetime, timezone
from email.utils import getaddresses
from uuid import uuid4

from personal_data_governance.application.ports.connector import (
    AuthorizationRequest,
    AuthorizationStatus,
    Capability,
    CapabilitySet,
    CollectionRequest,
    CollectionResult,
    Connector,
    ConnectorDescriptor,
    DisconnectResult,
    PermissionRequirements,
)
from personal_data_governance.connectors.gmail.api import (
    GmailApiClient,
    GmailMessageMetadata,
)
from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    SourceType,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.domain.values.identifiers import ObservationId
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import TemporalValue


GMAIL_CONNECTOR_ID = "gmail"

SERVICE_DISCOVERY_METADATA = Capability(
    "SERVICE_DISCOVERY_METADATA"
)

GMAIL_METADATA_SCOPE = (
    "https://www.googleapis.com/auth/gmail.metadata"
)

GMAIL_METADATA_HEADERS = (
    "From",
    "To",
    "Cc",
    "Subject",
)

DEFAULT_PAGE_SIZE = 100
MAX_GMAIL_PAGE_SIZE = 500


ObservationIdFactory = Callable[[], ObservationId]
Clock = Callable[[], datetime]


def default_observation_id_factory() -> ObservationId:
    return ObservationId(
        f"observation_{uuid4().hex}"
    )


def utc_clock() -> datetime:
    return datetime.now(timezone.utc)


class GmailConnector(Connector):
    def __init__(
        self,
        api_client: GmailApiClient,
        observation_id_factory: ObservationIdFactory | None = None,
        clock: Clock | None = None,
        connector_version: str = "1",
    ) -> None:
        if not connector_version.strip():
            raise ValueError(
                "Connector version must not be empty."
            )

        self._api_client = api_client

        self._observation_id_factory = (
            observation_id_factory
            if observation_id_factory is not None
            else default_observation_id_factory
        )

        self._clock = (
            clock
            if clock is not None
            else utc_clock
        )

        self._connector_version = connector_version

    def get_descriptor(self) -> ConnectorDescriptor:
        return ConnectorDescriptor(
            connector_id=GMAIL_CONNECTOR_ID,
            source_type=SourceType.EMAIL.value,
            provider=Provider(
                id="google",
                display_name="Google",
            ),
            version=self._connector_version,
        )

    def get_capabilities(
        self,
        connected_source: ConnectedSource,
    ) -> CapabilitySet:
        self._validate_connected_source(
            connected_source
        )

        return CapabilitySet(
            capabilities=(
                SERVICE_DISCOVERY_METADATA,
            )
        )

    def get_authorization_status(
        self,
        connected_source: ConnectedSource,
    ) -> AuthorizationStatus:
        self._validate_connected_source(
            connected_source
        )

        if self._api_client.is_authorized():
            return AuthorizationStatus(
                state=AuthorizationState.AUTHORIZED,
                reason_codes=(),
            )

        return AuthorizationStatus(
            state=AuthorizationState.NOT_AUTHORIZED,
            reason_codes=(
                "GMAIL_AUTHORIZATION_REQUIRED",
            ),
        )

    def get_permission_requirements(
        self,
        connected_source: ConnectedSource,
        capability: Capability,
    ) -> PermissionRequirements:
        self._validate_connected_source(
            connected_source
        )

        self._validate_capability(
            capability
        )

        return PermissionRequirements(
            capability=capability,
            required_permissions=(
                GMAIL_METADATA_SCOPE,
            ),
            requires_user_authorization=True,
        )

    def prepare_authorization(
        self,
        connected_source: ConnectedSource,
        capability: Capability,
    ) -> AuthorizationRequest:
        requirements = self.get_permission_requirements(
            connected_source=connected_source,
            capability=capability,
        )

        return AuthorizationRequest(
            connected_source_id=connected_source.id,
            capability=capability,
            required_permissions=(
                requirements.required_permissions
            ),
            explanation=(
                "Read Gmail message metadata required "
                "for service discovery. Message bodies "
                "and attachment contents are not requested."
            ),
        )

    def collect(
        self,
        request: CollectionRequest,
    ) -> CollectionResult:
        if (
            request.capability
            != SERVICE_DISCOVERY_METADATA
        ):
            return CollectionResult(
                observations=(),
                status="UNSUPPORTED",
                continuation=None,
                warnings=(),
                errors=(
                    "UNSUPPORTED_CAPABILITY",
                ),
            )

        if not self._api_client.is_authorized():
            return CollectionResult(
                observations=(),
                status="FAILED",
                continuation=request.continuation,
                warnings=(),
                errors=(
                    "GMAIL_NOT_AUTHORIZED",
                ),
            )

        page_size = self._determine_page_size(
            request.limit
        )

        try:
            page = self._api_client.list_messages(
                page_token=request.continuation,
                max_results=page_size,
            )
        except Exception as error:
            return CollectionResult(
                observations=(),
                status="FAILED",
                continuation=request.continuation,
                warnings=(),
                errors=(
                    f"GMAIL_LIST_FAILED:{type(error).__name__}",
                ),
            )

        observations: list[Observation] = []
        warnings: list[str] = []
        errors: list[str] = []

        for message_reference in page.messages:
            try:
                metadata = (
                    self._api_client.get_message_metadata(
                        message_reference.message_id
                    )
                )

                observation = (
                    self._map_message_to_observation(
                        connected_source_id=(
                            request.connected_source_id
                        ),
                        metadata=metadata,
                    )
                )

                observations.append(
                    observation
                )
            except Exception as error:
                errors.append(
                    "GMAIL_MESSAGE_COLLECTION_FAILED:"
                    f"{message_reference.message_id}:"
                    f"{type(error).__name__}"
                )

        if errors and observations:
            status = "PARTIAL"

            warnings.append(
                "ONE_OR_MORE_MESSAGES_COULD_NOT_BE_COLLECTED"
            )
        elif errors:
            status = "FAILED"
        elif page.next_page_token is not None:
            status = "PARTIAL"

            warnings.append(
                "ADDITIONAL_GMAIL_PAGE_AVAILABLE"
            )
        else:
            status = "COMPLETE"

        return CollectionResult(
            observations=tuple(
                observations
            ),
            status=status,
            continuation=page.next_page_token,
            warnings=tuple(
                warnings
            ),
            errors=tuple(
                errors
            ),
        )

    def disconnect(
        self,
        connected_source: ConnectedSource,
    ) -> DisconnectResult:
        self._validate_connected_source(
            connected_source
        )

        try:
            self._api_client.disconnect()
        except Exception as error:
            return DisconnectResult(
                success=False,
                warnings=(),
                errors=(
                    "GMAIL_DISCONNECT_FAILED:"
                    f"{type(error).__name__}",
                ),
            )

        return DisconnectResult(
            success=True,
            warnings=(),
            errors=(),
        )

    def _map_message_to_observation(
        self,
        connected_source_id,
        metadata: GmailMessageMetadata,
    ) -> Observation:
        sender = metadata.get_header(
            "From"
        )

        recipients = self._extract_recipients(
            metadata
        )

        subject = metadata.get_header(
            "Subject"
        )

        observed_at = self._map_internal_date(
            metadata.internal_date_milliseconds
        )

        return Observation(
            id=self._observation_id_factory(),
            connected_source_id=(
                connected_source_id
            ),
            observation_type=(
                ObservationType.EMAIL_MESSAGE_METADATA
            ),
            schema_version=SchemaVersion(1),
            source_reference=SourceReference(
                metadata.message_id
            ),
            observed_at=observed_at,
            collected_at=self._clock(),
            payload=EmailMessageMetadataV1(
                sender=sender,
                recipients=recipients,
                subject=subject,
                thread_reference=metadata.thread_id,
                labels=tuple(
                    metadata.label_ids
                ),
            ),
        )

    @staticmethod
    def _extract_recipients(
        metadata: GmailMessageMetadata,
    ) -> tuple[str, ...]:
        raw_values = (
            metadata.get_all_headers("To")
            + metadata.get_all_headers("Cc")
        )

        parsed_addresses = getaddresses(
            raw_values
        )

        recipients: dict[str, str] = {}

        for _, address in parsed_addresses:
            normalized = address.strip().lower()

            if normalized:
                recipients[
                    normalized
                ] = normalized

        return tuple(
            recipients[key]
            for key in sorted(
                recipients
            )
        )

    @staticmethod
    def _map_internal_date(
        internal_date_milliseconds: int | None,
    ) -> TemporalValue | None:
        if internal_date_milliseconds is None:
            return None

        timestamp = datetime.fromtimestamp(
            internal_date_milliseconds / 1000,
            tz=timezone.utc,
        )

        return TemporalValue(
            timestamp=timestamp,
            semantics=TemporalSemantics.MESSAGE_TIME,
        )

    @staticmethod
    def _determine_page_size(
        requested_limit: int | None,
    ) -> int:
        if requested_limit is None:
            return DEFAULT_PAGE_SIZE

        if requested_limit < 1:
            raise ValueError(
                "Collection limit must be "
                "greater than or equal to one."
            )

        return min(
            requested_limit,
            MAX_GMAIL_PAGE_SIZE,
        )

    @staticmethod
    def _validate_capability(
        capability: Capability,
    ) -> None:
        if capability != SERVICE_DISCOVERY_METADATA:
            raise ValueError(
                "Unsupported Gmail capability: "
                f"{capability.value}"
            )

    @staticmethod
    def _validate_connected_source(
        connected_source: ConnectedSource,
    ) -> None:
        if (
            connected_source.source_type
            != SourceType.EMAIL
        ):
            raise ValueError(
                "GmailConnector requires "
                "an EMAIL ConnectedSource."
            )

        if (
            connected_source.provider.id
            != "google"
        ):
            raise ValueError(
                "GmailConnector requires "
                "the Google Provider."
            )

        if (
            connected_source.connector_id
            != GMAIL_CONNECTOR_ID
        ):
            raise ValueError(
                "ConnectedSource connector id "
                "does not match GmailConnector."
            )
