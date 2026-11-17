import pytest

from personal_data_governance.config.loaders import (
    RelationshipPolicyConfiguration,
    load_relationship_policy,
)


@pytest.fixture
def relationship_policy(
) -> RelationshipPolicyConfiguration:
    return load_relationship_policy()
