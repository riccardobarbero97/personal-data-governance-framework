from personal_data_governance.application.results.discovery import (
    DiscoveryOutcome,
)
from personal_data_governance.application.services.discovery_service import (
    DiscoveryService,
)
from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.entities.relationship import Relationship
from personal_data_governance.domain.entities.service import Service


def test_core_packages_can_be_imported() -> None:
    assert Observation is not None
    assert Service is not None
    assert Evidence is not None
    assert Relationship is not None
    assert DiscoveryOutcome is not None
    assert DiscoveryService is not None
