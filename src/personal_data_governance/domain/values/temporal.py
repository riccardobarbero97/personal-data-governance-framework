from dataclasses import dataclass
from datetime import datetime

from personal_data_governance.domain.enums.observation import TemporalSemantics


@dataclass(frozen=True, slots=True)
class TemporalValue:
    timestamp: datetime
    semantics: TemporalSemantics
