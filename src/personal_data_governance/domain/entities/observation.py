from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from personal_data_governance.domain.enums.observation import ObservationType
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)
from personal_data_governance.domain.values.temporal import TemporalValue


class ObservationPayload(Protocol):
    pass


@dataclass(frozen=True, slots=True)
class Observation:
    id: ObservationId
    connected_source_id: ConnectedSourceId
    observation_type: ObservationType
    schema_version: SchemaVersion
    source_reference: SourceReference | None
    observed_at: TemporalValue | None
    collected_at: datetime
    payload: ObservationPayload
