# Discovery Domain Model

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial Domain Model for the Identity and Service Discovery capability of the Personal Data Governance Framework.

The model is derived from:

- the Identity and Service Discovery architecture;
- Scenario 001 - Gmail Service Discovery;
- Scenario 002 - Password Manager Service Discovery.

Its purpose is to identify the concepts that exist in the discovery domain and define the relationships between them before implementation-specific software interfaces, persistence models or APIs are created.

This document is deliberately implementation-independent.

It does not define:

- Python classes;
- database tables;
- REST resources;
- JSON schemas;
- graph database structures;
- persistence technologies;
- concrete Connector APIs.

The objective is to answer:

> What concepts must the framework represent in order to discover Services and explain why the user appears to have or have had Relationships with them?

---

## 2. Design Context

The Discovery architecture currently follows this conceptual pipeline:

```text
Identity Seed
      |
      v
Discovery Source
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
Observation
Evidence
Service
Relationship
```

represent information the domain may need to preserve.

By contrast:

```text
Entity Resolver
Evidence Classifier
Relationship Assessor
```

represent behavior applied to domain information.

The Domain Model must preserve this distinction.

---

## 3. Core Domain Principles

The model is based on the following boundaries:

```text
SOURCE != CONNECTOR

SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

EVIDENCE != RELATIONSHIP

IDENTIFIER != SERVICE

RELATIONSHIP != CURRENT DATA POSSESSION
```

These distinctions prevent source-specific information, interpretation and inferred relationships from being collapsed into a single representation.

---

## 4. Domain Overview

The initial conceptual model is:

```text
                         USER
                          |
                          | owns / declares
                          v
                    IDENTITY SEED
                          |
                          |
                          | participates in
                          v
                     RELATIONSHIP
                    /            \
                   /              \
        supported by              \ relates to
                 /                  \
                v                    v
            EVIDENCE              SERVICE
                ^                    ^
                |                    |
                |                    | resolved from
         interpreted from            |
                |               SERVICE IDENTIFIER
                |                    ^
                v                    |
           OBSERVATION --------------+
                ^
                |
                | produced from
                |
            CONNECTOR
                ^
                |
                | accesses
                |
        DISCOVERY SOURCE
```

The primary domain concepts are:

```text
User
IdentitySeed
DiscoverySource
Observation
ServiceIdentifier
Service
Evidence
Relationship
```

The primary processing concepts are:

```text
Connector
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

Some additional concepts remain under evaluation:

```text
Account
ConnectedSource
ResolutionResult
```

---

# 5. User

A User represents the person whose observed digital footprint is being analyzed.

The framework is currently designed from a single-user perspective.

The User owns or declares one or more Identity Seeds.

Conceptually:

```text
User
 |
 +-- Identity Seed
 |
 +-- Identity Seed
 |
 +-- Identity Seed
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

# 6. IdentitySeed

An `IdentitySeed` represents a digital identity explicitly declared by the User and used as a starting point for discovery.

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

## 6.1 Identity Ownership

An Identity Seed represents an identity the User claims or confirms belongs to them.

The framework should not automatically assume that every identifier encountered during Discovery belongs to the User.

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
OBSERVED IDENTIFIER
        !=
VERIFIED IDENTITY SEED
```

Automatic discovery of additional Identity Seeds remains an open question.

---

# 7. DiscoverySource

A `DiscoverySource` represents an external source from which information useful for Service Discovery may be obtained.

Examples include:

```text
Email Provider
Password Manager
Browser
Identity Provider
Manual Input
```

A Discovery Source describes where information comes from.

It does not represent the software component used to retrieve that information.

Therefore:

```text
DISCOVERY SOURCE != CONNECTOR
```

---

## 7.1 Source Types

Initial source categories may include:

```text
EMAIL
PASSWORD_MANAGER
BROWSER
IDENTITY_PROVIDER
MANUAL
```

These categories remain extensible.

Future sources should be introducible without redesigning the core Discovery Domain.

---

## 7.2 Providers

Sources of the same type may be provided by different products or organizations.

For example:

```text
EMAIL
 |
 +-- Gmail
 +-- Outlook
 +-- iCloud Mail
 +-- Proton Mail
 +-- Future Provider
```

and:

```text
PASSWORD_MANAGER
 |
 +-- Provider A
 +-- Provider B
 +-- Provider C
```

Provider-specific behavior must remain outside the common Discovery Domain whenever possible.

---

## 7.3 Multiple Connected Sources

A User may connect multiple sources simultaneously.

For example:

```text
User
 |
 +-- personal Gmail account
 |
 +-- secondary Gmail account
 |
 +-- Outlook account
 |
 +-- iCloud Mail account
 |
 +-- Password Manager A
 |
 +-- Password Manager B
 |
 +-- Browser Profile
```

These sources may independently produce Observations that eventually resolve to the same Service.

The Domain Model must therefore support:

```text
many connected sources
        |
        v
many observations
        |
        v
shared canonical Services
```

without creating provider-specific copies of the same Service.

---

## 7.4 DiscoverySource vs Connected Source

A distinction may eventually be required between:

```text
Source Type
Provider
Connected Source Instance
```

For example:

```text
Source Type:
EMAIL

Provider:
GMAIL

Connected Source:
user@gmail.com
```

A User may have multiple Connected Sources using the same Provider.

Example:

```text
Gmail
 |
 +-- user@gmail.com
 |
 +-- oldaddress@gmail.com
```

The exact representation of `ConnectedSource` is not yet defined.

It remains a candidate domain concept to be evaluated when Connector interfaces and authorization lifecycle are designed.

---

# 8. Connector

A `Connector` is responsible for communicating with a Discovery Source.

A Connector is currently considered a processing or integration boundary rather than a core persistent Domain Entity.

Conceptually:

```text
Discovery Source
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
PasswordManagerConnector
BrowserConnector
```

---

## 8.1 Connector Responsibilities

A Connector may be responsible for:

```text
Authorization
Source API interaction
Capability detection
Permission management
Data retrieval
Pagination
Synchronization
Source-specific error handling
Source-data minimization
Observation creation
```

Its responsibility ends at the boundary between source-specific representation and the common Discovery Domain.

---

## 8.2 Data Minimization at the Connector Boundary

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

Password Manager Service Discovery provides a clear example.

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

Authentication secrets should therefore remain outside the normal Discovery pipeline.

The exact security boundary of Connectors will be refined during software-interface design.

---

# 9. Observation

An `Observation` represents information obtained from a Discovery Source before the framework assigns semantic meaning to it.

It represents:

> What did the framework observe?

rather than:

> What does the framework believe that information means?

Therefore:

```text
OBSERVATION != EVIDENCE
```

---

## 9.1 Example: Email Observation

An email source may produce:

```text
Source:
Gmail

Sender:
no-reply@spotify.com

Subject:
Verify your email address

Message Date:
2026-01-01
```

At this stage, no Evidence type has necessarily been assigned.

---

## 9.2 Example: Password Manager Observation

A password-manager source may produce:

```text
Source:
Password Manager

Title:
Spotify

Username:
user@example.com

URI:
https://accounts.spotify.com
```

Again, this is an Observation rather than the final interpretation.

---

## 9.3 Observation Core

A common Observation representation may eventually contain concepts equivalent to:

```text
Observation

- id
- source_reference
- observed_at
- collected_at
- attributes
- associated_identity
- provenance
```

The exact schema remains undefined.

---

## 9.4 Source-Specific Attributes

Different Discovery Sources expose different information.

Email may expose:

```text
sender
recipient
subject
message date
```

A password manager may expose:

```text
title
username
URI
record modification time
```

The common Observation model must therefore avoid forcing every source into an email-shaped or password-manager-shaped structure.

A future representation may combine:

```text
Common Observation Metadata

+

Source-Specific Attributes
```

The exact mechanism will be determined during implementation design.

---

## 9.5 Temporal Semantics

Observation timestamps must preserve their original meaning.

For example:

```text
Email Date:
2024-02-01
```

may represent the message timestamp.

By contrast:

```text
Password Manager Modified At:
2024-02-01
```

may represent modification of the local credential record.

It must not automatically be interpreted as:

```text
Last Service Activity:
2024-02-01
```

Therefore temporal information must preserve both:

```text
timestamp
```

and its:

```text
source semantics
```

---

# 10. ServiceIdentifier

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

## 10.1 Identifier Is Not Service

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

The corresponding Service may be:

```text
Spotify
```

---

## 10.2 Multiple Identifiers

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

A single identifier may also require contextual interpretation before being associated with a Service.

The exact cardinality and historical model remain to be defined.

---

# 11. Service

A `Service` represents a normalized digital service with which the User may have or have had a relationship.

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
an Organization
```

---

## 11.1 Service Identity

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

## 11.2 Service vs Organization

A Service and the Organization operating that Service must not automatically be considered equivalent.

For example, conceptually:

```text
Organization
    |
    +-- Service A
    |
    +-- Service B
```

The framework may later need to identify:

```text
Service
Brand
Organization
Legal Data Controller
```

as separate concepts.

The current Discovery Domain does not yet contain enough evidence to define this model.

Therefore:

```text
SERVICE != ORGANIZATION
```

remains an architectural boundary.

---

# 12. Entity Resolution

Entity Resolution is the process that attempts to map observed identifiers to canonical Services.

It is behavior rather than a core Domain Entity.

Conceptually:

```text
Observation
     |
     v
Service Identifier
     |
     v
Entity Resolver
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

## 12.1 Resolution Result

Although Entity Resolution itself is behavior, the result of resolution may need to be preserved.

A future value or record may contain concepts such as:

```text
ResolutionResult

- observed_identifier
- normalized_identifier
- resolved_service
- resolution_status
- resolution_method
- timestamp
```

Potential states may include:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

The exact representation is not yet defined.

---

## 12.2 Resolution Provenance

Entity Resolution must never destroy the original identifier.

Conceptually:

```text
Original Observation
        |
        v
Observed Identifier
        |
        v
Normalized Identifier
        |
        v
Resolved Service
```

All relevant stages should remain explainable and reprocessable.

---

# 13. Evidence

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

Evidence taxonomies may vary across sources and capabilities.

---

## 13.1 Example

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

Password-manager entry
URI: accounts.spotify.com
```

may produce:

```text
Evidence:

PASSWORD_MANAGER_ENTRY
```

---

## 13.2 Evidence Core

A conceptual Evidence representation may contain:

```text
Evidence

- id
- type
- supporting_observation
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

## 13.3 Evidence May Remain Unknown

Classification must never be forced.

For example:

```text
classification_status:
UNKNOWN
```

is valid.

The supporting Observation must remain available.

---

## 13.4 No Arbitrary Confidence

Draft v0.1 of the Domain Model does not assign arbitrary numerical confidence values to Evidence.

Values such as:

```text
confidence = 0.87
```

must not be introduced until:

- their semantics are defined;
- calibration is possible;
- representative data exists;
- the values provide actual user benefit.

---

# 14. Evidence Classification

Evidence Classification is behavior applied to Observations.

It is not currently modeled as a persistent Domain Entity.

Conceptually:

```text
Observation
     |
     v
Evidence Classifier
     |
     v
Evidence
```

Different sources may use different classification strategies.

For example:

```text
Gmail
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

# 15. Evidence Aggregation

Evidence Aggregation combines Evidence associated with the same discovery context.

It is a process rather than a core Domain Entity.

Conceptually:

```text
Evidence A
Evidence B
Evidence C
    |
    v
Evidence Aggregator
    |
    v
Relationship Context
```

Aggregation must not destroy individual Evidence.

For example:

```text
100 Evidence items
```

may contribute to:

```text
1 Relationship
```

while all 100 Evidence items remain independently traceable.

---

# 16. Relationship

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

## 16.1 Relationship Core

A conceptual representation may contain:

```text
Relationship

- id
- identity_reference
- service_reference
- state
- first_observed
- last_observed
```

The final representation remains undefined.

---

## 16.2 Relationship State

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

## 16.3 Relationship Is Not Current Data Possession

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

# 17. Evidence Supporting Relationships

A Relationship may be supported by multiple Evidence items.

Conceptually:

```text
               Relationship
              /      |      \
             /       |       \
            v        v        v
        Evidence  Evidence  Evidence
```

Evidence may also originate from multiple Discovery Sources.

Example:

```text
                    Spotify
                       |
                 Relationship
                  /         \
                 /           \
                v             v
        Gmail Evidence   Password Manager Evidence
```

This cross-source support is a core requirement of the framework.

---

# 18. Multi-Source Convergence

The same canonical Service may be discovered independently through multiple sources.

For example:

```text
Gmail
  |
  v
Observation
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
Observation
  ^
  |
Password Manager
```

The framework must preserve:

```text
independent source provenance
```

while allowing:

```text
canonical Service convergence
```

This means the framework should not create provider-specific copies such as:

```text
Spotify_Gmail
Spotify_PasswordManager
Spotify_Outlook
```

when evidence indicates that they represent the same Service.

---

# 19. Multiple Sources of the Same Type

The User may connect multiple Discovery Sources of the same type.

For example:

```text
EMAIL

+-- Gmail Account A
+-- Gmail Account B
+-- Outlook Account
+-- iCloud Mail Account
+-- Proton Mail Account
```

Each connected source may produce its own Observations.

Conceptually:

```text
Gmail A --------+
                |
Gmail B --------+
                |
Outlook --------+--> Observations
                |         |
iCloud Mail ----+         v
                |      Services
Proton Mail ----+
```

The same principle applies to password managers or other future source categories.

Source multiplicity is therefore a first-class architectural requirement.

---

# 20. Candidate Concept: ConnectedSource

The need to connect multiple concrete instances suggests a possible domain concept:

```text
ConnectedSource
```

A ConnectedSource would represent:

> A specific external source instance authorized by the User.

Example:

```text
type:
EMAIL

provider:
GMAIL

account:
user@gmail.com
```

Another instance could be:

```text
type:
EMAIL

provider:
GMAIL

account:
oldaddress@gmail.com
```

Both use the same provider but represent different source instances.

Potential conceptual relationships are:

```text
User
 |
 +-- ConnectedSource
 |       |
 |       +-- provider: Gmail
 |       +-- identity: user@gmail.com
 |
 +-- ConnectedSource
         |
         +-- provider: Outlook
         +-- identity: user@outlook.com
```

However, this concept is not promoted to the core Domain Model yet.

It should be evaluated during Connector and authorization design because its lifecycle is strongly connected with:

```text
authorization
permissions
synchronization
revocation
```

---

# 21. Candidate Concept: Account

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

## 21.1 Why Account May Be Useful

An Account could allow the framework to represent:

- multiple accounts with the same Service;
- historical accounts;
- multiple identities used with one Service;
- shared accounts;
- migrated accounts.

---

## 21.2 Why Account Is Not Yet Included

Not every Service Relationship exposes an identifiable Account.

For example:

```text
Marketing Evidence
Browser Activity
Guest Purchase
Privacy Notice
```

may support a Service Relationship without revealing a distinct Account.

Therefore, additional scenarios are required before determining whether Account should become:

```text
a core entity
```

or:

```text
an optional relationship detail
```

For now:

```text
Account = CANDIDATE DOMAIN CONCEPT
```

---

# 22. Domain Processes

The following concepts currently represent behavior rather than persistent domain entities.

---

## 22.1 Connector

```text
Discovery Source
       |
       v
Connector
       |
       v
Observation
```

Responsibilities include authorized retrieval, minimization and source translation.

---

## 22.2 ServiceCandidateDetector

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

## 22.3 EntityResolver

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

## 22.4 EvidenceClassifier

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

## 22.5 EvidenceAggregator

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

## 22.6 RelationshipAssessor

```text
Aggregated Evidence
        |
        v
RelationshipAssessor
        |
        v
Relationship
```

Evaluates what accumulated Evidence suggests about the User-Service Relationship.

---

# 23. Domain Entities vs Processes

| Concept | Current Classification |
|---|---|
| User | Domain Entity |
| IdentitySeed | Domain Entity |
| DiscoverySource | Domain Concept / Configuration |
| Observation | Domain Entity |
| ServiceIdentifier | Domain Entity / Value Concept |
| Service | Domain Entity |
| Evidence | Domain Entity |
| Relationship | Domain Entity |
| Connector | Process / Integration Boundary |
| ServiceCandidateDetector | Domain Process |
| EntityResolver | Domain Process |
| EvidenceClassifier | Domain Process |
| EvidenceAggregator | Domain Process |
| RelationshipAssessor | Domain Process |
| ResolutionResult | Candidate Value Concept |
| ConnectedSource | Candidate Domain Concept |
| Account | Candidate Domain Concept |

These classifications are provisional.

They should be revised if implementation or additional scenarios expose contradictions.

---

# 24. Conceptual Multi-Source Model

The target Discovery Domain should support a topology similar to:

```text
                              USER
                                |
                +---------------+---------------+
                |                               |
                v                               v
          Identity Seed                   Identity Seed


     EMAIL SOURCES                    PASSWORD MANAGERS
           |                                |
   +-------+-------+                +-------+-------+
   |       |       |                |               |
   v       v       v                v               v
 Gmail  Outlook  Other          Provider A       Provider B
   |       |       |                |               |
   v       v       v                v               v
Connector Connector Connector     Connector       Connector
   |       |       |                |               |
   +-------+-------+----------------+---------------+
                    |
                    v
                OBSERVATIONS
                    |
        +-----------+-----------+
        |                       |
        v                       v
Service Identifiers       Evidence Classification
        |                       |
        v                       v
 Entity Resolution             Evidence
        |                       |
        v                       |
      SERVICE <-----------------+
        |
        v
  RELATIONSHIP
        |
        v
   SERVICE GRAPH
```

Future source types should be able to join this architecture without changing the common Discovery Domain.

---

# 25. Domain Invariants

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

An Observation must retain information identifying its Discovery Source.

---

### INV-004

An unresolved Observation must not require creation of a fabricated Service.

---

### INV-005

Classification failure must be representable as `UNKNOWN`.

---

### INV-006

A Relationship must not be interpreted as proof of current personal-data possession.

---

### INV-007

Multiple Observations may support one Service.

---

### INV-008

Multiple Discovery Sources may support one Service.

---

### INV-009

Multiple connected instances of the same source type must be supported.

---

### INV-010

Source-specific secrets unnecessary for Service Discovery must not become normal Discovery Observations.

---

### INV-011

Derived information must not destructively replace its source provenance.

---

### INV-012

AI availability must not be required for deterministic Discovery operations.

---

# 26. Lifecycle Considerations

Domain concepts have different lifecycles.

For example:

```text
Connected Source
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

Disconnecting a source does not necessarily imply deletion of every downstream concept.

Potential operations include:

```text
Disconnect Source
Revoke Authorization
Delete Credentials
Delete Cached Source Data
Delete Observations
Delete Evidence
Recalculate Relationships
```

These operations must remain conceptually distinguishable.

The exact lifecycle policy will be defined later by the Privacy and Security Architecture.

---

# 27. Reprocessing

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
      +--> Resolver v1
      |
      +--> Resolver v2
```

This allows the framework to improve classification and resolution without necessarily retrieving raw source information again.

The exact persistence required to enable this remains an open question.

---

# 28. User Correction

Future versions should allow the User to correct derived conclusions.

Examples include:

```text
"This identifier does not belong to Spotify."

"These two Services are the same."

"These two Services are different."

"This account does not belong to me."

"This was only a guest purchase."

"This Relationship is historical."
```

User correction should not silently destroy historical provenance.

Instead, corrections should themselves remain attributable to the User.

---

# 29. Deliberately Undefined

Draft v0.1 intentionally does not define:

```text
Database technology
Database schema
Python classes
Repository structure for code
REST API
Graph database
Service Graph implementation
Final Evidence taxonomy
Final Relationship states
Confidence algorithm
AI provider
Entity Resolution algorithm
Persistence strategy
ConnectedSource representation
Account representation
Organization model
Legal Data Controller model
```

These decisions should follow Domain validation rather than precede it.

---

# 30. Open Questions

## Identity

- Can new Identity Seeds be proposed from authorized Observations?
- Must the User explicitly confirm all newly discovered identities?
- How should historical identities be represented?
- How should aliases be represented?

## Discovery Sources

- Does `DiscoverySource` represent a source category, a provider, or both?
- Should `ConnectedSource` become a first-class Domain Entity?
- How should multiple connections to the same provider be represented?
- What state belongs to a connected source?

## Observation

- What is the minimal common Observation representation?
- How should source-specific attributes be stored?
- Which Observations should be persisted?
- Which information can safely be discarded after classification?
- How should source-specific temporal semantics be represented?

## Service Identifier

- Which identifier types are required?
- Can one identifier resolve to multiple Services in different contexts?
- How should historical identifiers be represented?
- How should third-party infrastructure identifiers be handled?

## Service

- When are two Services considered the same?
- How are rebranding and acquisitions represented?
- Should Service and Brand be separate?
- Should Service and Organization be separate?
- How should legal data controllers eventually relate to Services?

## Evidence

- Which Evidence Types should be common across sources?
- Which should remain source-specific?
- Can one Observation generate multiple Evidence items?
- Can multiple Observations generate one Evidence item?

## Relationship

- Is a Relationship between User and Service or Identity and Service?
- Can multiple Identity Seeds participate in one Relationship?
- How should historical Relationships be represented?
- How should conflicting Evidence affect a Relationship?

## ConnectedSource

- Should authorization state belong to `ConnectedSource`?
- Should synchronization state belong to it?
- Can one ConnectedSource be associated with multiple Identity Seeds?
- How should revocation affect its downstream Observations?

## Account

- Should Account become a first-class Domain Entity?
- Can a Relationship exist without an Account?
- Can multiple Accounts belong to the same Service?
- Can one Account use multiple Identity Seeds?
- How should shared Accounts be represented?

## Privacy

- What data should be removed at the Connector boundary?
- Which source attributes can be persisted?
- How long should Observations and Evidence remain locally stored?
- How should deletion propagate through derived information?

---

# 31. Validation Status

Draft v0.1 has been derived from two structurally different discovery scenarios.

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

No current scenario demonstrates that Account must yet become part of the core Domain Model.

---

# 32. Current Domain Model

The current baseline is:

```text
CORE DOMAIN

User
 |
 +-- IdentitySeed

DiscoverySource
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

ConnectedSource
Account
ResolutionResult
```

---

# 33. Next Design Step

The next step is to translate the validated Domain Model into implementation-oriented contracts without yet committing to a complete application implementation.

The first software interfaces should describe the behavior of:

```text
Connector
ServiceCandidateDetector
EntityResolver
EvidenceClassifier
EvidenceAggregator
RelationshipAssessor
```

The interface design should answer:

```text
What does each component receive?

What does each component return?

Which domain concepts cross the boundary?

Which errors or unresolved states can occur?

Which operations require permissions?

Which components may access source-specific information?
```

Only after these contracts have been defined should the first executable vertical Discovery pipeline be implemented.
