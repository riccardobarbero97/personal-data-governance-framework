from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class GmailMessageReference:
    message_id: str
    thread_id: str | None

    def __post_init__(self) -> None:
        if not self.message_id.strip():
            raise ValueError(
                "Gmail message id must not be empty."
            )


@dataclass(frozen=True, slots=True)
class GmailMessagePage:
    messages: tuple[GmailMessageReference, ...]
    next_page_token: str | None


@dataclass(frozen=True, slots=True)
class GmailMessageMetadata:
    message_id: str
    thread_id: str | None
    internal_date_milliseconds: int | None
    label_ids: tuple[str, ...]
    headers: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        if not self.message_id.strip():
            raise ValueError(
                "Gmail message id must not be empty."
            )

        if (
            self.internal_date_milliseconds is not None
            and self.internal_date_milliseconds < 0
        ):
            raise ValueError(
                "Gmail internal date must not be negative."
            )

    def get_header(
        self,
        name: str,
    ) -> str | None:
        normalized_name = name.strip().lower()

        for header_name, header_value in self.headers:
            if header_name.strip().lower() == normalized_name:
                return header_value

        return None

    def get_all_headers(
        self,
        name: str,
    ) -> tuple[str, ...]:
        normalized_name = name.strip().lower()

        return tuple(
            header_value
            for header_name, header_value in self.headers
            if header_name.strip().lower() == normalized_name
        )


class GmailApiClient(Protocol):

    def is_authorized(self) -> bool:
        ...

    def list_messages(
        self,
        page_token: str | None,
        max_results: int,
    ) -> GmailMessagePage:
        ...

    def get_message_metadata(
        self,
        message_id: str,
    ) -> GmailMessageMetadata:
        ...

    def disconnect(self) -> None:
        ...
