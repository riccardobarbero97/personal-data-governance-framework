from dataclasses import dataclass

from personal_data_governance.domain.entities.evidence import Evidence
from personal_data_governance.domain.enums.source import SourceType
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
)
from personal_data_governance.domain.values.provider import Provider
from personal_data_governance.domain.values.temporal import TemporalValue


@dataclass(frozen=True, slots=True)
class EvidenceContribution:
    evidence: Evidence
    connected_source_ids: tuple[ConnectedSourceId, ...]
    source_types: tuple[SourceType, ...]
    providers: tuple[Provider, ...]
    temporal_values: tuple[TemporalValue, ...]
