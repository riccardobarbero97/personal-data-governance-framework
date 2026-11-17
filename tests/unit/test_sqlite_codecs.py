from datetime import datetime, timezone

from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.infrastructure.persistence.sqlite.codecs import (
    EMAIL_MESSAGE_METADATA_V1_PAYLOAD_TYPE,
    SQLiteDeserializationError,
    SQLiteSerializationError,
    deserialize_datetime,
    deserialize_observation_payload,
    serialize_datetime,
    serialize_observation_payload,
)


def test_datetime_round_trip() -> None:
    value = datetime(
        2026,
        12,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )

    assert (
        deserialize_datetime(
            serialize_datetime(
                value
            )
        )
        == value
    )


def test_naive_datetime_is_rejected() -> None:
    try:
        serialize_datetime(
            datetime(
                2026,
                12,
                1,
                12,
                0,
            )
        )

    except SQLiteSerializationError:
        pass

    else:
        raise AssertionError(
            "Expected SQLiteSerializationError "
            "was not raised."
        )


def test_email_metadata_round_trip() -> None:
    payload = EmailMessageMetadataV1(
        sender="no-reply@example.com",
        recipients=(
            "user@example.com",
        ),
        subject="Verify your email",
        thread_reference="thread_001",
        labels=(
            "INBOX",
        ),
    )

    (
        payload_type,
        payload_json,
    ) = serialize_observation_payload(
        payload
    )

    assert (
        payload_type
        == EMAIL_MESSAGE_METADATA_V1_PAYLOAD_TYPE
    )

    assert (
        deserialize_observation_payload(
            payload_type,
            payload_json,
        )
        == payload
    )


def test_unknown_payload_type_is_rejected() -> None:
    try:
        deserialize_observation_payload(
            "UnknownPayload",
            "{}",
        )

    except SQLiteDeserializationError:
        pass

    else:
        raise AssertionError(
            "Expected SQLiteDeserializationError "
            "was not raised."
        )
