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

# 5. Architectural Style

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

# 6. Dependency Direction

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

---

# 7. Proposed Project Structure

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
├── integration/
└── vertical/
```

---

# 8. Domain Representation Strategy

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

# 9. Identifier Types

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

# 10. User

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

# 11. IdentitySeed

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

# 12. ConnectedSource

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

Those belong behind the CredentialStore port.

---

# 13. SourceType

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

# 14. Provider

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

# 15. Observation

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
    observed_at: datetime | None
    collected_at: datetime
    temporal_semantics: TemporalSemantics
    payload: ObservationPayload
```

---

# 16. ObservationPayload

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

# 17. EMAIL_MESSAGE_METADATA v1

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

---

# 18. ObservationType

Initial MVP enum:

```python
class ObservationType(StrEnum):
    EMAIL_MESSAGE_METADATA = "EMAIL_MESSAGE_METADATA"
```

Additional ObservationTypes should be introduced only when a corresponding source or capability is implemented.

The codebase should not populate enums with every hypothetical future ObservationType in advance.

---

# 19. SchemaVersion

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

# 20. TemporalSemantics

Initial values relevant to Gmail:

```python
class TemporalSemantics(StrEnum):
    MESSAGE_TIME = "MESSAGE_TIME"
    UNKNOWN = "UNKNOWN"
```

Additional semantics such as:

```text
SOURCE_RECORD_CREATED
SOURCE_RECORD_MODIFIED
VISIT_TIME
```

can be introduced when corresponding ObservationTypes are implemented.

---

# 21. CandidateIdentifier

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

---

# 22. ServiceIdentifier

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

---

# 23. Service

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

# 24. EvidenceType

The first implementation should use a controlled enum.

The Gmail MVP should initially support the EvidenceTypes required by Scenario 001:

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

# 25. EvidenceStatus

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

---

# 26. Evidence

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

Temporal provenance should remain available through supporting Observations.

If implementation demonstrates that Evidence requires independent derived TemporalValues, they may be introduced without changing the Entity boundary.

---

# 27. EvidenceCandidate

Classifier output should not construct Domain Evidence directly.

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
Evidence
```

---

# 28. RelationshipStatus

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

# 29. TemporalStatus

```python
class TemporalStatus(StrEnum):
    UNKNOWN = "UNKNOWN"
    CURRENTLY_OBSERVED = "CURRENTLY_OBSERVED"
    HISTORICAL = "HISTORICAL"
```

TemporalStatus remains independent from RelationshipStatus.

---

# 30. Relationship

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
    assessor_version: str
    assessment_policy_version: str
    assessed_at: datetime
```

The Relationship represents the current materialized assessment.

Historical assessment results remain separate.

---

# 31. Processing Status

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

---

# 32. CandidateDetectionResult

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

---

# 33. ResolutionResult

```python
@dataclass(frozen=True)
class ResolutionResult:
    observation_id: ObservationId
    input_identifiers: tuple[CandidateIdentifier, ...]
    normalized_identifiers: tuple[ServiceIdentifier, ...]
    processing_status: ProcessingStatus
    resolution_status: ResolutionStatus | None
    resolved_service_id: ServiceId | None
    alternative_service_ids: tuple[ServiceId, ...]
    method: ResolutionMethod | None
    reason_codes: tuple[str, ...]
    resolver_version: str
```

This remains:

```text
Processing Result / Value Object
```

and not a Service Entity.

---

# 34. ClassificationResult

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

---

# 35. EvidenceAggregate

EvidenceAggregate is a Derived View.

Conceptually:

```python
@dataclass(frozen=True)
class EvidenceAggregate:
    scope: AggregationScope
    service_id: ServiceId | None
    identity_seed_ids: tuple[IdentitySeedId, ...]
    evidence_ids: tuple[EvidenceId, ...]
    evidence_summary: EvidenceSummary
    source_summary: SourceSummary
    temporal_summary: TemporalSummary
    conflict_summary: ConflictSummary
    coverage_summary: CoverageSummary | None
    aggregator_version: str
```

It must remain rebuildable.

---

# 36. AggregationResult

```python
@dataclass(frozen=True)
class AggregationResult:
    processing_status: ProcessingStatus
    aggregation_status: AggregationStatus | None
    aggregate: EvidenceAggregate | None
    aggregator_version: str
```

This remains a Processing Result.

---

# 37. RelationshipAssessmentResult

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

The application layer uses this result to create or update `Relationship`.

---

# 38. Protocol Strategy

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

# 39. Connector Port

Conceptually:

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

    def collect(
        self,
        request: CollectionRequest,
    ) -> CollectionResult:
        ...
```

Disconnect/revoke operations may be added when needed by the Gmail integration lifecycle.

---

# 40. ServiceCandidateDetector Port

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

---

# 41. EntityResolver Port

```python
class EntityResolver(Protocol):

    def resolve(
        self,
        request: ResolutionRequest,
    ) -> ResolutionResult:
        ...
```

The Resolver should depend on:

```text
ServiceRegistry
```

through an interface.

It must not directly depend on the concrete Registry implementation.

---

# 42. EvidenceClassifier Port

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

---

# 43. EvidenceAggregator Port

```python
class EvidenceAggregator(Protocol):

    def aggregate(
        self,
        request: AggregationRequest,
    ) -> AggregationResult:
        ...
```

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

# 44. RelationshipAssessor Port

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

---

# 45. Repository Boundaries

The Domain must not depend on a specific persistence implementation.

Initial repository ports should include only what the vertical slice requires.

Potential interfaces include:

```text
ConnectedSourceRepository

ObservationRepository

ServiceRepository / ServiceRegistry

EvidenceRepository

RelationshipRepository
```

Repositories should expose use-case-oriented operations rather than generic persistence mechanics where practical.

---

# 46. ObservationRepository

Conceptually:

```python
class ObservationRepository(Protocol):

    def save(
        self,
        observation: Observation,
    ) -> None:
        ...

    def find_by_source_reference(
        self,
        connected_source_id: ConnectedSourceId,
        source_reference: SourceReference,
    ) -> Observation | None:
        ...
```

The second operation supports idempotent collection.

---

# 47. ServiceRegistry Port

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

The Domain must not know which implementation is used.

---

# 48. EvidenceRepository

Conceptually:

```python
class EvidenceRepository(Protocol):

    def save(
        self,
        evidence: Evidence,
    ) -> None:
        ...

    def find_active_by_service(
        self,
        service_id: ServiceId,
    ) -> tuple[Evidence, ...]:
        ...
```

Lifecycle operations may later require:

```text
supersede

reject

find_by_observation
```

They should be added when concrete orchestration requires them.

---

# 49. RelationshipRepository

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

The initial Domain invariant implies at most one current User-Service Relationship for a given pair under the current model.

---

# 50. CredentialStore Port

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

---

# 51. First Persistence Strategy

The first Gmail Vertical MVP should prefer the simplest persistence capable of validating the architecture.

The initial implementation may therefore use:

```text
in-memory repositories
```

for unit and vertical tests.

A local durable implementation may subsequently use:

```text
SQLite
```

if persistence becomes necessary for the MVP.

The Domain and application interfaces must make the choice replaceable.

The architecture must not depend on SQLite.

---

# 52. No Graph Database Requirement

Although the output is conceptually a Service Graph, the first vertical slice does not require:

```text
Neo4j
Amazon Neptune
Azure Cosmos DB Gremlin
```

The graph semantics can initially be represented through:

```text
Relationship entities

Service references

Identity references

repository queries
```

A graph database should be introduced only if concrete query and scale requirements justify it.

---

# 53. Gmail Connector Adapter

The first infrastructure adapter will be:

```text
GmailConnector
```

located conceptually under:

```text
connectors/gmail/
```

or:

```text
infrastructure/google/
```

depending on final package ownership.

It implements:

```text
Connector
```

and translates Gmail-specific data into:

```text
EMAIL_MESSAGE_METADATA v1
```

Observations.

---

# 54. Gmail API Isolation

Only the Gmail infrastructure adapter should directly depend on Google-specific API representations.

The following must not import Gmail API types:

```text
domain/

discovery/candidate_detection/

discovery/entity_resolution/

discovery/evidence_classification/

discovery/evidence_aggregation/

discovery/relationship_assessment/
```

This dependency rule should be enforced through tests or static architecture checks if practical.

---

# 55. Gmail MVP Collection Capability

The first implemented capability should be:

```text
SERVICE_DISCOVERY_METADATA
```

It should collect only the information required for metadata-based Discovery.

The first vertical slice should not require:

```text
EMAIL_MESSAGE_CONTENT

ATTACHMENT_CONTENT
```

Progressive Permission must therefore be preserved from the first implementation.

---

# 56. Gmail Observation Mapping

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

where appropriate.

---

# 57. Initial Candidate Detection Policy

The Gmail MVP should begin with deterministic candidate detection.

Initial signals may include:

```text
sender domain

known User IdentitySeeds

generic consumer email-provider domains

local/internal exclusion rules

known infrastructure patterns
```

The actual rule vocabulary should be stored outside the Domain entity classes.

---

# 58. Initial Identifier Extraction

For Gmail:

```text
sender email
      |
      v
email-domain parser
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

---

# 59. Initial Entity Resolution Strategy

The first Resolver should implement a small deterministic pipeline:

```text
CandidateIdentifier
        |
        v
normalize
        |
        v
ServiceRegistry exact lookup
        |
    +---+---+
    |       |
 match    no match
    |       |
    v       v
RESOLVED  UNRESOLVED
```

`AMBIGUOUS` must still exist even if early Registry data rarely produces it.

---

# 60. Initial ServiceRegistry Data

The initial ServiceRegistry should be intentionally small.

It may contain a curated set of Services needed by:

- unit tests;
- vertical fixtures;
- first empirical Gmail samples.

The Registry must not attempt to become a universal Internet Service database before the MVP.

Unknown domains should remain:

```text
UNRESOLVED
```

---

# 61. Initial Evidence Classification Strategy

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

# 62. Unknown Classification

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

---

# 63. Evidence Materialization

The application layer should perform:

```text
ClassificationResult
       |
       v
EvidenceCandidate
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

---

# 64. Evidence Lifecycle Operations

The application layer should eventually expose explicit operations conceptually equivalent to:

```text
activate

supersede

reject
```

Draft v0.1 does not require a generic lifecycle engine.

For the Gmail Vertical MVP, initial Evidence materialization as:

```text
ACTIVE
```

is sufficient until reclassification is exercised.

Tests should nevertheless model SUPERSEDED and REJECTED behavior.

---

# 65. Initial Aggregation Strategy

The first Aggregator should:

1. accept a Service scope;
2. select eligible Evidence;
3. include ACTIVE Evidence;
4. exclude SUPERSEDED Evidence;
5. exclude REJECTED Evidence;
6. count Evidence by EvidenceType;
7. preserve Evidence IDs;
8. preserve Identity references;
9. preserve ConnectedSource / SourceType provenance;
10. calculate typed temporal summaries;
11. preserve conflicts explicitly.

No weighting is required.

---

# 66. Aggregate Persistence Strategy

For the first vertical slice:

```text
compute EvidenceAggregate on demand
```

is preferred.

Reason:

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

---

# 67. Initial Relationship Assessment Policy

The first MVP requires an explicit deterministic policy.

It should remain conservative.

A candidate starting point is:

```text
No eligible Evidence
        ->
UNKNOWN
```

```text
MARKETING / NEWSLETTER / PRIVACY_NOTICE only
        ->
OBSERVED
```

```text
account-related or authentication Evidence
        ->
candidate for ESTABLISHED
```

```text
explicit User rejection
        ->
REJECTED
```

However, the exact `ESTABLISHED` rules must be validated against Scenario 001 fixtures before being treated as stable Domain policy.

The policy should therefore be represented explicitly rather than embedded throughout application code.

---

# 68. Relationship Policy Representation

Conceptually:

```python
class RelationshipPolicy(Protocol):

    def evaluate(
        self,
        aggregate: EvidenceAggregate,
    ) -> RelationshipPolicyDecision:
        ...
```

The initial implementation may instead use one concrete deterministic policy if additional abstraction provides no immediate value.

The policy itself must remain separately testable.

---

# 69. Initial Temporal Policy

The first temporal policy should remain conservative.

Potential principles:

```text
ACCOUNT_DELETION with no later meaningful activity
        ->
HISTORICAL candidate
```

```text
recent meaningful Evidence
        ->
CURRENTLY_OBSERVED candidate
```

```text
insufficient temporal semantics
        ->
UNKNOWN
```

A source-record modification timestamp must not automatically establish current Service activity.

---

# 70. Discovery Application Service

The primary application orchestration boundary should be:

```text
DiscoveryService
```

or an equivalently named application use case.

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

It must not absorb component-specific semantic logic.

---

# 71. Observation Processing Orchestration

Conceptually:

```text
Observation
     |
     +------------------------------+
     |                              |
     v                              v
CandidateDetector             EvidenceClassifier
     |                              |
     v                              v
CandidateDetectionResult      ClassificationResult
     |                              |
     v                              v
ServiceIdentifier             EvidenceCandidate
     |                              |
     v                              v
EntityResolver                Evidence Materialization
     |                              |
     v                              v
ResolutionResult                  Evidence
     |                              |
     +---------------+--------------+
                     |
                     v
             Service-Level Evidence
                     |
                     v
             EvidenceAggregator
                     |
                     v
             EvidenceAggregate
                     |
                     v
           RelationshipAssessor
                     |
                     v
      RelationshipAssessmentResult
                     |
                     v
         Relationship Materialization
```

The application service coordinates this flow.

---

# 72. Parallel Semantics vs Sequential Execution

Architecture defines Entity Resolution and Evidence Classification as independent branches.

The first Python implementation does not need actual parallel execution.

It may execute:

```text
Candidate Detection
Entity Resolution
Evidence Classification
```

sequentially in one process for simplicity, provided no semantic dependency is introduced between resolution success and classification success.

Therefore:

```text
parallel architecture
        !=
mandatory parallel threads/tasks
```

This distinction prevents unnecessary concurrency in the MVP.

---

# 73. DiscoveryOutcome

A higher-level application result may be useful for the vertical slice.

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

This is an application DTO rather than a Core Domain concept.

It should only be introduced if it simplifies vertical orchestration or testing.

---

# 74. Transaction Boundary

For the initial local MVP, one processed Observation may be one logical application transaction.

However, Gmail collection may produce batches.

Therefore the implementation should avoid coupling Domain semantics to one database transaction model.

Persistence transaction strategy belongs to infrastructure.

---

# 75. Error Model

Expected Domain outcomes must not use exceptions.

For example:

```text
UNKNOWN
UNRESOLVED
AMBIGUOUS
NOT_CANDIDATE
```

are valid processing outcomes.

Exceptions should represent unexpected technical failures.

This means:

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

---

# 76. Infrastructure Exceptions

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

---

# 77. Configuration

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

---

# 78. Configuration Format

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

The exact format should be selected based on readability and testing rather than abstract configurability.

---

# 79. Testing Strategy

The implementation requires multiple testing layers.

```text
Unit Tests

Contract Tests

Integration Tests

Vertical Tests
```

---

# 80. Unit Tests

Unit tests should cover:

```text
email parsing

domain normalization

Candidate Detection

Evidence Classification rules

EvidenceStatus filtering

aggregation

Relationship policy

temporal policy

Domain invariants
```

These tests should not require Gmail connectivity.

---

# 81. Contract Tests

Connector adapters should be tested against the common Connector expectations.

For example:

```text
every produced Observation references one ConnectedSource

no Provider credential appears in Observation payload

partial collection is not reported as complete

Provider failures are translated
```

Equivalent contract tests can later be reused for Outlook or other Connectors.

---

# 82. Integration Tests

Gmail adapter integration tests should validate:

```text
Google representation
        |
        v
GmailConnector
        |
        v
EmailMessageMetadataV1
```

External Gmail API calls should normally be isolated or mocked for automated tests.

Controlled live integration tests may be maintained separately.

---

# 83. Vertical Tests

The most important architecture-validation tests should exercise:

```text
Observation
      |
      v
Candidate Detection
      |
      v
Resolution
      |
      +
      |
Classification
      |
      v
Evidence
      |
      v
Aggregation
      |
      v
Assessment
      |
      v
Relationship
```

using fixed fixtures.

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

Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION

Relationship:
according to explicit MVP policy
```

---

# 84. Unknown-State Tests

Tests must deliberately validate uncertainty.

Examples:

```text
unknown domain
        ->
UNRESOLVED
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

UNKNOWN paths are first-class test cases.

---

# 85. Privacy Tests

Automated tests should verify that:

```text
password

OAuth token

refresh token

OTP seed

recovery code
```

cannot appear in ordinary Discovery Observations where schemas do not allow them.

For Gmail specifically, tests should demonstrate that:

```text
EMAIL_MESSAGE_METADATA
```

does not contain the message body.

---

# 86. Dependency Tests

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

A lightweight import-boundary test is sufficient initially.

---

# 87. Logging

Logs must not become an uncontrolled copy of User data.

The implementation should avoid logging:

```text
full email subjects by default

OAuth tokens

raw message bodies

password-manager secrets

complete Observation payloads
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

---

# 88. Provenance

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
Resolution           Classification
      |                  |
      v                  v
Service             Evidence
      \                  /
       \                /
        v              v
          Relationship
```

Version fields should be retained where materially relevant.

---

# 89. Versioning

The first implementation should distinguish versions of:

```text
Observation schemas

Candidate Detector

Entity Resolver

Evidence Classifier

Aggregator

Relationship Assessor

Relationship Policy

Service Registry data
```

Version identifiers may initially be simple strings or integers.

A complex framework-wide versioning system is not required.

---

# 90. AI Provider Boundary

No AI Provider is required for the Gmail Vertical MVP.

If AI is later introduced, it must sit behind a port such as:

```text
SemanticClassifier
```

or another task-specific interface.

The Domain and primary Discovery interfaces must not import:

```text
OpenAI
Gemini
Azure OpenAI
Anthropic
```

SDK types.

AI integration remains replaceable infrastructure.

---

# 91. Local-First MVP

The first MVP should be executable as a local application.

The initial design should not require:

```text
cloud backend

remote database

remote AI

distributed queue

remote graph database
```

unless Gmail authorization itself requires external Provider interaction.

This provides a concrete interpretation of the project's local-first principle.

---

# 92. Gmail Authorization

Google authorization is a Connector concern.

OAuth material should be managed through:

```text
GmailConnector
+
CredentialStore
```

and not stored inside:

```text
ConnectedSource
```

ordinary Domain fields.

The exact OAuth implementation must be validated against current official Gmail API documentation during implementation.

---

# 93. First Vertical Slice Boundary

The Gmail Vertical MVP should exercise:

```text
one User

one EMAIL IdentitySeed

one Gmail ConnectedSource

one GmailConnector

EMAIL_MESSAGE_METADATA v1

deterministic Candidate Detection

deterministic Entity Resolution through local ServiceRegistry

deterministic Evidence Classification

ACTIVE Evidence materialization

on-demand Evidence Aggregation

deterministic Relationship Assessment

Relationship output
```

This scope is intentionally narrow.

---

# 94. MVP Success Criteria

The vertical slice is successful when it can demonstrate, with controlled Gmail-derived fixtures or authorized metadata:

```text
Gmail-specific information remains inside GmailConnector

Observations conform to typed schemas

Candidate Detection does not treat every sender as a Service

known domains can resolve to canonical Services

unknown domains remain UNRESOLVED

clear email subjects produce deterministic Evidence

ambiguous subjects may remain UNKNOWN

Evidence is materialized as ACTIVE

Aggregates contain only eligible current Evidence

RelationshipStatus and TemporalStatus are evaluated independently

every Relationship remains explainable through Evidence provenance
```

---

# 95. MVP Does Not Require

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

graph database

production synchronization

continuous monitoring

commercial-scale Service Registry

numerical Confidence
```

---

# 96. Implementation Order

The preferred implementation order is:

```text
1. Domain identifiers and enums

2. Core Domain entities

3. Processing Result objects

4. Typed Observation payloads

5. Ports / Protocols

6. In-memory repositories

7. ServiceRegistry implementation

8. deterministic CandidateDetector

9. deterministic EntityResolver

10. deterministic EvidenceClassifier

11. Evidence materialization

12. EvidenceAggregator

13. RelationshipAssessor

14. application orchestration

15. GmailConnector adapter

16. end-to-end vertical tests

17. authorized Gmail integration
```

This allows most of the architecture to be validated without depending immediately on the Gmail API.

---

# 97. Decisions Made by Draft v0.1

The Implementation Model makes the following initial technical decisions:

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

Observation payloads must not default to arbitrary `dict[str, Any]`.

### IM-007 - Processing Results Are Separate Types

CandidateDetectionResult, ResolutionResult, ClassificationResult, AggregationResult and RelationshipAssessmentResult remain distinct processing objects.

### IM-008 - ServiceRegistry Is a Port

The Resolver depends on a ServiceRegistry abstraction.

### IM-009 - Aggregate Computed On Demand Initially

EvidenceAggregate is initially calculated rather than treated as authoritative persisted state.

### IM-010 - Deterministic-Only First Vertical Slice

AI is not required to complete the Gmail Vertical MVP.

### IM-011 - In-Memory Persistence First

Repository interfaces are validated first using in-memory implementations.

### IM-012 - Gmail Metadata First

The first Gmail capability is `SERVICE_DISCOVERY_METADATA`.

### IM-013 - No Graph Database Initially

Relationship and Service structures provide sufficient graph semantics for the first vertical slice.

### IM-014 - Expected Uncertainty Uses Results, Not Exceptions

UNKNOWN, UNRESOLVED, AMBIGUOUS and NOT_CANDIDATE remain ordinary semantic outcomes.

---

# 98. Decisions Deferred

The following implementation decisions remain deliberately deferred:

```text
SQLite vs another durable local store

final persistence schema

final Service Registry source

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

---

# 99. Validation Strategy

Implementation should proceed through a sequence of increasingly realistic tests:

```text
Domain unit tests
        |
        v
Component unit tests
        |
        v
Contract tests
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

This preserves the project principle:

> Implementation evidence before new abstractions.

---

# 100. Next Step

After this Implementation Model is accepted, the project should stop producing additional abstract Discovery design layers and begin the first executable implementation.

The next repository work should be:

```text
Python project skeleton
        |
        v
Domain types
        |
        v
Ports
        |
        v
In-memory implementations
        |
        v
Deterministic Discovery components
        |
        v
Application orchestration
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
```

survive contact with executable code and real Gmail-derived data.

Any subsequent change should be justified by:

```text
implementation evidence

empirical behavior

test results

privacy constraints

or new validated cross-source requirements
```

rather than speculative abstraction.
