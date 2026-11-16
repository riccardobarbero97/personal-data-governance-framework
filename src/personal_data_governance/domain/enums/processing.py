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


class DetectionMethod(StrEnum):
    RULE = "RULE"


class ResolutionMethod(StrEnum):
    EXACT_IDENTIFIER_MATCH = "EXACT_IDENTIFIER_MATCH"
    DOMAIN_NORMALIZATION = "DOMAIN_NORMALIZATION"
    KNOWN_ALIAS = "KNOWN_ALIAS"
    USER_CORRECTION = "USER_CORRECTION"


class ClassificationMethod(StrEnum):
    RULE = "RULE"
    AI = "AI"
    MANUAL = "MANUAL"
    COMPOSITE = "COMPOSITE"


class AssessmentMethod(StrEnum):
    RULE = "RULE"
    MANUAL = "MANUAL"
    COMPOSITE = "COMPOSITE"
    AI = "AI"


class AggregationScope(StrEnum):
    SERVICE = "SERVICE"
    UNRESOLVED_SERVICE_CANDIDATE = "UNRESOLVED_SERVICE_CANDIDATE"
    AMBIGUOUS_SERVICE_CANDIDATE = "AMBIGUOUS_SERVICE_CANDIDATE"


class AggregationStatus(StrEnum):
    AGGREGATED = "AGGREGATED"
    EMPTY = "EMPTY"
    PARTIAL = "PARTIAL"
