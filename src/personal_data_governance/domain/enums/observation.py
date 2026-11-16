from enum import StrEnum


class ObservationType(StrEnum):
    EMAIL_MESSAGE_METADATA = "EMAIL_MESSAGE_METADATA"


class TemporalSemantics(StrEnum):
    MESSAGE_TIME = "MESSAGE_TIME"
    UNKNOWN = "UNKNOWN"
