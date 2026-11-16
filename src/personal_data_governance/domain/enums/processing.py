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


class CandidateIdentifierType(StrEnum):
    EMAIL_DOMAIN = "EMAIL_DOMAIN"
    DOMAIN = "DOMAIN"
    HOSTNAME = "HOSTNAME"


class ServiceIdentifierType(StrEnum):
    EMAIL_DOMAIN = "EMAIL_DOMAIN"
    DOMAIN = "DOMAIN"
    HOSTNAME = "HOSTNAME"
