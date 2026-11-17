from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials

from personal_data_governance.application.ports.credential_store import (
    CredentialMaterial,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)
from personal_data_governance.infrastructure.google.gmail_api_client import (
    GoogleGmailApiClient,
)


class InMemoryCredentialStore:
    def __init__(self) -> None:
        self.material: CredentialMaterial | None = None
        self.deleted = False

    def load(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> CredentialMaterial | None:
        return self.material

    def save(
        self,
        connected_source_id: ConnectedSourceId,
        credential: CredentialMaterial,
    ) -> None:
        self.material = credential

    def delete(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> None:
        self.material = None
        self.deleted = True


class FakeExecutableRequest:
    def __init__(
        self,
        response: dict[str, Any],
    ) -> None:
        self._response = response

    def execute(self) -> dict[str, Any]:
        return self._response


class FakeMessagesResource:
    def __init__(self) -> None:
        self.last_list_arguments: dict[
            str,
            Any,
        ] | None = None

        self.last_get_arguments: dict[
            str,
            Any,
        ] | None = None

    def list(
        self,
        **arguments: Any,
    ) -> FakeExecutableRequest:
        self.last_list_arguments = arguments

        return FakeExecutableRequest(
            {
                "messages": [
                    {
                        "id": "message_001",
                        "threadId": "thread_001",
                    }
                ],
                "nextPageToken": "next_001",
            }
        )

    def get(
        self,
        **arguments: Any,
    ) -> FakeExecutableRequest:
        self.last_get_arguments = arguments

        return FakeExecutableRequest(
            {
                "id": "message_001",
                "threadId": "thread_001",
                "internalDate": "1763366400000",
                "labelIds": [
                    "INBOX",
                ],
                "payload": {
                    "headers": [
                        {
                            "name": "From",
                            "value": (
                                "Spotify "
                                "<no-reply@spotify.com>"
                            ),
                        },
                        {
                            "name": "Subject",
                            "value": (
                                "Verify your email address"
                            ),
                        },
                    ]
                },
            }
        )


class FakeUsersResource:
    def __init__(
        self,
        messages_resource: FakeMessagesResource,
    ) -> None:
        self._messages_resource = messages_resource

    def messages(
        self,
    ) -> FakeMessagesResource:
        return self._messages_resource


class FakeGoogleService:
    def __init__(
        self,
        messages_resource: FakeMessagesResource,
    ) -> None:
        self._users_resource = FakeUsersResource(
            messages_resource
        )

    def users(
        self,
    ) -> FakeUsersResource:
        return self._users_resource


def build_valid_credentials() -> Credentials:
    return Credentials(
        token="access_token",
        refresh_token="refresh_token",
        token_uri=(
            "https://oauth2.googleapis.com/token"
        ),
        client_id="client_id",
        client_secret="client_secret",
        scopes=[
            (
                "https://www.googleapis.com/"
                "auth/gmail.metadata"
            )
        ],
    )


def test_list_messages_maps_google_response() -> None:
    credential_store = InMemoryCredentialStore()

    messages_resource = FakeMessagesResource()

    google_service = FakeGoogleService(
        messages_resource
    )

    client = GoogleGmailApiClient(
        connected_source_id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        credential_store=credential_store,
        client_secrets_file=Path(
            "credentials.json"
        ),
        service_factory=lambda credentials: (
            google_service
        ),
    )

    client._credentials = build_valid_credentials()

    page = client.list_messages(
        page_token="page_001",
        max_results=50,
    )

    assert len(page.messages) == 1

    assert (
        page.messages[0].message_id
        == "message_001"
    )

    assert (
        page.messages[0].thread_id
        == "thread_001"
    )

    assert page.next_page_token == "next_001"

    assert messages_resource.last_list_arguments == {
        "userId": "me",
        "maxResults": 50,
        "includeSpamTrash": False,
        "pageToken": "page_001",
    }


def test_get_metadata_uses_metadata_format() -> None:
    credential_store = InMemoryCredentialStore()

    messages_resource = FakeMessagesResource()

    google_service = FakeGoogleService(
        messages_resource
    )

    client = GoogleGmailApiClient(
        connected_source_id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        credential_store=credential_store,
        client_secrets_file=Path(
            "credentials.json"
        ),
        service_factory=lambda credentials: (
            google_service
        ),
    )

    client._credentials = build_valid_credentials()

    metadata = client.get_message_metadata(
        "message_001"
    )

    assert metadata.message_id == "message_001"
    assert metadata.thread_id == "thread_001"

    assert (
        metadata.internal_date_milliseconds
        == 1763366400000
    )

    assert metadata.label_ids == (
        "INBOX",
    )

    assert metadata.get_header(
        "From"
    ) == (
        "Spotify <no-reply@spotify.com>"
    )

    assert metadata.get_header(
        "Subject"
    ) == "Verify your email address"

    assert (
        messages_resource.last_get_arguments
        is not None
    )

    assert (
        messages_resource.last_get_arguments[
            "format"
        ]
        == "metadata"
    )

    assert (
        messages_resource.last_get_arguments[
            "userId"
        ]
        == "me"
    )


def test_disconnect_deletes_local_credentials() -> None:
    credential_store = InMemoryCredentialStore()

    credential_store.material = CredentialMaterial(
        value='{"token": "example"}'
    )

    client = GoogleGmailApiClient(
        connected_source_id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        credential_store=credential_store,
        client_secrets_file=Path(
            "credentials.json"
        ),
    )

    client.disconnect()

    assert credential_store.deleted is True
    assert credential_store.material is None
