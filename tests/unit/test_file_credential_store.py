from pathlib import Path

from personal_data_governance.application.ports.credential_store import (
    CredentialMaterial,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)
from personal_data_governance.infrastructure.credentials.file_store import (
    FileCredentialStore,
)


def test_credential_can_be_saved_and_loaded(
    tmp_path: Path,
) -> None:
    store = FileCredentialStore(
        root_directory=tmp_path
    )

    connected_source_id = ConnectedSourceId(
        "source_gmail_personal"
    )

    material = CredentialMaterial(
        value='{"token": "example"}'
    )

    store.save(
        connected_source_id=connected_source_id,
        credential=material,
    )

    loaded = store.load(
        connected_source_id
    )

    assert loaded == material


def test_missing_credential_returns_none(
    tmp_path: Path,
) -> None:
    store = FileCredentialStore(
        root_directory=tmp_path
    )

    loaded = store.load(
        ConnectedSourceId(
            "source_missing"
        )
    )

    assert loaded is None


def test_credential_can_be_deleted(
    tmp_path: Path,
) -> None:
    store = FileCredentialStore(
        root_directory=tmp_path
    )

    connected_source_id = ConnectedSourceId(
        "source_gmail_personal"
    )

    store.save(
        connected_source_id=connected_source_id,
        credential=CredentialMaterial(
            value='{"token": "example"}'
        ),
    )

    store.delete(
        connected_source_id
    )

    assert store.load(
        connected_source_id
    ) is None


def test_connected_source_id_is_sanitized(
    tmp_path: Path,
) -> None:
    store = FileCredentialStore(
        root_directory=tmp_path
    )

    connected_source_id = ConnectedSourceId(
        "source:gmail/personal"
    )

    store.save(
        connected_source_id=connected_source_id,
        credential=CredentialMaterial(
            value='{"token": "example"}'
        ),
    )

    expected_path = (
        tmp_path
        / "source_gmail_personal.json"
    )

    assert expected_path.exists()


def test_empty_credential_is_rejected(
    tmp_path: Path,
) -> None:
    store = FileCredentialStore(
        root_directory=tmp_path
    )

    try:
        store.save(
            connected_source_id=ConnectedSourceId(
                "source_gmail_personal"
            ),
            credential=CredentialMaterial(
                value="   "
            ),
        )
    except ValueError as error:
        assert str(error) == (
            "Credential material must not be empty."
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
