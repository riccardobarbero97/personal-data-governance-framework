import json
from pathlib import Path

from personal_data_governance.connectors.gmail.offline_api_client import (
    OfflineGmailApiClient,
)


def write_fixture(
    fixture_path: Path,
) -> None:
    fixture_data = {
        "fixture_name": "test-fixture",
        "synthetic_data": True,
        "messages": [
            {
                "message_id": "message_001",
                "thread_id": "thread_001",
                "internal_date_milliseconds": 1000,
                "label_ids": [
                    "INBOX"
                ],
                "headers": [
                    {
                        "name": "From",
                        "value": "one@example.com"
                    }
                ]
            },
            {
                "message_id": "message_002",
                "thread_id": "thread_002",
                "internal_date_milliseconds": 2000,
                "label_ids": [],
                "headers": [
                    {
                        "name": "From",
                        "value": "two@example.com"
                    }
                ]
            },
            {
                "message_id": "message_003",
                "thread_id": None,
                "internal_date_milliseconds": None,
                "label_ids": [],
                "headers": []
            }
        ]
    }

    fixture_path.write_text(
        json.dumps(
            fixture_data
        ),
        encoding="utf-8",
    )


def test_offline_client_supports_pagination(
    tmp_path: Path,
) -> None:
    fixture_path = (
        tmp_path
        / "mailbox.json"
    )

    write_fixture(
        fixture_path
    )

    client = OfflineGmailApiClient(
        fixture_file=fixture_path
    )

    first_page = client.list_messages(
        page_token=None,
        max_results=2,
    )

    assert len(first_page.messages) == 2
    assert first_page.next_page_token == "2"

    second_page = client.list_messages(
        page_token=first_page.next_page_token,
        max_results=2,
    )

    assert len(second_page.messages) == 1
    assert second_page.next_page_token is None

    assert (
        second_page.messages[0].message_id
        == "message_003"
    )


def test_offline_client_returns_metadata(
    tmp_path: Path,
) -> None:
    fixture_path = (
        tmp_path
        / "mailbox.json"
    )

    write_fixture(
        fixture_path
    )

    client = OfflineGmailApiClient(
        fixture_file=fixture_path
    )

    metadata = client.get_message_metadata(
        "message_001"
    )

    assert metadata.thread_id == "thread_001"
    assert metadata.label_ids == ("INBOX",)

    assert metadata.get_header(
        "From"
    ) == "one@example.com"


def test_offline_fixture_must_be_marked_synthetic(
    tmp_path: Path,
) -> None:
    fixture_path = (
        tmp_path
        / "mailbox.json"
    )

    fixture_path.write_text(
        json.dumps(
            {
                "synthetic_data": False,
                "messages": []
            }
        ),
        encoding="utf-8",
    )

    try:
        OfflineGmailApiClient(
            fixture_file=fixture_path
        )
    except ValueError as error:
        assert "synthetic data" in str(
            error
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )


def test_disconnect_disables_client(
    tmp_path: Path,
) -> None:
    fixture_path = (
        tmp_path
        / "mailbox.json"
    )

    write_fixture(
        fixture_path
    )

    client = OfflineGmailApiClient(
        fixture_file=fixture_path
    )

    assert client.is_authorized() is True

    client.disconnect()

    assert client.is_authorized() is False
