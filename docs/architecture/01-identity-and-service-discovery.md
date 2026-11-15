# Discovery Implementation Model

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md` - Draft v0.3  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md` - Draft v0.3  
**Related Interfaces:** `docs/interfaces/01-connector-contract.md` through `docs/interfaces/07-relationship-assessor-contract.md`  
**Initial Implementation Target:** Gmail Vertical MVP

---

## 1. Purpose

This document defines the initial implementation model for the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Architecture and Domain Model define:

```text
what the system means
```

The software contracts define:

```text
what each processing boundary is responsible for
```

This document defines:

```text
how those concepts should initially be represented
and composed in executable software
```

The objective is to establish sufficient implementation structure to build the first end-to-end Discovery vertical slice without prematurely defining the entire future framework.

The initial implementation language is:

```text
Python
```

The first implementation target is:

```text
Gmail Vertical MVP
```

---

## 2. Implementation Principles

The implementation must preserve the architectural boundaries already established.

In particular:

```text
ConnectedSource != Connector

Observation != Evidence

CandidateIdentifier != ServiceIdentifier

ServiceIdentifier != Service

Normalization != Resolution

Evidence != Relationship

EvidenceAggregate != Authoritative Evidence

RelationshipAssessmentResult != Relationship

RelationshipStatus != TemporalStatus

Processing Result != Core Domain Entity
```

Implementation convenience must not collapse these distinctions.

The implementation should prefer:

```text
explicit types

explicit states

explicit provenance

replaceable infrastructure

deterministic behavior

small interfaces

local-first execution
```

over implicit coupling or framework-specific abstractions.

---

## 3. Implementation Scope

The first implementation model defines the software representation of:

```text
User

IdentitySeed

ConnectedSource

Observation

ServiceIdentifier

Service

Evidence

Relationship
```

the processing components:

```text
Connector

ServiceCandidateDetector

EntityResolver

EvidenceClassifier

EvidenceAggregator

RelationshipAssessor
```

and the principal application boundaries:

```text
ServiceRegistry

Repositories

Discovery Orchestration

Credential Boundary

Rule / Policy Configuration
```

It also defines the application-level wiring required to preserve the semantic boundaries between these concepts.

---

## 4. Explicit Non-Goals

Draft v0.1 does not attempt to define the complete future framework.

The implementation model does not currently require:

```text
Account

Organization

Brand

LegalDataController

IdentityServiceAssociation

graph database

distributed processing

microservices

event streaming platform

remote AI provider

numerical Confidence

production synchronization

multi-user SaaS deployment
```

These concepts must not be introduced into the initial codebase merely because they may eventually become useful.

---

## 5. Architectural Style

The initial implementation should use a:

> **modular monolith with explicit ports and adapters**

rather than:

```text
microservices
```

The project is currently validating one Domain and one executable vertical slice.

A distributed architecture would introduce infrastructure complexity without providing Domain value at this stage.

The implementation should nevertheless preserve boundaries that could later be separated if empirical requirements justify it.

---

## 6. Dependency Direction

The preferred dependency direction is:

```text
Infrastructure
      |
      v
Application
      |
      v
Domain
```

More precisely:

```text
External Providers
        |
        v
Infrastructure Adapters
        |
        v
Application Ports
        |
        v
Application Services
        |
        v
Domain Types + Domain Policies
```

Dependencies must point toward the Domain.

The Domain must not import:

```text
Gmail API libraries

Google OAuth libraries

SQLAlchemy

SQLite

PostgreSQL

FastAPI

Streamlit

LLM SDKs

cloud-provider SDKs
```

The infrastructure layer implements ports defined by the application or Domain-facing boundaries.

---

## 7. Proposed Project Structure

The initial Python project structure should be:

```text
src/
└── personal_data_governance/
    │
    ├── domain/
    │   ├── entities/
    │   │   ├── user.py
    │   │   ├── identity_seed.py
    │   │   ├── connected_source.py
    │   │   ├── observation.py
    │   │   ├── service.py
    │   │   ├── evidence.py
    │   │   └── relationship.py
    │   │
    │   ├── values/
    │   │   ├── identifiers.py
    │   │   ├── references.py
    │   │   ├── temporal.py
    │   │   └── provenance.py
    │   │
    │   ├── enums/
    │   │   ├── source.py
    │   │   ├── observation.py
    │   │   ├── evidence.py
    │   │   ├── relationship.py
    │   │   └── processing.py
    │   │
    │   └── views/
    │       └── evidence_aggregate.py
    │
    ├── application/
    │   ├── ports/
    │   │   ├── connector.py
    │   │   ├── service_registry.py
    │   │   ├── repositories.py
    │   │   └── credential_store.py
    │   │
    │   ├── values/
    │   │   └── evidence_contribution.py
    │   │
    │   ├── results/
    │   │   ├── candidate_detection.py
    │   │   ├── resolution.py
    │   │   ├── classification.py
    │   │   ├── aggregation.py
    │   │   └── assessment.py
    │   │
    │   └── services/
    │       └── discovery_service.py
    │
    ├── discovery/
    │   ├── candidate_detection/
    │   ├── entity_resolution/
    │   ├── evidence_classification/
    │   ├── evidence_aggregation/
    │   └── relationship_assessment/
    │
    ├── connectors/
    │   └── gmail/
    │
    ├── infrastructure/
    │   ├── persistence/
    │   ├── credentials/
    │   ├── service_registry/
    │   └── google/
    │
    └── config/
        ├── rules/
        ├── taxonomy/
        └── policies/
```

Tests should mirror the source structure:

```text
tests/
├── unit/
├── contract/
├── integration/
└── vertical/
```

---

## 8. Domain Representation Strategy

Core immutable or mostly immutable Domain structures should initially use Python:

```python
@dataclass
```

with:

```python
frozen=True
```

where meaningful.

Controlled states should use:

```python
Enum
```

or:

```python
StrEnum
```

when serialized string values are useful.

Interfaces should prefer:

```python
typing.Protocol
```

over deep inheritance hierarchies.

This keeps the Domain:

```text
simple

typed

testable

infrastructure-independent
```

---

## 9. Identifier Types

Domain identifiers should not initially be represented as arbitrary strings throughout the codebase.

The implementation should introduce typed wrappers such as:

```python
@dataclass(frozen=True)
class UserId:
    value: str
```

and equivalent types for:

```text
IdentitySeedId

ConnectedSourceId

ObservationId

ServiceId

EvidenceId

RelationshipId
```

This prevents accidental mixing of identifiers.

For example:

```python
relationship.service_id = observation.id
```

should become difficult to express accidentally.

---

## 10. User

`User` is a Core Domain Entity.

Initial representation:

```python
@dataclass
class User:
    id: UserId
```

The first MVP does not require a large User profile.

Information such as:

```text
name

address

preferences

profile picture
```

must not be introduced unless required by Discovery.

---

## 11. IdentitySeed

Initial representation:

```python
@dataclass
class IdentitySeed:
    id: IdentitySeedId
    user_id: UserId
    type: IdentitySeedType
    value: str
    verification_status: VerificationStatus
```

Candidate enums may initially include:

```python
class IdentitySeedType(StrEnum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    USERNAME = "USERNAME"
    GOOGLE_ACCOUNT = "GOOGLE_ACCOUNT"
    MICROSOFT_ACCOUNT = "MICROSOFT_ACCOUNT"
    APPLE_ACCOUNT = "APPLE_ACCOUNT"
```

The initial Gmail MVP requires at minimum:

```text
EMAIL
```

Other enum values may be introduced only when required.

---

## 12. ConnectedSource

`ConnectedSource` is a Core Domain Entity.

Conceptually:

```python
@dataclass
class ConnectedSource:
    id: ConnectedSourceId
    user_id: UserId
    source_type: SourceType
    provider: Provider
    connector_id: str
    display_name: str
    external_account_reference: str | None
    connection_state: ConnectionState
    authorization_state: AuthorizationState
```

The object must not contain:

```text
access token

refresh token

password

OAuth client secret
```

Those belong behind the `CredentialStore` port.

---

## 13. SourceType

Initial enum:

```python
class SourceType(StrEnum):
    EMAIL = "EMAIL"
    PASSWORD_MANAGER = "PASSWORD_MANAGER"
    BROWSER = "BROWSER"
    IDENTITY_PROVIDER = "IDENTITY_PROVIDER"
    MANUAL = "MANUAL"
```

The Gmail MVP uses:

```text
EMAIL
```

---

## 14. Provider

`Provider` should initially be a lightweight value rather than a complex Domain Entity.

Conceptually:

```python
@dataclass(frozen=True)
class Provider:
    id: str
    display_name: str
```

Example:

```python
Provider(
    id="google",
    display_name="Google",
)
```

Provider therefore remains distinct from:

```text
Service
```

even when the same real-world company occupies both roles.

---

## 15. Observation

Observation is a Core Domain Entity.

The common envelope should be represented separately from typed payloads.

Conceptually:

```python
@dataclass(frozen=True)
class Observation:
    id: ObservationId
    connected_source_id: ConnectedSourceId
    observation_type: ObservationType
    schema_version: SchemaVersion
    source_reference: SourceReference | None
    observed_at: TemporalValue | None
    collected_at: datetime
    payload: ObservationPayload
```

`observed_at` combines the source-derived timestamp with its temporal semantics.

`collected_at` remains a framework collection timestamp and therefore does not require a source temporal semantic.

The implementation must not duplicate temporal semantics in both:

```text
Observation.temporal_semantics
```

and:

```text
TemporalValue.semantics
```

The semantics belong to `TemporalValue`.

---

## 16. ObservationPayload

`ObservationPayload` should be a Protocol or tagged union over explicitly supported payload types.

Conceptually:

```python
class ObservationPayload(Protocol):
    ...
```

The first implementation should include:

```text
EmailMessageMetadataV1
```

The payload must not be:

```python
dict[str, Any]
```

as the default Domain representation.

Untyped dictionaries would weaken the schema boundary established by the Observation Contract.

---

## 17. EMAIL_MESSAGE_METADATA v1

The first concrete payload for the Gmail Vertical MVP should be:

```python
@dataclass(frozen=True)
class EmailMessageMetadataV1:
    sender: str | None
    recipients: tuple[str, ...]
    subject: str | None
    thread_reference: str | None
    labels: tuple[str, ...]
```

The exact fields should remain minimized to those required by the MVP.

Message body must not be part of this payload.

Attachment content must not be part of this payload.

The Gmail Provider message identifier should normally be represented through:

```text
Observation.source_reference
```

rather than duplicated inside the payload.

---

## 18. ObservationType

Initial MVP enum:

```python
class ObservationType(StrEnum):
    EMAIL_MESSAGE_METADATA = "EMAIL_MESSAGE_METADATA"
```

Additional ObservationTypes should be introduced only when a corresponding source or capability is implemented.

The codebase should not populate enums with every hypothetical future ObservationType in advance.

---

## 19. SchemaVersion

A lightweight value object is sufficient:

```python
@dataclass(frozen=True)
class SchemaVersion:
    value: int
```

For the first payload:

```text
EMAIL_MESSAGE_METADATA v1
```

---

## 20. TemporalSemantics and TemporalValue

Initial temporal semantics relevant to Gmail:

```python
class TemporalSemantics(StrEnum):
    MESSAGE_TIME = "MESSAGE_TIME"
    UNKNOWN = "UNKNOWN"
```

The Domain `TemporalValue` concept is represented as:

```python
@dataclass(frozen=True)
class TemporalValue:
    timestamp: datetime
    semantics: TemporalSemantics
```

`TemporalValue` ensures that a timestamp cannot silently lose the meaning provided by its source.

For example:

```text
2026-01-01
+
MESSAGE_TIME
```

must remain distinguishable from:

```text
2026-01-01
+
SOURCE_RECORD_MODIFIED
```

Additional semantics such as:

```text
SOURCE_EVENT_TIME

SOURCE_RECORD_CREATED

SOURCE_RECORD_MODIFIED

VISIT_TIME

USER_DECLARED_TIME
```

can be introduced when corresponding ObservationTypes are implemented.

The implementation must remain capable of carrying more than one typed TemporalValue where a future ObservationType exposes multiple independently meaningful timestamps.

---

## 21. CandidateIdentifier

`CandidateIdentifier` remains an application-processing value.

Conceptually:

```python
@dataclass(frozen=True)
class CandidateIdentifier:
    type: CandidateIdentifierType
    value: str
    source_attribute: str | None
```

It does not require persistent Domain identity in the first MVP.

CandidateIdentifier represents information detected in one processing execution.

It is not itself the retained Domain representation used by Entity Resolution.

---

## 22. ServiceIdentifier

`ServiceIdentifier` is a Domain Value Concept.

Conceptually:

```python
@dataclass(frozen=True)
class ServiceIdentifier:
    type: ServiceIdentifierType
    original_value: str
    normalized_value: str | None
    observation_id: ObservationId
```

Initial types may include:

```python
class ServiceIdentifierType(StrEnum):
    EMAIL_DOMAIN = "EMAIL_DOMAIN"
    DOMAIN = "DOMAIN"
    HOSTNAME = "HOSTNAME"
```

The Gmail MVP primarily requires:

```text
EMAIL_DOMAIN

DOMAIN
```

Original and normalized values must remain distinguishable.

---

### 22.1 CandidateIdentifier Materialization

`CandidateIdentifier` is a transient processing representation produced by Service Candidate Detection.

`ServiceIdentifier` is the Domain Value Concept consumed by Entity Resolution.

For the initial implementation, materialization occurs in the Application Layer:

```text
CandidateDetectionResult
        |
        v
CandidateIdentifier
        |
        v
Application Layer
        |
        v
ServiceIdentifier
        |
        v
ResolutionRequest
        |
        v
EntityResolver
```

The EntityResolver therefore receives ServiceIdentifier values rather than owning the CandidateIdentifier-to-ServiceIdentifier materialization step.

This preserves the boundary:

```text
CandidateIdentifier
        !=
ServiceIdentifier
        !=
Service
```

Materialization must preserve:

```text
original identifier value

identifier type

source Observation reference

normalization provenance where applicable
```

The materialization step does not resolve the identifier to a canonical Service.

---

## 23. Service

`Service` is a Core Domain Entity.

Initial representation:

```python
@dataclass
class Service:
    id: ServiceId
    canonical_name: str
```

The first MVP should not prematurely add:

```text
Organization

Brand

LegalDataController

Account
```

to Service.

Known identifiers belong through the ServiceRegistry rather than requiring the Service object to contain all Registry behavior.

---

## 24. EvidenceType

The first implementation should use a controlled enum.

The Gmail MVP should initially support EvidenceTypes required by Gmail Service Discovery:

```python
class EvidenceType(StrEnum):
    ACCOUNT_CREATION = "ACCOUNT_CREATION"
    ACCOUNT_VERIFICATION = "ACCOUNT_VERIFICATION"
    AUTHENTICATION = "AUTHENTICATION"
    PASSWORD_RESET = "PASSWORD_RESET"
    SECURITY_NOTIFICATION = "SECURITY_NOTIFICATION"
    PURCHASE = "PURCHASE"
    INVOICE = "INVOICE"
    SUBSCRIPTION = "SUBSCRIPTION"
    PAYMENT = "PAYMENT"
    ACCOUNT_UPDATE = "ACCOUNT_UPDATE"
    ACCOUNT_DELETION = "ACCOUNT_DELETION"
    MARKETING = "MARKETING"
    NEWSLETTER = "NEWSLETTER"
    PRIVACY_NOTICE = "PRIVACY_NOTICE"
```

`PASSWORD_MANAGER_ENTRY` may remain defined if useful for cross-scenario tests, but is not required by the Gmail Vertical MVP.

Evidence taxonomy should remain versionable.

---

## 25. EvidenceStatus

```python
class EvidenceStatus(StrEnum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
```

Newly materialized accepted Evidence should normally start as:

```text
ACTIVE
```

`SUPERSEDED` and `REJECTED` remain semantically different.

---

## 26. Evidence

Initial representation:

```python
@dataclass
class Evidence:
    id: EvidenceId
    evidence_type: EvidenceType
    evidence_status: EvidenceStatus
    observation_ids: tuple[ObservationId, ...]
    service_id: ServiceId | None
    identity_seed_ids: tuple[IdentitySeedId, ...]
    classification_method: ClassificationMethod
    classifier_version: str
    reason_codes: tuple[str, ...]
```

Evidence must remain traceable to supporting Observations.

Source provenance should not be duplicated unnecessarily inside Evidence.

Temporal provenance should remain recoverable through the supporting Observations.

If implementation demonstrates that Evidence requires independent derived TemporalValues, they may be introduced without changing the Entity boundary.

Evidence may exist with:

```python
service_id = None
```

when Entity Resolution remains:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

---

## 27. EvidenceCandidate

Classifier output should not construct persistent Domain Evidence directly.

Conceptually:

```python
@dataclass(frozen=True)
class EvidenceCandidate:
    evidence_type: EvidenceType
    observation_ids: tuple[ObservationId, ...]
    method: ClassificationMethod
    reason_codes: tuple[str, ...]
    classifier_version: str
```

The application layer is responsible for materialization:

```text
EvidenceCandidate
        |
        v
Application Layer
        |
        v
Evidence
```

A newly materialized accepted interpretation normally receives:

```text
EvidenceStatus.ACTIVE
```

---

## 28. RelationshipStatus

```python
class RelationshipStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    ESTABLISHED = "ESTABLISHED"
    REJECTED = "REJECTED"
```

No:

```text
POSSIBLE

PROBABLE

CONFIRMED
```

values should be introduced into the initial implementation.

---

## 29. TemporalStatus

```python
class TemporalStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    CURRENTLY_OBSERVED = "CURRENTLY_OBSERVED"
    HISTORICAL = "HISTORICAL"
```

TemporalStatus remains independent from RelationshipStatus.

---

## 30. Relationship

Initial representation:

```python
@dataclass
class Relationship:
    id: RelationshipId
    user_id: UserId
    service_id: ServiceId
    relationship_status: RelationshipStatus
    temporal_status: TemporalStatus
    identity_seed_ids: tuple[IdentitySeedId, ...]
    evidence_ids: tuple[EvidenceId, ...]
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    assessment_method: AssessmentMethod
    assessor_version: str
    assessment_policy_version: str
    assessed_at: datetime
```

The Relationship represents the current materialized User-Service assessment.

The following provenance remains explicit:

```text
Assessment Method

Assessor Version

Assessment Policy Version

Assessment Time

Evidence Basis
```

Historical assessment results remain separate.

---

## 31. ProcessingStatus

A shared controlled enum should initially support:

```python
class ProcessingStatus(StrEnum):
    SUCCESS = "SUCCESS"
    UNSUPPORTED = "UNSUPPORTED"
    FAILED = "FAILED"
```

Component-specific semantic status remains separate.

For example:

```text
ProcessingStatus.SUCCESS
+
ResolutionStatus.UNRESOLVED
```

is valid.

Likewise:

```text
ProcessingStatus.SUCCESS
+
ClassificationStatus.UNKNOWN
```

is valid.

---

## 32. CandidateDetectionResult

```python
@dataclass(frozen=True)
class CandidateDetectionResult:
    observation_id: ObservationId
    processing_status: ProcessingStatus
    candidate_status: CandidateStatus | None
    candidate_identifiers: tuple[CandidateIdentifier, ...]
    reason_codes: tuple[str, ...]
    method: DetectionMethod
    detector_version: str
```

This remains a Processing Result.

It must not become a Domain Entity merely because it may later be persisted for provenance.

---

## 33. ResolutionRequest and ResolutionResult

Entity Resolution consumes Domain ServiceIdentifiers rather than CandidateIdentifiers.

The request is:

```python
@dataclass(frozen=True)
class ResolutionRequest:
    observation_id: ObservationId
    service_identifiers: tuple[ServiceIdentifier, ...]
    context: ResolutionContext
```

The result is:

```python
@dataclass(frozen=True)
class ResolutionResult:
    observation_id: ObservationId
    input_identifiers: tuple[ServiceIdentifier, ...]
    normalized_identifiers: tuple[ServiceIdentifier, ...]
    processing_status: ProcessingStatus
    resolution_status: ResolutionStatus | None
    resolved_service_id: ServiceId | None
    alternative_service_ids: tuple[ServiceId, ...]
    method: ResolutionMethod | None
    reason_codes: tuple[str, ...]
    resolver_version: str
```

`ResolutionRequest` receives ServiceIdentifier values materialized by the Application Layer.

The EntityResolver must not implicitly convert CandidateIdentifiers into ServiceIdentifiers.

`normalized_identifiers` preserve normalization results without destroying the original ServiceIdentifier values.

ResolutionResult remains:

```text
Processing Result / Value Object
```

and not a Service Entity.

---

## 34. ClassificationResult

```python
@dataclass(frozen=True)
class ClassificationResult:
    observation_id: ObservationId
    processing_status: ProcessingStatus
    classification_status: ClassificationStatus | None
    evidence_candidates: tuple[EvidenceCandidate, ...]
    method: ClassificationMethod | None
    reason_codes: tuple[str, ...]
    classifier_version: str
```

ClassificationResult remains a Processing Result.

It must remain distinct from:

```text
EvidenceCandidate

Evidence
```

---

## 35. EvidenceAggregate

EvidenceAggregate is a Derived View.

Conceptually:

```python
@dataclass(frozen=True)
class EvidenceAggregate:
    scope: AggregationScope

    service_id: ServiceId | None

    unresolved_identifiers: tuple[ServiceIdentifier, ...]

    alternative_service_ids: tuple[ServiceId, ...]

    identity_seed_ids: tuple[IdentitySeedId, ...]

    evidence_ids: tuple[EvidenceId, ...]

    evidence_summary: EvidenceSummary

    source_summary: SourceSummary

    temporal_summary: TemporalSummary

    conflict_summary: ConflictSummary

    coverage_summary: CoverageSummary | None

    aggregator_version: str
```

The Aggregate must support all initial Discovery aggregation scopes:

```text
SERVICE

UNRESOLVED_SERVICE_CANDIDATE

AMBIGUOUS_SERVICE_CANDIDATE
```

Their expected representations are:

```text
SERVICE
    -> service_id populated
```

```text
UNRESOLVED_SERVICE_CANDIDATE
    -> unresolved_identifiers populated
```

```text
AMBIGUOUS_SERVICE_CANDIDATE
    -> unresolved_identifiers populated
    -> alternative_service_ids populated
```

Fields that do not apply to a selected scope remain empty.

Evidence must not disappear solely because Entity Resolution returns:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

EvidenceAggregate must remain rebuildable.

---

### 35.1 EvidenceContribution and Source Provenance

Evidence does not duplicate ConnectedSource or SourceType provenance already available through supporting Observations.

Before invoking the EvidenceAggregator, the Application Layer resolves the minimum provenance required for aggregation.

The initial implementation uses:

```python
@dataclass(frozen=True)
class EvidenceContribution:
    evidence: Evidence
    connected_source_ids: tuple[ConnectedSourceId, ...]
    source_types: tuple[SourceType, ...]
    providers: tuple[Provider, ...]
    temporal_values: tuple[TemporalValue, ...]
```

Conceptually:

```text
Evidence
   |
   v
supporting Observation IDs
   |
   v
ObservationRepository
   |
   v
Observations
   |
   v
ConnectedSource IDs
   |
   v
ConnectedSourceRepository
   |
   v
SourceType / Provider
   |
   v
EvidenceContribution
   |
   v
EvidenceAggregator
```

`EvidenceContribution` is an Application Value Object.

It is not a Core Domain Entity.

It must not become an alternative authoritative provenance representation.

Its purpose is to provide the Aggregator with already-resolved context necessary to construct:

```text
EvidenceSummary

SourceSummary

TemporalSummary

ConflictSummary
```

without requiring the EvidenceAggregator to query infrastructure repositories directly.

The authoritative provenance remains:

```text
Evidence
   |
   v
Observation
   |
   v
ConnectedSource
```

---

## 36. AggregationResult

```python
@dataclass(frozen=True)
class AggregationResult:
    processing_status: ProcessingStatus
    aggregation_status: AggregationStatus | None
    aggregate: EvidenceAggregate | None
    aggregator_version: str
```

This remains a Processing Result.

It must remain distinct from:

```text
EvidenceAggregate
```

which is a Derived View.

---

## 37. RelationshipAssessmentResult

```python
@dataclass(frozen=True)
class RelationshipAssessmentResult:
    processing_status: ProcessingStatus
    service_id: ServiceId | None
    relationship_status: RelationshipStatus | None
    temporal_status: TemporalStatus | None
    identity_seed_ids: tuple[IdentitySeedId, ...]
    evidence_ids: tuple[EvidenceId, ...]
    reason_codes: tuple[str, ...]
    warnings: tuple[str, ...]
    method: AssessmentMethod | None
    assessor_version: str
    assessment_policy_version: str
```

The application layer uses this result to create or update Relationship only when a canonical Service context exists.

An assessment over unresolved or ambiguous aggregation context must not fabricate a canonical User-Service Relationship.

---

## 38. Protocol Strategy

Behavioral boundaries should initially use:

```python
typing.Protocol
```

rather than concrete base classes where inheritance is unnecessary.

Example:

```python
class ServiceCandidateDetector(Protocol):

    def detect(
        self,
        observation: Observation,
        context: CandidateDetectionContext,
    ) -> CandidateDetectionResult:
        ...
```

This allows alternative implementations without forcing shared inheritance.

---

## 39. Connector Port

The minimum Connector port is:

```python
class Connector(Protocol):

    def get_descriptor(
        self,
    ) -> ConnectorDescriptor:
        ...

    def get_capabilities(
        self,
        connected_source: ConnectedSource,
    ) -> CapabilitySet:
        ...

    def get_authorization_status(
        self,
        connected_source: ConnectedSource,
    ) -> AuthorizationStatus:
        ...

    def get_permission_requirements(
        self,
        connected_source: ConnectedSource,
        capability: Capability,
    ) -> PermissionRequirements:
        ...

    def prepare_authorization(
        self,
        connected_source: ConnectedSource,
        capability: Capability,
    ) -> AuthorizationRequest:
        ...

    def collect(
        self,
        request: CollectionRequest,
    ) -> CollectionResult:
        ...

    def disconnect(
        self,
        connected_source: ConnectedSource,
    ) -> DisconnectResult:
        ...
```

`disconnect()` belongs to the minimum Connector port because ConnectedSource lifecycle is independently managed per source instance.

Optional operations such as:

```text
refresh_authorization()

revoke()
```

may be represented through additional capability-specific Protocols or added to Connector implementations when required.

The core port must not assume OAuth as the only authorization mechanism.

---

## 40. ServiceCandidateDetector Port

```python
class ServiceCandidateDetector(Protocol):

    def detect(
        self,
        observation: Observation,
        context: CandidateDetectionContext,
    ) -> CandidateDetectionResult:
        ...
```

The first implementation should be deterministic.

The detector returns CandidateIdentifiers rather than Domain Services.

---

## 41. EntityResolver Port

```python
class EntityResolver(Protocol):

    def resolve(
        self,
        request: ResolutionRequest,
    ) -> ResolutionResult:
        ...
```

The Resolver receives ServiceIdentifiers.

It depends on:

```text
ServiceRegistry
```

through an interface.

It must not:

- materialize CandidateIdentifiers;
- create new Services implicitly;
- persist Relationships;
- depend on concrete Registry persistence.

---

## 42. EvidenceClassifier Port

```python
class EvidenceClassifier(Protocol):

    def classify(
        self,
        observation: Observation,
        context: ClassificationContext,
    ) -> ClassificationResult:
        ...
```

The first Gmail implementation should be deterministic-first.

AI should not be necessary to prove the first vertical slice.

The classifier returns EvidenceCandidates rather than persisting Evidence itself.

---

## 43. EvidenceAggregator Port

```python
class EvidenceAggregator(Protocol):

    def aggregate(
        self,
        request: AggregationRequest,
    ) -> AggregationResult:
        ...
```

The AggregationRequest should contain already-resolved EvidenceContribution values or equivalent application-prepared aggregation input.

The Aggregator must not depend directly on infrastructure repositories.

The current-view policy should include:

```text
ACTIVE
```

and exclude:

```text
SUPERSEDED

REJECTED
```

by default.

---

## 44. RelationshipAssessor Port

```python
class RelationshipAssessor(Protocol):

    def assess(
        self,
        aggregate: EvidenceAggregate,
        context: RelationshipAssessmentContext,
    ) -> RelationshipAssessmentResult:
        ...
```

The initial implementation should use deterministic policy.

The Assessor determines Relationship semantics.

It does not persist Relationship entities.

---

## 45. Repository Boundaries

The Domain must not depend on a specific persistence implementation.

Initial repository ports should include only what the vertical slice requires.

Initial interfaces include:

```text
ConnectedSourceRepository

ObservationRepository

ServiceRegistry

EvidenceRepository

RelationshipRepository
```

Repositories should expose use-case-oriented operations rather than generic persistence mechanics where practical.

---

## 46. ObservationRepository

Conceptually:

```python
class ObservationRepository(Protocol):

    def save(
        self,
        observation: Observation,
    ) -> None:
        ...

    def get(
        self,
        observation_id: ObservationId,
    ) -> Observation | None:
        ...

    def find_by_source_reference(
        self,
        connected_source_id: ConnectedSourceId,
        source_reference: SourceReference,
    ) -> Observation | None:
        ...
```

`find_by_source_reference()` supports idempotent source collection.

`get()` supports provenance resolution for Evidence aggregation.

---

## 47. ServiceRegistry Port

The initial ServiceRegistry needs enough behavior for deterministic lookup.

Conceptually:

```python
class ServiceRegistry(Protocol):

    def resolve(
        self,
        identifier: ServiceIdentifier,
    ) -> tuple[Service, ...]:
        ...

    def get(
        self,
        service_id: ServiceId,
    ) -> Service | None:
        ...
```

For the first MVP, an in-memory or local-file-backed Registry is acceptable.

A return value of:

```python
()
```

means no canonical Service match exists.

One returned Service may produce:

```text
RESOLVED
```

Multiple plausible Services may produce:

```text
AMBIGUOUS
```

The Domain and Resolver must not know which concrete Registry implementation is being used.

---

## 48. EvidenceRepository

The EvidenceRepository must support both persistence and lifecycle operations.

Conceptually:

```python
class EvidenceRepository(Protocol):

    def save(
        self,
        evidence: Evidence,
    ) -> None:
        ...

    def get(
        self,
        evidence_id: EvidenceId,
    ) -> Evidence | None:
        ...

    def find_by_observation(
        self,
        observation_id: ObservationId,
    ) -> tuple[Evidence, ...]:
        ...

    def find_active_by_service(
        self,
        service_id: ServiceId,
    ) -> tuple[Evidence, ...]:
        ...

    def change_status(
        self,
        evidence_id: EvidenceId,
        new_status: EvidenceStatus,
        provenance: EvidenceLifecycleProvenance,
    ) -> None:
        ...
```

Lifecycle provenance is represented conceptually as:

```python
@dataclass(frozen=True)
class EvidenceLifecycleProvenance:
    changed_at: datetime
    reason_code: str
    actor: str
    superseded_by: EvidenceId | None = None
```

For Draft v0.1 the repository must support transitions required by the consolidated lifecycle:

```text
ACTIVE
  |
  +--> SUPERSEDED
  |
  +--> REJECTED
```

Lifecycle transitions must preserve provenance.

A new interpretation replacing an older interpretation should normally be materialized as a separate Evidence Entity while the previous Evidence becomes:

```text
SUPERSEDED
```

`REJECTED` remains semantically different.

The repository must not silently mutate one EvidenceType into another EvidenceType.

---

## 49. RelationshipRepository

Conceptually:

```python
class RelationshipRepository(Protocol):

    def get_by_user_and_service(
        self,
        user_id: UserId,
        service_id: ServiceId,
    ) -> Relationship | None:
        ...

    def save(
        self,
        relationship: Relationship,
    ) -> None:
        ...
```

The current Domain invariant implies one current User-Service Relationship for a given pair under the initial model.

Historical RelationshipAssessmentResults, if persisted later, remain separate from the current Relationship.

---

## 50. CredentialStore Port

Credential storage must be isolated.

Conceptually:

```python
class CredentialStore(Protocol):

    def load(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> CredentialMaterial:
        ...

    def save(
        self,
        connected_source_id: ConnectedSourceId,
        credential: CredentialMaterial,
    ) -> None:
        ...

    def delete(
        self,
        connected_source_id: ConnectedSourceId,
    ) -> None:
        ...
```

`CredentialMaterial` must not be part of the ordinary Domain model.

The Domain must never import Provider credential representations.

---

## 51. First Persistence Strategy

The first Gmail Vertical MVP should prefer the simplest persistence capable of validating the architecture.

The initial implementation should therefore use:

```text
in-memory repositories
```

for:

```text
unit tests

contract tests

vertical tests
```

A durable local implementation may subsequently use:

```text
SQLite
```

if persistence becomes necessary for the MVP.

The Domain and application interfaces must make the choice replaceable.

The architecture must not depend on SQLite.

---

## 52. No Graph Database Requirement

Although the output is conceptually a Service Graph, the first vertical slice does not require:

```text
Neo4j

Amazon Neptune

Azure Cosmos DB Gremlin
```

The initial graph semantics can be represented through:

```text
Relationship entities

Service references

Identity references

Evidence references

repository queries
```

A graph database should be introduced only when concrete graph-query or scale requirements justify it.

---

## 53. Gmail Connector Adapter

The first external-source adapter will be:

```text
GmailConnector
```

The preferred conceptual location is:

```text
connectors/gmail/
```

while reusable Google-specific authorization or API infrastructure may live under:

```text
infrastructure/google/
```

`GmailConnector` implements:

```text
Connector
```

and translates Gmail-specific information into:

```text
EMAIL_MESSAGE_METADATA v1
```

Observations.

---

## 54. Gmail API Isolation

Only Gmail-specific infrastructure may directly depend on Google API representations.

The following must not import Gmail API types:

```text
domain/

application/

discovery/candidate_detection/

discovery/entity_resolution/

discovery/evidence_classification/

discovery/evidence_aggregation/

discovery/relationship_assessment/
```

This dependency rule should be enforced through tests or static architecture checks where practical.

---

## 55. Gmail MVP Collection Capability

The first implemented Gmail capability should be:

```text
SERVICE_DISCOVERY_METADATA
```

It should collect only information required for metadata-based Service Discovery.

The first vertical slice must not require:

```text
EMAIL_MESSAGE_CONTENT

ATTACHMENT_CONTENT
```

Progressive Permission must therefore be preserved from the first implementation.

---

## 56. Gmail Observation Mapping

The Gmail adapter should conceptually map:

```text
Gmail message
      |
      v
selected authorized metadata
      |
      v
EmailMessageMetadataV1
      |
      v
Observation
```

The adapter should preserve:

```text
Gmail message ID
```

as:

```text
SourceReference
```

where technically appropriate.

Provider message representations must not cross the Connector boundary.

---

## 57. Initial Candidate Detection Policy

The Gmail MVP should begin with deterministic Candidate Detection.

Initial signals may include:

```text
sender address

sender domain

known User IdentitySeeds

generic consumer email-provider domains

local/internal exclusion rules

known infrastructure patterns
```

The actual rule vocabulary should be stored outside Domain entity classes.

A rule-set version should become traceable when changes materially affect results.

---

## 58. Initial Identifier Extraction

For Gmail:

```text
sender email
      |
      v
email-address parser
      |
      v
email domain
      |
      v
EMAIL_DOMAIN CandidateIdentifier
```

Example:

```text
no-reply@spotify.com
        |
        v
spotify.com
```

Parsing must be deterministic.

The result remains:

```text
CandidateIdentifier
```

until Application Layer materialization.

---

## 59. Initial Entity Resolution Strategy

The initial pipeline is:

```text
CandidateIdentifier
        |
        v
Application Layer
        |
        v
ServiceIdentifier
        |
        v
ResolutionRequest
        |
        v
EntityResolver
        |
        v
normalize where required
        |
        v
ServiceRegistry lookup
        |
    +---+----------------+
    |         |          |
    v         v          v
RESOLVED  UNRESOLVED  AMBIGUOUS
```

Normalization must remain distinguishable from canonical Service Resolution.

`AMBIGUOUS` must exist even if the first curated Registry rarely produces it.

---

## 60. Initial ServiceRegistry Data

The initial ServiceRegistry should be intentionally small.

It may contain a curated set of Services needed by:

- unit tests;
- contract fixtures;
- vertical fixtures;
- first empirical Gmail samples.

The Registry must not attempt to become a universal Internet Service database before the MVP.

Unknown identifiers should remain:

```text
UNRESOLVED
```

The Resolver must never create a Service merely to avoid UNRESOLVED.

---

## 61. Initial Evidence Classification Strategy

The Gmail MVP should begin with deterministic classification rules over:

```text
sender metadata

subject

ObservationType
```

Example rules:

```text
"verify your email"
        ->
ACCOUNT_VERIFICATION
```

```text
"reset your password"
        ->
PASSWORD_RESET
```

```text
"payment successful"
        ->
PAYMENT
```

```text
"privacy policy"
        ->
PRIVACY_NOTICE
```

Internationalization should be handled incrementally.

AI is not required for MVP completion.

---

## 62. Unknown Classification

If no rule safely matches:

```text
ClassificationStatus.UNKNOWN
```

should be returned.

The MVP must not treat:

```text
UNKNOWN
```

as an error.

Likewise, unsupported ObservationTypes should use:

```text
ProcessingStatus.UNSUPPORTED
```

rather than semantic UNKNOWN.

---

## 63. Evidence Materialization

The Application Layer performs:

```text
ClassificationResult
       |
       v
EvidenceCandidate
       |
       v
Application Layer
       |
       v
Evidence
```

For accepted current classifications:

```text
EvidenceStatus.ACTIVE
```

is assigned during materialization.

Classifier implementations must not persist Evidence directly.

If the same Observation already has an earlier accepted Evidence interpretation, lifecycle policy determines whether that Evidence must first become:

```text
SUPERSEDED
```

or:

```text
REJECTED
```

---

## 64. Evidence Lifecycle Operations

The initial lifecycle is:

```text
ACTIVE
  |
  +--> SUPERSEDED
  |
  +--> REJECTED
```

The Application Layer coordinates lifecycle changes through EvidenceRepository.

No generic lifecycle engine is required for Draft v0.1.

The Gmail Vertical MVP may initially exercise primarily:

```text
new Evidence -> ACTIVE
```

but automated tests must validate:

```text
ACTIVE -> SUPERSEDED
```

and:

```text
ACTIVE -> REJECTED
```

with provenance.

A new semantic interpretation should normally be a new Evidence Entity rather than a destructive mutation of the previous EvidenceType.

---

## 65. Initial Aggregation Strategy

The first Aggregator should:

1. accept one explicit aggregation scope;
2. receive Application-prepared EvidenceContribution values;
3. include ACTIVE Evidence;
4. exclude SUPERSEDED Evidence;
5. exclude REJECTED Evidence;
6. count eligible Evidence by EvidenceType;
7. preserve Evidence IDs;
8. preserve Identity references;
9. preserve ConnectedSource provenance;
10. preserve SourceType provenance;
11. preserve Provider provenance where relevant;
12. calculate typed temporal summaries;
13. preserve conflicts explicitly;
14. support SERVICE scope;
15. support UNRESOLVED_SERVICE_CANDIDATE scope;
16. support AMBIGUOUS_SERVICE_CANDIDATE scope.

No weighting is required.

---

## 66. Aggregate Persistence Strategy

For the first vertical slice:

```text
compute EvidenceAggregate on demand
```

is preferred.

Reasons:

```text
Evidence count is initially small

+

Aggregate is derived state

+

simpler consistency model

+

easy validation against contracts
```

Materialized aggregates may be introduced later if performance measurements justify them.

A persisted materialized Aggregate would still remain:

```text
Derived View
```

rather than authoritative Domain state.

---

## 67. Initial Relationship Assessment Policy

The first MVP requires explicit deterministic policy.

It should remain conservative.

A candidate starting point is:

```text
No eligible Evidence
        |
        v
UNKNOWN
```

```text
MARKETING / NEWSLETTER / PRIVACY_NOTICE only
        |
        v
OBSERVED
```

```text
account-related or authentication Evidence
        |
        v
candidate for ESTABLISHED
```

```text
explicit User rejection
        |
        v
REJECTED
```

The exact rules for:

```text
ESTABLISHED
```

must be validated against Gmail fixtures before being treated as stable Domain policy.

This policy must remain independently testable and versioned.

---

## 68. Relationship Policy Representation

Conceptually:

```python
class RelationshipPolicy(Protocol):

    def evaluate(
        self,
        aggregate: EvidenceAggregate,
    ) -> RelationshipPolicyDecision:
        ...
```

The first implementation may instead use one concrete deterministic policy if introducing a Protocol provides no immediate implementation value.

Regardless of representation, policy rules must remain:

```text
explicit

testable

versionable

explainable
```

They must not become hidden conditions distributed throughout DiscoveryService.

---

## 69. Initial Temporal Policy

The first temporal policy should remain conservative.

Potential principles:

```text
ACCOUNT_DELETION
+
no later meaningful activity
        |
        v
HISTORICAL candidate
```

```text
recent meaningful Evidence
        |
        v
CURRENTLY_OBSERVED candidate
```

```text
insufficient temporal semantics
        |
        v
UNKNOWN
```

A source-record modification timestamp must not automatically establish current Service activity.

Temporal policy must operate on typed temporal information.

---

## 70. Discovery Application Service

The primary application orchestration boundary should be:

```text
DiscoveryService
```

or another equivalently scoped application use case.

Conceptually:

```python
class DiscoveryService:

    def process_observation(
        self,
        observation: Observation,
    ) -> DiscoveryOutcome:
        ...
```

Its responsibility is orchestration.

It must not absorb:

```text
Candidate Detection rules

Entity Resolution rules

Evidence Classification rules

Aggregation semantics

Relationship Assessment policy
```

Those remain in their respective components or policies.

---

## 71. Observation Processing Orchestration

Conceptually:

```text
Observation
     |
     +--------------------------------+
     |                                |
     v                                v
CandidateDetector               EvidenceClassifier
     |                                |
     v                                v
CandidateDetectionResult        ClassificationResult
     |                                |
     v                                v
CandidateIdentifier             EvidenceCandidate
     |                                |
     v                                v
Application Layer               Evidence Materialization
     |                                |
     v                                v
ServiceIdentifier                   Evidence
     |                                |
     v                                |
EntityResolver                        |
     |                                |
     +----------+----------+          |
     |          |          |          |
     v          v          v          |
 RESOLVED   UNRESOLVED  AMBIGUOUS     |
     |          |          |          |
     +----------+----------+----------+
                |
                v
      Aggregation Context
                |
                v
       EvidenceAggregator
                |
                v
       EvidenceAggregate
 SERVICE / UNRESOLVED / AMBIGUOUS
                |
                v
      RelationshipAssessor
                |
                v
 RelationshipAssessmentResult
                |
                v
       Application Layer
                |
                v
         Relationship
```

Canonical Relationship materialization requires a resolved canonical Service.

Evidence associated with:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

Service contexts remains available through the corresponding EvidenceAggregate scope.

It must not be arbitrarily materialized as a canonical User-Service Relationship.

An unresolved or ambiguous assessment may still be useful as an application processing result without creating a Domain Relationship.

---

## 72. Parallel Semantics vs Sequential Execution

Architecture defines Entity Resolution and Evidence Classification as independent branches.

The first Python implementation does not need actual parallel execution.

It may execute:

```text
Candidate Detection

Entity Resolution

Evidence Classification
```

sequentially in one process for simplicity, provided no semantic dependency is introduced between:

```text
resolution success
```

and:

```text
classification success
```

Therefore:

```text
parallel architecture
        !=
mandatory parallel threads/tasks
```

Valid combinations remain:

```text
Service RESOLVED
+
Evidence UNKNOWN
```

and:

```text
Service UNRESOLVED
+
Evidence PAYMENT
```

---

## 73. DiscoveryOutcome

A higher-level Application DTO may be useful for vertical orchestration.

Conceptually:

```python
@dataclass(frozen=True)
class DiscoveryOutcome:
    observation_id: ObservationId
    candidate_result: CandidateDetectionResult
    resolution_result: ResolutionResult | None
    classification_result: ClassificationResult
    evidence_ids: tuple[EvidenceId, ...]
    relationship_id: RelationshipId | None
```

This is an Application DTO rather than a Core Domain concept.

It should only be introduced if it simplifies orchestration or testing.

For:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

cases:

```python
relationship_id = None
```

may be valid while Evidence is still retained.

---

## 74. Transaction Boundary

For the initial local MVP, processing one Observation may represent one logical Application transaction.

However, Gmail collection may return batches.

Therefore the implementation must not couple Domain semantics to one database transaction model.

Persistence transaction strategy belongs to infrastructure.

The Application Layer is responsible for coordinating consistency between:

```text
Evidence lifecycle changes

Evidence materialization

Relationship updates
```

when those operations eventually share durable persistence.

---

## 75. Error Model

Expected Domain outcomes must not use exceptions.

For example:

```text
UNKNOWN

UNRESOLVED

AMBIGUOUS

NOT_CANDIDATE
```

are valid semantic outcomes.

Exceptions represent unexpected technical failures.

Therefore:

```python
resolve(...)
```

should return:

```text
ResolutionStatus.UNRESOLVED
```

rather than throwing:

```text
ServiceNotFoundError
```

for an ordinary unresolved identifier.

Likewise:

```text
ClassificationStatus.UNKNOWN
```

must not be implemented as a classification exception.

---

## 76. Infrastructure Exceptions

Provider-specific failures should be translated at the adapter boundary.

For example:

```text
Google API exception
        |
        v
GmailConnector
        |
        v
provider-independent collection error
```

Downstream Discovery components must not depend on Google exception classes.

Previously valid Domain data must not become invalid simply because a later Provider interaction fails.

---

## 77. Configuration

Rules and policies likely to evolve should not all be hard-coded inside component classes.

Candidate configuration areas include:

```text
generic email Provider domains

Candidate Detection patterns

Evidence Classification rules

Service Registry mappings

Relationship Assessment policy

Temporal policy
```

Configuration should remain:

```text
versionable

testable

local-first

human-reviewable
```

Material configuration changes should remain traceable when they affect reproducibility.

---

## 78. Configuration Format

The first implementation may use:

```text
YAML
```

or:

```text
JSON
```

for small rule and Registry datasets.

Python code remains appropriate for:

```text
complex deterministic algorithms

validation

normalization

policy composition
```

The exact format should be selected according to:

```text
clarity

testability

versionability

implementation simplicity
```

rather than abstract configurability.

---

## 79. Testing Strategy

The implementation requires multiple testing layers:

```text
Unit Tests

Contract Tests

Integration Tests

Vertical Tests
```

Tests are part of architecture validation rather than only regression protection.

---

## 80. Unit Tests

Unit tests should cover:

```text
email-address parsing

domain normalization

Candidate Detection

CandidateIdentifier materialization

ServiceIdentifier normalization

Evidence Classification rules

Evidence lifecycle transitions

EvidenceStatus filtering

EvidenceContribution construction

resolved aggregation

unresolved aggregation

ambiguous aggregation

Relationship policy

Temporal policy

Domain invariants
```

These tests must not require Gmail connectivity.

---

## 81. Contract Tests

Connector adapters should be tested against common Connector expectations.

For example:

```text
every produced Observation references one ConnectedSource

no Provider credential appears in Observation payload

partial collection is not reported as complete

Provider failures are translated

authorization requirements can be prepared before collection

one ConnectedSource can be disconnected independently
```

Equivalent contract tests should later be reusable for Outlook or other Connectors.

---

## 82. Integration Tests

Gmail adapter integration tests should validate:

```text
Google representation
        |
        v
GmailConnector
        |
        v
EmailMessageMetadataV1
        |
        v
Observation
```

External Gmail API calls should normally be isolated or mocked for automated tests.

Controlled live integration tests may be maintained separately.

---

## 83. Vertical Tests

The most important architecture-validation tests should exercise:

```text
Observation
      |
      +--------------------+
      |                    |
      v                    v
Candidate Detection   Classification
      |                    |
      v                    v
CandidateIdentifier      EvidenceCandidate
      |                    |
      v                    v
ServiceIdentifier       Evidence
      |
      v
Resolution
      |
   +--+---------+
   |     |      |
   v     v      v
 RES   UNR     AMB
   \     |      /
    \    |     /
     v   v    v
     Aggregation
         |
         v
     Assessment
         |
         v
Relationship when resolvable
```

Example fixture:

```text
From:
no-reply@spotify.com

Subject:
Verify your email address
```

Expected:

```text
Candidate:
CANDIDATE

ServiceIdentifier:
spotify.com

Resolution:
Spotify

Evidence:
ACCOUNT_VERIFICATION

Relationship:
according to explicit MVP policy
```

---

## 84. Unknown-State Tests

Tests must deliberately validate uncertainty.

Examples:

```text
unknown domain
        ->
ResolutionStatus.UNRESOLVED
```

```text
multiple Registry matches
        ->
ResolutionStatus.AMBIGUOUS
```

```text
ambiguous subject
        ->
ClassificationStatus.UNKNOWN
```

```text
unsupported ObservationType
        ->
ProcessingStatus.UNSUPPORTED
```

```text
insufficient Relationship Evidence
        ->
RelationshipStatus.UNKNOWN
```

UNKNOWN, UNRESOLVED and AMBIGUOUS paths are first-class test cases.

---

## 85. Privacy Tests

Automated tests should verify that:

```text
password

OAuth token

refresh token

OTP seed

recovery code

private key
```

cannot appear in ordinary Discovery Observations where schemas do not allow them.

For Gmail specifically, tests should demonstrate that:

```text
EMAIL_MESSAGE_METADATA
```

does not contain:

```text
message body

attachment content

OAuth credentials
```

Credential material must remain behind CredentialStore.

---

## 86. Dependency Tests

The codebase should, where practical, test architectural dependency rules.

For example:

```text
domain/
```

must not import modules from:

```text
connectors/

infrastructure/
```

Likewise, Discovery components should not import:

```text
Google Gmail API types

concrete repositories

SQLite implementations
```

A lightweight import-boundary test is sufficient initially.

---

## 87. Logging

Logs must not become an uncontrolled copy of User data.

The implementation should avoid logging:

```text
full email subjects by default

OAuth tokens

raw message bodies

password-manager secrets

complete Observation payloads

credentials
```

Logs should prefer:

```text
internal IDs

processing states

component versions

reason codes

counts

sanitized references
```

Diagnostic usefulness does not override data minimization.

---

## 88. Provenance

The implementation must preserve sufficient provenance to reconstruct:

```text
ConnectedSource
      |
      v
Observation
      |
      +------------------+
      |                  |
      v                  v
ServiceIdentifier      Evidence
      |                  |
      v                  |
Resolution              |
      |                  |
      v                  |
Service ----------------+
            |
            v
EvidenceAggregate
            |
            v
RelationshipAssessmentResult
            |
            v
Relationship
```

Application helper objects such as:

```text
EvidenceContribution
```

must not replace source provenance.

Version fields should be retained where materially relevant.

---

## 89. Versioning

The first implementation should distinguish versions of:

```text
Observation schemas

Candidate Detector

Candidate Detection rule sets where material

Entity Resolver

Service Registry data

Evidence Classifier

Evidence Classification rule sets where material

Aggregator

Aggregation Policy

Relationship Assessor

Relationship Policy
```

Version identifiers may initially be simple strings or integers.

A framework-wide semantic versioning system is not required for the MVP.

---

## 90. AI Provider Boundary

No AI Provider is required for the Gmail Vertical MVP.

If AI is later introduced, it must sit behind a task-specific port such as:

```text
SemanticClassifier

ResolutionAssistant

ExplanationGenerator
```

depending on the task.

The Domain and primary Discovery interfaces must not import SDK types from providers such as:

```text
OpenAI

Google Gemini

Azure OpenAI

Anthropic
```

AI integration remains replaceable infrastructure.

---

## 91. Local-First MVP

The first MVP should be executable as a local application.

The initial design should not require:

```text
cloud backend

remote database

remote AI

distributed queue

remote graph database
```

except for interaction with the explicitly authorized external source itself.

For Gmail, Provider interaction is remote by definition.

Discovery processing should nevertheless remain local where practical.

---

## 92. Gmail Authorization

Google authorization is a Connector concern.

OAuth material should be managed through:

```text
GmailConnector
+
CredentialStore
```

and not stored inside ordinary:

```text
ConnectedSource
```

Domain fields.

The Connector must support:

```text
authorization status

permission requirements

authorization preparation

collection

disconnect
```

The exact Google OAuth implementation must be validated against current official Gmail API documentation during implementation.

---

## 93. First Vertical Slice Boundary

The Gmail Vertical MVP should exercise:

```text
one User

one EMAIL IdentitySeed

one Gmail ConnectedSource

one GmailConnector

EMAIL_MESSAGE_METADATA v1

deterministic Candidate Detection

Application-level CandidateIdentifier materialization

ServiceIdentifier

deterministic Entity Resolution through local ServiceRegistry

RESOLVED / UNRESOLVED / AMBIGUOUS handling

deterministic Evidence Classification

ACTIVE Evidence materialization

Evidence lifecycle repository semantics

EvidenceContribution construction

on-demand Evidence Aggregation

SERVICE / UNRESOLVED / AMBIGUOUS aggregation scopes

deterministic Relationship Assessment

Relationship materialization for canonical Service contexts
```

This scope is intentionally narrow.

---

## 94. MVP Success Criteria

The vertical slice is successful when it can demonstrate, with controlled Gmail-derived fixtures or authorized metadata:

```text
Gmail-specific information remains inside GmailConnector

Observations conform to typed schemas

source timestamps preserve TemporalSemantics

Candidate Detection does not treat every sender as a Service

CandidateIdentifier remains distinct from ServiceIdentifier

Application Layer materializes ServiceIdentifier

known identifiers resolve to canonical Services

unknown identifiers remain UNRESOLVED

ambiguous resolution remains representable

clear email subjects produce deterministic Evidence

ambiguous subjects may remain UNKNOWN

Evidence is materialized as ACTIVE

Evidence lifecycle transitions are representable

unresolved Evidence is preserved

ambiguous Evidence is preserved

Aggregates contain only eligible current Evidence

SourceSummary can be reconstructed from provenance

RelationshipStatus and TemporalStatus are evaluated independently

canonical Relationships reference one User and one Service

every Relationship remains explainable through Evidence provenance
```

---

## 95. MVP Does Not Require

The first vertical slice does not require:

```text
message body access

attachments

AI

Password Manager integration

Outlook integration

browser integration

Account Entity

Organization Entity

Service creation workflow

automatic Registry expansion

graph database

production synchronization

continuous monitoring

commercial-scale Service Registry

numerical Confidence
```

An unknown Service may remain UNRESOLVED throughout the MVP.

---

## 96. Implementation Order

The preferred implementation order is:

```text
1. Domain identifiers and enums

2. TemporalValue and Domain value objects

3. Core Domain entities

4. Processing Result objects

5. Typed Observation payloads

6. Ports / Protocols

7. In-memory repositories

8. ServiceRegistry implementation

9. deterministic CandidateDetector

10. CandidateIdentifier -> ServiceIdentifier materialization

11. deterministic EntityResolver

12. deterministic EvidenceClassifier

13. Evidence materialization

14. Evidence lifecycle operations

15. EvidenceContribution construction

16. EvidenceAggregator

17. RelationshipAssessor

18. Relationship materialization

19. application orchestration

20. GmailConnector adapter

21. Connector contract tests

22. end-to-end vertical tests

23. authorized Gmail integration
```

This allows almost the entire architecture to be validated without depending immediately on live Gmail connectivity.

---

## 97. Decisions Made by Draft v0.1

The Implementation Model makes the following initial technical decisions.

### IM-001 - Python Modular Monolith

The first implementation uses one Python application with explicit internal boundaries.

### IM-002 - Domain Has No Infrastructure Dependency

Core Domain modules must not import Provider, persistence or UI frameworks.

### IM-003 - Dataclasses for Domain Structures

Python dataclasses are the initial representation for Domain structures and processing values.

### IM-004 - Explicit Enums

Controlled states use explicit Enum / StrEnum types.

### IM-005 - Protocol-Based Ports

Behavioral boundaries use Python Protocols where practical.

### IM-006 - Typed Observation Payloads

Observation payloads must not default to arbitrary:

```python
dict[str, Any]
```

### IM-007 - Processing Results Are Separate Types

The implementation preserves separate:

```text
CandidateDetectionResult

ResolutionResult

ClassificationResult

AggregationResult

RelationshipAssessmentResult
```

types.

### IM-008 - ServiceRegistry Is a Port

The Resolver depends on a ServiceRegistry abstraction.

### IM-009 - Aggregate Computed On Demand Initially

EvidenceAggregate is initially calculated rather than treated as authoritative persisted state.

### IM-010 - Deterministic-Only First Vertical Slice

AI is not required to complete the Gmail Vertical MVP.

### IM-011 - In-Memory Persistence First

Repository interfaces are validated first using in-memory implementations.

### IM-012 - Gmail Metadata First

The first Gmail capability is:

```text
SERVICE_DISCOVERY_METADATA
```

### IM-013 - No Graph Database Initially

Relationship and Service structures provide sufficient graph semantics for the first vertical slice.

### IM-014 - Expected Uncertainty Uses Results, Not Exceptions

```text
UNKNOWN

UNRESOLVED

AMBIGUOUS

NOT_CANDIDATE
```

remain ordinary semantic outcomes.

### IM-015 - ServiceIdentifier Materialization Belongs to the Application Layer

CandidateIdentifier is converted into the Domain ServiceIdentifier representation before EntityResolver invocation.

The Resolver therefore operates on:

```text
ServiceIdentifier
```

rather than:

```text
CandidateIdentifier
```

### IM-016 - Aggregation Supports Resolved, Unresolved and Ambiguous Contexts

Evidence is not discarded when canonical Service resolution is incomplete.

The Aggregator supports:

```text
SERVICE

UNRESOLVED_SERVICE_CANDIDATE

AMBIGUOUS_SERVICE_CANDIDATE
```

scopes.

### IM-017 - Aggregation Provenance Is Prepared by the Application Layer

The Application Layer resolves Observation and ConnectedSource provenance into EvidenceContribution values before invoking the EvidenceAggregator.

The Aggregator does not query infrastructure repositories directly.

### IM-018 - Temporal Information Uses Typed TemporalValue

Source-derived timestamps are represented together with their TemporalSemantics.

The implementation must preserve:

```text
timestamp
+
meaning
```

as one typed value.

### IM-019 - Evidence Lifecycle Transitions Are Explicit

EvidenceRepository supports explicit:

```text
ACTIVE

SUPERSEDED

REJECTED
```

lifecycle transitions with provenance.

Evidence reinterpretation does not silently rewrite the previous EvidenceType.

### IM-020 - Relationship Materializes Assessment Provenance

Current Relationship state preserves:

```text
AssessmentMethod

AssessorVersion

AssessmentPolicyVersion

Evidence basis
```

### IM-021 - Minimum Connector Port Includes Authorization Preparation and Disconnect

The initial Connector interface includes:

```text
prepare_authorization()

disconnect()
```

in addition to capability inspection, permission analysis, authorization-state inspection and collection.

---

## 98. Decisions Deferred

The following implementation decisions remain deliberately deferred:

```text
SQLite vs another durable local store

final persistence schema

final Service Registry source

Service creation workflow

Service merge implementation

Service split implementation

final Gmail OAuth library integration

incremental Gmail synchronization

CollectionRun representation

final Evidence taxonomy

complete multilingual support

semantic Evidence deduplication

final Relationship assessment thresholds

AI adapter design

Service Graph persistence

Account implementation

Organization implementation
```

They should be decided only when required by the vertical slice or subsequent empirical validation.

In particular:

```text
UNRESOLVED
```

must remain a valid outcome rather than forcing an early Service-creation policy.

---

## 99. Validation Strategy

Implementation should proceed through increasingly realistic validation layers:

```text
Domain unit tests
        |
        v
Component unit tests
        |
        v
Repository and lifecycle tests
        |
        v
Connector contract tests
        |
        v
In-memory Discovery vertical tests
        |
        v
Gmail adapter integration tests
        |
        v
Authorized Gmail Vertical MVP
        |
        v
Empirical findings
        |
        v
Architecture / Domain refinement if justified
```

The first important milestone is not Gmail API connectivity.

It is successful execution of the complete Discovery pipeline using controlled in-memory fixtures.

That pipeline must demonstrate:

```text
Observation
        |
        +---------------------+
        |                     |
        v                     v
Candidate Detection     Classification
        |                     |
        v                     v
CandidateIdentifier       EvidenceCandidate
        |                     |
        v                     v
ServiceIdentifier          Evidence
        |                     |
        v                     |
Resolution                  |
        |                     |
 RES / UNR / AMB             |
        \                     /
         \                   /
          v                 v
          Evidence Aggregation
                   |
                   v
           EvidenceAggregate
                   |
                   v
        Relationship Assessment
                   |
                   v
       Relationship materialization
       when canonical Service exists
```

This preserves the project principle:

> **Implementation evidence before new abstractions.**

---

## 100. Next Step

After this Implementation Model passes consistency review, the project should stop producing additional abstract Discovery design layers and begin executable implementation.

The next repository work should be:

```text
Python project skeleton
        |
        v
Domain IDs and Enums
        |
        v
Domain Value Objects
        |
        v
Core Domain Entities
        |
        v
Processing Results
        |
        v
Ports
        |
        v
In-Memory Repositories
        |
        v
ServiceRegistry
        |
        v
Deterministic CandidateDetector
        |
        v
ServiceIdentifier Materialization
        |
        v
Deterministic EntityResolver
        |
        v
Deterministic EvidenceClassifier
        |
        v
Evidence Materialization
        |
        v
Evidence Lifecycle
        |
        v
EvidenceContribution
        |
        v
EvidenceAggregator
        |
        v
RelationshipAssessor
        |
        v
Application Orchestration
        |
        v
GmailConnector
        |
        v
Gmail Vertical MVP
```

The objective is not to prove that every implementation decision in Draft v0.1 is final.

The objective is to create the smallest clean implementation that can verify whether:

```text
Architecture v0.3
+
Domain Model v0.3
+
Discovery Contracts v0.1
+
Implementation Model v0.1
```

survive contact with executable code and real Gmail-derived data.

The initial implementation must preserve:

```text
Provider isolation

data minimization

Progressive Permission

typed Observations

explicit temporal semantics

CandidateIdentifier / ServiceIdentifier separation

explicit uncertainty

unresolved Evidence preservation

ambiguous Evidence preservation

Evidence lifecycle

derived Aggregate semantics

RelationshipStatus / TemporalStatus separation

no numerical Confidence

deterministic-first processing

local-first processing

explainability

source provenance
```

Any subsequent architecture, Domain or contract change should be justified by:

```text
implementation evidence

empirical behavior

test results

privacy constraints

new validated cross-source requirements

or a demonstrated inconsistency
```

rather than speculative abstraction.

The implementation phase may now begin without introducing another Discovery processing layer.
