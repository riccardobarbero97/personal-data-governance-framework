from pathlib import Path
from tempfile import NamedTemporaryFile

from personal_data_governance.application.ports.credential_store import (
    CredentialMaterial,
    CredentialStore,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)


class FileCredentialStore(CredentialStore):
    def __init__(
        self,
        root_directory: Path,
    ) -> None:
        self._root_directory = root_directory

    def load(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> CredentialMaterial | None:
        token_path = self._token_path(
            connected_source_id
        )

        if not token_path.exists():
            return None

        serialized_credential = token_path.read_text(
            encoding="utf-8"
        )

        if not serialized_credential.strip():
            return None

        return CredentialMaterial(
            value=serialized_credential
        )

    def save(
        self,
        connected_source_id: ConnectedSourceId,
        credential: CredentialMaterial,
    ) -> None:
        if not credential.value.strip():
            raise ValueError(
                "Credential material must not be empty."
            )

        self._root_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        safe_identifier = self._safe_file_name(
            connected_source_id.value
        )

        token_path = self._token_path(
            connected_source_id
        )

        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self._root_directory,
            prefix=f"{safe_identifier}_",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(
                credential.value
            )

            temporary_path = Path(
                temporary_file.name
            )

        temporary_path.replace(
            token_path
        )

    def delete(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> None:
        token_path = self._token_path(
            connected_source_id
        )

        if token_path.exists():
            token_path.unlink()

    def _token_path(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> Path:
        safe_identifier = self._safe_file_name(
            connected_source_id.value
        )

        return (
            self._root_directory
            / f"{safe_identifier}.json"
        )

    @staticmethod
    def _safe_file_name(
        value: str,
    ) -> str:
        safe_characters = []

        for character in value:
            if (
                character.isalnum()
                or character in {"-", "_"}
            ):
                safe_characters.append(
                    character
                )
            else:
                safe_characters.append(
                    "_"
                )

        safe_value = "".join(
            safe_characters
        ).strip("_")

        if not safe_value:
            raise ValueError(
                "ConnectedSourceId cannot be converted "
                "to a safe credential file name."
            )

        return safe_value
