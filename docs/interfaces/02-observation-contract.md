# Observation Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md` - Draft v0.3  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md` - Draft v0.3  
**Related Interface:** `docs/interfaces/01-connector-contract.md`  
**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for `Observation` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

An Observation is the primary source-derived Domain object produced by a Connector and consumed by the common Discovery Core.

Conceptually:

```text
External Source
      |
      v
   Connector
      |
      v
  Observation
      |
      v
Discovery Core
```

The Observation Contract must allow structurally different sources to participate in the same Discovery pipeline without exposing provider-specific API objects to downstream components.

Examples include:

```text
Gmail
Outlook
iCloud Mail
Proton Mail
Password Managers
Browsers
Identity Providers
Future Sources
```

The contract must therefore satisfy two competing requirements:

```text
Common enough
for the Discovery Core

        +

Flexible enough
for different source types
```

The architectural solution is:

```text
COMMON OBSERVATION ENVELOPE
            +
TYPED SOURCE-SPECIFIC PAYLOAD
```

The consolidated Domain Model classifies `Observation` as a Core Domain Entity.

---

## 2. Role of Observation

An Observation represents information obtained from exactly one ConnectedSource before the framework assigns final semantic meaning to it.

It answers:

> What information did the framework observe from this ConnectedSource?

It does not answer:

> What does this information mean for the User-Service Relationship?

That interpretation belongs to downstream components.

Therefore:

```text
CONNECTED SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

OBSERVATION != SERVICE

OBSERVATION != RELATIONSHIP
```

For example:

```text
Observation:

sender:
no-reply@spotify.com

subject:
Verify your email address
```

may later contribute to:

```text
Evidence:

ACCOUNT_VERIFICATION
```

But the Observation itself remains the source-derived information.

---

## 3. Architectural Position

The Observation boundary sits between provider-specific integration logic and common Discovery processing.

```text
PROVIDER-SPECIFIC WORLD

Gmail API Object
Password Manager Record
Browser History Entry
Identity Provider Record

            |
            v

         CONNECTOR

==============================
      OBSERVATION CONTRACT
==============================

            |
            v

COMMON DISCOVERY WORLD

              Observation
               /       \
              /         \
             v           v
Service Candidate     Evidence
Detection             Classification
       |
       v
CandidateIdentifier
       |
       v
Entity Resolution
```

Entity Resolution and Evidence Classification are independent downstream branches.

Provider-specific objects should not normally cross the Observation boundary.

---

## 4. Design Goals

The Observation Contract should provide:

- a stable common envelope;
- explicit ConnectedSource provenance;
- typed source-specific payloads;
- source-reference support;
- temporal semantics;
- schema versioning;
- data minimization;
- deterministic identity where practical;
- reprocessing support;
- extensibility for future source types.

The Observation Contract should avoid:

- provider-specific API objects;
- authentication credentials;
- unnecessary secrets;
- Evidence conclusions;
- canonical Service conclusions;
- Relationship conclusions;
- provider-specific pagination state;
- collection-completeness state.

---

## 5. Common Envelope and Typed Payload

Different source types expose fundamentally different information.

For example, email may contain:

```text
sender
recipient
subject
message timestamp
thread
```

while a password manager may contain:

```text
title
username
URI
record timestamp
```

A browser may later contain:

```text
URL
page title
visit timestamp
```

Attempting to represent every source using one flat structure would lead to an object such as:

```text
Observation

sender?
recipient?
subject?
uri?
username?
page_title?
browser_profile?
message_id?
password_manager_title?
...
```

This does not scale.

Instead, the contract uses:

```text
Observation
 |
 +-- Common Envelope
 |
 +-- Typed Payload
```

Conceptually:

```json
{
  "id": "...",
  "connected_source_id": "...",
  "observation_type": "...",
  "schema_version": "...",
  "source_reference": "...",
  "temporal": {},
  "payload": {}
}
```

The envelope remains common.

The payload depends on:

```text
observation_type
+
schema_version
```

---

## 6. Conceptual Observation Contract

The initial conceptual representation is:

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

This structure is conceptual.

It is not yet:

- a Python class;
- a database schema;
- an API schema;
- a JSON Schema;
- a persistence format.

The Domain Model owns the semantic definition of Observation.

This contract defines how software components exchange, validate and process Observations.

---

## 7. `id`

Every Observation must have an internal framework identifier.

Conceptually:

```text
id:
observation_001
```

The identifier distinguishes the framework Observation from the Provider's source identifier.

Therefore:

```text
OBSERVATION ID
      !=
SOURCE REFERENCE
```

The exact identifier format is not yet defined.

Possible future implementations may use:

- UUIDs;
- ULIDs;
- deterministic identifiers;
- persistence-generated identifiers.

That decision should be made during implementation design.

---

## 8. `connected_source_id`

Every Observation must reference exactly one ConnectedSource from which it originated.

Example:

```text
connected_source_id:
source_001
```

This is mandatory provenance and a Domain invariant.

Conceptually:

```text
ConnectedSource
       |
       +-- Observation A
       |
       +-- Observation B
       |
       +-- Observation C
```

This allows identical source information collected through different Connected Sources to remain distinguishable.

For example:

```text
spotify.com
```

may be observed through:

```text
Personal Gmail
Work Outlook
Primary Password Manager
Browser Profile
```

Each Observation retains its own source provenance.

Therefore:

```text
CONTENT EQUALITY
      !=
OBSERVATION IDENTITY
```

and:

```text
Observation
      |
      v
exactly one ConnectedSource
```

---

## 9. `observation_type`

Every Observation must declare its semantic source structure.

Examples may include:

```text
EMAIL_MESSAGE_METADATA
PASSWORD_MANAGER_ENTRY_METADATA
BROWSER_VISIT
IDENTITY_PROVIDER_RELATIONSHIP
MANUAL_RELATIONSHIP_DECLARATION
```

These values describe:

> What kind of source-derived object is represented?

They do not describe:

> What Evidence does it provide?

For example:

```text
EMAIL_MESSAGE_METADATA
```

is an Observation Type.

```text
ACCOUNT_VERIFICATION
```

is an Evidence Type.

Therefore:

```text
OBSERVATION TYPE != EVIDENCE TYPE
```

---

## 10. Why Observation Type Is Required

SourceType alone is insufficient.

For example, one future email Connector may produce:

```text
EMAIL_MESSAGE_METADATA
```

and, under a separately authorized capability:

```text
EMAIL_MESSAGE_CONTENT
```

A browser Connector may eventually produce:

```text
BROWSER_VISIT
BOOKMARK
SITE_PERMISSION
```

Therefore the Observation should identify the structure it carries independently from the broader ConnectedSource SourceType.

Conceptually:

```text
ConnectedSource

SourceType:
EMAIL

        |
        +-- EMAIL_MESSAGE_METADATA
        |
        +-- EMAIL_MESSAGE_CONTENT
```

The exact Observation Type vocabulary remains open.

---

## 11. `schema_version`

Every Observation payload must be associated with a schema version.

Conceptually:

```text
observation_type:
EMAIL_MESSAGE_METADATA

schema_version:
1
```

This permits the shape of an Observation to evolve without silently changing historical semantics.

For example:

```text
EMAIL_MESSAGE_METADATA v1
```

might contain:

```text
sender
recipient
subject
message_date
```

while:

```text
EMAIL_MESSAGE_METADATA v2
```

might later introduce a new optional normalized field.

Downstream components should therefore reason about:

```text
observation_type
+
schema_version
```

rather than assuming that all Observations of a given type always have an identical historical representation.

---

## 12. `source_reference`

An Observation should preserve a stable Provider-side or Connector-side reference where technically possible and safe.

Examples may include:

```text
Gmail message ID
Outlook message reference
Password-manager item ID
Browser history record reference
```

Conceptually:

```text
source_reference:
provider-record-123
```

This may support:

- deduplication;
- synchronization;
- change detection;
- reprocessing;
- debugging;
- source traceability.

A source reference must not contain unnecessary secret information.

---

## 13. Source Reference Characteristics

A source reference should ideally be:

```text
stable
opaque
non-secret
unique within the ConnectedSource
```

when the Provider permits this.

Uniqueness should not automatically be assumed globally.

The safe conceptual identity is:

```text
ConnectedSource ID
        +
Source Reference
```

rather than:

```text
Source Reference
```

alone.

For example:

```text
(source_001, message_123)
```

and:

```text
(source_002, message_123)
```

may represent completely unrelated source records.

---

## 14. `observed_at`

`observed_at` represents the time associated with the observed source event when that meaning is available.

Example:

```text
Email received:
2025-04-05T10:30:00Z
```

may produce:

```text
observed_at:
2025-04-05T10:30:00Z
```

However, not every source provides a timestamp that represents an actual Service interaction.

Therefore `observed_at` must be interpreted together with temporal semantics.

---

## 15. `collected_at`

`collected_at` represents when the framework collected or materialized the Observation.

Example:

```text
Email message date:
2025-04-05

Framework collection:
2026-11-13
```

Conceptually:

```text
observed_at:
2025-04-05T10:30:00Z

collected_at:
2026-11-13T14:00:00Z
```

These values represent different events and must not be conflated.

---

## 16. `temporal_semantics`

A timestamp must retain information about what it means.

For example:

```text
EMAIL_MESSAGE_DATE
```

is semantically different from:

```text
PASSWORD_MANAGER_RECORD_MODIFIED
```

even if both contain the same timestamp.

Conceptually:

```text
observed_at:
2024-02-01T12:00:00Z

temporal_semantics:
SOURCE_RECORD_MODIFIED
```

Downstream processing must not automatically reinterpret this as:

```text
LAST_SERVICE_ACTIVITY
```

unless the source semantics justify that interpretation.

---

## 17. Temporal Model

The initial conceptual model is:

```text
TemporalInformation

- observed_at
- collected_at
- temporal_semantics
```

Potential semantic categories may eventually include:

```text
SOURCE_EVENT_TIME
SOURCE_RECORD_CREATED
SOURCE_RECORD_MODIFIED
MESSAGE_TIME
VISIT_TIME
USER_DECLARED_TIME
UNKNOWN
```

The final vocabulary remains undefined.

The consolidated Domain Model also permits the future introduction of multiple typed `TemporalValue` values when one Observation exposes several independently meaningful timestamps.

---

## 18. `payload`

`payload` contains the source-type-specific information required by downstream Discovery components.

The payload must conform to:

```text
observation_type
+
schema_version
```

For example:

```text
Observation
 |
 +-- observation_type:
 |      EMAIL_MESSAGE_METADATA
 |
 +-- schema_version:
 |      1
 |
 +-- payload:
        EmailMessageMetadataV1
```

The payload must not be interpreted as an arbitrary dump of the Provider object.

---

## 19. Payload Is Not Raw Provider Data

The intended flow is:

```text
Provider Object
      |
      v
Connector
      |
      v
Select / Normalize / Minimize
      |
      v
Typed Observation Payload
```

not:

```text
Provider Object
      |
      v
serialize everything
      |
      v
payload
```

The Connector must expose only information required by the corresponding framework capability where reasonably possible.

This behavior is now formally aligned with Architecture Decision:

```text
D-018 - Connector Is a Data-Minimization Boundary
```

---

## 20. Email Metadata Payload

A conceptual `EMAIL_MESSAGE_METADATA` payload may contain information such as:

```text
EmailMessageMetadata

- sender
- recipients
- subject
- message_reference
- thread_reference
- labels
```

The exact fields depend on what is justified by the Discovery capability and available through the Provider.

Provider-specific structures should be normalized where reasonable.

For example:

```text
Gmail API message object
```

must not become the Observation payload directly.

---

## 21. Example: Gmail Metadata Observation

Conceptually:

```json
{
  "id": "observation_001",
  "connected_source_id": "source_gmail_personal",
  "observation_type": "EMAIL_MESSAGE_METADATA",
  "schema_version": 1,
  "source_reference": "provider-message-123",
  "observed_at": "2025-04-05T10:30:00Z",
  "collected_at": "2026-11-13T14:00:00Z",
  "temporal_semantics": "MESSAGE_TIME",
  "payload": {
    "sender": "no-reply@spotify.com",
    "recipients": [
      "user@example.com"
    ],
    "subject": "Verify your email address",
    "thread_reference": "provider-thread-456"
  }
}
```

This is illustrative.

It does not define the final JSON representation.

---

## 22. Password Manager Payload

A conceptual `PASSWORD_MANAGER_ENTRY_METADATA` payload may contain:

```text
PasswordManagerEntryMetadata

- title
- username_reference
- uris
- record_created_at
- record_modified_at
```

It must not normally contain:

```text
password
OTP seed
recovery codes
private keys
secret tokens
```

for Service Discovery.

---

## 23. Example: Password Manager Observation

Conceptually:

```json
{
  "id": "observation_002",
  "connected_source_id": "source_password_manager_primary",
  "observation_type": "PASSWORD_MANAGER_ENTRY_METADATA",
  "schema_version": 1,
  "source_reference": "provider-item-789",
  "observed_at": "2024-06-01T08:00:00Z",
  "collected_at": "2026-11-13T14:03:00Z",
  "temporal_semantics": "SOURCE_RECORD_MODIFIED",
  "payload": {
    "title": "Spotify",
    "username_reference": "user@example.com",
    "uris": [
      "https://accounts.spotify.com"
    ]
  }
}
```

The timestamp must not automatically imply that Spotify was used on `2024-06-01`.

It describes the semantics declared by `temporal_semantics`.

---

## 24. Browser Example

A future browser Connector might produce:

```text
observation_type:
BROWSER_VISIT
```

with a payload conceptually equivalent to:

```text
BrowserVisit

- url
- page_title
- visit_time
```

Example:

```json
{
  "id": "observation_003",
  "connected_source_id": "source_browser_primary",
  "observation_type": "BROWSER_VISIT",
  "schema_version": 1,
  "source_reference": "history-entry-123",
  "observed_at": "2026-11-10T17:30:00Z",
  "collected_at": "2026-11-13T14:10:00Z",
  "temporal_semantics": "VISIT_TIME",
  "payload": {
    "url": "https://open.spotify.com",
    "page_title": "Spotify"
  }
}
```

This example validates the extensibility of the envelope.

It does not imply that Browser Discovery is currently implemented.

---

## 25. Provider Independence

Different Providers of the same SourceType should produce the same framework ObservationType when their semantics are equivalent.

For example:

```text
GmailConnector
      |
      v
EMAIL_MESSAGE_METADATA
```

and:

```text
OutlookConnector
      |
      v
EMAIL_MESSAGE_METADATA
```

and potentially:

```text
ProtonMailConnector
      |
      v
EMAIL_MESSAGE_METADATA
```

The downstream Evidence Classifier should therefore not need:

```text
if provider == Gmail:
    ...

elif provider == Outlook:
    ...
```

for normal email-semantic interpretation.

Provider-specific differences should remain inside Connectors wherever possible.

This principle is now formalized by:

```text
D-019 - Observation Types Are Provider-Neutral Where Possible
```

---

## 26. Provider-Specific Information

Some Provider-specific information may still be necessary.

If so, the contract should not force it into the common payload unless it has meaningful cross-provider semantics.

Provider-specific metadata may eventually be placed in a controlled extension area.

Conceptually:

```text
payload:
    common typed payload

extensions:
    provider-specific non-secret metadata
```

However, an `extensions` mechanism is not part of the required Draft v0.1 contract yet.

It should be introduced only if concrete Provider integrations demonstrate the need.

---

## 27. Provenance

Observation provenance has multiple layers.

Conceptually:

```text
User
 |
 v
ConnectedSource
 |
 v
Connector
 |
 v
Source Reference
 |
 v
Observation
```

The minimum required provenance is:

```text
Observation
        |
        +-- connected_source_id
        |
        +-- source_reference
        |
        +-- collected_at
```

Additional provenance may eventually include:

```text
connector version
collection run
payload schema version
normalization version
```

These are not yet mandatory.

The consolidated Domain Model requires every Observation to reference exactly one ConnectedSource.

Therefore:

```text
Observation
      |
      v
exactly one ConnectedSource
```

is a Domain invariant rather than an optional implementation detail.

`ConnectedSource` is the authoritative source-instance boundary for Observation provenance.

Provider, Connector and User Identity information must not replace this reference.

---

## 28. Connector Version Provenance

A Connector may evolve over time.

For example:

```text
GmailConnector v1
```

may normalize source data differently from:

```text
GmailConnector v2
```

The framework may eventually need to record which Connector implementation produced an Observation.

Conceptually:

```text
producer:

connector_id
connector_version
```

Draft v0.1 does not require this in the minimum Observation envelope, but the need should be evaluated before persistent implementation.

---

## 29. Collection Run Provenance

A future `CollectionRun` concept may identify the collection operation that produced a set of Observations.

Conceptually:

```text
CollectionRun
      |
      +-- Observation A
      +-- Observation B
      +-- Observation C
```

This may help represent:

- partial collection;
- retries;
- synchronization history;
- Connector errors;
- measurement;
- debugging;
- coverage.

`CollectionRun` is not a Core Domain Entity.

The consolidated Domain Model currently classifies it as:

```text
Application-Level Candidate
```

Its necessity should be evaluated during implementation of synchronization and coverage tracking.

---

## 30. Collection Completeness

Collection completeness must not be encoded inside individual Observations.

For example:

```text
Observation.complete = false
```

would be misleading because partiality normally describes the collection operation rather than an individual source record.

Instead:

```text
CollectionResult
      |
      +-- status: PARTIAL
      |
      +-- Observation A
      +-- Observation B
```

is the preferred model.

Therefore:

```text
OBSERVATION STATUS
      !=
COLLECTION STATUS
```

---

## 31. Observation Validity

An Observation asserts only that:

> The Connector observed the represented source information.

It does not assert that the information is true.

For example:

```text
sender:
security@fake-example.com
```

may originate from phishing.

The Observation remains valid as an Observation if that sender value was actually observed.

Its semantic interpretation may later be:

```text
misleading
malicious
irrelevant
unknown
```

Therefore:

```text
OBSERVED VALUE
      !=
TRUSTED FACT
```

This distinction is critical.

---

## 32. Observation Immutability

Observations should be treated as immutable source-derived records where practical.

If source information changes, the preferred model is not to silently rewrite history without traceability.

Possible models include:

```text
Observation v1
      |
      v
Observation v2
```

or:

```text
Observation
      |
      +-- revised source snapshot
```

The exact versioning strategy remains undefined.

The important invariant is:

> Reprocessing must not silently alter what was originally observed.

---

## 33. Reprocessing

An Observation should remain usable by later versions of downstream logic where compatible.

For example:

```text
Observation
    |
    +--> EvidenceClassifier v1
    |           |
    |           v
    |       Evidence A
    |
    +--> EvidenceClassifier v2
                |
                v
            Evidence B
```

The Observation must not need to be rewritten merely because its interpretation changes.

Evidence lifecycle is now represented separately through:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

Similarly, preserved identifiers derived from the Observation may be processed by later Entity Resolver versions.

```text
ServiceIdentifier
      |
      +--> EntityResolver v1
      |
      +--> EntityResolver v2
```

The Observation remains the preserved source-derived entity.

---

## 34. Sensitive Data

Observations may contain personal information.

Examples include:

```text
email addresses
usernames
URLs
message subjects
account references
service identifiers
timestamps
```

The fact that information is not a password does not mean that it is non-sensitive.

Observations must therefore be subject to:

- data minimization;
- local-first processing;
- retention controls;
- access controls;
- secure persistence where persistence is required.

---

## 35. Secrets

Authentication secrets unnecessary for Discovery must not become normal Observation attributes.

Examples include:

```text
passwords
OAuth access tokens
OAuth refresh tokens
OTP seeds
recovery codes
API secrets
private keys
session secrets
```

Therefore:

```text
AUTHENTICATION SECRET
        !=
DISCOVERY OBSERVATION ATTRIBUTE
```

unless a future capability explicitly requires such information and defines an appropriate isolated security boundary.

Service Discovery does not currently justify such access.

This principle is reinforced by Architecture Decision D-018.

---

## 36. Message Content

Message bodies represent a more sensitive information level than message metadata.

If a future email capability produces message-content Observations, these should not simply expand `EMAIL_MESSAGE_METADATA` until it contains everything.

A cleaner model may be:

```text
EMAIL_MESSAGE_METADATA
```

and separately:

```text
EMAIL_MESSAGE_CONTENT
```

with distinct:

- permissions;
- sensitivity;
- retention;
- processing requirements.

This supports Progressive Permission.

---

## 37. Attachments

Attachments should also remain distinct from basic metadata Observations.

Conceptually:

```text
EMAIL_MESSAGE_METADATA
        |
        +-- may reference
               |
               v
        ATTACHMENT_METADATA
```

and, only when authorized and required:

```text
ATTACHMENT_CONTENT
```

The final model remains open.

Scenario 001 does not require attachment content for Service Discovery.

---

## 38. Identity References inside Observations

An Observation may contain an identifier that appears to correspond to an Identity Seed.

For example:

```text
recipient:
personal@example.com
```

or:

```text
password manager username:
personal@example.com
```

A Connector should not automatically convert every observed identifier into a verified `IdentitySeed`.

Instead, the payload may preserve the observed value.

A downstream identity-association process may determine whether:

```text
observed identifier
        |
        v
known IdentitySeed
```

can safely be established.

Therefore:

```text
OBSERVED IDENTITY REFERENCE
           !=
VERIFIED IDENTITY SEED
```

The consolidated Domain Model preserves Identity references in Evidence, Aggregates and Relationships without automatically creating Identity-Service Relationships.

---

## 39. Service Identifiers inside Observations

Observations may expose potential Service identifiers.

For example:

```text
sender:
no-reply@spotify.com
```

may yield:

```text
spotify.com
```

while:

```text
URI:
https://accounts.spotify.com/login
```

may yield:

```text
accounts.spotify.com
```

The consolidated processing path is:

```text
Observation
     |
     v
ServiceCandidateDetector
     |
     v
CandidateIdentifier
     |
     v
ServiceIdentifier
     |
     v
EntityResolver
     |
     v
Service
```

`CandidateIdentifier` is the processing representation.

`ServiceIdentifier` is the Domain Value Concept used when identifier provenance or resolution history is retained.

The Connector may perform source-format normalization where necessary, but canonical Service Resolution belongs downstream.

No separate `ServiceIdentifierExtractor` is required by the current architecture.

---

## 40. Normalization Boundary

Some normalization belongs naturally inside the Connector.

For example:

```text
Provider-specific sender representation
        |
        v
standard email address representation
```

may be Connector responsibility.

By contrast:

```text
accounts.spotify.com
        |
        v
Spotify
```

belongs to Entity Resolution.

A useful rule is:

> Connectors normalize representation. Domain processes interpret meaning.

Conceptually:

```text
PROVIDER FORMAT
      |
      v
Connector normalization
      |
      v
COMMON REPRESENTATION
      |
      v
Domain interpretation
```

---

## 41. Deduplication

Repeated collection must not necessarily produce unrelated duplicate Observations.

When a stable source reference exists, the tuple:

```text
connected_source_id
+
source_reference
```

may provide a strong deduplication key.

Example:

```text
source_gmail_personal
+
message_123
```

Repeatedly collecting the same source record should not automatically create multiple unrelated Observations.

However, duplicate semantics become more complex when:

- source references change;
- Providers duplicate data;
- imports create copies;
- Provider-side records change;
- the source exposes snapshots rather than stable records.

The exact deduplication algorithm remains outside Draft v0.1.

---

## 42. Observation Identity vs Content Equality

Two Observations containing identical information are not necessarily the same Observation.

For example:

```text
Personal Gmail:
subject = "Verify your email"
```

and:

```text
Work Outlook:
subject = "Verify your email"
```

may contain identical values but originate from different Connected Sources.

Therefore:

```text
CONTENT EQUALITY
     !=
OBSERVATION IDENTITY
```

ConnectedSource provenance participates in Observation identity.

---

## 43. Null and Missing Information

The contract must distinguish, where necessary, between:

```text
field unavailable

field unsupported

field not collected because of permission

field absent in source

field intentionally omitted for minimization
```

Collapsing all of these into:

```text
null
```

may lose important semantics.

The exact representation remains open.

Potential future strategies may include:

```text
explicit field status
typed optional values
payload metadata
```

This should be decided during concrete schema design.

---

## 44. Unknown Is Valid

Observation processing must preserve the framework principle:

```text
UNKNOWN IS VALID
```

A Connector should not fabricate missing information merely to satisfy an Observation schema.

For example, if a subject is unavailable, the implementation should represent that absence appropriately rather than generate a guessed subject.

Similarly, `observed_at` may be unavailable if the source provides no meaningful temporal information.

The schema should therefore avoid making semantically unavailable fields artificially mandatory.

---

## 45. Payload Validation

Every Observation must be validated against the structure defined by:

```text
observation_type
+
schema_version
```

Conceptually:

```text
Observation
 |
 +-- EMAIL_MESSAGE_METADATA
     |
     +-- schema_version: 1
     |
     +-- validate against
         EmailMessageMetadataV1
```

Invalid Provider data must not silently become valid framework Observations.

Possible outcomes may include:

```text
VALID
INVALID_SOURCE_DATA
UNSUPPORTED_SCHEMA
CONNECTOR_ERROR
```

These outcomes belong primarily to Connector collection and validation rather than Evidence Classification.

---

## 46. Observation Schema Registry

The framework may eventually require a registry such as:

```text
Observation Type
        |
        +-- EMAIL_MESSAGE_METADATA
        |      |
        |      +-- v1
        |      +-- v2
        |
        +-- PASSWORD_MANAGER_ENTRY_METADATA
        |      |
        |      +-- v1
        |
        +-- BROWSER_VISIT
               |
               +-- v1
```

This registry would allow:

- validation;
- schema evolution;
- compatible Connector development;
- downstream contract negotiation.

The implementation mechanism is not yet defined.

---

## 47. Extensibility

A new Connector should be able to introduce support for new source structures without modifying the semantics of existing Observation Types.

For example:

```text
Future Financial Source
      |
      v
FINANCIAL_TRANSACTION_METADATA
```

could be introduced without changing:

```text
EMAIL_MESSAGE_METADATA
```

or:

```text
PASSWORD_MANAGER_ENTRY_METADATA
```

The common Observation envelope should remain stable as the payload vocabulary grows.

---

## 48. Backward Compatibility

Schema evolution should aim to avoid breaking existing persisted Observations.

Possible strategies include:

```text
read old schemas forever
```

or:

```text
explicit migration
```

or:

```text
runtime adaptation into a canonical view
```

The implementation strategy remains undefined.

The contract requirement is:

> Historical Observation semantics must not change silently when a schema evolves.

---

## 49. Provider-Specific Evolution

Provider APIs may change independently from Observation schemas.

For example:

```text
Gmail API representation vA
        |
        v
GmailConnector
        |
        v
EMAIL_MESSAGE_METADATA v1
```

may later become:

```text
Gmail API representation vB
        |
        v
Updated GmailConnector
        |
        v
EMAIL_MESSAGE_METADATA v1
```

if the common Observation semantics remain unchanged.

This demonstrates why Provider API version and Observation schema version are separate concerns.

---

## 50. Error Boundary

An Observation represents successfully materialized source-derived information.

Provider retrieval errors must not be encoded as fake Observations.

For example:

```text
Observation:
{
  "type": "GMAIL_ERROR"
}
```

should not be the normal error model.

Instead:

```text
Connector
   |
   +-- CollectionResult
          |
          +-- observations
          |
          +-- errors
```

keeps integration errors outside the Observation Domain.

Therefore:

```text
CONNECTOR ERROR != OBSERVATION
```

---

## 51. Partial Source Objects

A Provider may return incomplete but still usable source information.

A Connector may produce an Observation if the payload contract can still be satisfied without fabrication.

For example:

```text
sender:
available

subject:
unavailable
```

may remain a valid email metadata Observation if `subject` is optional.

The payload schema should define:

```text
required fields
optional fields
```

according to semantic necessity rather than Provider convenience.

---

## 52. Manual Observations

Manual User input should ultimately be capable of entering the same Discovery Domain.

For example:

```text
User:
"I had a Spotify account in 2018."
```

could eventually become:

```text
observation_type:
MANUAL_RELATIONSHIP_DECLARATION
```

with provenance showing that the source was the User rather than an external Provider.

Manual Observations must remain distinguishable from automatically collected source data.

This preserves explainability.

The exact representation of manual input as a ConnectedSource remains open in the Domain Model.

---

## 53. Observation Sensitivity

Not all Observations have the same sensitivity.

For example:

```text
public website hostname
```

and:

```text
email subject
```

may expose very different information.

A future contract may require a sensitivity classification such as:

```text
PUBLIC_LIKE
IDENTIFIER
METADATA
CONTENT
HIGHLY_SENSITIVE
SECRET
```

However, Draft v0.1 does not introduce a final sensitivity taxonomy.

Sensitivity may belong partly to:

- ObservationType;
- payload field;
- Capability;
- policy.

This requires further Privacy and Security Architecture work.

---

## 54. Storage

The Observation Contract does not require that every Observation be persisted permanently.

Potential strategies include:

```text
persist all minimized Observations

persist only selected Observations

process and discard

persist derived Evidence only
```

The choice must balance:

```text
Data Minimization
        vs
Explainability
        vs
Reprocessing
```

The final persistence strategy remains deliberately undefined.

Observation being a Core Domain Entity does not imply that every Observation must be stored permanently.

---

## 55. Retention

Observation retention cannot be decided independently from:

- source sensitivity;
- reprocessing requirements;
- User expectations;
- deletion semantics;
- storage architecture;
- legal or policy constraints.

The Observation Contract therefore defines representation, not retention duration.

---

## 56. Deletion

Deleting an Observation may affect:

```text
Evidence
EvidenceAggregate
Relationship
Service Graph
```

Therefore Observation deletion should not occur as an isolated persistence operation without considering derived state.

Conceptually:

```text
Delete Observation
        |
        v
Identify Dependent Evidence
        |
        v
Delete or Reject Evidence
        |
        v
Rebuild EvidenceAggregate
        |
        v
Reassess Relationship
```

If dependent Evidence is retained for provenance rather than deleted, its `EvidenceStatus` must prevent invalid Evidence from participating in current assessment.

The exact lifecycle mechanism remains outside this contract.

---

## 57. Observation Contract Summary

The minimum common Observation contract is:

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
```

with the following properties:

```text
Core Domain Entity

exactly one ConnectedSource

source traceable

typed

versioned

minimized

non-secret by default

Provider-independent envelope

source-semantic typed payload

reprocessable

not semantically interpreted yet
```

---

## 58. Conceptual Language-Independent Contract

The contract may be represented conceptually as:

```text
Observation {

    ObservationId id

    ConnectedSourceId connectedSourceId

    ObservationType observationType

    SchemaVersion schemaVersion

    Optional<SourceReference> sourceReference

    Optional<Timestamp> observedAt

    Timestamp collectedAt

    TemporalSemantics temporalSemantics

    TypedPayload payload
}
```

This is pseudocode.

It is not the final implementation interface.

---

## 59. Typed Payload Contract

Conceptually:

```text
TypedPayload
```

is constrained by:

```text
ObservationType
+
SchemaVersion
```

For example:

```text
ObservationType:
EMAIL_MESSAGE_METADATA

SchemaVersion:
1

Payload:
EmailMessageMetadataV1
```

or:

```text
ObservationType:
PASSWORD_MANAGER_ENTRY_METADATA

SchemaVersion:
1

Payload:
PasswordManagerEntryMetadataV1
```

A consumer must not interpret a payload independently of its declared type and version.

---

## 60. Observation Invariants

### OBS-INV-001

Every Observation must reference exactly one ConnectedSource.

### OBS-INV-002

An Observation must not contain Provider credentials required only for source access.

### OBS-INV-003

Authentication secrets unnecessary for Discovery must not become normal Observation attributes.

### OBS-INV-004

ObservationType must be distinct from EvidenceType.

### OBS-INV-005

The payload must conform to its declared ObservationType and SchemaVersion.

### OBS-INV-006

Provider-specific raw objects must not be exposed directly as common Observation payloads.

### OBS-INV-007

The original source reference should be preserved where technically possible and safe.

### OBS-INV-008

`collected_at` and `observed_at` must not be treated as equivalent.

### OBS-INV-009

Temporal semantics must not be inferred beyond what the source supports.

### OBS-INV-010

An Observation must not contain a canonical Relationship conclusion.

### OBS-INV-011

An Observation must not require a canonical Service conclusion.

### OBS-INV-012

Unknown or unavailable information must not be fabricated to satisfy the payload schema.

### OBS-INV-013

Collection failure must not be represented as an Observation.

### OBS-INV-014

Collection completeness must not be inferred from the existence or absence of individual Observations.

### OBS-INV-015

Content equality must not automatically imply Observation identity.

### OBS-INV-016

Observations from different Connected Sources must remain distinguishable even when their payloads are identical.

### OBS-INV-017

Reclassification must not require destructive modification of the source Observation.

### OBS-INV-018

Entity re-resolution must not require destructive modification of the source Observation.

### OBS-INV-019

The Observation envelope must remain independent of a specific SourceType or Provider.

### OBS-INV-020

New ObservationTypes must be introducible without changing the semantics of existing ObservationTypes.

### OBS-INV-021

An Observation belongs to exactly one ConnectedSource even when its payload references multiple identities, Services or source-level objects.

---

## 61. Gmail Flow Example

Conceptually:

```text
Personal Gmail ConnectedSource
        |
        v
GmailConnector
        |
        v
Gmail API Message
        |
        v
Connector Minimization
        |
        v
Observation

type:
EMAIL_MESSAGE_METADATA

payload:
sender
recipients
subject
...
        |
        v
Discovery Core
```

The downstream core does not require Gmail API objects.

---

## 62. Outlook Flow Example

The same Discovery Core can consume:

```text
Work Outlook ConnectedSource
        |
        v
OutlookConnector
        |
        v
Microsoft Provider Object
        |
        v
Connector Minimization
        |
        v
Observation

type:
EMAIL_MESSAGE_METADATA

payload:
sender
recipients
subject
...
        |
        v
Same Discovery Core
```

If Gmail and Outlook Observations have equivalent framework semantics, they should use the same ObservationType rather than Provider-specific types such as:

```text
GMAIL_MESSAGE
OUTLOOK_MESSAGE
```

unless concrete differences demonstrate that separate types are necessary.

---

## 63. Multi-Provider Example

The target architecture is:

```text
GmailConnector ---------+
                        |
OutlookConnector -------+
                        |
ICloudConnector --------+--> EMAIL_MESSAGE_METADATA
                        |             |
ProtonConnector --------+             v
                                Discovery Core
```

not:

```text
GMAIL_MESSAGE
OUTLOOK_MESSAGE
ICLOUD_MESSAGE
PROTON_MESSAGE
```

followed by Provider-specific branching throughout the core.

This is formalized by Architecture Decision D-019.

---

## 64. Cross-Source Example

Different SourceTypes produce different ObservationTypes but enter the same Domain.

```text
Gmail
  |
  v
EMAIL_MESSAGE_METADATA
  |
  +-------------------+
                      |
                      v
                 Discovery Core
                      ^
                      |
  +-------------------+
  |
PASSWORD_MANAGER_ENTRY_METADATA
  ^
  |
Password Manager
```

Downstream components may extract different identifiers and Evidence from the different ObservationTypes.

---

## 65. Open Questions

### Observation Envelope

- Is the proposed minimum envelope sufficient?
- Should provenance be an explicit structured field?
- Should producer Connector ID and version be mandatory?
- Should a `collection_run_id` be included?
- Should Observation sensitivity be part of the envelope?

### Observation Type

- Who owns the ObservationType registry?
- Should ObservationTypes be centrally defined?
- Can Connectors introduce extension types?
- How are naming collisions prevented?
- Which ObservationTypes should exist initially?

### Schema Version

- Integer version?
- Semantic version?
- Per-ObservationType version?
- Global framework version?
- How are incompatible schema changes handled?

### Payload

- How should TypedPayloads be implemented?
- Tagged unions?
- Interface inheritance?
- JSON Schema?
- Dataclasses?
- Another mechanism?
- How are optional fields represented without losing missing-value semantics?

### Source Reference

- Must every Observation have one?
- What happens when the Provider exposes no stable source ID?
- Should source references be hashed?
- Should they be persisted in plaintext?
- How are source-reference changes handled?

### Temporal Information

- Is one `observed_at` sufficient?
- Can a source record expose multiple meaningful timestamps?
- Should timestamps be represented as repeated typed TemporalValues instead?
- How should Provider timezone ambiguity be handled?

### Identity Association

- Should Observation carry `associated_identity_reference`?
- Or should Identity matching be entirely downstream?
- How should multiple possible Identity Seeds be represented?

### Service Identifier Extraction

- Should Connectors produce normalized identifiers?
- Should identifier extraction remain inside ServiceCandidateDetector?
- Where exactly is the boundary between representation normalization and semantic identifier extraction?
- At what complexity threshold would a dedicated extractor become justified?

### Deduplication

- Which component owns deduplication?
- Connector?
- Observation Repository?
- Collection Layer?
- How are modified source records distinguished from true duplicates?

### Persistence

- Which ObservationTypes should be persisted?
- Can highly sensitive ObservationTypes be ephemeral?
- Is reprocessing worth the privacy cost of persistence?
- Can minimized representations provide both?

### Deletion

- How is derived Evidence invalidated when an Observation is deleted?
- Should dependent Evidence be deleted or marked `REJECTED`?
- How are affected Relationships identified?
- Should deletion create an auditable tombstone?
- How does deletion interact with re-synchronization?

### Provider Extensions

- Do we need a controlled Provider-extension mechanism?
- If yes, how do we prevent downstream logic from becoming Provider-dependent again?

---

## 66. Findings from Contract Design

### Finding 1 - Observation Requires a Stable Common Envelope

The common Discovery pipeline needs a small set of fields that exist independently of Provider-specific payload structure.

The current proposed envelope is:

```text
id
connected_source_id
observation_type
schema_version
source_reference
observed_at
collected_at
temporal_semantics
payload
```

### Finding 2 - Payload Must Be Typed

A generic unstructured dictionary would provide flexibility but insufficient contract guarantees.

The payload should therefore be typed according to:

```text
ObservationType
+
SchemaVersion
```

The implementation mechanism remains open.

### Finding 3 - Provider and Observation Type Must Be Separate

Gmail and Outlook can potentially produce:

```text
EMAIL_MESSAGE_METADATA
```

rather than forcing Provider-specific ObservationTypes.

This keeps Provider details behind Connectors.

This principle is now consolidated through Architecture Decision D-019.

### Finding 4 - Temporal Semantics Are First-Class

A timestamp alone is insufficient.

The framework must know what source event the timestamp represents.

This finding was particularly reinforced by Password Manager Service Discovery and is now represented in the Domain Model through TemporalSemantics and TemporalValue concepts.

### Finding 5 - Observation and Collection State Are Separate

Completeness, pagination failures and partial scans describe collection operations, not individual Observations.

Therefore collection state must not be embedded into each Observation.

### Finding 6 - Observation Is a Privacy Boundary

An Observation should not be a serialized copy of Provider data.

The Connector must minimize the source representation before information enters the common Discovery Core.

This principle is now consolidated through Architecture Decision D-018.

### Finding 7 - Observation Should Support Reprocessing

If minimized Observations are persisted, Evidence Classification and identifier processing should be able to evolve without requiring source retrieval for every change.

This must be balanced against data-minimization requirements.

### Finding 8 - Observation Is a Core Domain Entity

The consolidated Domain Model classifies `Observation` as a Core Domain Entity.

Its common envelope represents a stable boundary between Provider-specific collection and the common Discovery Domain.

Every Observation belongs to exactly one ConnectedSource.

Concrete typed payload schemas remain implementation-specific.

---

## 67. Architecture Alignment and Remaining Decision Candidates

### Architecture Alignment - Common Envelope, Typed Payload

Observations consist of a stable common envelope and a typed, versioned payload appropriate to the ObservationType.

Provider-specific raw source objects must not cross the Connector boundary as default Observation payloads.

This is part of the consolidated Domain Model and implementation baseline.

### Architecture Alignment - Provider-Neutral Observation Types

ObservationTypes represent source semantics rather than Provider identity wherever the semantics are compatible.

Equivalent Observations from different Providers should use the same ObservationType where practical.

This principle is formalized by:

```text
D-019 - Observation Types Are Provider-Neutral Where Possible
```

### Architecture Alignment - Explicit Temporal Semantics

Temporal values derived from external sources must preserve their source semantics and must not automatically be interpreted as Service activity.

This is now represented explicitly in Architecture v0.3 and Domain Model v0.3.

### Decision Candidate - Collection State Outside Observation

Collection completeness, pagination and synchronization state belong to collection context rather than individual Observations.

This remains consistent with the current architecture.

The exact future `CollectionRun` / synchronization model remains open.

### Architecture Alignment - Secrets Excluded by Default

Authentication secrets unnecessary for the requested capability must not become normal Observation attributes.

This is supported by:

```text
D-018 - Connector Is a Data-Minimization Boundary
```

and by the consolidated Privacy and Security invariants.

---

## 68. Current Contract Baseline

The minimum Observation contract is:

```text
Observation
 |
 +-- id
 |
 +-- connected_source_id
 |
 +-- observation_type
 |
 +-- schema_version
 |
 +-- source_reference
 |
 +-- observed_at
 |
 +-- collected_at
 |
 +-- temporal_semantics
 |
 +-- typed payload
```

with the following guarantees:

```text
Observation is a Core Domain Entity

exactly one ConnectedSource per Observation

ConnectedSource provenance

Provider-independent envelope

typed source semantics

versioned payload

explicit time semantics

no forced semantic interpretation

no canonical Service requirement

no Relationship conclusion

no Provider credential exposure

no unnecessary authentication secrets

reprocessing-compatible design
```

---

## 69. Downstream Contract

The next contract in the Discovery dependency chain is:

```text
ServiceCandidateDetector
```

and has now been defined in:

```text
docs/interfaces/03-service-candidate-detector-contract.md
```

Its responsibility is to determine whether a valid Observation should participate in Service Discovery.

The dependency remains:

```text
Connector
    |
    v
Observation
    |
    v
ServiceCandidateDetector
```

while Evidence Classification operates as an independent semantic branch from the same Observation:

```text
             Observation
             /         \
            v           v
Candidate Detection   Evidence Classification
```

The two paths later converge through Entity Resolution, Evidence Aggregation and Relationship Assessment.

The Observation Contract is now aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- ConnectedSource as a Core Domain Entity;
- Observation as a Core Domain Entity;
- Connector minimization boundary D-018;
- Provider-neutral Observation semantics D-019;
- the parallel Entity Resolution / Evidence Classification model.

No additional Observation-domain abstraction is required before the Implementation Model phase.
