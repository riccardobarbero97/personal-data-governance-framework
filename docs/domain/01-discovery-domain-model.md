# Discovery Domain Model

**Status:** Draft v0.3  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Related Interfaces:** `docs/interfaces/01-connector-contract.md` through `docs/interfaces/07-relationship-assessor-contract.md`  
**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the consolidated Domain Model for the Identity and Service Discovery capability of the Personal Data Governance Framework.

The model is derived from:

- the Identity and Service Discovery Architecture Draft v0.3;
- Scenario 001 - Gmail Service Discovery;
- Scenario 002 - Password Manager Service Discovery;
- the Connector Contract;
- the Observation Contract;
- the Service Candidate Detector Contract;
- the Entity Resolver Contract;
- the Evidence Classifier Contract;
- the Evidence Aggregator Contract;
- the Relationship Assessor Contract;
- the complete Discovery consistency review.

Draft v0.3 incorporates the following cross-cutting findings:

1. a Relationship is primarily modeled between a User and a Service;
2. relevant Identity Seeds remain associated with the Relationship;
3. Relationship support and temporal interpretation are separate dimensions;
4. Evidence requires lifecycle semantics to support reclassification and User correction;
5. Evidence Aggregates are derived state rather than authoritative Domain information;
6. Entity Resolution and Evidence Classification are independent processing branches;
7. numerical Confidence is not part of the initial Discovery Domain Model.

This document remains implementation-independent.

It does not define:

- Python classes;
- database tables;
- REST resources;
- JSON schemas;
- graph-database structures;
- persistence technologies;
- provider-specific APIs;
- concrete authentication implementations;
- final Evidence taxonomy;
- final Service Registry implementation.

The objective is to answer:

> What concepts must the framework represent to collect minimized information from multiple Connected Sources, discover canonical Services and explain why the User appears to have or have had Relationships with them?

---

# 2. Design Context

The consolidated Discovery architecture is:

```text
USER
 |
 +-- Identity Seeds
 |
 +-- Connected Sources
         |
         v
      Connector
         |
         v
     Observation
       /       \
      /         \
     v           v
Service        Evidence
Candidate      Classification
Detection          |
     |             v
     v          Evidence
Candidate          |
Identifiers        |
     |             |
     v             |
Entity             |
Resolution         |
     |             |
     v             |
  Service ---------+
         |
         v
Evidence Aggregation
         |
         v
Evidence Aggregate
         |
         v
Relationship Assessment
         |
         v
Relationship
         |
         v
Service Graph
```

The Domain Model must distinguish between:

```text
Domain Entities
```

```text
Domain Value Concepts
```

```text
Derived Views
```

```text
Processing Results
```

```text
Domain Processes
```

For example:

```text
User
ConnectedSource
Observation
Service
Evidence
Relationship
```

represent information the framework may need to preserve as part of the Discovery Domain.

By contrast:

```text
Connector
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

represent behavior applied to Domain information.

Results such as:

```text
CandidateDetectionResult
ResolutionResult
ClassificationResult
AggregationResult
RelationshipAssessmentResult
```

represent processing outputs.

They may be persisted for provenance, but they are not automatically Core Domain Entities.

---

# 3. Core Domain Principles

The consolidated model is based on the following boundaries:

```text
SOURCE TYPE != PROVIDER

PROVIDER != CONNECTED SOURCE

CONNECTED SOURCE != CONNECTOR

IDENTITY SEED != CONNECTED SOURCE

CONNECTED SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

OBSERVATION TYPE != EVIDENCE TYPE

CANDIDATE != RESOLVED SERVICE

IDENTIFIER != SERVICE

NORMALIZATION != RESOLUTION

EVIDENCE != CONFIRMED FACT

EVIDENCE != RELATIONSHIP

EVIDENCE AGGREGATE != AUTHORITATIVE EVIDENCE

RELATIONSHIP != ACCOUNT

RELATIONSHIP STATUS != TEMPORAL STATUS

SERVICE != ORGANIZATION

PROVIDER ROLE != SERVICE ROLE

RELATIONSHIP != CURRENT DATA POSSESSION

DOMAIN OUTCOME != PROCESSING FAILURE
```

These boundaries prevent external-system definitions, collected information, semantic interpretations, technical identifiers and assessed Relationships from being collapsed into one representation.

---

# 4. Domain Overview

The consolidated conceptual model is:

```text
                                  USER
                      +------------+------------+
                      |                         |
                      | declares                | connects
                      v                         v
                IDENTITY SEED            CONNECTED SOURCE
                                                |
                                                | accessed through
                                                v
                                            CONNECTOR
                                                |
                                                | produces
                                                v
                                          OBSERVATION
                                           /        \
                                          /          \
                                         v            v
                           SERVICE IDENTIFIER        EVIDENCE
                                  |                     |
                                  | resolved to         |
                                  v                     |
                               SERVICE                  |
                                  \                     /
                                   \                   /
                                    v                 v
                                      RELATIONSHIP
                                           |
                         +-----------------+------------------+
                         |                                    |
                         v                                    v
               RELATIONSHIP STATUS                    TEMPORAL STATUS
```

The Core Domain Entities are:

```text
User
IdentitySeed
ConnectedSource
Observation
Service
Evidence
Relationship
```

The supporting Domain Value and Classification Concepts include:

```text
SourceType
Provider
Capability
ObservationType
SchemaVersion
TemporalValue
TemporalSemantics
ServiceIdentifier
EvidenceType
EvidenceStatus
RelationshipStatus
TemporalStatus
```

Derived Views include:

```text
EvidenceAggregate
EvidenceSummary
SourceSummary
TemporalSummary
ConflictSummary
CoverageSummary
```

Processing Results include:

```text
CandidateDetectionResult
ResolutionResult
ClassificationResult
AggregationResult
RelationshipAssessmentResult
```

The primary Domain Processes are:

```text
Connector
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

Concepts that remain under evaluation include:

```text
Account
Organization
Brand
LegalDataController
IdentityServiceAssociation
CollectionRun
RelationshipAssessmentHistory
```

---

# 5. User

A `User` represents the person whose observed digital footprint is being analyzed.

The current framework is designed from a single-user perspective, although the Domain Model should not assume that only one User can ever exist in a deployment.

The User may:

- declare one or more Identity Seeds;
- authorize one or more Connected Sources;
- connect multiple sources of the same type;
- connect multiple accounts through the same provider;
- correct derived conclusions;
- reject incorrect Relationships;
- disconnect source instances;
- request removal of retained information.

Conceptually:

```text
User
 |
 +-- IdentitySeed
 |
 +-- IdentitySeed
 |
 +-- ConnectedSource
 |
 +-- ConnectedSource
 |
 +-- Relationship
 |
 +-- Relationship
```

The User is the primary subject of the observed digital footprint.

The framework does not currently require separate Domain Entities such as:

```text
UserProfile
NaturalPerson
DataSubjectProfile
Principal
```

unless future framework capabilities demonstrate that they are necessary.

---

# 6. IdentitySeed

An `IdentitySeed` represents a digital identity explicitly declared or confirmed by the User and used as a starting point for Discovery.

Examples include:

```text
Email Address
Phone Number
Username
Google Account
Apple Account
Microsoft Account
```

Conceptually:

```text
IdentitySeed

- id
- type
- value
- verification_status
- created_at
```

This is a conceptual representation rather than a persistent schema.

---

## 6.1 Identity Ownership

An Identity Seed represents an identity the User claims or confirms belongs to them.

The framework must not automatically assume that every identifier encountered during Discovery belongs to the User.

For example:

```text
Password Manager Observation

username:
old-address@example.com
```

when the only verified Identity Seed is:

```text
user@example.com
```

may represent:

- another Identity belonging to the User;
- a historical Identity;
- a username unrelated to email ownership;
- a shared account;
- another person's Identity;
- obsolete information;
- incorrect information.

Therefore:

```text
OBSERVED IDENTITY IDENTIFIER
              !=
VERIFIED IDENTITY SEED
```

The framework may eventually propose candidate Identity Seeds to the User.

Automatic promotion into a verified Identity Seed is outside the current model.

---

## 6.2 IdentitySeed and ConnectedSource

An Identity Seed may be associated with one or more Connected Sources.

Example:

```text
IdentitySeed:
personal@gmail.com

ConnectedSource:
Personal Gmail
```

However:

```text
IDENTITY SEED != CONNECTED SOURCE
```

An Identity Seed represents a digital identity belonging to the User.

A Connected Source represents a particular authorized source instance.

A password-manager ConnectedSource may expose information related to several Identity Seeds.

---

## 6.3 IdentitySeed and Relationship

Identity Seeds may be associated with a User-Service Relationship.

Example:

```text
User
 |
 v
Relationship
 |
 +-- Service: Spotify
 |
 +-- IdentitySeed: personal@example.com
 |
 +-- IdentitySeed: oldmail@example.net
```

Multiple Identity references do not automatically imply:

```text
multiple Accounts
```

or:

```text
one shared Account
```

They preserve the identities through which the Relationship was observed.

---

# 7. SourceType

A `SourceType` classifies a source by the general kind of information it exposes.

Initial examples include:

```text
EMAIL
PASSWORD_MANAGER
BROWSER
IDENTITY_PROVIDER
MANUAL
```

These categories must remain extensible.

`SourceType` answers:

> What general category of source is this?

It does not identify:

- a provider;
- a product;
- a particular User connection;
- an Observation structure.

For example:

```text
EMAIL
```

is a SourceType.

```text
Google
```

is a Provider.

```text
Personal Gmail
```

is a ConnectedSource.

```text
EMAIL_MESSAGE_METADATA
```

is an ObservationType.

---

# 8. Provider

A `Provider` identifies the external product, platform or organization providing access to a source.

Examples may include:

```text
Google
Microsoft
Apple
Proton
1Password
Bitwarden
KeePass
```

Provider answers:

> Which external platform or product provides the source?

Providers supporting the same SourceType may expose different:

- authorization mechanisms;
- APIs;
- permission models;
- capabilities;
- metadata;
- synchronization methods;
- local or remote access models.

Therefore:

```text
SOURCE TYPE != PROVIDER
```

Provider-specific behavior belongs primarily behind Connector implementations.

---

## 8.1 Provider Role and Service Role

A real-world entity may appear in more than one Domain role.

For example, Google may be:

```text
Provider of a Gmail ConnectedSource
```

and separately:

```text
a discovered Service associated with the User
```

These roles must remain distinct.

Therefore:

```text
GOOGLE AS PROVIDER
        !=
GOOGLE AS DISCOVERED SERVICE
```

even when they refer to the same real-world organization.

---

# 9. DiscoverySource

`DiscoverySource` remains an architectural category describing an external source from which relevant information may be obtained.

Examples include:

```text
Email Provider
Password Manager
Browser
Identity Provider
Manual Input
```

At Domain Model level, source information is represented more precisely through:

```text
SourceType
Provider
ConnectedSource
```

Therefore `DiscoverySource` does not currently require promotion to a separate Core Domain Entity.

---

# 10. ConnectedSource

A `ConnectedSource` represents a particular external source instance connected or authorized by the User.

It is a Core Domain Entity.

Examples include:

```text
Personal Gmail account
Old Gmail account
Work Outlook account
Personal Proton Mail account
Primary password-manager vault
Imported password-manager archive
Browser profile
```

A ConnectedSource is distinct from:

- SourceType;
- Provider;
- Connector implementation;
- IdentitySeed;
- Observation.

Therefore:

```text
PROVIDER != CONNECTED SOURCE
```

```text
CONNECTED SOURCE != CONNECTOR
```

```text
CONNECTED SOURCE != IDENTITY SEED
```

---

## 10.1 Conceptual Representation

A ConnectedSource may conceptually contain:

```text
ConnectedSource

- id
- user_reference
- source_type
- provider
- connector_reference
- display_name
- external_account_reference
- connection_state
- authorization_state
- created_at
- updated_at
```

This is not a final persistence schema.

Authorization secrets must not be stored as ordinary ConnectedSource attributes.

---

## 10.2 Multiple Instances

A Connector implementation may support multiple independent Connected Sources.

```text
                    GmailConnector
                    /            \
                   /              \
                  v                v
         Personal Gmail        Old Gmail
```

Each source may independently:

- authorize;
- expire;
- require additional permission;
- synchronize;
- fail;
- be revoked;
- be disconnected;
- produce Observations.

---

## 10.3 ConnectedSource State

Connection lifecycle and authorization state may need to remain distinct.

For example:

```text
connection_state:
CONNECTED

authorization_state:
INSUFFICIENT
```

may mean that the source instance exists but the selected capability requires additional access.

Potential conceptual states include:

```text
Connection State

PENDING
CONNECTED
DISCONNECTED
ERROR
```

and:

```text
Authorization State

NOT_AUTHORIZED
AUTHORIZED
EXPIRED
INSUFFICIENT
REVOKED
ERROR
```

The final enumerations remain implementation-dependent.

---

## 10.4 Authorization Material

A ConnectedSource may reference authorization material but must not contain its secret values as ordinary Domain attributes.

The conceptual boundary is:

```text
ConnectedSource
       |
       v
Credential Reference
       |
       v
Secure Credential Storage
```

not:

```text
ConnectedSource
 |
 +-- access_token
 +-- refresh_token
 +-- password
```

Secure credential storage belongs to the Privacy and Security Architecture.

---

## 10.5 ConnectedSource Capabilities

Available capabilities may depend on:

- Connector implementation;
- Provider capability;
- granted permissions;
- User configuration;
- source configuration;
- deployment environment;
- local application availability.

Therefore:

```text
Connector Potential Capabilities
              |
              v
ConnectedSource Available Capabilities
```

may differ between source instances using the same Connector.

---

# 11. Connector

A `Connector` is the provider-specific processing and security boundary through which the framework communicates with one or more Connected Sources.

It is not a persistent Core Domain Entity.

Conceptually:

```text
ConnectedSource
       |
       v
    Connector
       |
       v
External Provider
```

and:

```text
External Provider
       |
       v
    Connector
       |
       v
  Observation
```

---

## 11.1 Connector Responsibilities

A Connector may be responsible for:

```text
Authorization
Capability Discovery
Permission Analysis
Provider API Interaction
Pagination
Synchronization
Source Error Handling
Representation Normalization
Data Minimization
Observation Creation
```

Its responsibility ends at the boundary between provider-specific representation and the common Discovery Domain.

---

## 11.2 Connector as Minimization Boundary

A Connector should prevent unnecessary information from entering the Discovery Core.

Example:

```text
Password Manager Record
 |
 +-- title ----------+
 +-- username -------+--> Observation
 +-- URI ------------+
 |
 +-- password -------X
 +-- OTP seed -------X
 +-- recovery code --X
```

Authentication secrets unnecessary for Discovery must remain outside normal Observations.

---

# 12. Capability

A `Capability` represents an intentional framework operation requiring defined information and permissions.

Examples may include:

```text
SERVICE_DISCOVERY_METADATA
EMAIL_CONTENT_DISCOVERY
ATTACHMENT_DISCOVERY
INCREMENTAL_SYNCHRONIZATION
```

A Capability is distinct from a concrete provider permission.

Conceptually:

```text
Capability
     |
     v
Required Information
     |
     v
Provider-Specific Permission
```

The final capability vocabulary remains open.

---

# 13. Observation

An `Observation` represents source-derived information obtained from exactly one ConnectedSource before final semantic interpretation.

It answers:

> What did the framework observe?

It does not answer:

> What does this information mean?

Therefore:

```text
CONNECTED SOURCE != OBSERVATION
```

```text
OBSERVATION != EVIDENCE
```

```text
OBSERVATION != SERVICE
```

```text
OBSERVATION != RELATIONSHIP
```

---

## 13.1 Conceptual Representation

The consolidated Observation model is:

```text
Observation

- id
- connected_source_id
- observation_type
- schema_version
- source_reference
- observed_at
- collected_at
- temporal_semantics
- payload
- provenance
```

The representation consists of:

```text
Common Envelope
        +
Typed Payload
```

---

## 13.2 Common Envelope

The common envelope contains provider-independent framework fields such as:

```text
id
connected_source_id
observation_type
schema_version
source_reference
temporal information
```

---

## 13.3 Typed Payload

The payload is constrained by:

```text
ObservationType
+
SchemaVersion
```

Examples include:

```text
EMAIL_MESSAGE_METADATA v1
PASSWORD_MANAGER_ENTRY_METADATA v1
BROWSER_VISIT v1
MANUAL_RELATIONSHIP_DECLARATION v1
```

The payload must not be an unrestricted serialization of the provider object.

---

## 13.4 Provider-Neutral Observation Types

Equivalent source semantics should use the same ObservationType across providers where possible.

```text
Gmail --------+
              |
Outlook ------+
              |
iCloud -------+--> EMAIL_MESSAGE_METADATA
              |
Proton -------+
```

Provider-specific Observation Types should be introduced only when the framework semantics genuinely differ.

---

## 13.5 Source Reference

A source reference should be preserved where technically possible and safe.

Conceptually:

```text
Observation Identity Context

ConnectedSourceId
        +
SourceReference
```

This may support:

- deduplication;
- synchronization;
- source updates;
- reprocessing;
- traceability.

A source reference must not expose unnecessary secret information.

---

## 13.6 Temporal Semantics

Temporal values must preserve both:

```text
timestamp
```

and:

```text
meaning of the timestamp
```

For example:

```text
MESSAGE_TIME
```

is distinct from:

```text
SOURCE_RECORD_MODIFIED
```

A password-manager record modification time must not automatically become:

```text
Last Service Activity
```

---

## 13.7 Observation Validity

An Observation asserts that the Connector observed the represented information.

It does not assert that the information is true.

For example, a phishing message may produce a valid Observation containing a misleading sender.

Therefore:

```text
OBSERVED VALUE != TRUSTED FACT
```

---

## 13.8 Observation Immutability

Observations should be treated as immutable source-derived records where practical.

A later interpretation or reprocessing operation must not destructively rewrite what was originally observed.

---

# 14. ObservationType

`ObservationType` identifies the semantic source structure represented by an Observation.

Examples include:

```text
EMAIL_MESSAGE_METADATA
EMAIL_MESSAGE_CONTENT
PASSWORD_MANAGER_ENTRY_METADATA
BROWSER_VISIT
IDENTITY_PROVIDER_RELATIONSHIP
MANUAL_RELATIONSHIP_DECLARATION
```

ObservationType is distinct from both:

```text
SourceType
```

and:

```text
EvidenceType
```

Therefore:

```text
SOURCE TYPE != OBSERVATION TYPE
```

```text
OBSERVATION TYPE != EVIDENCE TYPE
```

---

# 15. SchemaVersion

`SchemaVersion` identifies the structure and semantic version of a typed Observation payload.

Historical payload semantics must not change silently.

Downstream consumers should interpret:

```text
ObservationType
+
SchemaVersion
```

rather than ObservationType alone.

---

# 16. TemporalValue and TemporalSemantics

A `TemporalValue` conceptually combines:

```text
timestamp
temporal_semantics
```

Potential semantics include:

```text
SOURCE_EVENT_TIME
MESSAGE_TIME
SOURCE_RECORD_CREATED
SOURCE_RECORD_MODIFIED
VISIT_TIME
USER_DECLARED_TIME
UNKNOWN
```

The final vocabulary remains open.

The Domain Model must support multiple typed temporal values if future Observation structures require them.

---

# 17. Candidate Detection

Service Candidate Detection determines whether an Observation should participate in the Service Discovery capability.

It is a Domain Process.

Conceptual outcomes include:

```text
CANDIDATE
NOT_CANDIDATE
UNKNOWN
```

A technical processing failure must remain separate from these outcomes.

---

## 17.1 Candidate Is Not Resolved

An Observation can be a valid candidate even when its Service remains unresolved.

Therefore:

```text
CANDIDATE != RESOLVED
```

---

## 17.2 Candidate Identifiers

Candidate Detection may extract one or more technical identifiers.

Examples include:

```text
EMAIL_DOMAIN
DOMAIN
HOSTNAME
URL
DISPLAY_NAME
PROVIDER_SPECIFIC_IDENTIFIER
```

These values contribute to ServiceIdentifier creation or processing.

They must not be treated as canonical Services.

---

# 18. ServiceIdentifier

A `ServiceIdentifier` represents a technical identifier that may contribute to identifying a canonical Service.

Examples include:

```text
spotify.com
accounts.spotify.com
https://accounts.spotify.com/login
no-reply@spotify.com
provider-specific application identifier
```

Potential identifier types include:

```text
DOMAIN
HOSTNAME
URL
EMAIL_ADDRESS
EMAIL_DOMAIN
DISPLAY_NAME
PROVIDER_SPECIFIC
```

The final taxonomy remains extensible.

---

## 18.1 ServiceIdentifier Classification

`ServiceIdentifier` is best treated as a Domain Value Concept rather than a standalone aggregate root.

It may possess identity for persistence and provenance purposes, but it is primarily meaningful through:

- its value;
- its type;
- its source Observation;
- its normalization history;
- its resolution history.

---

## 18.2 Identifier Is Not Service

```text
IDENTIFIER != SERVICE
```

A domain, URL or email address is not automatically a canonical Service.

---

## 18.3 Original and Normalized Values

The Domain Model should preserve:

```text
Original Identifier
        |
        v
Normalized Identifier
        |
        v
Resolved Service
```

Normalization must not destroy the original value.

---

# 19. Entity Resolution

Entity Resolution attempts to map one or more ServiceIdentifiers to a canonical Service.

It is a Domain Process.

Conceptual resolution states include:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

Technical processing state remains separate.

---

## 19.1 Normalization Is Not Resolution

For example:

```text
accounts.spotify.com
        |
        v
spotify.com
```

may be normalization.

```text
spotify.com
        |
        v
Spotify
```

is canonical Entity Resolution.

Therefore:

```text
NORMALIZATION != RESOLUTION
```

---

## 19.2 Cross-Source Resolution

Identifiers derived from multiple Connected Sources may resolve to the same Service.

```text
Gmail Observation
      |
      v
spotify.com
      |
      +---------------+
                      |
                      v
                   Spotify
                      ^
                      |
      +---------------+
      |
accounts.spotify.com
      ^
      |
Password Manager Observation
```

Provider identity must not create duplicate Services.

---

## 19.3 ResolutionResult

A `ResolutionResult` represents the output of Entity Resolution.

Conceptually:

```text
ResolutionResult

- input_identifiers
- normalized_identifiers
- processing_status
- resolution_status
- resolved_service_reference
- alternative_service_references
- method
- reason_codes
- resolver_version
- provenance
```

`ResolutionResult` is classified as:

```text
Processing Result / Value Object
```

not a Core Domain Entity.

It may be persisted when needed for:

- explainability;
- re-resolution;
- debugging;
- historical comparison;
- User correction.

---

# 20. Service

A `Service` represents a canonical digital Service with which the User may have or have had a Relationship.

Examples include:

```text
Spotify
GitHub
Netflix
Amazon
```

A Service is distinct from:

```text
email sender
domain
hostname
URL
credential record
Observation
ConnectedSource
Provider
Organization
Account
```

---

## 20.1 Conceptual Representation

```text
Service

- id
- canonical_name
- status
- identifiers
- created_at
- updated_at
```

This remains conceptual.

---

## 20.2 Service Granularity

The Domain Model does not yet define universal Service granularity.

For example:

```text
Google
Google Account
Gmail
```

may represent different Service levels.

Granularity must not be inferred solely from a domain.

The appropriate model should be validated against real Discovery and later Personal Data Acquisition scenarios.

---

## 20.3 Service and Organization

A Service may be operated by an Organization.

One Organization may operate many Services.

Therefore:

```text
SERVICE != ORGANIZATION
```

Potential future concepts include:

```text
Brand
Organization
Legal Data Controller
```

These are not Core Domain Entities in Draft v0.3.

---

## 20.4 Service Registry

A Service Registry is conceptually required to manage canonical Services and identifiers.

However, it is currently treated as:

```text
Application / Repository Boundary
```

rather than a new Core Domain Entity.

Its responsibilities may eventually include:

- locating Services;
- storing ServiceIdentifier mappings;
- registering new Services;
- maintaining aliases;
- managing merges;
- managing splits;
- retaining historical identifiers.

The exact contract remains undefined.

---

# 21. Evidence Classification

Evidence Classification interprets one Observation and produces zero, one or multiple semantic Evidence candidates.

It is a Domain Process.

The process may return:

```text
CLASSIFIED
UNKNOWN
```

when processing succeeds.

Technical failures and unsupported schemas remain separate.

---

# 22. EvidenceType

`EvidenceType` identifies the semantic interpretation of an Observation.

Examples currently validated include:

```text
ACCOUNT_CREATION
ACCOUNT_VERIFICATION
AUTHENTICATION
PASSWORD_RESET
SECURITY_NOTIFICATION
PURCHASE
INVOICE
SUBSCRIPTION
PAYMENT
ACCOUNT_UPDATE
ACCOUNT_DELETION
MARKETING
NEWSLETTER
PRIVACY_NOTICE
PASSWORD_MANAGER_ENTRY
```

The Evidence taxonomy must be:

- controlled;
- versionable;
- provider-neutral where possible;
- extensible based on real scenarios.

Source-specific Evidence Types may be introduced only when common semantic types cannot adequately represent the source meaning.

---

# 23. Evidence

`Evidence` represents a semantic interpretation supported by one or more Observations.

It answers:

> What does the observed information appear to tell the framework about a possible User-Service Relationship?

Therefore:

```text
OBSERVATION != EVIDENCE
```

and:

```text
EVIDENCE != CONFIRMED FACT
```

and:

```text
EVIDENCE != RELATIONSHIP
```

---

## 23.1 Conceptual Representation

```text
Evidence

- id
- evidence_type
- evidence_status
- supporting_observation_references
- service_reference
- identity_references
- classification_method
- classifier_version
- reason_codes
- temporal_values
- created_at
- provenance
```

The exact persistent schema remains undefined.

---

## 23.2 Evidence Without Resolved Service

Evidence does not require successful Entity Resolution.

Example:

```text
EvidenceType:
PAYMENT

Service:
UNRESOLVED
```

is valid.

If Entity Resolution later succeeds, the Evidence may become associated with the resolved Service without reclassifying the Observation.

---

## 23.3 Multiple Evidence Items

One Observation may support zero, one or several Evidence items.

For example:

```text
Observation:
Your subscription was renewed and payment was successful
```

may support:

```text
SUBSCRIPTION
PAYMENT
```

if both meanings are independently justified.

The classifier must not generate implied categories merely because events commonly occur together.

---

# 24. EvidenceStatus

`EvidenceStatus` represents whether an Evidence interpretation should participate in current Discovery assessment.

The initial conceptual states are:

```text
ACTIVE
SUPERSEDED
REJECTED
```

---

## 24.1 ACTIVE

`ACTIVE` means that the Evidence represents a currently accepted semantic interpretation.

Only ACTIVE Evidence should normally participate in current Evidence Aggregation and Relationship Assessment.

---

## 24.2 SUPERSEDED

`SUPERSEDED` means that an Evidence interpretation has been replaced by a newer accepted interpretation.

Example:

```text
Classifier v1:
Evidence = MARKETING
Status = SUPERSEDED

Classifier v2:
Evidence = PRIVACY_NOTICE
Status = ACTIVE
```

The superseded Evidence remains available for provenance and historical analysis.

It must not normally be counted as simultaneous current Evidence.

---

## 24.3 REJECTED

`REJECTED` means that an Evidence interpretation has been explicitly invalidated or rejected.

Possible reasons include:

- User correction;
- classification error;
- invalid source association;
- processing defect;
- later information demonstrating that the interpretation was incorrect.

Rejected Evidence remains preserved where required for provenance.

It must not participate in the current Relationship assessment.

---

## 24.4 EvidenceStatus Is Not RelationshipStatus

```text
EvidenceStatus.REJECTED
```

means:

> This Evidence interpretation is not currently accepted.

```text
RelationshipStatus.REJECTED
```

means:

> The apparent User-Service Relationship should not currently be attributed to the User.

These concepts must remain distinct.

---

## 24.5 Evidence Lifecycle

Potential lifecycle transitions include:

```text
ACTIVE
   |
   +--> SUPERSEDED
   |
   +--> REJECTED
```

A newer Evidence interpretation may then become:

```text
ACTIVE
```

The final transition policy remains open.

---

# 25. EvidenceCandidate

`EvidenceCandidate` represents the immediate semantic output of the EvidenceClassifier before persistence and lifecycle management.

Conceptually:

```text
EvidenceCandidate

- evidence_type
- supporting_observation_references
- method
- reason_codes
- classifier_version
```

It is classified as:

```text
Interface Value Object / Processing Output
```

It is not a Core Domain Entity.

The application layer may materialize a valid EvidenceCandidate as `Evidence`.

---

# 26. Evidence Aggregation

Evidence Aggregation combines current Evidence associated with the same discovery context.

It is a Domain Process.

The primary aggregation boundary is the canonical Service where available.

Conceptually:

```text
ACTIVE Evidence
ACTIVE Evidence
ACTIVE Evidence
      |
      v
EvidenceAggregator
      |
      v
EvidenceAggregate
```

Superseded or Rejected Evidence should not normally participate in the current aggregate.

---

# 27. EvidenceAggregate

An `EvidenceAggregate` is a derived view over Evidence.

It is not an authoritative Core Domain Entity.

Conceptually:

```text
EvidenceAggregate

- scope
- service_reference
- unresolved_identifier_reference
- identity_references
- evidence_references
- evidence_summary
- source_summary
- temporal_summary
- conflict_summary
- coverage_summary
- aggregator_version
```

---

## 27.1 Derived State

```text
EVIDENCE AGGREGATE != AUTHORITATIVE EVIDENCE
```

An Aggregate must remain reconstructable from its contributing Evidence where that Evidence is retained.

Deleting a materialized Aggregate must not delete underlying Evidence.

---

## 27.2 Service-Level Aggregation

The primary scope is:

```text
SERVICE
```

Additional scopes may include:

```text
UNRESOLVED_SERVICE_CANDIDATE
AMBIGUOUS_SERVICE_CANDIDATE
```

Evidence must not disappear solely because canonical Service resolution is incomplete.

---

## 27.3 Identity Preservation

Aggregation must preserve relevant Identity references.

It must not automatically infer:

```text
one Account
```

or:

```text
multiple Accounts
```

from multiple Identity references.

---

## 27.4 Source Summary

The Aggregate may preserve:

```text
ConnectedSource count
SourceType diversity
Provider diversity
Evidence count by source
Evidence count by source type
```

These values describe provenance.

They do not automatically determine Relationship strength.

---

## 27.5 Evidence Frequency

Evidence frequency is descriptive.

Therefore:

```text
100 MARKETING
```

does not automatically outweigh:

```text
1 ACCOUNT_VERIFICATION
```

Semantic interpretation belongs to Relationship Assessment.

---

## 27.6 Temporal Summary

Temporal summary may include:

```text
first_observed
last_observed
typed temporal values
Evidence timeline
```

These values must preserve temporal semantics.

`first_observed` must not automatically mean account creation.

`last_observed` must not automatically mean last Service use.

---

## 27.7 Conflicting Evidence

Evidence conflicts must remain preserved.

Example:

```text
2024 ACCOUNT_DELETION
2026 AUTHENTICATION
```

The Aggregate may report a conflict.

It must not invent the explanation.

---

# 28. EvidenceSummary

`EvidenceSummary` is a derived value containing information such as:

```text
total Evidence count
Evidence count by type
active Evidence types
historical Evidence types
```

It is calculated only from Evidence permitted by the active aggregation policy.

---

# 29. SourceSummary

`SourceSummary` is a derived value describing the provenance dimensions supporting an Aggregate.

Conceptually:

```text
SourceSummary

- connected_source_count
- source_types
- providers
- evidence_count_by_connected_source
- evidence_count_by_source_type
```

Provider information should be omitted when unnecessary.

---

# 30. TemporalSummary

`TemporalSummary` is a derived value preserving typed temporal information.

Conceptually:

```text
TemporalSummary

- first_observed
- last_observed
- evidence_timeline
- typed_temporal_values
```

All summary values must remain traceable to Evidence or supporting Observations.

---

# 31. ConflictSummary

`ConflictSummary` is a derived value describing potential semantic conflicts.

Conceptually:

```text
ConflictSummary

- has_potential_conflicts
- conflict_types
- involved_evidence_references
```

The final conflict taxonomy remains open.

---

# 32. CoverageSummary

`CoverageSummary` describes the known completeness state of configured source processing.

Conceptually:

```text
CoverageSummary

- configured_sources
- completed_sources
- partial_sources
- failed_sources
- unavailable_sources
```

Coverage information originates from collection and synchronization context.

The EvidenceAggregator and RelationshipAssessor may consume or summarize coverage, but they must not invent it.

Coverage is currently classified as:

```text
Derived Application / Processing Context
```

rather than a Core Domain Entity.

---

# 33. Relationship

A `Relationship` represents the framework's current assessment that a meaningful digital Relationship exists or existed between a User and a Service.

The primary relationship is:

```text
User
 |
 v
Relationship
 |
 v
Service
```

Relevant Identity Seeds remain associated with the Relationship.

This replaces the earlier primary model that treated the Relationship as fundamentally IdentitySeed-to-Service.

---

## 33.1 Conceptual Representation

```text
Relationship

- id
- user_reference
- service_reference
- relationship_status
- temporal_status
- identity_references
- evidence_basis
- reason_codes
- warnings
- assessment_method
- assessor_version
- assessment_policy_version
- assessed_at
```

This remains conceptual.

---

## 33.2 Why User-Service Is Primary

The primary User-facing Discovery question is:

> Which Services appear to have or have had a Relationship with me?

Therefore the User-Service Relationship is the primary graph edge.

Identity references support additional questions such as:

> Which Services were associated with `oldmail@example.net`?

without requiring a separate Relationship for each Identity at this stage.

---

## 33.3 Relationship Is Not Account

Relationships may arise through:

```text
account Evidence
subscription
purchase
guest transaction
newsletter
mailing list
browser interaction
privacy communication
historical interaction
```

Therefore:

```text
RELATIONSHIP != ACCOUNT
```

---

## 33.4 Relationship Is Not Current Data Possession

A Relationship does not establish which personal data a Service currently possesses.

Therefore:

```text
RELATIONSHIP
        !=
CURRENT DATA POSSESSION
```

That question belongs to later Personal Data Acquisition and Understanding capabilities.

---

# 34. RelationshipStatus

`RelationshipStatus` describes the level of semantic support for a User-Service Relationship.

The initial conceptual states are:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

---

## 34.1 UNKNOWN

Available Evidence is insufficient to justify that a meaningful Relationship existed.

This does not mean that no Relationship exists.

It means only that available observed information does not justify a stronger conclusion.

---

## 34.2 OBSERVED

Evidence demonstrates some interaction or communication involving the Service, but does not justify a stronger Relationship conclusion.

Possible examples may include:

```text
marketing
newsletter
privacy communication
browser visit
```

depending on explicit assessment policy.

---

## 34.3 ESTABLISHED

Available Evidence provides a justified basis for concluding that a meaningful Relationship existed.

Potential supporting information may include:

```text
account-related Evidence
commercial Evidence
authentication Evidence
password-manager Evidence
multi-source Evidence
User confirmation
```

The exact Evidence combinations required for this state remain subject to empirical validation.

---

## 34.4 REJECTED

The apparent Relationship should not currently be attributed to the User.

Potential reasons include:

- explicit User rejection;
- verified misattribution;
- Evidence belonging to another person;
- correction demonstrating an incorrect Service association.

REJECTED requires provenance.

Weak Evidence alone must not automatically produce rejection.

---

# 35. TemporalStatus

`TemporalStatus` describes the temporal interpretation of a Relationship independently from its semantic support.

The initial conceptual states are:

```text
UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

---

## 35.1 UNKNOWN

The framework cannot safely determine whether the Relationship is current or historical.

Example:

```text
RelationshipStatus:
ESTABLISHED

Evidence:
PASSWORD_MANAGER_ENTRY

TemporalStatus:
UNKNOWN
```

The entry does not establish whether credentials still work or the account still exists.

---

## 35.2 CURRENTLY_OBSERVED

Recent Evidence indicates ongoing observable interaction.

This does not mean:

```text
Active Account Confirmed
```

A recent newsletter may indicate ongoing communication without proving account activity.

---

## 35.3 HISTORICAL

Available Evidence supports that the Relationship existed in the past, while current continuation is not established or Evidence indicates that it ended.

Example:

```text
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

may support:

```text
RelationshipStatus:
ESTABLISHED

TemporalStatus:
HISTORICAL
```

Historical does not imply that the Service currently retains no data.

---

# 36. RelationshipStatus and TemporalStatus

Relationship support and time are separate dimensions.

Valid combinations may include:

```text
ESTABLISHED + HISTORICAL
```

```text
ESTABLISHED + UNKNOWN
```

```text
OBSERVED + CURRENTLY_OBSERVED
```

```text
REJECTED + UNKNOWN
```

The model intentionally does not use one flat state enumeration containing:

```text
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
```

because those values mix support level and time.

---

# 37. Relationship Assessment

Relationship Assessment interprets an EvidenceAggregate and produces a Relationship assessment.

It is a Domain Process.

Conceptually:

```text
EvidenceAggregate
       |
       v
RelationshipAssessor
       |
       v
RelationshipAssessmentResult
       |
       v
Relationship
```

Assessment should use explicit, explainable and versionable policy.

---

# 38. RelationshipAssessmentResult

A `RelationshipAssessmentResult` is a processing result.

Conceptually:

```text
RelationshipAssessmentResult

- processing_status
- relationship_status
- temporal_status
- service_reference
- identity_references
- evidence_basis
- reason_codes
- warnings
- method
- assessor_version
- assessment_policy_version
```

It is classified as:

```text
Processing Result / Value Object
```

rather than a Core Domain Entity.

It may be used to create or update the current Relationship representation.

---

# 39. Relationship Assessment History

Historical assessments may need to remain available when assessment logic or Evidence changes.

Example:

```text
January 2026:
OBSERVED + CURRENTLY_OBSERVED

April 2026:
ESTABLISHED + CURRENTLY_OBSERVED

October 2026:
ESTABLISHED + HISTORICAL
```

A possible future `RelationshipAssessmentHistory` concept may preserve this sequence.

Draft v0.3 does not promote it to a Core Domain Entity.

The initial implementation may instead persist versioned RelationshipAssessmentResults.

---

# 40. No Numerical Confidence

Numerical Confidence is not part of the initial Discovery Domain Model.

The model prefers:

```text
RelationshipStatus
TemporalStatus
Evidence Basis
Source Diversity
Temporal Timeline
Reason Codes
Warnings
```

over:

```text
confidence = 0.87
```

This applies across:

- Candidate Detection;
- Entity Resolution;
- Evidence Classification;
- Relationship Assessment.

Confidence may be reconsidered only if:

- its exact semantics are defined;
- representative validation data exists;
- calibration is possible;
- it provides measurable User value.

---

# 41. Account

`Account` remains a candidate Domain Concept.

It may eventually represent:

```text
Service
 |
 +-- Account
 |      |
 |      +-- IdentitySeed
 |
 +-- Account
        |
        +-- IdentitySeed
```

Potential uses include:

- multiple accounts with the same Service;
- multiple identities;
- historical accounts;
- migrated accounts;
- shared accounts.

However, Account is not required for:

- guest purchases;
- newsletter Relationships;
- privacy communications;
- browser interactions;
- historical commercial Relationships.

Therefore:

```text
Account = CANDIDATE DOMAIN CONCEPT
```

---

# 42. Organization

An `Organization` may operate one or more Services.

Potential future structure:

```text
Organization
    |
    +-- Brand
    |     |
    |     +-- Service
    |
    +-- Service
```

A legal data controller may be distinct from both Brand and Service.

The current Discovery Domain lacks sufficient validated requirements to formalize these concepts.

Therefore:

```text
Organization = CANDIDATE DOMAIN CONCEPT
```

---

# 43. IdentityServiceAssociation

A future `IdentityServiceAssociation` could explicitly model:

```text
IdentitySeed
      |
      v
IdentityServiceAssociation
      |
      v
Service
```

This may support queries such as:

```text
Which Services were associated with this historical email address?
```

Draft v0.3 does not promote this concept because Identity references can currently be preserved through the User-Service Relationship and its Evidence basis.

Therefore:

```text
IdentityServiceAssociation = CANDIDATE DOMAIN CONCEPT
```

---

# 44. CollectionRun

A future `CollectionRun` may represent one collection or synchronization execution.

Conceptually:

```text
CollectionRun

- id
- connected_source_reference
- capability
- started_at
- completed_at
- status
- continuation
- errors
- coverage
```

It may support:

- partial collection;
- retries;
- measurement;
- synchronization;
- debugging;
- coverage reporting.

CollectionRun currently belongs more naturally to the application and synchronization model than to the Core Discovery Domain.

Therefore:

```text
CollectionRun = APPLICATION-LEVEL CANDIDATE
```

---

# 45. Domain Entities, Values and Processes

| Concept | Draft v0.3 classification |
|---|---|
| `User` | Core Domain Entity |
| `IdentitySeed` | Core Domain Entity |
| `ConnectedSource` | Core Domain Entity |
| `Observation` | Core Domain Entity |
| `Service` | Core Domain Entity |
| `Evidence` | Core Domain Entity |
| `Relationship` | Core Domain Entity |
| `ServiceIdentifier` | Domain Value Concept |
| `SourceType` | Classification Concept |
| `Provider` | Reference / Classification Concept |
| `Capability` | Classification / Policy Concept |
| `ObservationType` | Controlled Type Concept |
| `SchemaVersion` | Value Concept |
| `TemporalValue` | Value Concept |
| `TemporalSemantics` | Controlled Type Concept |
| `EvidenceType` | Controlled Taxonomy Concept |
| `EvidenceStatus` | Lifecycle State Concept |
| `RelationshipStatus` | Relationship State Concept |
| `TemporalStatus` | Relationship Temporal State Concept |
| `EvidenceAggregate` | Derived View |
| `EvidenceSummary` | Derived Value |
| `SourceSummary` | Derived Value |
| `TemporalSummary` | Derived Value |
| `ConflictSummary` | Derived Value |
| `CoverageSummary` | Derived Processing Context |
| `CandidateDetectionResult` | Processing Result |
| `ResolutionResult` | Processing Result / Value Object |
| `ClassificationResult` | Processing Result |
| `EvidenceCandidate` | Interface Value Object |
| `AggregationResult` | Processing Result |
| `RelationshipAssessmentResult` | Processing Result |
| `Connector` | Integration Boundary / Process |
| `ServiceCandidateDetector` | Domain Process |
| `EntityResolver` | Domain Process |
| `EvidenceClassifier` | Domain Process |
| `EvidenceAggregator` | Domain Process |
| `RelationshipAssessor` | Domain Process |
| `ServiceRegistry` | Application / Repository Boundary |
| `Account` | Candidate Domain Concept |
| `Organization` | Candidate Domain Concept |
| `IdentityServiceAssociation` | Candidate Domain Concept |
| `CollectionRun` | Application-Level Candidate |
| `RelationshipAssessmentHistory` | Candidate Historical Concept |

---

# 46. Conceptual Multi-Source Model

```text
                                      USER
                     +-----------------+-----------------+
                     |                                   |
                     v                                   v
              IDENTITY SEEDS                    CONNECTED SOURCES
                                                        |
                               +------------------------+----------------------+
                               |                        |                      |
                               v                        v                      v
                        Personal Gmail            Work Outlook         Password Manager
                               |                        |                      |
                               v                        v                      v
                        GmailConnector           OutlookConnector       VaultConnector
                               |                        |                      |
                               +------------------------+----------------------+
                                                        |
                                                        v
                                                   OBSERVATIONS
                                                    /        \
                                                   /          \
                                                  v            v
                                     SERVICE IDENTIFIERS      EVIDENCE
                                                  |            |
                                                  v            |
                                          ENTITY RESOLUTION    |
                                                  |            |
                                                  v            |
                                               SERVICE         |
                                                  \            /
                                                   \          /
                                                    v        v
                                                EVIDENCE AGGREGATE
                                                        |
                                                        v
                                                   RELATIONSHIP
                                                   /     |      \
                                                  /      |       \
                                                 v       v        v
                                             STATUS   TEMPORAL  IDENTITIES
                                                        |
                                                        v
                                                  SERVICE GRAPH
```

Future providers should be able to join this architecture without changing the common Domain Model.

---

# 47. Domain Invariants

## INV-001

Every ConnectedSource must belong to one User.

---

## INV-002

A Connector implementation may serve multiple independent Connected Sources.

---

## INV-003

Disconnecting one ConnectedSource must not automatically disconnect another ConnectedSource.

---

## INV-004

IdentitySeed and ConnectedSource must not be assumed equivalent.

---

## INV-005

Every Observation must reference exactly one ConnectedSource.

---

## INV-006

An Observation must not expose provider credentials required only for source access.

---

## INV-007

Authentication secrets unnecessary for Discovery must not become normal Observation attributes.

---

## INV-008

Observation payload must conform to its ObservationType and SchemaVersion.

---

## INV-009

Provider-specific raw objects must not become common Observation payloads without minimization and normalization.

---

## INV-010

Observation temporal values must preserve source semantics.

---

## INV-011

Collection completeness must not be inferred from the presence or absence of individual Observations.

---

## INV-012

Candidate status must remain distinct from Entity Resolution status.

---

## INV-013

An unresolved identifier must not require creation of a fabricated Service.

---

## INV-014

Original identifiers must remain traceable after normalization and resolution.

---

## INV-015

Provider identity must not create provider-specific copies of canonical Services.

---

## INV-016

Multiple identifiers may resolve to one Service.

---

## INV-017

One identifier must not be assumed to identify one Service in every context.

---

## INV-018

Service and Organization must remain distinct concepts.

---

## INV-019

Evidence must remain traceable to supporting Observations.

---

## INV-020

Evidence Classification must not require successful Entity Resolution.

---

## INV-021

Entity Resolution must not require successful Evidence Classification.

---

## INV-022

One Observation may produce zero, one or multiple Evidence items.

---

## INV-023

Multiple Evidence items from one Observation must be independently justified.

---

## INV-024

Evidence must not be interpreted as a confirmed real-world event.

---

## INV-025

Only currently accepted Evidence should normally participate in current Aggregation.

---

## INV-026

Superseded Evidence must remain distinguishable from Active Evidence.

---

## INV-027

Rejected Evidence must not participate in current Relationship Assessment.

---

## INV-028

EvidenceStatus.REJECTED must remain distinct from RelationshipStatus.REJECTED.

---

## INV-029

An EvidenceAggregate must remain traceable to its contributing Evidence.

---

## INV-030

An EvidenceAggregate must be treated as derived state.

---

## INV-031

Deleting a materialized EvidenceAggregate must not delete underlying Evidence.

---

## INV-032

Evidence frequency must not automatically determine Relationship strength.

---

## INV-033

Source diversity must not automatically determine Relationship strength.

---

## INV-034

Unresolved-Service Evidence must not be discarded.

---

## INV-035

Ambiguous-Service Evidence must not be arbitrarily assigned to a canonical Service.

---

## INV-036

Conflicting Evidence must remain preserved.

---

## INV-037

Temporal aggregation must not erase source-specific temporal semantics.

---

## INV-038

A Relationship must reference one User and one Service.

---

## INV-039

A Relationship may preserve zero, one or multiple Identity references.

---

## INV-040

Multiple Identity references must not automatically imply multiple Accounts.

---

## INV-041

RelationshipStatus and TemporalStatus must remain separate dimensions.

---

## INV-042

A Relationship must not imply a conventional Account.

---

## INV-043

A Relationship must not imply current personal-data possession.

---

## INV-044

Historical Relationships must remain representable in the Service Graph.

---

## INV-045

User corrections must not destructively rewrite source Observations.

---

## INV-046

Derived information must not destructively replace its source provenance.

---

## INV-047

Technical processing failure must remain distinct from Domain uncertainty.

---

## INV-048

AI availability must not be required for deterministic Discovery operations.

---

## INV-049

No numerical Confidence is required by the initial Discovery Domain Model.

---

## INV-050

Relationships must be reassessable when their supporting Evidence or assessment policy changes.

---

# 48. Lifecycle Model

The primary lifecycle chain is:

```text
ConnectedSource
      |
      v
Observation
      |
      v
Evidence
      |
      v
EvidenceAggregate
      |
      v
Relationship
```

Each concept has an independent lifecycle.

Potential operations include:

```text
Disconnect ConnectedSource
Revoke Authorization
Delete Credentials
Delete Cached Provider Data
Delete Observation
Reject Evidence
Supersede Evidence
Rebuild Aggregate
Reassess Relationship
Delete Relationship
```

These operations must not be treated as equivalent.

---

# 49. ConnectedSource Lifecycle

When a ConnectedSource is disconnected:

- new collection must stop;
- authorization material should be revoked or removed as appropriate;
- other Connected Sources must remain unaffected;
- existing Observations require an explicit retention decision;
- derived Evidence may require deletion or invalidation;
- affected Aggregates require rebuilding;
- affected Relationships require reassessment.

Disconnection must not mechanically delete all downstream information without policy evaluation.

---

# 50. Observation Lifecycle

Observations may be:

- retained for reprocessing;
- minimized;
- stored ephemerally;
- deleted after derived information is created;
- deleted by User request or retention policy.

Deleting an Observation may require:

```text
Identify dependent Evidence
        |
        v
Reject or delete dependent Evidence
        |
        v
Rebuild affected Aggregates
        |
        v
Reassess affected Relationships
```

The exact retention policy remains outside this Domain Model.

---

# 51. Evidence Lifecycle

Evidence lifecycle must support reclassification.

Example:

```text
Evidence A
Type:
MARKETING
Status:
ACTIVE
```

after reclassification may become:

```text
Evidence A
Status:
SUPERSEDED
```

while:

```text
Evidence B
Type:
PRIVACY_NOTICE
Status:
ACTIVE
```

is created from the same Observation.

The older Evidence remains historically explainable but should not be counted as a simultaneous current semantic event.

---

# 52. Aggregate Lifecycle

EvidenceAggregates may be:

```text
computed on demand
```

or:

```text
materialized
```

If materialized, they must be invalidated or rebuilt when:

- Active Evidence changes;
- Evidence is superseded;
- Evidence is rejected;
- Service Resolution changes;
- Identity association changes;
- Service merge occurs;
- Service split occurs;
- aggregation policy changes;
- relevant source data is deleted.

---

# 53. Relationship Lifecycle

A Relationship may be created, updated, rejected or reassessed.

Reassessment may be triggered by:

```text
new Evidence
Evidence removal
Evidence status change
Entity re-resolution
Service merge
Service split
Identity reassociation
User correction
ConnectedSource deletion
Assessment policy change
Assessor version change
```

A historical Relationship should not be deleted merely because it is no longer currently observed.

---

# 54. Reprocessing

The Domain Model supports controlled reprocessing.

```text
Observation
    |
    +--> Classifier v1
    |
    +--> Classifier v2
```

and:

```text
ServiceIdentifier
      |
      +--> Resolver v1
      |
      +--> Resolver v2
```

Reprocessing must preserve enough provenance to determine:

- which processing version produced a result;
- which result is currently accepted;
- which result was superseded;
- why a Relationship changed.

---

# 55. User Correction

The User should eventually be able to correct:

- Service resolution;
- Service merge or split;
- Evidence classification;
- Identity association;
- Relationship attribution;
- temporal interpretation.

Examples include:

```text
"This identifier does not belong to Spotify."

"These two Services are the same."

"This was not my account."

"This was a guest purchase."

"This Relationship was historical."

"This Evidence was misclassified."
```

Corrections must remain attributable to the User.

They must not silently rewrite original Observations or historical processing results.

---

# 56. Deliberately Undefined

Draft v0.3 intentionally does not define:

```text
Database technology
Graph technology
Python classes
Package architecture
REST API
JSON Schema
Final Observation payload schemas
Final Evidence taxonomy
Final relationship assessment rules
Service granularity
Service Registry implementation
Service creation workflow
Service merge implementation
Service split implementation
Account representation
Organization model
Legal Data Controller model
CollectionRun implementation
Retention policy
Credential storage technology
AI provider
Numerical Confidence
```

These decisions should follow implementation-oriented design and empirical validation.

---

# 57. Open Questions

## User and Identity

- Can new Identity Seeds be proposed from authorized Observations?
- Must all newly discovered identities be explicitly confirmed?
- How should historical identities be represented?
- How should aliases be modeled?
- When is IdentityServiceAssociation required?

## ConnectedSource

- What exact connection states are required?
- Should connection and authorization state remain separate?
- Where should synchronization state be stored?
- How should locally imported files be represented?
- How should manual input be represented as a ConnectedSource?

## Observation

- Which Observation Types belong to the first MVP?
- How will typed payload schemas be implemented?
- Which Observations should be persisted?
- Which Observations may remain ephemeral?
- Should Connector version be mandatory provenance?
- Is a CollectionRun reference required?

## ServiceIdentifier

- Which identifier types belong to the initial vocabulary?
- Should full URLs remain identifiers?
- How are historical identifiers represented?
- How are third-party infrastructure identifiers handled?
- How should public-suffix reference data be versioned?

## Service

- At what granularity should Services be canonicalized?
- Who creates a new Service?
- How is the initial Service Registry populated?
- How are aliases maintained?
- How are rebranding and acquisitions represented?
- How are Service merge and split operations governed?

## Evidence

- What is the first controlled Evidence taxonomy?
- Which Evidence Types are provider-neutral?
- Which source-specific Evidence Types are justified?
- What are the exact EvidenceStatus transition rules?
- Can Rejected Evidence become Active again?
- How are User corrections prioritized?
- What constitutes duplicate logical Evidence?

## Aggregation

- Should Aggregates be computed on demand or materialized?
- How should unresolved candidate contexts be grouped?
- What constitutes a semantic Evidence conflict?
- Which coverage information belongs in an Aggregate?
- How are incremental and full rebuild results kept equivalent?

## Relationship

- Are the proposed RelationshipStatus values sufficient?
- Are the proposed TemporalStatus values sufficient?
- Which Evidence combinations justify ESTABLISHED?
- How should User confirmation affect status?
- Does REJECTED require explicit User input?
- Should assessment history become a first-class concept?

## Account

- When should Account be promoted?
- How should shared accounts be represented?
- How should migrated accounts be represented?
- How should guest interactions coexist with Account entities?

## Organization

- When should Organization enter the Domain Model?
- How should Brands and Products relate to Services?
- How should Legal Data Controllers be modeled?

## Coverage

- Should CollectionRun become a formal application entity?
- How is source completeness exposed to Relationship Assessment?
- How is partial discovery communicated to the User?

## Privacy

- What retention period applies to Observations?
- What retention period applies to superseded Evidence?
- How are source references protected?
- How does deletion propagate?
- Which Observation Types may be processed by remote AI?

---

# 58. Validation Status

Draft v0.3 is validated against two structurally different scenarios.

## Scenario 001 - Gmail Service Discovery

Validated:

```text
Email metadata Observations
Service Candidate Detection
Entity Resolution
Evidence Classification
Evidence Aggregation
Historical Relationships
Progressive Permission
Provenance
UNKNOWN classifications
```

## Scenario 002 - Password Manager Service Discovery

Further validated:

```text
Source-independent Connector boundary
Non-email Observation types
Sensitive-source minimization
Deterministic classification
Cross-source Service convergence
Multiple Identity references
Source-specific timestamps
Historical credentials
Unresolved Services
```

## Software Contract Cycle

The seven software contracts further validated:

```text
ConnectedSource as Core Entity
Common Observation envelope
Typed Observation payloads
Provider-neutral Observation Types
Candidate / Resolution separation
Parallel Entity Resolution and Classification
Explicit resolution states
Controlled Evidence taxonomy
Evidence lifecycle requirement
Derived Aggregate semantics
RelationshipStatus / TemporalStatus separation
No numerical Confidence in the initial model
```

---

# 59. Current Domain Model

The consolidated Domain Model is:

```text
CORE DOMAIN

USER
 |
 +-- IDENTITY SEED
 |
 +-- CONNECTED SOURCE
 |       |
 |       v
 |   OBSERVATION
 |      /     \
 |     /       \
 |    v         v
 | SERVICE    EVIDENCE
 | IDENTIFIER    |
 |    |          |
 |    v          |
 | SERVICE ------+
 |    |
 +----+----------------------+
      |                      |
      v                      v
 RELATIONSHIP          IDENTITY REFERENCES
      |
      +-- RELATIONSHIP STATUS
      |
      +-- TEMPORAL STATUS
      |
      +-- EVIDENCE BASIS
```

with:

```text
DOMAIN PROCESSES

Connector
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

with:

```text
DERIVED VIEWS

EvidenceAggregate
EvidenceSummary
SourceSummary
TemporalSummary
ConflictSummary
CoverageSummary
```

and:

```text
CANDIDATE CONCEPTS

Account
Organization
Brand
LegalDataController
IdentityServiceAssociation
CollectionRun
RelationshipAssessmentHistory
```

---

# 60. Changes from Draft v0.2

## Relationship Reoriented

The primary Relationship changes from:

```text
IdentitySeed -> Relationship -> Service
```

to:

```text
User -> Relationship -> Service
```

Identity references remain preserved inside the Relationship context.

---

## Relationship State Split

The previous provisional flat state model:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
REJECTED
```

is replaced by two dimensions:

```text
RelationshipStatus

UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

and:

```text
TemporalStatus

UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

---

## Evidence Lifecycle Added

Evidence now has an explicit lifecycle concept:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

This allows reclassification and User correction without counting incompatible historical interpretations simultaneously.

---

## EvidenceAggregate Classified as Derived State

EvidenceAggregate is no longer treated as a possible Domain Entity.

It is explicitly classified as a rebuildable derived view.

---

## Parallel Processing Formalized

Entity Resolution and Evidence Classification are formally represented as independent branches.

Either process may succeed while the other remains unresolved.

---

## Processing Results Classified

The following are explicitly classified as processing results rather than Core Domain Entities:

```text
CandidateDetectionResult
ResolutionResult
ClassificationResult
AggregationResult
RelationshipAssessmentResult
```

---

## Confidence Removed from Initial Domain

Numerical Confidence is explicitly excluded from the initial Discovery Domain Model.

---

## Service Registry Boundary Recognized

The need for a Service Registry is acknowledged while leaving its application and persistence design open.

---

## Account Remains Candidate

Account is not promoted because meaningful Relationships may exist without identifiable accounts.

---

# 61. Next Design Step

With Architecture Draft v0.3 and Domain Model Draft v0.3 aligned, the next step is a limited terminology alignment across the existing software contracts.

The alignment should update only affected concepts:

```text
Evidence
    -> include EvidenceStatus lifecycle

EvidenceAggregator
    -> aggregate ACTIVE Evidence by default

Relationship
    -> primarily User-Service

RelationshipAssessor
    -> use consolidated RelationshipStatus and TemporalStatus

EvidenceAggregate
    -> explicitly derived view

Confidence
    -> outside initial Discovery model
```

The seven contracts should not be rewritten from scratch.

After alignment, the project can begin an implementation-oriented model defining:

- concrete value-object boundaries;
- Python protocols or abstract interfaces;
- package structure;
- repositories;
- Service Registry boundary;
- application orchestration;
- first Observation payload schemas;
- first Evidence taxonomy;
- first deterministic assessment policy;
- vertical Gmail Discovery MVP.

Implementation must preserve the Domain boundaries established in this document rather than collapsing the pipeline into provider-specific application code.
