import json
from pathlib import Path
from typing import Any

from personal_data_governance.connectors.gmail.api import (
    GmailApiClient,
    GmailMessageMetadata,
    GmailMessagePage,
    GmailMessageReference,
)


class OfflineGmailApiClient(GmailApiClient):
    def __init__(
        self,
        fixture_file: Path,
    ) -> None:
        self._fixture_file = fixture_file
        self._authorized = True
        self._messages = self._load_messages(
            fixture_file
        )

    def is_authorized(self) -> bool:
        return self._authorized

    def list_messages(
        self,
        page_token: str | None,
        max_results: int,
    ) -> GmailMessagePage:
        if not self._authorized:
            raise PermissionError(
                "Offline Gmail client is disconnected."
            )

        if max_results < 1:
            raise ValueError(
                "Maximum results must be at least one."
            )

        start_index = self._parse_page_token(
            page_token
        )

        end_index = min(
            start_index + max_results,
            len(self._messages),
        )

        selected_messages = self._messages[
            start_index:end_index
        ]

        references = tuple(
            GmailMessageReference(
                message_id=message.message_id,
                thread_id=message.thread_id,
            )
            for message in selected_messages
        )

        next_page_token = (
            str(end_index)
            if end_index < len(self._messages)
            else None
        )

        return GmailMessagePage(
            messages=references,
            next_page_token=next_page_token,
        )

    def get_message_metadata(
        self,
        message_id: str,
    ) -> GmailMessageMetadata:
        if not self._authorized:
            raise PermissionError(
                "Offline Gmail client is disconnected."
            )

        for message in self._messages:
            if message.message_id == message_id:
                return message

        raise KeyError(
            f"Offline Gmail message not found: {message_id}"
        )

    def disconnect(self) -> None:
        self._authorized = False

    @staticmethod
    def _parse_page_token(
        page_token: str | None,
    ) -> int:
        if page_token is None:
            return 0

        try:
            start_index = int(
                page_token
            )
        except ValueError as error:
            raise ValueError(
                "Offline Gmail page token "
                "must be an integer offset."
            ) from error

        if start_index < 0:
            raise ValueError(
                "Offline Gmail page token "
                "must not be negative."
            )

        return start_index

    @staticmethod
    def _load_messages(
        fixture_file: Path,
    ) -> tuple[GmailMessageMetadata, ...]:
        if not fixture_file.exists():
            raise FileNotFoundError(
                "Offline Gmail fixture not found: "
                f"{fixture_file}"
            )

        fixture_data = json.loads(
            fixture_file.read_text(
                encoding="utf-8"
            )
        )

        if fixture_data.get("synthetic_data") is not True:
            raise ValueError(
                "Offline fixture must be explicitly "
                "marked as synthetic data."
            )

        raw_messages = fixture_data.get(
            "messages"
        )

        if not isinstance(
            raw_messages,
            list,
        ):
            raise ValueError(
                "Offline fixture messages "
                "must be a list."
            )

        messages: list[
            GmailMessageMetadata
        ] = []

        seen_message_ids: set[str] = set()

        for raw_message in raw_messages:
            if not isinstance(
                raw_message,
                dict,
            ):
                raise ValueError(
                    "Every offline Gmail message "
                    "must be an object."
                )

            message = (
                OfflineGmailApiClient
                ._map_message(
                    raw_message
                )
            )

            if (
                message.message_id
                in seen_message_ids
            ):
                raise ValueError(
                    "Duplicate offline Gmail message id: "
                    f"{message.message_id}"
                )

            seen_message_ids.add(
                message.message_id
            )

            messages.append(
                message
            )

        return tuple(
            messages
        )

    @staticmethod
    def _map_message(
        raw_message: dict[str, Any],
    ) -> GmailMessageMetadata:
        message_id = raw_message.get(
            "message_id"
        )

        if not isinstance(
            message_id,
            str,
        ):
            raise ValueError(
                "Offline Gmail message_id "
                "must be a string."
            )

        thread_id = raw_message.get(
            "thread_id"
        )

        if (
            thread_id is not None
            and not isinstance(thread_id, str)
        ):
            raise ValueError(
                "Offline Gmail thread_id "
                "must be a string or null."
            )

        internal_date = raw_message.get(
            "internal_date_milliseconds"
        )

        if (
            internal_date is not None
            and not isinstance(internal_date, int)
        ):
            raise ValueError(
                "Offline Gmail internal date "
                "must be an integer or null."
            )

        raw_label_ids = raw_message.get(
            "label_ids",
            [],
        )

        if not isinstance(
            raw_label_ids,
            list,
        ):
            raise ValueError(
                "Offline Gmail label_ids "
                "must be a list."
            )

        raw_headers = raw_message.get(
            "headers",
            [],
        )

        if not isinstance(
            raw_headers,
            list,
        ):
            raise ValueError(
                "Offline Gmail headers "
                "must be a list."
            )

        headers: list[
            tuple[str, str]
        ] = []

        for raw_header in raw_headers:
            if not isinstance(
                raw_header,
                dict,
            ):
                raise ValueError(
                    "Offline Gmail header "
                    "must be an object."
                )

            header_name = raw_header.get(
                "name"
            )

            header_value = raw_header.get(
                "value"
            )

            if not isinstance(
                header_name,
                str,
            ):
                raise ValueError(
                    "Offline Gmail header name "
                    "must be a string."
                )

            if not isinstance(
                header_value,
                str,
            ):
                raise ValueError(
                    "Offline Gmail header value "
                    "must be a string."
                )

            headers.append(
                (
                    header_name,
                    header_value,
                )
            )

        return GmailMessageMetadata(
            message_id=message_id,
            thread_id=thread_id,
            internal_date_milliseconds=(
                internal_date
            ),
            label_ids=tuple(
                str(label_id)
                for label_id in raw_label_ids
            ),
            headers=tuple(
                headers
            ),
        )
