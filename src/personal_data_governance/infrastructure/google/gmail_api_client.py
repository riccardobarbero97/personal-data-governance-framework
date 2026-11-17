import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from personal_data_governance.application.ports.credential_store import (
    CredentialMaterial,
    CredentialStore,
)
from personal_data_governance.connectors.gmail.api import (
    GmailApiClient,
    GmailMessageMetadata,
    GmailMessagePage,
    GmailMessageReference,
)
from personal_data_governance.connectors.gmail.connector import (
    GMAIL_METADATA_HEADERS,
    GMAIL_METADATA_SCOPE,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)


GoogleServiceFactory = Callable[
    [Credentials],
    Any,
]


def default_google_service_factory(
    credentials: Credentials,
) -> Any:
    return build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )


class GoogleGmailApiClient(GmailApiClient):
    def __init__(
        self,
        connected_source_id: ConnectedSourceId,
        credential_store: CredentialStore,
        client_secrets_file: Path,
        service_factory: GoogleServiceFactory | None = None,
    ) -> None:
        self._connected_source_id = connected_source_id
        self._credential_store = credential_store
        self._client_secrets_file = client_secrets_file

        self._service_factory = (
            service_factory
            if service_factory is not None
            else default_google_service_factory
        )

        self._credentials: Credentials | None = None
        self._service: Any | None = None

    def is_authorized(self) -> bool:
        credentials = self._load_credentials()

        if credentials is None:
            return False

        if (
            credentials.expired
            and credentials.refresh_token
        ):
            try:
                credentials.refresh(
                    Request()
                )
            except Exception:
                return False

            self._save_credentials(
                credentials
            )

        return bool(
            credentials.valid
        )

    def authorize(self) -> None:
        credentials = self._load_credentials()

        if (
            credentials is not None
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(
                Request()
            )

            self._credentials = credentials
            self._save_credentials(
                credentials
            )

            return

        if (
            credentials is not None
            and credentials.valid
        ):
            self._credentials = credentials
            return

        if not self._client_secrets_file.exists():
            raise FileNotFoundError(
                "Google OAuth client secrets file not found: "
                f"{self._client_secrets_file}"
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(
                self._client_secrets_file
            ),
            scopes=[
                GMAIL_METADATA_SCOPE,
            ],
        )

        credentials = flow.run_local_server(
            host="127.0.0.1",
            port=0,
            open_browser=True,
            authorization_prompt_message=(
                "Open this URL in your browser "
                "to authorize Gmail metadata access: {url}"
            ),
            success_message=(
                "Gmail authorization completed. "
                "You may close this browser window."
            ),
        )

        self._credentials = credentials

        self._save_credentials(
            credentials
        )

        self._service = None

    def list_messages(
        self,
        page_token: str | None,
        max_results: int,
    ) -> GmailMessagePage:
        service = self._get_service()

        request_arguments: dict[
            str,
            Any,
        ] = {
            "userId": "me",
            "maxResults": max_results,
            "includeSpamTrash": False,
        }

        if page_token is not None:
            request_arguments[
                "pageToken"
            ] = page_token

        response = (
            service.users()
            .messages()
            .list(
                **request_arguments
            )
            .execute()
        )

        raw_messages = response.get(
            "messages",
            [],
        )

        messages = tuple(
            GmailMessageReference(
                message_id=raw_message["id"],
                thread_id=raw_message.get(
                    "threadId"
                ),
            )
            for raw_message in raw_messages
            if raw_message.get("id")
        )

        return GmailMessagePage(
            messages=messages,
            next_page_token=response.get(
                "nextPageToken"
            ),
        )

    def get_message_metadata(
        self,
        message_id: str,
    ) -> GmailMessageMetadata:
        if not message_id.strip():
            raise ValueError(
                "Gmail message id must not be empty."
            )

        service = self._get_service()

        response = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=list(
                    GMAIL_METADATA_HEADERS
                ),
            )
            .execute()
        )

        payload = response.get(
            "payload",
            {},
        )

        raw_headers = payload.get(
            "headers",
            [],
        )

        headers = tuple(
            (
                raw_header["name"],
                raw_header["value"],
            )
            for raw_header in raw_headers
            if (
                raw_header.get("name")
                and raw_header.get("value")
                is not None
            )
        )

        raw_internal_date = response.get(
            "internalDate"
        )

        internal_date_milliseconds = (
            int(raw_internal_date)
            if raw_internal_date is not None
            else None
        )

        return GmailMessageMetadata(
            message_id=response.get(
                "id",
                message_id,
            ),
            thread_id=response.get(
                "threadId"
            ),
            internal_date_milliseconds=(
                internal_date_milliseconds
            ),
            label_ids=tuple(
                response.get(
                    "labelIds",
                    [],
                )
            ),
            headers=headers,
        )

    def disconnect(self) -> None:
        self._credential_store.delete(
            self._connected_source_id
        )

        self._credentials = None
        self._service = None

    def _get_service(self) -> Any:
        credentials = self._require_credentials()

        if self._service is None:
            self._service = (
                self._service_factory(
                    credentials
                )
            )

        return self._service

    def _require_credentials(
        self,
    ) -> Credentials:
        credentials = self._load_credentials()

        if credentials is None:
            raise PermissionError(
                "Gmail authorization is required."
            )

        if (
            credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(
                Request()
            )

            self._save_credentials(
                credentials
            )

        if not credentials.valid:
            raise PermissionError(
                "Stored Gmail credentials are not valid."
            )

        self._credentials = credentials

        return credentials

    def _load_credentials(
        self,
    ) -> Credentials | None:
        if self._credentials is not None:
            return self._credentials

        credential_material = (
            self._credential_store.load(
                self._connected_source_id
            )
        )

        if credential_material is None:
            return None

        credential_data = json.loads(
            credential_material.value
        )

        credentials = Credentials.from_authorized_user_info(
            credential_data,
            scopes=[
                GMAIL_METADATA_SCOPE,
            ],
        )

        self._credentials = credentials

        return credentials

    def _save_credentials(
        self,
        credentials: Credentials,
    ) -> None:
        serialized_credentials = credentials.to_json()

        self._credential_store.save(
            connected_source_id=(
                self._connected_source_id
            ),
            credential=CredentialMaterial(
                value=serialized_credentials
            ),
        )
