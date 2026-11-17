from datetime import datetime, timezone

from personal_data_governance.application.ports.connector import (
    Capability,
    CollectionRequest,
)
from personal_data_governance.connectors.gmail.api import (
    GmailMessageMetadata,
    GmailMessagePage,
    GmailMessageReference,
)
from personal_data_governance.connectors.gmail.connector import (
    GMAIL_METADATA_SCOPE,
    SERVICE_DISCOVERY_METADATA,
    GmailConnector,
)
from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.enums.observation import (
    ObservationType,
    TemporalSemantics,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
    UserId,
)
from personal_data_governance.domain.values.provider import Provider


FIXED_TIME = datetime(
    2026,
    11,
    17,
    8,
    30,
    tzinfo=timezone.utc,
)


class SequentialObservationIdFactory:
    def __init__(self) -> None:
        self._counter = 0

    def __call__(self) -> ObservationId:
        self._counter += 1

        return ObservationId(
            f"observation_{self._counter:03d}"
        )


class FakeGmailApiClient:
    def __init__(
        self,
        authorized: bool = True,
        page: GmailMessagePage | None = None,
        metadata_by_id: dict[
            str,
            GmailMessageMetadata,
        ] | None = None,
    ) -> None:
        self.authorized = authorized

        self.page = (
            page
            if page is not None
            else GmailMessagePage(
                messages=(),
                next_page_token=None,
            )
        )

        self.metadata_by_id = (
            metadata_by_id
            if metadata_by_id is not None
            else {}
        )

        self.last_page_token: str | None = None
        self.last_max_results: int | None = None
        self.disconnected = False

    def is_authorized(self) -> bool:
        return self.authorized

    def list_messages(
        self,
        page_token: str | None,
        max_results: int,
    ) -> GmailMessagePage:
        self.last_page_token = page_token
        self.last_max_results = max_results

        return self.page

    def get_message_metadata(
        self,
        message_id: str,
    ) -> GmailMessageMetadata:
        return self.metadata_by_id[
            message_id
        ]

    def disconnect(self) -> None:
        self.disconnected = True
        self.authorized = False


def build_connected_source() -> ConnectedSource:
    return ConnectedSource(
        id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        user_id=UserId("user_001"),
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="google",
            display_name="Google",
        ),
        connector_id="gmail",
        display_name="Personal Gmail",
        external_account_reference=(
            "user@example.com"
        ),
        connection_state=ConnectionState.CONNECTED,
        authorization_state=(
            AuthorizationState.AUTHORIZED
        ),
    )


def build_connector(
    api_client: FakeGmailApiClient,
) -> GmailConnector:
    return GmailConnector(
        api_client=api_client,
        observation_id_factory=(
            SequentialObservationIdFactory()
        ),
        clock=lambda: FIXED_TIME,
        connector_version="1",
    )


def test_descriptor_is_provider_specific() -> None:
    connector = build_connector(
        FakeGmailApiClient()
    )

    descriptor = connector.get_descriptor()

    assert descriptor.connector_id == "gmail"
    assert descriptor.source_type == "EMAIL"
    assert descriptor.provider == Provider(
        id="google",
        display_name="Google",
    )
    assert descriptor.version == "1"


def test_connector_exposes_metadata_capability() -> None:
    connector = build_connector(
        FakeGmailApiClient()
    )

    capabilities = connector.get_capabilities(
        build_connected_source()
    )

    assert capabilities.capabilities == (
        SERVICE_DISCOVERY_METADATA,
    )


def test_connector_requires_only_metadata_scope() -> None:
    connector = build_connector(
        FakeGmailApiClient()
    )

    requirements = (
        connector.get_permission_requirements(
            connected_source=build_connected_source(),
            capability=SERVICE_DISCOVERY_METADATA,
        )
    )

    assert requirements.required_permissions == (
        GMAIL_METADATA_SCOPE,
    )

    assert requirements.requires_user_authorization is True


def test_authorization_request_explains_data_minimization() -> None:
    connector = build_connector(
        FakeGmailApiClient()
    )

    request = connector.prepare_authorization(
        connected_source=build_connected_source(),
        capability=SERVICE_DISCOVERY_METADATA,
    )

    assert request.required_permissions == (
        GMAIL_METADATA_SCOPE,
    )

    assert "metadata" in request.explanation.lower()
    assert "message bodies" in request.explanation.lower()
    assert "attachment" in request.explanation.lower()


def test_unauthorized_client_is_reported() -> None:
    connector = build_connector(
        FakeGmailApiClient(
            authorized=False
        )
    )

    status = connector.get_authorization_status(
        build_connected_source()
    )

    assert (
        status.state
        == AuthorizationState.NOT_AUTHORIZED
    )

    assert status.reason_codes == (
        "GMAIL_AUTHORIZATION_REQUIRED",
    )


def test_metadata_is_mapped_to_observation() -> None:
    page = GmailMessagePage(
        messages=(
            GmailMessageReference(
                message_id="gmail_message_001",
                thread_id="gmail_thread_001",
            ),
        ),
        next_page_token=None,
    )

    metadata = GmailMessageMetadata(
        message_id="gmail_message_001",
        thread_id="gmail_thread_001",
        internal_date_milliseconds=(
            1763366400000
        ),
        label_ids=(
            "INBOX",
            "CATEGORY_UPDATES",
        ),
        headers=(
            (
                "From",
                "Spotify <no-reply@spotify.com>",
            ),
            (
                "To",
                "User <user@example.com>",
            ),
            (
                "Subject",
                "Verify your email address",
            ),
        ),
    )

    api_client = FakeGmailApiClient(
        page=page,
        metadata_by_id={
            "gmail_message_001": metadata,
        },
    )

    connector = build_connector(
        api_client
    )

    result = connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=SERVICE_DISCOVERY_METADATA,
            limit=100,
        )
    )

    assert result.status == "COMPLETE"
    assert result.continuation is None
    assert result.errors == ()
    assert len(result.observations) == 1

    observation = result.observations[0]

    assert observation.id == ObservationId(
        "observation_001"
    )

    assert (
        observation.connected_source_id
        == ConnectedSourceId(
            "source_gmail_personal"
        )
    )

    assert (
        observation.observation_type
        == ObservationType.EMAIL_MESSAGE_METADATA
    )

    assert (
        observation.source_reference.value
        == "gmail_message_001"
    )

    assert observation.observed_at is not None

    assert (
        observation.observed_at.semantics
        == TemporalSemantics.MESSAGE_TIME
    )

    assert observation.collected_at == FIXED_TIME

    assert (
        observation.payload.sender
        == "Spotify <no-reply@spotify.com>"
    )

    assert observation.payload.recipients == (
        "user@example.com",
    )

    assert (
        observation.payload.subject
        == "Verify your email address"
    )

    assert (
        observation.payload.thread_reference
        == "gmail_thread_001"
    )

    assert observation.payload.labels == (
        "INBOX",
        "CATEGORY_UPDATES",
    )


def test_to_and_cc_recipients_are_combined() -> None:
    page = GmailMessagePage(
        messages=(
            GmailMessageReference(
                message_id="gmail_message_001",
                thread_id=None,
            ),
        ),
        next_page_token=None,
    )

    metadata = GmailMessageMetadata(
        message_id="gmail_message_001",
        thread_id=None,
        internal_date_milliseconds=None,
        label_ids=(),
        headers=(
            (
                "From",
                "no-reply@spotify.com",
            ),
            (
                "To",
                "User <user@example.com>",
            ),
            (
                "Cc",
                "Other <other@example.com>, "
                "USER@example.com",
            ),
            (
                "Subject",
                "Payment successful",
            ),
        ),
    )

    connector = build_connector(
        FakeGmailApiClient(
            page=page,
            metadata_by_id={
                "gmail_message_001": metadata,
            },
        )
    )

    result = connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=SERVICE_DISCOVERY_METADATA,
        )
    )

    recipients = (
        result.observations[0]
        .payload
        .recipients
    )

    assert recipients == (
        "other@example.com",
        "user@example.com",
    )


def test_next_page_is_returned_as_continuation() -> None:
    api_client = FakeGmailApiClient(
        page=GmailMessagePage(
            messages=(),
            next_page_token="next_page_001",
        )
    )

    connector = build_connector(
        api_client
    )

    result = connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=SERVICE_DISCOVERY_METADATA,
            continuation="current_page",
            limit=50,
        )
    )

    assert result.status == "PARTIAL"

    assert result.continuation == (
        "next_page_001"
    )

    assert (
        "ADDITIONAL_GMAIL_PAGE_AVAILABLE"
        in result.warnings
    )

    assert (
        api_client.last_page_token
        == "current_page"
    )

    assert api_client.last_max_results == 50


def test_page_size_is_capped_at_gmail_maximum() -> None:
    api_client = FakeGmailApiClient()

    connector = build_connector(
        api_client
    )

    connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=SERVICE_DISCOVERY_METADATA,
            limit=1000,
        )
    )

    assert api_client.last_max_results == 500


def test_unauthorized_collection_fails_without_api_call() -> None:
    api_client = FakeGmailApiClient(
        authorized=False
    )

    connector = build_connector(
        api_client
    )

    result = connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=SERVICE_DISCOVERY_METADATA,
        )
    )

    assert result.status == "FAILED"
    assert result.observations == ()

    assert result.errors == (
        "GMAIL_NOT_AUTHORIZED",
    )

    assert api_client.last_max_results is None


def test_one_failed_message_produces_partial_result() -> None:
    page = GmailMessagePage(
        messages=(
            GmailMessageReference(
                message_id="gmail_message_good",
                thread_id=None,
            ),
            GmailMessageReference(
                message_id="gmail_message_missing",
                thread_id=None,
            ),
        ),
        next_page_token=None,
    )

    metadata = GmailMessageMetadata(
        message_id="gmail_message_good",
        thread_id=None,
        internal_date_milliseconds=None,
        label_ids=(),
        headers=(
            (
                "From",
                "no-reply@spotify.com",
            ),
            (
                "Subject",
                "Verify your email address",
            ),
        ),
    )

    connector = build_connector(
        FakeGmailApiClient(
            page=page,
            metadata_by_id={
                "gmail_message_good": metadata,
            },
        )
    )

    result = connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=SERVICE_DISCOVERY_METADATA,
        )
    )

    assert result.status == "PARTIAL"
    assert len(result.observations) == 1
    assert len(result.errors) == 1

    assert (
        "ONE_OR_MORE_MESSAGES_COULD_NOT_BE_COLLECTED"
        in result.warnings
    )


def test_unsupported_capability_is_rejected() -> None:
    connector = build_connector(
        FakeGmailApiClient()
    )

    result = connector.collect(
        CollectionRequest(
            connected_source_id=(
                ConnectedSourceId(
                    "source_gmail_personal"
                )
            ),
            capability=Capability(
                "EMAIL_MESSAGE_CONTENT"
            ),
        )
    )

    assert result.status == "UNSUPPORTED"
    assert result.observations == ()

    assert result.errors == (
        "UNSUPPORTED_CAPABILITY",
    )


def test_disconnect_delegates_to_api_client() -> None:
    api_client = FakeGmailApiClient()

    connector = build_connector(
        api_client
    )

    result = connector.disconnect(
        build_connected_source()
    )

    assert result.success is True
    assert api_client.disconnected is True
    assert api_client.authorized is False
