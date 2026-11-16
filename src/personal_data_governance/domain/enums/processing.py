from enum import StrEnum


class ProcessingStatus(StrEnum):
    SUCCESS = "SUCCESS"
    UNSUPPORTED = "UNSUPPORTED"
    FAILED = "FAILED"


class CandidateStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    NOT_CANDIDATE = "NOT_CANDIDATE"
    UNKNOWN = "UNKNOWN"


class ResolutionStatus(StrEnum):
    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    AMBIGUOUS = "AMBIGUOUS"


class ClassificationStatus(StrEnum):
    CLASSIFIED = "CLASSIFIED"
    UNKNOWN = "UNKNOWN"
