from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmailMessageMetadataV1:
    sender: str | None
    recipients: tuple[str, ...]
    subject: str | None
    thread_reference: str | None
    labels: tuple[str, ...]
