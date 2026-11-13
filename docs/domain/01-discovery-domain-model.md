# Discovery Domain Model

**Status:** Draft v0.2  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Related Interface:** `docs/interfaces/01-connector-contract.md`  
**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial Domain Model for the Identity and Service Discovery capability of the Personal Data Governance Framework.

The model is derived from:

- the Identity and Service Discovery architecture;
- Scenario 001 - Gmail Service Discovery;
- Scenario 002 - Password Manager Service Discovery;
- the initial Connector Contract.

Its purpose is to identify the concepts that exist in the Discovery Domain and define the relationships between them before implementation-specific software interfaces, persistence models or APIs are finalized.

Draft v0.2 promotes `ConnectedSource` to a core Domain Entity.

This change reflects the requirement that one User may connect:

- multiple source types;
- multiple providers of the same source type;
- multiple accounts using the same provider;
- multiple independent instances of the same Connector implementation.

This document remains implementation-independent.

It does not define:

- Python classes;
- database tables;
- REST resources;
- JSON schemas;
- graph database structures;
- persistence technologies;
- concrete provider APIs;
- concrete authentication implementations.

The objective is to answer:

> What concepts must the framework represent in order to collect information from multiple connected sources, discover Services and explain why the User appears to have or have had Relationships with them?

---

## 2. Design Context

The Discovery architecture currently follows this conceptual pipeline:

```text
User
  |
  v
Identity Seed
  |
  v
Connected Source
  |
  v
Connector
  |
  v
Observation
  |
  v
Service Candidate Detection
  |
  v
Entity Resolution
  |
  v
Evidence Classification
  |
  v
Evidence
  |
  v
Evidence Aggregation
  |
  v
Relationship Assessment
  |
  v
Service Graph
```

This pipeline contains both:

```text
Domain Concepts
```

and:

```text
Domain Processes
```

These must not automatically be treated as the same thing.

For example:

```text
ConnectedSource
Observation
Evidence
Service
Relationship
```

represent information the framework may need to preserve.

By contrast:

```text
Connector
EntityResolver
EvidenceClassifier
RelationshipAssessor
```

represent behavior applied to domain information.

The Domain Model preserves this distinction.

---

## 3. Core Domain Principles

The model is based on the following boundaries:

```text
SOURCE TYPE != PROVIDER

PROVIDER != CONNECTED SOURCE

CONNECTED SOURCE != CONNECTOR

CONNECTED SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

EVIDENCE != RELATIONSHIP

IDENTIFIER != SERVICE

SERVICE != ORGANIZATION

RELATIONSHIP != CURRENT DATA POSSESSION
```

These distinctions prevent provider definitions, concrete user connections, source information, semantic interpretations and inferred Relationships from being collapsed into a single representation.

---

## 4. Domain Overview

The core conceptual model is:

```text
                              USER
                               |
                +--------------+--------------+
                |                             |
                | owns / declares            | connects
                v                             v
          IDENTITY SEED                CONNECTED SOURCE
                |                             |
                |                             | accessed through
                |                             v
                |                         CONNECTOR
                |                             |
                |                             | produces
                |                             v
                |                       OBSERVATION
                |                          /     \
                |                         /       \
                |              interpreted as     \ exposes
                |                      /            \
                |                     v              v
                |                 EVIDENCE     SERVICE IDENTIFIER
                |                     |              |
                |                     |              | resolved to
                |                     |              v
                |                     |           SERVICE
                |                     |              |
                +---------------------+--------------+
                                      |
                                      v
                                RELATIONSHIP
```

The core Domain Entities are:

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

The common classification and configuration concepts include:

```text
SourceType
Provider
ConnectorDescriptor
Capability
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

Additional concepts remain under evaluation:

```text
Account
Organization
ResolutionResult
```

---

## 5. User

A `User` represents the person whose observed digital footprint is being analyzed.

The framework is currently designed from a single-user perspective.

The User may:

- declare one or more Identity Seeds;
- authorize one or more Connected Sources;
- connect multiple sources of the same type;
- connect multiple accounts using the same provider;
- correct derived conclusions;
- revoke individual source connections.

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
```

At this stage, the User does not require a complex profile model.

The framework does not yet need concepts such as:

```text
UserProfile
NaturalPerson
DataSubjectProfile
Principal
```

unless future capabilities demonstrate that they are necessary.

---

## 6. IdentitySeed

An `IdentitySeed` represents a digital identity explicitly declared by the User and used as a starting point for Discovery.

Examples include:

```text
Email Address
Phone Number
Username
Google Account
Apple Account
Microsoft Account
```

Example:

```text
type: EMAIL
value: user@example.com
verification_status: VERIFIED
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

### 6.1 Identity Ownership

An Identity Seed represents an identity the User claims or confirms belongs to them.

The framework must not automatically assume that every identifier encountered during Discovery belongs to the User.

For example, a password-manager Observation may expose:

```text
username:
old-address@example.com
```

when the only known Identity Seed is:

```text
user@example.com
```

The newly observed address may represent:

- another Identity belonging to the User;
- a historical Identity;
- a username unrelated to email ownership;
- a shared account;
- another person's Identity;
- incorrect or obsolete information.

Therefore:

```text
OBSERVED IDENTITY IDENTIFIER
              !=
VERIFIED IDENTITY SEED
```

Automatic creation of additional Identity Seeds remains outside the current model.

The framework may eventually suggest candidate identities to the User, but explicit confirmation may be required before they become verified Identity Seeds.

---

### 6.2 IdentitySeed and ConnectedSource

An Identity Seed may be associated with one or more Connected Sources.

For example:

```text
IdentitySeed:
personal@gmail.com

ConnectedSource:
Personal Gmail
```

However, the concepts remain separate.

An Identity Seed represents an identity belonging to the User.

A Connected Source represents an authorized external source instance.

Therefore:

```text
IDENTITY SEED != CONNECTED SOURCE
```

A Connected Source may also expose information related to multiple Identity Seeds.

For example, a password manager may contain entries associated with several email addresses belonging to the User.

---

## 7. SourceType

A `SourceType` classifies a Discovery Source by the general kind of information it exposes.

Initial source categories may include:

```text
EMAIL
PASSWORD_MANAGER
BROWSER
IDENTITY_PROVIDER
MANUAL
```

These categories must remain extensible.

SourceType answers:

> What general kind of source is this?

It does not identify a specific product, provider or User connection.

For example:

```text
EMAIL
```

is a SourceType.

```text
Gmail
```

is a provider or provider-specific service.

```text
Personal Gmail
```

is a Connected Source belonging to a User.

---

## 8. Provider

A `Provider` identifies the product, platform or organization providing access to a source.

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

> Which external product or platform provides this source?

The core Domain Model must not assume that every provider exposes the same capabilities merely because they support the same SourceType.

For example:

```text
SourceType:
EMAIL
```

may be provided by:

```text
Google
Microsoft
Apple
Proton
```

with different:

- authorization mechanisms;
- APIs;
- metadata availability;
- permission models;
- synchronization capabilities;
- local or remote access models.

Therefore:

```text
SOURCE TYPE != PROVIDER
```

Provider-specific behavior belongs primarily behind the relevant Connector implementation.

---

## 9. DiscoverySource

`DiscoverySource` remains an architectural category describing an external source from which relevant information may be obtained.

Examples include:

```text
Email Provider
Password Manager
Browser
Identity Provider
Manual Input
```

At the Domain Model level, source information is represented more precisely through:

```text
SourceType
Provider
ConnectedSource
```

Conceptually:

```text
Discovery Source Category
        |
        +-- SourceType
        |
        +-- Provider
        |
        +-- ConnectedSource
```

`DiscoverySource` is therefore retained as a useful architectural term but does not need to become a separate persistent entity if the required semantics are already represented by the more precise concepts.

---

## 10. ConnectedSource

A `ConnectedSource` represents a specific external source instance connected or authorized by the User.

It is a core Domain Entity.

Examples include:

```text
Personal Gmail account
Old Gmail account
Work Outlook account
Personal iCloud Mail account
Proton Mail account
Primary password manager
Secondary password manager
Browser profile
```

A Connected Source is distinct from:

- the general SourceType;
- the Provider;
- the Connector implementation;
- the User identity associated with the source;
- the Observations obtained from it.

Therefore:

```text
PROVIDER != CONNECTED SOURCE
```

and:

```text
CONNECTED SOURCE != CONNECTOR
```

---

### 10.1 Why ConnectedSource Is a Core Entity

A single Connector implementation may be used for multiple independent source instances.

For example:

```text
                         GmailConnector
                          /           \
                         /             \
                        v               v
            ConnectedSource A   ConnectedSource B
            personal@gmail.com  oldaddress@gmail.com
```

Each Connected Source may have its own:

- authorization state;
- permission state;
- external account reference;
- synchronization state;
- connection lifecycle;
- revocation state;
- collection history;
- Observations.

Without ConnectedSource, the framework could not cleanly represent multiple accounts using the same provider.

---

### 10.2 Conceptual Representation

A Connected Source may conceptually contain:

```text
ConnectedSource

- id
- source_type
- provider
- connector_id
- display_name
- external_account_reference
- connection_state
- authorization_state
- created_at
- updated_at
```

This is not a final persistence schema.

Sensitive provider identifiers may require protection or minimization.

Authorization credentials and tokens must not be treated as ordinary ConnectedSource attributes.

---

### 10.3 Multiple Sources of the Same Type

A User may connect multiple sources of the same type.

Example:

```text
User
 |
 +-- EMAIL / Gmail / personal@gmail.com
 |
 +-- EMAIL / Gmail / oldaddress@gmail.com
 |
 +-- EMAIL / Outlook / user@outlook.com
 |
 +-- EMAIL / iCloud Mail / user@icloud.com
 |
 +-- EMAIL / Proton Mail / user@proton.me
```

Every Connected Source remains independently identifiable and manageable.

---

### 10.4 Multiple Password Managers

The same model applies to password managers.

For example:

```text
User
 |
 +-- PASSWORD_MANAGER / Provider A / Primary Vault
 |
 +-- PASSWORD_MANAGER / Provider B / Imported Archive
```

Evidence from both sources may eventually resolve to the same Services while retaining independent source provenance.

---

### 10.5 ConnectedSource State

A Connected Source may move through states conceptually equivalent to:

```text
PENDING_AUTHORIZATION
CONNECTED
AUTHORIZATION_EXPIRED
PERMISSION_INSUFFICIENT
REVOKED
DISCONNECTED
ERROR
```

The final state model is not yet defined.

Connection state and authorization state may ultimately need to remain separate.

For example:

```text
Connection State:
CONNECTED

Authorization State:
INSUFFICIENT
```

may be possible when the source is known but a requested capability requires additional permission.

---

### 10.6 Authorization Material

A Connected Source may reference authorization material, but secrets must not be stored as ordinary Domain attributes.

The preferred conceptual boundary is:

```text
ConnectedSource
       |
       v
Credential Reference
       |
       v
Secure Credential Storage
```

rather than:

```text
ConnectedSource
       |
       +-- access_token
       +-- refresh_token
       +-- password
```

The implementation of secure credential storage belongs to the Privacy and Security Architecture.

---

### 10.7 ConnectedSource Capabilities

A Connected Source may support only a subset of the capabilities exposed by its Connector implementation.

Capabilities can depend on:

- provider features;
- granted permissions;
- account configuration;
- deployment environment;
- local software availability;
- user authorization.

Therefore, supported capabilities may need to be evaluated per Connected Source, not only per Connector implementation.

Conceptually:

```text
Connector Implementation
        |
        v
Potential Capabilities
        |
        v
ConnectedSource
        |
        v
Currently Available Capabilities
```

---

### 10.8 ConnectedSource Lifecycle

A Connected Source has a lifecycle independent from the Connector implementation.

For example:

```text
Created
  |
  v
Authorization Pending
  |
  v
Connected
  |
  +--> Authorization Expired
  |
  +--> Permission Insufficient
  |
  +--> Revoked
  |
  +--> Disconnected
```

Disconnecting one Connected Source must not affect another Connected Source using the same Connector.

Example:

```text
Personal Gmail     -> remain connected
Old Gmail          -> disconnect
Outlook            -> remain connected
```

---

## 11. Connector

A `Connector` is responsible for communicating with one or more Connected Sources supported by a provider-specific integration.

A Connector is considered a processing and integration boundary rather than a persistent Domain Entity.

Conceptually:

```text
ConnectedSource
       |
       v
    Connector
       |
       v
  Observation
```

Possible implementations may eventually include:

```text
GmailConnector
OutlookConnector
ICloudMailConnector
ProtonMailConnector
OnePasswordConnector
BitwardenConnector
BrowserConnector
```

The existence and technical feasibility of these examples must be validated individually before implementation.

---

### 11.1 Connector Responsibilities

A Connector may be responsible for:

```text
Authorization
Provider API interaction
Capability detection
Permission analysis
Data retrieval
Pagination
Synchronization
Source-specific error handling
Source-data minimization
Observation creation
```

Its responsibility ends at the boundary between provider-specific representation and the common Discovery Domain.

---

### 11.2 Connector Implementation vs ConnectedSource

The distinction is:

```text
Connector
```

answers:

> How does the framework communicate with this provider?

Whereas:

```text
ConnectedSource
```

answers:

> Which specific external source instance has this User connected?

Example:

```text
Connector:
GmailConnector

Connected Sources:
- Personal Gmail
- Old Gmail
- Secondary Gmail
```

---

### 11.3 Data Minimization at the Connector Boundary

A Connector should avoid exposing information to the rest of the framework when that information is unnecessary for the requested capability.

Conceptually:

```text
External Source
      |
      v
   Connector
      |
      +-- required data --------+
      |                         |
      +-- unnecessary data -- X |
                                |
                                v
                         Observation
```

A password-manager Connector provides a clear example.

A source may expose:

```text
Title
Username
URI
Password
OTP Secret
Recovery Code
```

while Service Discovery may require only:

```text
Title
Username
URI
```

Authentication secrets should remain outside the normal Discovery pipeline.

---

## 12. Observation

An `Observation` represents information obtained from a specific Connected Source before the framework assigns semantic meaning to it.

It represents:

> What did the framework observe from this Connected Source?

rather than:

> What does the framework believe that information means?

Therefore:

```text
CONNECTED SOURCE != OBSERVATION
```

and:

```text
OBSERVATION != EVIDENCE
```

---

### 12.1 Observation and ConnectedSource

Every Observation must retain a reference to the Connected Source from which it originated.

Conceptually:

```text
ConnectedSource
       |
       +-- Observation
       |
       +-- Observation
       |
       +-- Observation
```

This allows the framework to distinguish between identical-looking observations collected from different sources.

For example:

```text
spotify.com
```

may be observed through:

- a personal Gmail account;
- a work Outlook account;
- a password manager;
- a browser profile.

These Observations may converge on the same Service while maintaining separate provenance.

---

### 12.2 Email Observation

An email Connected Source may produce:

```text
Connected Source:
Personal Gmail

Sender:
no-reply@spotify.com

Subject:
Verify your email address

Message Date:
2026-01-01
```

At this stage, no Evidence type has necessarily been assigned.

---

### 12.3 Password Manager Observation

A password-manager Connected Source may produce:

```text
Connected Source:
Primary Password Manager

Title:
Spotify

Username:
user@example.com

URI:
https://accounts.spotify.com
```

This remains an Observation rather than the final semantic interpretation.

---

### 12.4 Observation Core

A common Observation representation may eventually contain concepts equivalent to:

```text
Observation

- id
- connected_source_id
- source_reference
- observation_type
- observed_at
- collected_at
- attributes
- associated_identity_reference
- provenance
```

The exact schema remains undefined.

---

### 12.5 Source-Specific Attributes

Different source types expose different information.

Email may expose:

```text
sender
recipient
subject
message date
thread reference
```

A password manager may expose:

```text
title
username
URI
record modification time
```

The common Observation model must not force every source into an email-shaped or password-manager-shaped structure.

A future representation may combine:

```text
Common Observation Envelope

+

Source-Specific Typed Attributes
```

---

### 12.6 Temporal Semantics

Observation timestamps must preserve their original meaning.

For example:

```text
Email Message Date:
2024-02-01
```

may represent the time associated with a message.

By contrast:

```text
Password Manager Record Modified At:
2024-02-01
```

may represent modification of the password-manager record.

It must not automatically be interpreted as:

```text
Last Service Activity:
2024-02-01
```

Temporal information must therefore preserve both:

```text
timestamp
```

and:

```text
timestamp semantics
```

---

### 12.7 Collection Completeness

An Observation must not imply that the Connected Source was completely analyzed.

Collection status belongs to the collection or synchronization context.

The framework must distinguish:

```text
No relevant Observations found after a complete collection
```

from:

```text
No Observations returned because collection was partial or failed
```

---

## 13. ServiceIdentifier

A `ServiceIdentifier` represents a technical identifier that may contribute to identifying a canonical Service.

Examples include:

```text
spotify.com
accounts.spotify.com
no-reply@spotify.com
https://accounts.spotify.com/login
source-specific service identifier
```

Potential identifier types include:

```text
DOMAIN
HOSTNAME
URL
EMAIL_ADDRESS
EMAIL_DOMAIN
SOURCE_SPECIFIC
```

The final taxonomy remains open.

---

### 13.1 Identifier Is Not Service

A ServiceIdentifier must not automatically be treated as a Service.

Therefore:

```text
IDENTIFIER != SERVICE
```

For example:

```text
accounts.spotify.com
```

may be an observed technical identifier.

The corresponding canonical Service may be:

```text
Spotify
```

---

### 13.2 Multiple Identifiers

A Service may have multiple identifiers.

Conceptually:

```text
Spotify
 |
 +-- spotify.com
 |
 +-- accounts.spotify.com
 |
 +-- open.spotify.com
 |
 +-- other identifiers
```

Identifiers from multiple Connected Sources may resolve to the same Service.

---

### 13.3 Identifier Provenance

A ServiceIdentifier derived from an Observation must remain traceable to:

- the Observation;
- the Connected Source;
- the original source value;
- any normalization steps;
- the final Entity Resolution result.

---

## 14. Service

A `Service` represents a normalized digital service with which the User may have or have had a Relationship.

Examples include:

```text
Spotify
Netflix
GitHub
Amazon
```

A Service is distinct from:

```text
an email sender
a domain
a URL
a credential record
an Observation
a Connected Source
an Organization
```

---

### 14.1 Service Identity

Conceptually:

```text
Service

- id
- name
- identifiers
- status
```

This is not a database schema.

---

### 14.2 Provider and Service

A Provider used for Discovery may also be discovered as a Service.

For example, Google may act as:

- the Provider of a Gmail Connected Source;
- a Service with which the User has a Relationship.

These roles must remain distinguishable.

Conceptually:

```text
Google as Source Provider
             !=
Google as Discovered Service
```

The same real-world organization may participate in multiple domain roles.

---

### 14.3 Service vs Organization

A Service and the Organization operating that Service must not automatically be considered equivalent.

For example:

```text
Organization
    |
    +-- Service A
    |
    +-- Service B
```

The framework may later need to distinguish:

```text
Service
Brand
Organization
Legal Data Controller
```

The current Discovery Domain does not yet contain enough evidence to define this model.

Therefore:

```text
SERVICE != ORGANIZATION
```

remains an architectural boundary.

---

## 15. Entity Resolution

Entity Resolution is the process that attempts to map observed ServiceIdentifiers to canonical Services.

It is behavior rather than a core Domain Entity.

Conceptually:

```text
Observation
     |
     v
ServiceIdentifier
     |
     v
EntityResolver
     |
     +-----------+
     |           |
     v           v
Resolved      Unresolved
     |
     v
Service
```

---

### 15.1 Cross-Source Resolution

Identifiers derived from different Connected Sources may resolve to the same Service.

Example:

```text
Personal Gmail
      |
      v
no-reply@spotify.com
      |
      v
spotify.com
      |
      +-------------------+
                          |
                          v
                       Spotify
                          ^
                          |
      +-------------------+
      |
accounts.spotify.com
      ^
      |
Primary Password Manager
```

The canonical Service must not be duplicated merely because the supporting identifiers originated from different Connected Sources.

---

### 15.2 Resolution Result

Although Entity Resolution itself is behavior, the result of resolution may need to be preserved.

A future value or record may contain concepts such as:

```text
ResolutionResult

- observed_identifier
- normalized_identifier
- resolved_service
- resolution_status
- resolution_method
- created_at
```

Potential states may include:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

The exact representation is not yet defined.

---

### 15.3 Resolution Provenance

Entity Resolution must never destroy the original identifier.

Conceptually:

```text
Connected Source
       |
       v
Observation
       |
       v
Original Identifier
       |
       v
Normalized Identifier
       |
       v
Resolved Service
```

All relevant stages should remain explainable and reprocessable.

---

## 16. Evidence

`Evidence` represents the framework's semantic interpretation of one or more Observations in the context of Service Discovery.

It answers:

> What does this Observation appear to tell us about a possible Relationship?

Examples include:

```text
ACCOUNT_VERIFICATION
SUBSCRIPTION
PAYMENT
PASSWORD_MANAGER_ENTRY
```

Evidence taxonomies may vary across source types and capabilities.

---

### 16.1 Example

```text
Observation:

Subject:
Verify your email address
```

may produce:

```text
Evidence:

ACCOUNT_VERIFICATION
```

Similarly:

```text
Observation:

Password-manager record
URI: accounts.spotify.com
```

may produce:

```text
Evidence:

PASSWORD_MANAGER_ENTRY
```

---

### 16.2 Evidence Core

A conceptual Evidence representation may contain:

```text
Evidence

- id
- type
- supporting_observation_references
- service_reference
- classification_method
- classification_status
- created_at
- provenance
```

Potential classification methods may include:

```text
RULE
AI
MANUAL
```

The exact model remains open.

---

### 16.3 Evidence May Remain Unknown

Classification must never be forced.

For example:

```text
classification_status:
UNKNOWN
```

is valid.

The supporting Observation must remain available.

---

### 16.4 No Arbitrary Confidence

Draft v0.2 does not assign arbitrary numerical confidence values to Evidence.

Values such as:

```text
confidence = 0.87
```

must not be introduced until:

- their semantics are defined;
- calibration is possible;
- representative data exists;
- they provide measurable user benefit.

---

## 17. Evidence Classification

Evidence Classification is behavior applied to Observations.

It is not currently modeled as a persistent Domain Entity.

Conceptually:

```text
Observation
     |
     v
EvidenceClassifier
     |
     v
Evidence
```

Different sources may use different classification strategies.

For example:

```text
Email
 |
 +-- deterministic rules
 |
 +-- AI for ambiguous cases
```

while:

```text
Password Manager
 |
 +-- primarily deterministic classification
```

The domain must support this variation without making AI mandatory.

---

## 18. Evidence Aggregation

Evidence Aggregation combines Evidence associated with the same discovery context.

It is a process rather than a core Domain Entity.

Conceptually:

```text
Evidence A
Evidence B
Evidence C
    |
    v
EvidenceAggregator
    |
    v
Relationship Context
```

Aggregation must not destroy individual Evidence or its ConnectedSource provenance.

For example:

```text
100 Evidence items
```

may contribute to:

```text
1 Relationship
```

while all Evidence items remain independently traceable.

---

## 19. Relationship

A `Relationship` represents the framework's current assessment that an Identity and a Service are or were related.

Conceptually:

```text
IdentitySeed
     |
     v
Relationship
     |
     v
Service
```

A Relationship is derived from Evidence.

Therefore:

```text
EVIDENCE != RELATIONSHIP
```

---

### 19.1 Relationship Core

A conceptual representation may contain:

```text
Relationship

- id
- identity_references
- service_reference
- state
- first_observed
- last_observed
```

The final representation remains undefined.

---

### 19.2 Relationship State

Potential states may eventually include:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
REJECTED
```

These values remain provisional.

The framework should not freeze a Relationship state model before additional empirical validation.

---

### 19.3 Relationship Is Not Current Data Possession

A discovered Relationship does not establish which personal data the Service currently holds.

Therefore:

```text
RELATIONSHIP
        !=
CURRENT DATA POSSESSION
```

A Relationship belongs to Discovery.

Current data possession belongs to later Personal Data Acquisition and Understanding capabilities.

---

### 19.4 Relationship and ConnectedSource

A Relationship is not owned by one Connected Source.

It may be supported by Evidence originating from multiple Connected Sources.

Example:

```text
                       Spotify
                          |
                    Relationship
                    /     |      \
                   /      |       \
                  v       v        v
            Gmail A   Outlook   Password Manager
            Evidence  Evidence      Evidence
```

Disconnecting one Connected Source must not automatically remove a Relationship if other Evidence still supports it.

The Relationship may instead require reassessment.

---

## 20. Evidence Supporting Relationships

A Relationship may be supported by multiple Evidence items.

Conceptually:

```text
               Relationship
              /      |      \
             /       |       \
            v        v        v
        Evidence  Evidence  Evidence
```

Evidence may originate from:

- different Observations;
- different Connected Sources;
- different SourceTypes;
- different providers;
- different times.

This cross-source support is a core requirement of the framework.

---

## 21. Multi-Source Convergence

The same canonical Service may be discovered independently through multiple Connected Sources.

For example:

```text
Personal Gmail
      |
      v
Observation
      |
      v
spotify.com
      |
      +----------------------+
                             |
                             v
                          Spotify
                             ^
                             |
      +----------------------+
      |
accounts.spotify.com
      ^
      |
Primary Password Manager
```

The framework must preserve:

```text
independent ConnectedSource provenance
```

while allowing:

```text
canonical Service convergence
```

This means the framework should not create provider-specific copies such as:

```text
Spotify_Gmail
Spotify_Outlook
Spotify_PasswordManager
```

when available Evidence indicates that they represent the same Service.

---

## 22. Multiple Connected Sources

The target Domain Model must support structures such as:

```text
User
 |
 +-- ConnectedSource
 |     |
 |     +-- SourceType: EMAIL
 |     +-- Provider: Google
 |     +-- Account: personal@gmail.com
 |
 +-- ConnectedSource
 |     |
 |     +-- SourceType: EMAIL
 |     +-- Provider: Google
 |     +-- Account: oldaddress@gmail.com
 |
 +-- ConnectedSource
 |     |
 |     +-- SourceType: EMAIL
 |     +-- Provider: Microsoft
 |     +-- Account: user@outlook.com
 |
 +-- ConnectedSource
 |     |
 |     +-- SourceType: PASSWORD_MANAGER
 |     +-- Provider: Provider A
 |     +-- Display Name: Primary Vault
 |
 +-- ConnectedSource
       |
       +-- SourceType: PASSWORD_MANAGER
       +-- Provider: Provider B
       +-- Display Name: Archive
```

Each Connected Source may independently:

- authorize;
- collect;
- synchronize;
- fail;
- require additional permission;
- expire;
- be revoked;
- be disconnected.

---

## 23. Candidate Concept: Account

Scenario 002 exposed a possible distinction between:

```text
Service
```

and:

```text
Account
```

For example:

```text
Service:
Spotify

Account A:
personal@example.com

Account B:
oldmail@example.net
```

This could eventually produce:

```text
Service
   |
   +-- Account
   |      |
   |      +-- Identity
   |
   +-- Account
          |
          +-- Identity
```

However, `Account` is not currently a core Domain Entity.

---

### 23.1 Why Account May Be Useful

An Account could allow the framework to represent:

- multiple accounts with the same Service;
- historical accounts;
- multiple identities used with one Service;
- shared accounts;
- migrated accounts.

---

### 23.2 Why Account Is Not Yet Included

Not every Service Relationship exposes an identifiable Account.

For example:

```text
Marketing Evidence
Browser Activity
Guest Purchase
Privacy Notice
```

may support a Relationship without revealing a distinct Account.

Therefore, additional evidence is required before determining whether Account should become:

```text
a core entity
```

or:

```text
an optional Relationship detail
```

For now:

```text
Account = CANDIDATE DOMAIN CONCEPT
```

---

## 24. Candidate Concept: Organization

A Service may be operated by an Organization.

An Organization may operate multiple Services.

A Service may change owner over time.

The framework may eventually need:

```text
Organization
Brand
Service
Legal Data Controller
```

as separate concepts.

However, Identity and Service Discovery currently focuses on canonical Services.

Therefore:

```text
Organization = CANDIDATE DOMAIN CONCEPT
```

until later acquisition and governance scenarios demonstrate the required semantics.

---

## 25. Candidate Concept: ResolutionResult

Entity Resolution is behavior, but its result may need to be persistable and versionable.

A `ResolutionResult` could preserve:

```text
Observed Identifier
Normalized Identifier
Resolved Service
Resolution Status
Resolution Method
Resolver Version
Creation Time
```

This concept remains under evaluation because some of its information may instead belong to ServiceIdentifier provenance.

---

## 26. Domain Processes

The following concepts represent behavior rather than persistent Domain Entities.

---

### 26.1 Connector

```text
ConnectedSource
       |
       v
Connector
       |
       v
Observation
```

Responsibilities include authorized retrieval, source minimization and translation.

---

### 26.2 ServiceCandidateDetector

```text
Observation
     |
     v
Candidate Detector
    / \
 yes   no
```

Determines whether an Observation is relevant to Service Discovery.

---

### 26.3 EntityResolver

```text
ServiceIdentifier
      |
      v
EntityResolver
      |
      v
Service / Unresolved
```

Determines which canonical Service an observed identifier may represent.

---

### 26.4 EvidenceClassifier

```text
Observation
     |
     v
EvidenceClassifier
     |
     v
Evidence
```

Assigns semantic meaning while allowing `UNKNOWN`.

---

### 26.5 EvidenceAggregator

```text
Evidence
Evidence
Evidence
    |
    v
EvidenceAggregator
```

Combines Evidence for Relationship Assessment without destroying individual provenance.

---

### 26.6 RelationshipAssessor

```text
Aggregated Evidence
        |
        v
RelationshipAssessor
        |
        v
Relationship
```

Evaluates what accumulated Evidence suggests about the Identity-Service Relationship.

---

## 27. Domain Entities vs Processes

| Concept | Current Classification |
|---|---|
| `User` | Core Domain Entity |
| `IdentitySeed` | Core Domain Entity |
| `ConnectedSource` | Core Domain Entity |
| `Observation` | Core Domain Entity |
| `ServiceIdentifier` | Core Domain Entity / Value Concept |
| `Service` | Core Domain Entity |
| `Evidence` | Core Domain Entity |
| `Relationship` | Core Domain Entity |
| `SourceType` | Classification Concept |
| `Provider` | Classification / Reference Concept |
| `Connector` | Process / Integration Boundary |
| `ServiceCandidateDetector` | Domain Process |
| `EntityResolver` | Domain Process |
| `EvidenceClassifier` | Domain Process |
| `EvidenceAggregator` | Domain Process |
| `RelationshipAssessor` | Domain Process |
| `ResolutionResult` | Candidate Value Concept |
| `Account` | Candidate Domain Concept |
| `Organization` | Candidate Domain Concept |

These classifications remain provisional and may be revised if implementation or additional scenarios expose contradictions.

---

## 28. Conceptual Multi-Source Model

The target Discovery Domain should support a topology similar to:

```text
                                  USER
                                    |
                  +-----------------+-----------------+
                  |                                   |
                  v                                   v
            IDENTITY SEED                     CONNECTED SOURCE
                                                      |
                                  +-------------------+-------------------+
                                  |                   |                   |
                                  v                   v                   v
                            Personal Gmail      Work Outlook       Password Manager
                                  |                   |                   |
                                  v                   v                   v
                            GmailConnector     OutlookConnector     VaultConnector
                                  |                   |                   |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                                 OBSERVATIONS
                                                      |
                                      +---------------+---------------+
                                      |                               |
                                      v                               v
                              SERVICE IDENTIFIERS          EVIDENCE CLASSIFICATION
                                      |                               |
                                      v                               v
                               ENTITY RESOLUTION                    EVIDENCE
                                      |                               |
                                      v                               |
                                   SERVICE <--------------------------+
                                      |
                                      v
                                RELATIONSHIP
                                      |
                                      v
                                 SERVICE GRAPH
```

Future source types and providers should be able to join this architecture without changing the common Discovery Domain.

---

## 29. Domain Invariants

The following invariants should hold unless future scenarios demonstrate otherwise.

### INV-001

A Service must not be created solely because an arbitrary external identifier was observed.

```text
IDENTIFIER != SERVICE
```

---

### INV-002

Evidence must remain traceable to supporting Observations.

```text
Evidence
   |
   v
Observation
```

must remain reconstructable.

---

### INV-003

Every Observation must retain a reference to the Connected Source from which it originated.

---

### INV-004

Every Connected Source must belong to a User.

---

### INV-005

A Connector implementation may serve multiple independent Connected Sources.

---

### INV-006

Multiple Connected Sources using the same provider must be independently manageable.

---

### INV-007

Disconnecting one Connected Source must not automatically disconnect another Connected Source.

---

### INV-008

An unresolved Observation must not require creation of a fabricated Service.

---

### INV-009

Classification failure must be representable as `UNKNOWN`.

---

### INV-010

A Relationship must not be interpreted as proof of current personal-data possession.

---

### INV-011

Multiple Observations may support one Service.

---

### INV-012

Multiple Connected Sources may support one Service.

---

### INV-013

Multiple providers may contribute Evidence to one canonical Service.

---

### INV-014

Source-specific secrets unnecessary for Service Discovery must not become normal Discovery Observations.

---

### INV-015

Derived information must not destructively replace its source provenance.

---

### INV-016

AI availability must not be required for deterministic Discovery operations.

---

### INV-017

Provider authorization credentials must not be represented as ordinary ConnectedSource attributes.

---

### INV-018

The absence of Observations must not be interpreted as absence of relevant source information unless collection completed successfully.

---

### INV-019

A Connected Source and an Identity Seed must not be assumed to be equivalent.

---

### INV-020

A Provider and a discovered Service must remain distinguishable domain roles, even when they refer to the same real-world organization.

---

## 30. Lifecycle Considerations

Domain concepts have different lifecycles.

Conceptually:

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
Relationship
```

Disconnecting a Connected Source does not necessarily imply automatic deletion of every downstream concept.

Potential operations include:

```text
Disconnect Source
Revoke Authorization
Delete Credentials
Delete Cached Provider Data
Delete Observations
Delete Evidence
Recalculate Relationships
Delete ConnectedSource
```

These operations must remain conceptually distinguishable.

---

### 30.1 Source Disconnection

When a Connected Source is disconnected:

- new collection must stop;
- authorization material should be invalidated or removed as appropriate;
- other Connected Sources must remain unaffected;
- existing Observations and Evidence require an explicit lifecycle decision;
- Relationships may need reassessment if they depended only on that source.

The exact deletion and retention policy belongs to the Privacy and Security Architecture.

---

### 30.2 Authorization Expiration

Authorization expiration does not necessarily mean that the Connected Source no longer exists.

Conceptually:

```text
ConnectedSource:
exists

Authorization:
expired
```

The source may be reauthorized later.

---

### 30.3 Revocation

Revocation must be distinguishable from voluntary disconnection where the provider supports that distinction.

Both operations stop future collection, but they may have different security and provider-side semantics.

---

### 30.4 Relationship Reassessment

If Evidence from one Connected Source is removed, the framework may need to reassess affected Relationships.

Example:

```text
Spotify Relationship
 |
 +-- Gmail Evidence
 |
 +-- Password Manager Evidence
```

If Gmail Evidence is deleted, the Relationship may remain supported by Password Manager Evidence.

The Relationship must not be deleted mechanically without reassessment.

---

## 31. Reprocessing

Observations should support reprocessing where practical.

Example:

```text
Observation
    |
    +--> EvidenceClassifier v1
    |           |
    |           v
    |       Evidence v1
    |
    +--> EvidenceClassifier v2
                |
                v
            Evidence v2
```

Similarly:

```text
ServiceIdentifier
      |
      +--> EntityResolver v1
      |
      +--> EntityResolver v2
```

This allows the framework to improve classification and resolution without necessarily retrieving source information again.

The exact persistence required to enable reprocessing remains an open question.

---

## 32. User Correction

Future versions should allow the User to correct derived conclusions.

Examples include:

```text
"This identifier does not belong to Spotify."

"These two Services are the same."

"These two Services are different."

"This account does not belong to me."

"This was only a guest purchase."

"This Relationship is historical."

"This Connected Source is associated with a different Identity Seed."
```

User correction should not silently destroy historical provenance.

Corrections should remain attributable to the User and distinguishable from automated conclusions.

---

## 33. Deliberately Undefined

Draft v0.2 intentionally does not define:

```text
Database technology
Database schema
Python classes
Application package structure
REST API
Graph database
Service Graph implementation
Final Observation schema
Final Evidence taxonomy
Final Relationship states
Confidence algorithm
AI provider
Entity Resolution algorithm
Persistence strategy
Authorization credential storage
Account representation
Organization model
Legal Data Controller model
Connector plugin registration
```

These decisions should follow Domain and interface validation rather than precede it.

---

## 34. Open Questions

### User and Identity

- Can new Identity Seeds be proposed from authorized Observations?
- Must the User explicitly confirm all newly discovered identities?
- How should historical identities be represented?
- How should aliases be represented?
- Can one Connected Source be associated with multiple Identity Seeds?

### ConnectedSource

- Which connection states are required?
- Should connection state and authorization state be separate?
- Which synchronization state belongs to ConnectedSource?
- Which state should remain internal to the Connector?
- How should external account references be protected?
- Can one Connected Source change Provider identity?
- How should locally imported files be represented as Connected Sources?
- How should manual input be represented if it has no external authorization lifecycle?

### Provider

- Should Provider be an entity, enum or external registry entry?
- How should provider rebranding be handled?
- How should self-hosted or local providers be represented?
- How should multiple products from the same organization be distinguished?

### Connector

- How are Connector implementations registered?
- Can a Connector support more than one SourceType?
- Can different Connector implementations support the same Provider?
- How should Connector versions be managed?
- How are provider-specific capabilities mapped to common framework capabilities?

### Observation

- What is the minimal common Observation envelope?
- How should typed source-specific attributes be represented?
- Which Observations should be persisted?
- Which source information can safely be discarded after classification?
- How should source-specific temporal semantics be represented?
- How should Observations be versioned?

### ServiceIdentifier

- Which identifier types are required?
- Can one identifier resolve to multiple Services in different contexts?
- How should historical identifiers be represented?
- How should third-party infrastructure identifiers be handled?
- Should normalized and original identifiers be separate values?

### Service

- When are two Services considered the same?
- How should rebranding and acquisitions be represented?
- Should Service and Brand be separate?
- Should Service and Organization be separate?
- How should legal data controllers eventually relate to Services?

### Evidence

- Which Evidence Types should be common across source types?
- Which should remain source-specific?
- Can one Observation generate multiple Evidence items?
- Can multiple Observations generate one Evidence item?
- How should conflicting Evidence be represented?

### Relationship

- Is a Relationship primarily between User and Service or IdentitySeed and Service?
- Can multiple Identity Seeds participate in one Relationship?
- How should historical Relationships be represented?
- How should conflicting Evidence affect a Relationship?
- How should removal of source Evidence trigger reassessment?

### Account

- Should Account become a first-class Domain Entity?
- Can a Relationship exist without an Account?
- Can multiple Accounts belong to the same Service?
- Can one Account use multiple Identity Seeds?
- How should shared Accounts be represented?
- How should guest purchases be represented?

### Privacy

- What information must be removed at the Connector boundary?
- Which provider attributes may be persisted?
- How long should Observations and Evidence remain locally stored?
- How should deletion propagate through derived information?
- How should external account references be encrypted or minimized?
- How should credential references be separated from Domain persistence?

---

## 35. Validation Status

Draft v0.2 is based on two structurally different Discovery scenarios and the first Connector Contract.

### Scenario 001 - Gmail Service Discovery

Validated:

```text
Connector
Observation
ServiceIdentifier
Entity Resolution
Evidence Classification
Evidence Aggregation
Relationship Assessment
Progressive Permission
Provenance
```

### Scenario 002 - Password Manager Service Discovery

Further validated:

```text
Source-independent Observation
Source-independent Entity Resolution
Deterministic Evidence Classification
Cross-source Service convergence
Sensitive-source minimization
Multiple identities per Service
Historical Relationships
```

Scenario 002 also exposed:

```text
Account
```

as a candidate Domain Concept.

### Connector Contract

The Connector Contract demonstrated that the framework must distinguish between:

```text
Connector Implementation
```

and:

```text
A particular external source instance connected by the User
```

This distinction is required to support:

- multiple Gmail accounts;
- multiple email providers;
- multiple password managers;
- independent authorization states;
- independent synchronization states;
- per-source collection;
- per-source revocation;
- per-source disconnection;
- Observation provenance.

For this reason, Draft v0.2 promotes:

```text
ConnectedSource
```

to a core Domain Entity.

---

## 36. Current Domain Model

The current baseline is:

```text
CORE DOMAIN

User
 |
 +-- IdentitySeed
 |
 +-- ConnectedSource
        |
        v
    Observation
        |
        +-----------> ServiceIdentifier
        |                    |
        |                    v
        |              Entity Resolution
        |                    |
        |                    v
        |                 Service
        |
        v
     Evidence
        |
        v
   Relationship
        |
        +------------ IdentitySeed
        |
        +------------ Service
```

with:

```text
CLASSIFICATION AND REFERENCE CONCEPTS

SourceType
Provider
Capability
```

and:

```text
DOMAIN PROCESSES

Connector
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

and:

```text
CANDIDATE CONCEPTS

Account
Organization
ResolutionResult
```

---

## 37. Changes from Draft v0.1

Draft v0.2 introduces the following changes.

### ConnectedSource Promoted

`ConnectedSource` is promoted from:

```text
Candidate Domain Concept
```

to:

```text
Core Domain Entity
```

### DiscoverySource Refined

The broad architectural concept of DiscoverySource is refined through:

```text
SourceType
Provider
ConnectedSource
```

### Connector Relationship Clarified

A Connector implementation may serve multiple Connected Sources.

```text
Connector
   |
   +-- ConnectedSource A
   |
   +-- ConnectedSource B
```

### Observation Provenance Strengthened

Every Observation must reference the Connected Source from which it originated.

### Source Lifecycle Added

Independent authorization, revocation, disconnection and synchronization requirements are now represented at the ConnectedSource level.

### Multi-Instance Support Formalized

The Domain Model explicitly supports:

- multiple accounts using the same provider;
- multiple providers of the same SourceType;
- multiple password managers;
- independent connection lifecycle.

### Invariants Updated

New invariants prevent:

- conflating Provider and ConnectedSource;
- conflating IdentitySeed and ConnectedSource;
- disconnecting all provider accounts when only one source instance is selected;
- storing authorization secrets as normal Domain attributes.

---

## 38. Next Design Step

The next step is to define the software contract for:

```text
Observation
```

Every Connector must produce Observations, and every downstream Discovery component depends on them.

The Observation Contract should determine:

```text
What belongs in the common Observation envelope?

How are source-specific attributes represented?

How is ConnectedSource provenance preserved?

How are source references represented?

How are temporal semantics represented?

How is schema evolution handled?

How are sensitive attributes excluded?

How are duplicate observations detected?

How is collection completeness represented?
```

Only after the Observation boundary is sufficiently stable should downstream contracts be defined for:

```text
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

The recommended dependency order remains:

```text
Connector Contract
        |
        v
Observation Contract
        |
        v
Service Candidate Detector Contract
        |
        v
Entity Resolver Contract
        |
        v
Evidence Classifier Contract
        |
        v
Evidence Aggregator Contract
        |
        v
Relationship Assessor Contract
```
