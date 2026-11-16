from enum import StrEnum


class RelationshipStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    ESTABLISHED = "ESTABLISHED"
    REJECTED = "REJECTED"


class TemporalStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    CURRENTLY_OBSERVED = "CURRENTLY_OBSERVED"
    HISTORICAL = "HISTORICAL"
