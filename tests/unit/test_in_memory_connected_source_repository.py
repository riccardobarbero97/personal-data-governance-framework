from personal_data_governance.domain.entities.connected_source import (
    ConnectedSource,
)
from personal_data_governance.domain.enums.source import (
    AuthorizationState,
    ConnectionState,
    SourceType,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    UserId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.infrastructure.persistence.in_memory import (
    InMemoryConnectedSourceRepository,
)


def test_connected_source_can_be_saved_and_loaded() -> None:
    repository = InMemoryConnectedSourceRepository()

    source = ConnectedSource(
        id=ConnectedSourceId("source_gmail_personal"),
        user_id=UserId("user_001"),
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="google",
            display_name="Google",
        ),
        connector_id="gmail",
        display_name="Personal Gmail",
        external_account_reference="user@example.com",
        connection_state=ConnectionState.CONNECTED,
        authorization_state=AuthorizationState.AUTHORIZED,
    )

    repository.save(source)

    stored = repository.get(source.id)

    assert stored == source


def test_connected_sources_can_be_found_by_user() -> None:
    repository = InMemoryConnectedSourceRepository()

    user_id = UserId("user_001")

    source_one = ConnectedSource(
        id=ConnectedSourceId("source_001"),
        user_id=user_id,
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="google",
            display_name="Google",
        ),
        connector_id="gmail",
        display_name="Personal Gmail",
        external_account_reference="user@gmail.com",
        connection_state=ConnectionState.CONNECTED,
        authorization_state=AuthorizationState.AUTHORIZED,
    )

    source_two = ConnectedSource(
        id=ConnectedSourceId("source_002"),
        user_id=user_id,
        source_type=SourceType.EMAIL,
        provider=Provider(
            id="microsoft",
            display_name="Microsoft",
        ),
        connector_id="outlook",
        display_name="Personal Outlook",
        external_account_reference="user@outlook.com",
        connection_state=ConnectionState.CONNECTED,
        authorization_state=AuthorizationState.AUTHORIZED,
    )

    repository.save(source_one)
    repository.save(source_two)

    stored = repository.find_by_user(user_id)

    assert len(stored) == 2
    assert source_one in stored
    assert source_two in stored
