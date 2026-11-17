from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)


EMAIL_MESSAGE_METADATA_V1_PAYLOAD_TYPE = (
    "EmailMessageMetadataV1"
)


class SQLiteSerializationError(
    ValueError
):
    """Raised when a domain object cannot be serialized."""


class SQLiteDeserializationError(
    ValueError
):
    """Raised when persisted data cannot be reconstructed."""


def serialize_datetime(
    value: datetime,
) -> str:
    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise SQLiteSerializationError(
            "Persisted datetime values "
            "must be timezone-aware."
        )

    return value.isoformat()


def deserialize_datetime(
    value: str,
) -> datetime:
    try:
        result = datetime.fromisoformat(
            value
        )

    except ValueError as error:
        raise SQLiteDeserializationError(
            "Persisted datetime value "
            f"is not valid ISO-8601: {value}"
        ) from error

    if (
        result.tzinfo is None
        or result.utcoffset() is None
    ):
        raise SQLiteDeserializationError(
            "Persisted datetime value "
            "must be timezone-aware."
        )

    return result


def serialize_optional_datetime(
    value: datetime | None,
) -> str | None:
    if value is None:
        return None

    return serialize_datetime(
        value
    )


def deserialize_optional_datetime(
    value: str | None,
) -> datetime | None:
    if value is None:
        return None

    return deserialize_datetime(
        value
    )


def serialize_observation_payload(
    payload: object,
) -> tuple[str, str]:
    if isinstance(
        payload,
        EmailMessageMetadataV1,
    ):
        payload_data = {
            "sender": payload.sender,
            "recipients": list(
                payload.recipients
            ),
            "subject": payload.subject,
            "thread_reference": (
                payload.thread_reference
            ),
            "labels": list(
                payload.labels
            ),
        }

        return (
            EMAIL_MESSAGE_METADATA_V1_PAYLOAD_TYPE,
            json.dumps(
                payload_data,
                ensure_ascii=False,
                separators=(
                    ",",
                    ":",
                ),
                sort_keys=True,
            ),
        )

    raise SQLiteSerializationError(
        "Unsupported Observation payload type: "
        f"{type(payload).__name__}"
    )


def deserialize_observation_payload(
    payload_type: str,
    payload_json: str,
) -> object:
    try:
        payload_data = json.loads(
            payload_json
        )

    except json.JSONDecodeError as error:
        raise SQLiteDeserializationError(
            "Persisted Observation payload "
            "contains invalid JSON."
        ) from error

    if not isinstance(
        payload_data,
        dict,
    ):
        raise SQLiteDeserializationError(
            "Persisted Observation payload "
            "must be a JSON object."
        )

    if (
        payload_type
        == EMAIL_MESSAGE_METADATA_V1_PAYLOAD_TYPE
    ):
        return _deserialize_email_metadata(
            payload_data
        )

    raise SQLiteDeserializationError(
        "Unsupported persisted Observation "
        f"payload type: {payload_type}"
    )


def _deserialize_email_metadata(
    payload_data: dict[str, Any],
) -> EmailMessageMetadataV1:
    sender = payload_data.get(
        "sender"
    )

    recipients = payload_data.get(
        "recipients"
    )

    subject = payload_data.get(
        "subject"
    )

    thread_reference = payload_data.get(
        "thread_reference"
    )

    labels = payload_data.get(
        "labels"
    )

    if not isinstance(
        sender,
        str,
    ):
        raise SQLiteDeserializationError(
            "EmailMessageMetadataV1.sender "
            "must be a string."
        )

    if not isinstance(
        recipients,
        list,
    ) or not all(
        isinstance(
            recipient,
            str,
        )
        for recipient in recipients
    ):
        raise SQLiteDeserializationError(
            "EmailMessageMetadataV1.recipients "
            "must be a list of strings."
        )

    if not isinstance(
        subject,
        str,
    ):
        raise SQLiteDeserializationError(
            "EmailMessageMetadataV1.subject "
            "must be a string."
        )

    if (
        thread_reference is not None
        and not isinstance(
            thread_reference,
            str,
        )
    ):
        raise SQLiteDeserializationError(
            "EmailMessageMetadataV1."
            "thread_reference must be "
            "a string or null."
        )

    if not isinstance(
        labels,
        list,
    ) or not all(
        isinstance(
            label,
            str,
        )
        for label in labels
    ):
        raise SQLiteDeserializationError(
            "EmailMessageMetadataV1.labels "
            "must be a list of strings."
        )

    return EmailMessageMetadataV1(
        sender=sender,
        recipients=tuple(
            recipients
        ),
        subject=subject,
        thread_reference=(
            thread_reference
        ),
        labels=tuple(
            labels
        ),
    )
