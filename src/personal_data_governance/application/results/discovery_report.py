from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DiscoveryReportEvidence:
    evidence_type: str
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DiscoveryReportEntry:
    observation_id: str
    candidate_status: str | None
    candidate_identifiers: tuple[str, ...]
    resolution_status: str | None
    resolved_service_id: str | None
    alternative_service_ids: tuple[str, ...]
    classification_status: str | None
    evidence: tuple[DiscoveryReportEvidence, ...]
    relationship_status: str | None
    temporal_status: str | None
    relationship_id: str | None
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DiscoveryRelationshipEvidence:
    evidence_type: str
    evidence_count: int


@dataclass(frozen=True, slots=True)
class DiscoveryRelationship:
    service_id: str
    service_name: str
    relationship_id: str
    relationship_status: str
    temporal_status: str
    evidence_count: int
    evidence: tuple[
        DiscoveryRelationshipEvidence,
        ...,
    ]
    observation_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UnresolvedDiscovery:
    identifiers: tuple[str, ...]
    evidence_types: tuple[str, ...]
    observation_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DiscoveryReportSummary:
    observation_count: int
    candidate_count: int
    resolved_count: int
    unresolved_count: int
    ambiguous_count: int
    classified_count: int
    unknown_classification_count: int
    materialized_relationship_count: int


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    schema_version: int
    generated_at: str
    source_mode: str
    synthetic_data: bool
    summary: DiscoveryReportSummary
    relationships: tuple[
        DiscoveryRelationship,
        ...,
    ]
    unresolved_discoveries: tuple[
        UnresolvedDiscovery,
        ...,
    ]
    entries: tuple[
        DiscoveryReportEntry,
        ...,
    ]

    def __post_init__(self) -> None:
        if self.schema_version < 1:
            raise ValueError(
                "Discovery report schema version "
                "must be at least one."
            )

        if not self.generated_at.strip():
            raise ValueError(
                "Discovery report generated_at "
                "must not be empty."
            )

        if not self.source_mode.strip():
            raise ValueError(
                "Discovery report source mode "
                "must not be empty."
            )
