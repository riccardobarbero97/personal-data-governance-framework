# Identity & Service Discovery

**Status:** Draft v0.3  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  

---

## 1. Purpose

The first problem addressed by the Personal Data Governance Framework is:

> Given one or more digital identities provided by a User and one or more explicitly authorized data sources, which digital Services appear to have or have had a Relationship with that User?

The objective of this capability is not to determine exactly what personal data each Service currently holds.

Its objective is to discover, normalize and document evidence of observable digital Relationships between the User and external Services.

The framework therefore builds an:

> **Observed Digital Relationship Graph**

rather than claiming to reconstruct an objective and complete digital footprint.

The current Discovery architecture is:

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

The output of Discovery becomes the starting point for subsequent framework capabilities that may:

- determine how personal data can be obtained from identified Services;
- request or retrieve that data;
- ingest and normalize returned information;
- identify and classify personal data;
- construct a Personal Data Graph;
- monitor changes;
- support User governance actions.

This document focuses exclusively on **Identity and Service Discovery**.

---

# 2. Observed Footprint

The framework does not attempt to reconstruct absolute truth.

It operates on information that can be observed through authorized sources.

Therefore:

```text
Observed Footprint
        !=
Complete Footprint
```

and:

```text
Observed Relationship
        !=
Current Data Possession
```

Every conclusion must remain relative to the information currently available to the framework.

The architecture must preserve distinctions between:

```text
Observed information
Interpretation
Resolved identity
Evidence
Relationship assessment
Unknown information
```

Uncertainty is a feature of the data model rather than a condition the framework attempts to hide.

---

# 3. Core Architectural Boundaries

The Discovery architecture is based on the following boundaries:

```text
SOURCE TYPE != PROVIDER

PROVIDER != CONNECTED SOURCE

CONNECTED SOURCE != CONNECTOR

CONNECTED SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

CANDIDATE != RESOLVED SERVICE

IDENTIFIER != SERVICE

NORMALIZATION != RESOLUTION

EVIDENCE != RELATIONSHIP

RELATIONSHIP != ACCOUNT

SERVICE != ORGANIZATION

RELATIONSHIP != CURRENT DATA POSSESSION
```

These distinctions are fundamental.

They prevent:

- external systems from leaking into the core Domain Model;
- collected information from being confused with interpretation;
- technical identifiers from becoming canonical Services automatically;
- Evidence from being treated as confirmed facts;
- Relationships from being interpreted as proof of active accounts;
- historical interaction from being mistaken for current data possession.

---

# 4. Design Principles

## 4.1 Evidence Before Inference

The framework must distinguish between:

- what has been observed;
- what has been interpreted;
- what has been resolved;
- what has been inferred;
- what has been confirmed by the User;
- what remains unknown.

For example:

```text
Observation:
Subject = "Verify your email address"

Evidence:
ACCOUNT_VERIFICATION
```

does not independently prove:

```text
Account currently active
```

nor:

```text
Service currently stores personal data
```

Every derived conclusion must remain traceable to the Evidence that supports it.

---

## 4.2 Unknown Is a Valid State

The framework must not fabricate information to close knowledge gaps.

Valid outcomes include:

```text
Candidate Status:
UNKNOWN

Resolution Status:
UNRESOLVED

Resolution Status:
AMBIGUOUS

Evidence Classification:
UNKNOWN

Relationship Status:
UNKNOWN

Temporal Status:
UNKNOWN
```

Insufficient information is not a system failure.

It is a legitimate domain state.

---

## 4.3 Multiple Independent Sources

No individual source can be considered sufficient to reconstruct the User's complete digital footprint.

The framework must support multiple source categories such as:

```text
Email
Password Manager
Browser
Identity Provider
Manual Input
Future Authorized Sources
```

and multiple concrete source instances simultaneously.

Example:

```text
User
 |
 +-- Personal Gmail
 |
 +-- Old Gmail
 |
 +-- Work Outlook
 |
 +-- iCloud Mail
 |
 +-- Proton Mail
 |
 +-- Password Manager A
 |
 +-- Password Manager B
```

Evidence originating from these sources may eventually converge on the same canonical Service.

---

## 4.4 Provider Independence

Core Discovery components must not depend on one particular provider.

The target model is:

```text
Gmail --------- GmailConnector --------+
                                       |
Outlook ------- OutlookConnector ------+
                                       |
iCloud -------- ICloudConnector -------+--> Observations
                                       |          |
Proton -------- ProtonConnector -------+          v
                                       |    Discovery Core
PasswordMgr --- PasswordConnector -----+
```

Provider-specific behavior should remain behind Connectors whenever reasonably possible.

---

## 4.5 Explainability

The framework should be able to answer:

> Why do you think I have or had a Relationship with this Service?

The explanation should be reconstructable through:

```text
Connected Source
      |
      v
Observation
      |
      v
Interpretation / Resolution
      |
      v
Evidence
      |
      v
Evidence Aggregate
      |
      v
Relationship Assessment
```

Explainability should not require exposing irrelevant raw personal information.

---

## 4.6 Local-First

The framework must avoid becoming another centralized repository containing the User's complete digital life.

Where technically practical:

```text
External Source
      |
      v
Privileged Connector
      |
      v
Minimize
      |
      v
Observation
      |
      v
Local Discovery Processing
      |
      v
Evidence / Relationship
      |
      v
Minimum Necessary Persistence
```

Sensitive source information should remain local whenever practical.

---

## 4.7 Progressive Permission

Source access must be capability-driven.

Connecting a source must not automatically grant every framework capability access to all information available from that source.

The general model is:

```text
Capability
    |
    v
Required Information
    |
    v
Minimum Required Permission
```

If existing information is insufficient:

```text
Current Permission
      |
      v
Attempt Capability
    /         \
 enough     insufficient
   |             |
   v             v
continue     explain need
                 |
                 v
           User decision
            /       \
         allow      deny
           |          |
           v          v
        continue     remain
                   unresolved
```

No component may silently escalate provider permissions.

---

## 4.8 Preserve Provenance

Derived information must not destructively replace source information.

Conceptually:

```text
Source Record
      |
      v
Observation
      |
      v
Candidate Identifier
      |
      v
Normalized Identifier
      |
      v
Resolved Service
```

and:

```text
Observation
      |
      v
Evidence
      |
      v
Evidence Aggregate
      |
      v
Relationship Assessment
```

must remain traceable.

Provenance enables:

- explainability;
- debugging;
- auditability;
- User correction;
- reclassification;
- re-resolution;
- Policy evolution;
- Service merge and split operations.

---

## 4.9 Deterministic First

Operations that can be reliably implemented deterministically should remain deterministic.

Examples include:

```text
email-address parsing
URL parsing
hostname extraction
domain normalization
known mapping lookup
Evidence counting
temporal sorting
rule-based classification
```

The preferred pattern is:

```text
Deterministic Processing
        |
   +----+----+
   |         |
resolved   ambiguous
   |         |
   |         v
   |     AI when justified
   |         |
   +----+----+
        |
        v
      Result
```

AI is an optional strategy available to components.

AI is not the Discovery architecture itself.

---

# 5. Identity Seed

An `IdentitySeed` represents a digital identity explicitly declared by the User and used as a starting point for Discovery.

Possible examples include:

```text
email address
phone number
username
Google account
Apple account
Microsoft account
```

Conceptually:

```text
IdentitySeed

id
type
value
verification_status
```

A User may define multiple Identity Seeds.

Example:

```text
User
 |
 +-- personal@gmail.com
 |
 +-- oldmail@example.net
 |
 +-- user@outlook.com
 |
 +-- +39XXXXXXXXXX
 |
 +-- username123
```

An observed identifier must not automatically become a verified Identity Seed.

Therefore:

```text
OBSERVED IDENTITY IDENTIFIER
              !=
VERIFIED IDENTITY SEED
```

---

# 6. SourceType

`SourceType` describes the general category of a source.

Initial examples include:

```text
EMAIL
PASSWORD_MANAGER
BROWSER
IDENTITY_PROVIDER
MANUAL
```

The vocabulary must remain extensible.

`EMAIL` describes a source category.

It does not describe a specific provider or User connection.

---

# 7. Provider

`Provider` represents the external product, platform or organization through which a source is accessed.

Conceptually:

```text
EMAIL
 |
 +-- Google / Gmail
 +-- Microsoft / Outlook
 +-- Apple / iCloud Mail
 +-- Proton / Proton Mail
```

and:

```text
PASSWORD_MANAGER
 |
 +-- Provider A
 +-- Provider B
```

Provider capabilities may differ even when their SourceType is the same.

The Discovery Core must therefore not infer available capabilities solely from SourceType.

---

# 8. ConnectedSource

A `ConnectedSource` represents a specific source instance connected or authorized by the User.

Examples include:

```text
Personal Gmail
Old Gmail
Work Outlook
Personal Proton Mail
Primary Password Manager
Archived Password Manager
Browser Profile
```

Conceptually:

```text
ConnectedSource

id
source_type
provider
connector_reference
display_name
external_account_reference
connection_state
authorization_state
```

This representation remains conceptual.

---

## 8.1 Multiple Source Instances

The architecture must support:

```text
                    GmailConnector
                    /            \
                   /              \
                  v                v
         Personal Gmail        Old Gmail
```

Both use the same Connector implementation but remain independent Connected Sources.

Each may have independent:

- authorization;
- permissions;
- synchronization;
- revocation;
- collection history;
- Observations.

---

## 8.2 ConnectedSource Is Not IdentitySeed

Example:

```text
IdentitySeed:
personal@gmail.com

ConnectedSource:
Personal Gmail
```

These concepts may be related but remain different.

A password-manager ConnectedSource may contain information associated with several Identity Seeds.

---

## 8.3 ConnectedSource Lifecycle

A ConnectedSource may move through states conceptually equivalent to:

```text
authorization pending
connected
authorization expired
permission insufficient
revoked
disconnected
error
```

The final state model remains implementation-dependent.

Disconnecting one source must not implicitly disconnect another source using the same Connector.

---

# 9. Connector

A `Connector` isolates provider-specific integration logic.

Conceptually:

```text
ConnectedSource
       |
       v
    Connector
       |
       v
Provider System
```

and:

```text
Provider System
       |
       v
Connector
       |
       v
Observation
```

Connector responsibilities may include:

- authorization;
- provider API interaction;
- capability discovery;
- permission analysis;
- pagination;
- synchronization;
- provider-specific error handling;
- source-format normalization;
- minimization;
- Observation creation.

---

## 9.1 Connector as Security Boundary

A Connector is also a privileged security boundary.

The preferred model is:

```text
Highly Sensitive Source
         |
         v
      Connector
         |
    +----+----+
    |         |
 required   unnecessary
   data      sensitive
    |         data
    |          |
    v          X
Observation
```

For example, a password-manager Connector may encounter:

```text
title
username
URI
password
OTP seed
recovery codes
```

while Service Discovery requires only:

```text
title
username
URI
```

Secrets unnecessary for Discovery should not cross the Connector boundary.

---

# 10. Connector Capabilities

Connectors should explicitly advertise supported capabilities.

The framework must not assume:

```text
SourceType EMAIL
       ->
all email capabilities available
```

Examples of capability concepts may include:

```text
SERVICE_DISCOVERY_METADATA
CONTENT_COLLECTION
ATTACHMENT_COLLECTION
INCREMENTAL_SYNC
```

Capabilities should describe meaningful framework behavior rather than unnecessarily mirror provider-specific APIs.

---

# 11. Observation

An `Observation` represents source-derived information obtained from one ConnectedSource before semantic interpretation.

Therefore:

```text
OBSERVATION != EVIDENCE
```

The preferred representation is:

```text
Observation
 |
 +-- Common Envelope
 |
 +-- Typed Payload
```

Conceptually:

```text
Observation

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

---

## 11.1 Common Envelope

The common envelope preserves framework-wide semantics such as:

```text
ConnectedSource provenance
Observation type
Schema version
Source reference
Temporal information
```

---

## 11.2 Typed Payload

Different source structures should use different typed payloads.

Examples:

```text
EMAIL_MESSAGE_METADATA v1

PASSWORD_MANAGER_ENTRY_METADATA v1

BROWSER_VISIT v1
```

The architecture should avoid both:

```text
one huge flat object with hundreds of optional fields
```

and:

```text
arbitrary untyped JSON
```

---

## 11.3 Provider-Neutral Observation Types

Equivalent source semantics from different providers should use the same Observation Type where possible.

For example:

```text
Gmail --------+
              |
Outlook ------+
              |
iCloud -------+--> EMAIL_MESSAGE_METADATA
              |
Proton -------+
```

rather than:

```text
GMAIL_MESSAGE
OUTLOOK_MESSAGE
ICLOUD_MESSAGE
PROTON_MESSAGE
```

unless concrete semantic differences justify different types.

---

## 11.4 Temporal Semantics

A timestamp is not sufficient without its meaning.

For example:

```text
Email:
MESSAGE_TIME
```

and:

```text
Password Manager:
SOURCE_RECORD_MODIFIED
```

must not automatically be interpreted identically.

Therefore temporal values must preserve:

```text
timestamp
+
temporal_semantics
```

---

# 12. Service Candidate Detection

Not every Observation represents information relevant to Service Discovery.

Candidate Detection determines:

> Should this Observation participate in Service Discovery?

Candidate outcomes are conceptually:

```text
CANDIDATE
NOT_CANDIDATE
UNKNOWN
```

`UNKNOWN` is valid.

---

## 12.1 Candidate Is Not Resolved

A Candidate may exist even when the Service cannot be identified.

Therefore:

```text
CANDIDATE != RESOLVED
```

Example:

```text
Password Manager Entry:
old-service.example

Candidate:
YES

Resolution:
UNRESOLVED
```

---

## 12.2 Candidate Identifiers

Candidate Detection may extract simple technical identifiers needed for Entity Resolution.

Examples include:

```text
DOMAIN
HOSTNAME
URL
EMAIL_DOMAIN
SOURCE_SPECIFIC_IDENTIFIER
```

The current architecture does not require a separate Identifier Extractor.

If identifier extraction becomes independently complex in future scenarios, this decision may be revisited.

---

# 13. ServiceIdentifier

A `ServiceIdentifier` represents a technical identifier potentially associated with a Service.

Examples include:

```text
spotify.com
accounts.spotify.com
https://accounts.spotify.com/login
no-reply@spotify.com
provider-specific application ID
```

Therefore:

```text
IDENTIFIER != SERVICE
```

A Service may have many identifiers.

An identifier may also be insufficient to uniquely identify one Service.

---

# 14. Entity Resolution

Entity Resolution determines whether Candidate Identifiers correspond to a canonical Service.

Conceptually:

```text
CandidateIdentifier
      |
      v
EntityResolver
      |
  +---+---------+
  |             |
  v             v
Resolved     Unresolved
  |
  v
Service
```

An additional state is required for competing plausible mappings:

```text
AMBIGUOUS
```

The minimum resolution model is therefore:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

---

## 14.1 Normalization Is Not Resolution

For example:

```text
accounts.spotify.com
       |
       v
spotify.com
```

may be normalization.

While:

```text
spotify.com
       |
       v
Spotify
```

is Entity Resolution.

Therefore:

```text
NORMALIZATION != RESOLUTION
```

Both should remain explainable.

---

## 14.2 Cross-Source Resolution

Identifiers from multiple sources should be able to resolve to the same Service.

Example:

```text
Personal Gmail
      |
      v
spotify.com
      |
      +----------------+
                       |
                       v
                    Spotify
                       ^
                       |
      +----------------+
      |
accounts.spotify.com
      ^
      |
Password Manager
```

The framework must not create provider-specific copies of canonical Services.

---

## 14.3 Shared Infrastructure

Technical infrastructure may belong to an intermediary rather than the Service relevant to the User.

Examples include:

```text
email delivery provider
payment provider
customer-support platform
cloud provider
CDN
identity infrastructure
```

The Resolver must not automatically convert every observed infrastructure provider into the discovered Service.

`UNRESOLVED` or `AMBIGUOUS` may be preferable.

---

## 14.4 Service Registry

Entity Resolution requires access to some concept of known canonical Services and their identifiers.

Conceptually:

```text
Service Registry

Service
   |
   +-- Identifier
   +-- Identifier
   +-- Identifier
```

The architecture recognizes the need for Service Registry semantics.

However, Draft v0.3 does not yet define:

- Service Registry persistence;
- Service creation workflow;
- Service merge workflow;
- Service split workflow;
- registry ownership.

These remain implementation and domain-design questions.

The Entity Resolver must not silently absorb all Service Registry lifecycle responsibilities.

---

# 15. Service

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
domain
URL
email sender
ConnectedSource
Provider
Organization
Account
```

---

## 15.1 Service Granularity

The canonical granularity of Service remains deliberately unresolved.

For example:

```text
Google
Google Account
Gmail
```

may represent different levels of abstraction.

The framework must not define service identity implicitly through technical identifiers alone.

Service granularity should be validated against real data and later framework capabilities.

---

## 15.2 Service Is Not Organization

A Service may be operated by an Organization.

One Organization may operate multiple Services.

Therefore:

```text
SERVICE != ORGANIZATION
```

The future model may require:

```text
Service
Brand
Organization
Legal Data Controller
```

but Draft v0.3 does not yet formalize them.

---

# 16. Evidence Classification

Evidence Classification interprets the semantic meaning of an Observation.

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

The classifier may return:

```text
CLASSIFIED
```

or:

```text
UNKNOWN
```

while technical processing failures remain separate.

---

## 16.1 Evidence Taxonomy

Examples currently validated through scenarios include:

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

This is not yet a final taxonomy.

Evidence Types must eventually belong to a controlled and versionable taxonomy.

Equivalent semantics from different providers should map to the same Evidence Type where possible.

---

## 16.2 Multiple Evidence Items

One Observation may produce zero, one or multiple Evidence items.

For example:

```text
Your subscription was renewed and your payment was successful
```

may justify:

```text
SUBSCRIPTION
PAYMENT
```

when each semantic classification is independently supported.

The classifier must not generate implied Evidence merely because categories commonly co-occur.

---

## 16.3 Deterministic Classification

Explicit rules should be preferred when they reliably classify the Observation.

Examples include:

```text
"Verify your email address"
      ->
ACCOUNT_VERIFICATION
```

or:

```text
"Reset your password"
      ->
PASSWORD_RESET
```

AI is reserved for ambiguity where it provides measurable value.

---

## 16.4 Evidence and Service Resolution Are Independent

Evidence Classification and Entity Resolution are parallel concerns.

Therefore valid states include:

```text
Service:
UNRESOLVED

Evidence:
PAYMENT
```

and:

```text
Service:
Spotify

Evidence:
UNKNOWN
```

The architecture must not force one process to wait for successful completion of the other when that dependency is unnecessary.

---

# 17. Parallel Discovery Branches

Draft v0.3 explicitly models Entity Resolution and Evidence Classification as parallel semantic branches.

```text
                     Observation
                     /         \
                    /           \
                   v             v
       Candidate Detection    Evidence Classification
                   |             |
                   v             v
          CandidateIdentifier  Evidence
                   |
                   v
           Entity Resolution
                   |
                   v
                Service
                   \             /
                    \           /
                     v         v
                 Evidence Aggregation
```

This replaces the earlier simplified sequential representation.

The two branches may complete independently before their results are combined.

---

# 18. Evidence

`Evidence` represents a semantic interpretation supported by one or more Observations.

Therefore:

```text
EVIDENCE != FACT
```

An Evidence item such as:

```text
ACCOUNT_VERIFICATION
```

means:

> Available source information was interpreted as account-verification Evidence.

It does not mean:

> The User definitely has a currently active account.

---

## 18.1 Evidence Provenance

Evidence should remain traceable to:

```text
Supporting Observation
ConnectedSource
Evidence Type
Classification Method
Classifier Version
Relevant Service if resolved
Relevant Identity if known
Temporal information
```

---

## 18.2 Evidence Lifecycle

Classification logic may evolve.

Example:

```text
Observation
    |
    +--> Classifier v1
    |        |
    |        v
    |     MARKETING
    |
    +--> Classifier v2
             |
             v
       PRIVACY_NOTICE
```

The architecture must not treat both classifications as simultaneous current semantic facts merely because both are historically preserved.

The Domain Model therefore requires explicit Evidence lifecycle semantics.

Conceptually:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

### ACTIVE

The Evidence represents the currently accepted interpretation.

### SUPERSEDED

The Evidence remains preserved for provenance but has been replaced by a newer accepted interpretation.

### REJECTED

The Evidence interpretation has been explicitly invalidated or rejected and must not participate in current Relationship Assessment.

Exact transition rules remain to be defined.

Historical provenance must remain preserved.

---

# 19. Evidence Aggregation

Evidence Aggregation structures multiple Evidence items associated with the same discovery context.

Conceptually:

```text
Evidence
Evidence
Evidence
    |
    v
EvidenceAggregator
    |
    v
EvidenceAggregate
```

The primary grouping boundary is the canonical Service where available.

---

## 19.1 Service-Level Aggregation

Example:

```text
Spotify
 |
 +-- ACCOUNT_VERIFICATION
 +-- SUBSCRIPTION
 +-- PAYMENT
 +-- PASSWORD_MANAGER_ENTRY
```

Evidence frequencies, source provenance, Identity references and temporal information may be summarized.

---

## 19.2 Preserve Identity Information

Service-level aggregation must not erase relevant Identity references.

Example:

```text
Spotify
 |
 +-- Evidence
 |      identity: personal@example.com
 |
 +-- Evidence
        identity: oldmail@example.net
```

This does not automatically imply:

```text
two Spotify Accounts
```

Account remains a separate candidate concept.

---

## 19.3 Source Diversity

The Aggregate should preserve independently:

```text
ConnectedSource diversity
SourceType diversity
Provider diversity
Evidence frequency
```

For example:

```text
150 marketing emails from one Gmail account
```

is structurally different from:

```text
1 account-verification email
+
1 password-manager entry
```

The Aggregator describes those differences.

It does not assign Relationship strength.

---

## 19.4 Evidence Frequency Is Descriptive

Therefore:

```text
100 MARKETING
```

does not automatically outweigh:

```text
1 ACCOUNT_VERIFICATION
```

Frequency is descriptive.

Semantic importance belongs to Relationship Assessment.

---

## 19.5 Unresolved Evidence

Evidence must not disappear when Entity Resolution fails.

Conceptually:

```text
Evidence:
PAYMENT

Identifier:
unknown.example

Service:
UNRESOLVED
```

remains valid Discovery information.

It should remain available for later re-resolution.

---

## 19.6 Aggregate Is Derived State

An Evidence Aggregate is derived state.

Therefore:

```text
Evidence Aggregate
        |
        v
rebuildable
        |
        v
from active Evidence
```

where source Evidence remains available.

A materialized Aggregate must not become the only source of provenance.

---

# 20. Relationship

A `Relationship` represents the framework's current assessment that a meaningful digital Relationship exists or existed between the User and a Service.

The core relationship is therefore:

```text
USER
  |
  v
RELATIONSHIP
  |
  v
SERVICE
```

Relevant Identity Seeds remain associated with and preserved inside the Relationship context.

---

## 20.1 Why Relationship Is User-Oriented

The primary user-facing question is:

> Which Services appear connected to me?

Therefore User-Service is the primary Relationship perspective.

However, Identity information remains important for questions such as:

> Which Services were associated with `oldmail@example.net`?

A Relationship may therefore preserve:

```text
Identity References
```

without requiring separate Relationship entities for every Identity at this stage.

---

## 20.2 Relationship Is Not Account

The framework may discover Relationships through:

```text
account Evidence
guest purchases
newsletter subscriptions
privacy communications
historical interactions
browser activity
other authorized sources
```

Therefore:

```text
RELATIONSHIP != ACCOUNT
```

`Account` remains a candidate Domain Concept rather than a requirement for basic Discovery.

---

# 21. RelationshipStatus

Relationship support and temporal interpretation are separate dimensions.

Draft v0.3 therefore introduces:

```text
RelationshipStatus
```

with an initial conceptual model:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

---

## 21.1 UNKNOWN

Available Evidence is insufficient to justify a meaningful Relationship conclusion.

This does not prove that no Relationship exists.

---

## 21.2 OBSERVED

Interaction or communication with the Service has been observed, but available Evidence does not justify a stronger Relationship conclusion.

Possible examples may include:

```text
marketing
newsletter
privacy communication
browser visits
```

depending on future validated assessment policy.

---

## 21.3 ESTABLISHED

Available Evidence provides a justified basis for concluding that a meaningful Relationship existed.

The exact Evidence combinations required for `ESTABLISHED` remain subject to empirical validation.

Draft v0.3 does not define arbitrary fixed weights.

---

## 21.4 REJECTED

Available information or explicit User correction establishes that the apparent Relationship should not currently be attributed to the User.

A rejection requires provenance.

Weak Evidence alone must not automatically produce `REJECTED`.

---

# 22. TemporalStatus

Temporal interpretation is represented separately through:

```text
TemporalStatus
```

with an initial conceptual model:

```text
UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

---

## 22.1 UNKNOWN

The framework cannot safely determine whether the Relationship is current or historical.

This may be a common state.

---

## 22.2 CURRENTLY_OBSERVED

Recent Evidence indicates ongoing observable interaction.

This must not automatically mean:

```text
Active Account Confirmed
```

For example, recent marketing communication may represent ongoing communication without proving account activity.

---

## 22.3 HISTORICAL

Available Evidence supports that a meaningful Relationship existed in the past, while current continuation is not established or Evidence indicates that it ended.

Example:

```text
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

may eventually support:

```text
RelationshipStatus:
ESTABLISHED

TemporalStatus:
HISTORICAL
```

---

# 23. RelationshipStatus and TemporalStatus Are Independent

The architecture must allow combinations such as:

```text
ESTABLISHED + HISTORICAL
```

```text
ESTABLISHED + UNKNOWN
```

```text
OBSERVED + CURRENTLY_OBSERVED
```

This replaces the earlier flat conceptual state model that mixed:

```text
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
```

into one dimension.

---

# 24. Relationship Assessment

Relationship Assessment interprets an Evidence Aggregate.

Conceptually:

```text
Evidence Aggregate
       |
       v
RelationshipAssessor
       |
       v
RelationshipStatus
+
TemporalStatus
+
Evidence Basis
+
Reason Codes
+
Warnings
```

The assessment should use explicit, explainable and versionable policy.

---

## 24.1 No Arbitrary Weighting

Draft v0.3 does not define formulas such as:

```text
ACCOUNT_VERIFICATION = 0.8
PASSWORD_MANAGER_ENTRY = 0.9
MARKETING = 0.1
```

Such values would imply calibration that does not yet exist.

---

## 24.2 Evidence Semantics Matter

Relationship Assessment should consider:

```text
Evidence Types
Evidence chronology
SourceType diversity
ConnectedSource diversity
Identity references
Conflicts
User corrections
```

without collapsing them into an arbitrary score.

---

## 24.3 Conflicting Evidence

Evidence may conflict.

Example:

```text
2024 ACCOUNT_DELETION
2026 AUTHENTICATION
```

The framework must not fabricate an explanation.

Possible assessment:

```text
RelationshipStatus:
ESTABLISHED

TemporalStatus:
UNKNOWN

Warning:
CONFLICTING_TEMPORAL_EVIDENCE
```

---

# 25. No Numerical Confidence in Initial Discovery

Numerical Confidence is explicitly excluded from the initial Discovery Domain Model.

The framework should initially prefer:

```text
RelationshipStatus
TemporalStatus
Evidence Basis
Source Diversity
Timeline
Reason Codes
Warnings
```

over:

```text
confidence = 0.87
```

Confidence may be reconsidered later only if:

- its semantics are explicitly defined;
- representative validation data exists;
- calibration is possible;
- it provides measurable value to the User.

This applies similarly to Candidate Detection, Entity Resolution, Evidence Classification and Relationship Assessment.

Explicit states are preferred over uncalibrated numerical pseudo-precision.

---

# 26. Historical Relationships

Historical Relationships remain part of the User's observed digital footprint.

Therefore:

```text
HISTORICAL
      !=
REMOVE FROM SERVICE GRAPH
```

A historical Service may still matter because:

- transaction records may remain;
- legal retention may apply;
- residual personal data may exist;
- backups may exist;
- later Personal Data Acquisition may still be relevant.

Historical Relationship does not imply:

```text
no personal data remains
```

---

# 27. Account

`Account` remains a candidate Domain Concept.

It may eventually be useful for representing:

```text
Service:
Spotify

Account A:
personal@example.com

Account B:
oldmail@example.net
```

Potential use cases include:

- multiple accounts with one Service;
- historical accounts;
- shared accounts;
- migrated accounts;
- multiple identities.

However, the current Discovery pipeline does not require Account.

Relationships can exist without conventional accounts.

Therefore:

```text
Account = CANDIDATE DOMAIN CONCEPT
```

in Draft v0.3.

---

# 28. Multiple Sources and Cross-Source Evidence

Evidence from different Connected Sources may contribute to one canonical Relationship.

Example:

```text
                       Spotify
                          |
                    Relationship
                    /           \
                   /             \
                  v               v
          Email Evidence     Password Manager
                                 Evidence
```

The framework should preserve source provenance while avoiding provider-specific Service duplication.

---

# 29. Multi-Provider Email

Multiple email providers should enter the same semantic Discovery pipeline.

Conceptually:

```text
Gmail ----------+
                |
Outlook --------+
                |
iCloud Mail ----+--> EMAIL_MESSAGE_METADATA
                |             |
Proton Mail ----+             v
                       Candidate Detection
                               +
                       Evidence Classification
```

Provider-specific APIs and authorization remain behind their Connectors.

---

# 30. Evidence Reprocessing

Observation preservation enables later reclassification.

```text
Observation
    |
    +--> Classifier v1
    |         |
    |         v
    |     Evidence v1
    |
    +--> Classifier v2
              |
              v
          Evidence v2
```

Evidence lifecycle ensures that historical interpretations can remain preserved without both automatically contributing to the current Relationship.

---

# 31. Entity Re-Resolution

Similarly:

```text
ServiceIdentifier
      |
      +--> Resolver v1
      |       |
      |       v
      |   UNRESOLVED
      |
      +--> Resolver v2
              |
              v
           Service
```

must be possible without automatically retrieving source information again where preserved minimized information is sufficient.

---

# 32. Re-Aggregation

Changes to Evidence or Service Resolution may require rebuilding aggregates.

Triggers may include:

```text
new Evidence
Evidence deletion
Evidence reclassification
Evidence status change
Entity re-resolution
Service merge
Service split
Identity reassociation
ConnectedSource removal
aggregation policy change
```

Because Aggregates are derived state, they should remain rebuildable.

---

# 33. Relationship Reassessment

Relationship assessments must also remain recalculable.

Triggers may include:

```text
Evidence Aggregate change
User correction
assessment policy change
Service merge
Service split
Identity association change
ConnectedSource data removal
```

Assessment policy should remain explicit and versionable.

---

# 34. User Correction

The framework must support future User correction without destructive rewriting of source provenance.

Examples include:

```text
"This identifier does not belong to Spotify."

"These two Services are the same."

"These two Services are different."

"This Relationship does not belong to me."

"This was a guest purchase."

"This Relationship is historical."
```

Corrections themselves require provenance.

---

# 35. Service Graph

The output of Discovery is a Service Graph representing observed and assessed Relationships.

Conceptually:

```text
                         USER
                          |
            +-------------+-------------+
            |                           |
            v                           v
      Relationship                Relationship
            |                           |
            v                           v
        Spotify                       GitHub
            |                           |
            v                           v
      Evidence Basis             Evidence Basis
```

The graph should answer:

> Which Services appear to have or have had a Relationship with me?

and:

> Why does the framework believe that?

It does not answer:

> Exactly what personal data does each Service currently possess?

That belongs to later capabilities.

---

# 36. Service Graph Is Not Absolute Truth

Every Service Graph Relationship remains grounded in:

```text
Observed Evidence
        +
Assessment Policy
        +
Assessment Provenance
```

The graph represents current framework knowledge.

It must not be presented as a complete external truth.

---

# 37. Privacy and Security Requirements

Identity and Service Discovery may process highly sensitive information including:

- email metadata;
- potentially email content;
- account-related Evidence;
- browsing information;
- authentication relationships;
- personal identifiers;
- password-manager metadata;
- historical digital activity.

A privacy framework must not solve one privacy problem by creating another.

---

## 37.1 Data Minimization

Only information necessary for the requested capability should be collected and propagated.

Technical availability does not independently justify collection.

---

## 37.2 Connector Minimization Boundary

The Connector must minimize provider-specific information before it enters the common Discovery Core where technically practical.

Source secrets unnecessary for Discovery must remain outside normal Observations.

---

## 37.3 Least Privilege

Connectors should request the narrowest access capable of supporting the selected capability.

Access should not be broadened merely for implementation convenience.

---

## 37.4 Local Processing

The following should remain local where technically practical:

```text
Observation processing
Candidate Detection
Identifier normalization
Entity Resolution
Rule-based Evidence Classification
Evidence Aggregation
Relationship Assessment
```

Remote processing should be deliberate and justified.

---

## 37.5 Credentials

Provider credentials and authorization tokens must remain isolated from downstream Discovery components.

Components processing preserved Observations must not need provider credentials merely to reinterpret existing information.

---

# 38. AI Architecture

AI may contribute to selected Discovery strategies.

Potential areas include:

```text
ambiguous Evidence Classification
ambiguous Entity Resolution
multilingual semantic interpretation
complex explanation generation
future conflict analysis
```

The architecture remains AI-provider independent.

---

## 38.1 AI Is a Strategy

The correct abstraction is:

```text
Discovery Component
      |
      +-- Deterministic Strategy
      |
      +-- AI-Assisted Strategy
      |
      +-- UNKNOWN / UNRESOLVED fallback
```

not:

```text
All User Data
      |
      v
     LLM
      |
      v
Discovery Result
```

---

## 38.2 Graceful Degradation

If AI is unavailable:

```text
deterministic processing continues
```

and unresolved states remain explicit.

Basic Discovery must not depend on AI availability.

---

# 39. Failure Model

Each component may fail independently.

Technical failures must remain separate from uncertainty states.

For example:

```text
Connector failure
       !=
No Observations Found
```

```text
Detector failure
       !=
NOT_CANDIDATE
```

```text
Resolver failure
       !=
UNRESOLVED
```

```text
Classifier failure
       !=
UNKNOWN
```

```text
Aggregator failure
       !=
EMPTY
```

```text
Assessor failure
       !=
RelationshipStatus UNKNOWN
```

This distinction is required across the Discovery pipeline.

---

# 40. Collection Completeness

The absence of Evidence must not be interpreted as complete absence of a Relationship unless relevant source collection completed successfully.

Conceptually:

```text
No Evidence Found
       !=
Source Analysis Incomplete
```

Partial source coverage should remain visible to downstream assessment and User explanations.

---

# 41. Non-Goals

## 41.1 Complete Discovery

The framework cannot guarantee discovery of every Service holding personal information about the User.

```text
Observed Footprint != Complete Footprint
```

---

## 41.2 Current Data Possession

Discovery does not establish which personal information a Service currently possesses.

---

## 41.3 Account Verification

Discovery does not universally prove that a conventional Account exists.

---

## 41.4 Personal Data Acquisition

Discovery does not retrieve the User's full personal dataset from Services.

That belongs to later framework capabilities.

---

## 41.5 Public Internet Discovery

Searching the public Internet for leaked information, public profiles or occurrences of identifiers is a separate technical capability.

---

## 41.6 Final Service Ontology

Draft v0.3 does not define a universal taxonomy connecting:

```text
Service
Product
Brand
Organization
Legal Data Controller
```

---

## 41.7 Numerical Confidence

Numerical Confidence is outside the initial Discovery model.

---

## 41.8 Final Persistence Design

This architecture does not define:

```text
database technology
graph database
SQL schema
file format
API representation
object-relational mapping
```

---

# 42. End-to-End Discovery Architecture

The current Identity and Service Discovery architecture is:

```text
                               USER
                                |
               +----------------+----------------+
               |                                 |
               v                                 v
        IDENTITY SEEDS                    CONNECTED SOURCES
                                                  |
                                                  v
                                             CONNECTOR
                                                  |
                                                  v
                                             OBSERVATION
                                              /       \
                                             /         \
                                            v           v
                               SERVICE CANDIDATE      EVIDENCE
                                   DETECTION       CLASSIFICATION
                                      |                 |
                                      v                 v
                                CANDIDATE            EVIDENCE
                                IDENTIFIERS             |
                                      |                 |
                                      v                 |
                               ENTITY RESOLUTION        |
                                      |                 |
                              +-------+-------+         |
                              |               |         |
                              v               v         |
                           SERVICE        UNRESOLVED     |
                              |              CONTEXT    |
                              |               |         |
                              +-------+-------+---------+
                                      |
                                      v
                              EVIDENCE AGGREGATION
                                      |
                                      v
                               EVIDENCE AGGREGATE
                                      |
                                      v
                             RELATIONSHIP ASSESSMENT
                                      |
                                      v
                                 RELATIONSHIP
                                      |
                                      v
                                 SERVICE GRAPH
```

This architecture is the baseline for the first executable Discovery implementation.

---

# 43. Architecture Decisions

## D-001 - Discovery Is Evidence-Based

A discovered Service does not imply that it currently holds personal data.

Discovery identifies observable Evidence of possible current or historical Relationships.

---

## D-002 - Multiple Discovery Sources

No single Discovery Source defines the framework.

Multiple source types and source instances must be able to contribute to the same canonical Service Relationship.

---

## D-003 - Unknown Is a Valid State

Unknown, ambiguous and unresolved information must remain explicitly representable.

The system must not fabricate certainty to remove incomplete states.

---

## D-004 - Local-First

Raw and sensitive personal information should be processed locally whenever technically practical.

---

## D-005 - Explainability

Every Relationship should remain explainable through its supporting Evidence and provenance.

---

## D-006 - Discovery and Acquisition Are Separate

Discovering a Service Relationship and obtaining personal data from that Service are separate framework capabilities.

---

## D-007 - Commercial Licensing

The project is intended to allow permitted non-commercial use without a commercial license.

Commercial use will require separate licensing terms established before public release.

---

## D-008 - Provider-Independent AI

The framework must not depend on one specific AI model or provider.

---

## D-009 - AI Does Not Replace Reliable Deterministic Processing

Deterministic operations should remain deterministic when they reliably solve the problem.

---

## D-010 - Progressive Permission

Connectors must request the minimum access required for a capability.

Additional access requires explicit User authorization.

---

## D-011 - AI for Ambiguity

AI should primarily address ambiguity that cannot be adequately resolved through deterministic logic.

---

## D-012 - Preserve Source Provenance

Derived information must remain traceable to its source Observations and processing history.

---

## D-013 - Observation and Evidence Are Separate

```text
OBSERVATION != EVIDENCE
```

Source-derived information must remain distinct from semantic interpretation.

---

## D-014 - Evidence and Relationship Are Separate

```text
EVIDENCE != RELATIONSHIP
```

Relationship Assessment operates on aggregated Evidence.

---

## D-015 - Identifier and Service Are Separate

```text
IDENTIFIER != SERVICE
```

Technical identifiers must not automatically become canonical Services.

---

## D-016 - Core Discovery Degrades Gracefully

Failure or absence of optional capabilities, including AI, must not prevent deterministic Discovery from operating.

---

## D-017 - Multiple Connected Source Instances

A User may connect multiple independent source instances, including multiple instances using the same Provider and Connector implementation.

Each ConnectedSource has an independent lifecycle.

---

## D-018 - Connector Is a Data-Minimization Boundary

Connectors must minimize provider-specific information before exposing Observations to the common Discovery Core where technically practical.

Information unnecessary for the requested capability should not cross the Connector boundary.

---

## D-019 - Observation Types Are Provider-Neutral Where Possible

Equivalent source semantics from different providers should use the same Observation Type where their framework semantics are compatible.

Provider identity should not unnecessarily leak into downstream Discovery logic.

---

## D-020 - Entity Resolution and Evidence Classification Are Independent

Entity Resolution and Evidence Classification are parallel Discovery concerns.

Either may succeed while the other remains unresolved.

For example:

```text
Service:
UNRESOLVED

Evidence:
PAYMENT
```

is valid.

Likewise:

```text
Service:
Spotify

Evidence:
UNKNOWN
```

is valid.

---

## D-021 - Evidence Aggregates Are Derived State

Evidence Aggregates must remain reconstructable from authoritative Evidence where that Evidence is retained.

Aggregates must not become the sole source of Discovery provenance.

---

## D-022 - Relationship Support and Temporal Status Are Separate

Relationship support and temporal interpretation must be represented independently.

The initial model is:

```text
RelationshipStatus:
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

and:

```text
TemporalStatus:
UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

---

## D-023 - No Numerical Confidence in Initial Discovery Model

The initial Discovery Domain Model does not require numerical Confidence scores.

Explicit states, Evidence basis, provenance, temporal information, source diversity and reason codes should be evaluated before introducing calibrated Confidence.

---

# 44. Open Questions

The following questions remain intentionally unresolved.

## Identity

- How are newly observed identity identifiers suggested to the User?
- Must every new Identity Seed be explicitly confirmed?
- How are historical identities represented?
- How should aliases be represented?

## ConnectedSource

- What exact connection states are required?
- Should authorization state and connection state remain separate?
- Where should synchronization state live?
- How should local files and manual sources be represented?

## Connector

- How are Connector implementations registered?
- Which capabilities belong to the common vocabulary?
- How is secure credential storage implemented?
- How is synchronization state persisted?

## Observation

- Which Observation Types are required for the first implementation?
- Which payload schema mechanism should be used?
- Which Observations should be persisted?
- When may sensitive Observations remain ephemeral?
- Is `CollectionRun` required for synchronization and coverage tracking?

## Candidate Detection

- What initial reason-code taxonomy is required?
- Which reference data is necessary?
- When, if ever, should AI assist Candidate Detection?
- Will identifier extraction remain part of Candidate Detection?

## Entity Resolution

- What is the initial Service Registry?
- Who creates a new canonical Service?
- How are Service mappings updated?
- How are Service merge and split operations managed?
- Which external reference datasets, if any, are appropriate?
- When should AI assist Entity Resolution?

## Service

- What is the canonical Service granularity?
- How should `Google`, `Google Account` and `Gmail` be represented?
- How should product, Service, Brand and Organization eventually relate?
- How should historical rebranding be represented?

## Evidence

- What is the minimum initial Evidence taxonomy?
- Which Evidence Types are source-independent?
- Which source-specific types are justified?
- What are the exact EvidenceStatus transition rules?
- How should reclassification history be stored?
- How should User-corrected Evidence interact with automated Evidence?

## Aggregation

- What constitutes duplicate semantic Evidence?
- How should unresolved aggregation contexts be persisted?
- Which temporal conflict rules are useful?
- Should Evidence Aggregates be materialized or computed on demand?

## Relationship

- Are `UNKNOWN`, `OBSERVED`, `ESTABLISHED`, `REJECTED` sufficient?
- Are `UNKNOWN`, `CURRENTLY_OBSERVED`, `HISTORICAL` sufficient temporal states?
- Which Evidence combinations justify `ESTABLISHED`?
- How should Evidence independence be defined?
- How should User confirmation affect RelationshipStatus?

## Account

- Should Account become a first-class Domain Entity?
- How should multiple accounts with one Service be represented?
- How should shared accounts be represented?
- How should guest purchases be represented if Account is introduced?

## Organization

- When should Organization become a Domain Entity?
- How should legal data controllers relate to Services?
- Is Organization Resolution a separate capability?

## Coverage

- Should collection coverage become a formal domain or application concept?
- How should partial source coverage be exposed to Relationship Assessment?
- Should a `CollectionRun` model be introduced?

## Privacy

- Which Observations may be persisted?
- What are retention rules?
- How are external account identifiers protected?
- Which Observation Types may be sent to remote AI?
- How does deletion propagate through derived state?

## AI

- Which unresolved cases demonstrate measurable improvement from AI?
- Which tasks should remain entirely deterministic?
- How should local and remote AI policies be represented?
- How are AI model changes reflected in reprocessing provenance?

---

# 45. Validation Status

Draft v0.3 has been consolidated against:

```text
SCN-001
Gmail Service Discovery
```

and:

```text
SCN-002
Password Manager Service Discovery
```

as well as the first software-contract cycle:

```text
Connector Contract

Observation Contract

Service Candidate Detector Contract

Entity Resolver Contract

Evidence Classifier Contract

Evidence Aggregator Contract

Relationship Assessor Contract
```

The two scenarios demonstrated that the core Discovery architecture can represent structurally different sources.

The contract cycle further validated:

```text
ConnectedSource
provider independence
typed Observations
parallel Entity Resolution and Evidence Classification
explicit uncertainty states
cross-source Service convergence
Evidence aggregation
Relationship reassessment
deterministic-first processing
Progressive Permission
Source provenance
```

and exposed additional concepts now incorporated into Draft v0.3:

```text
EvidenceStatus
RelationshipStatus
TemporalStatus
Aggregate as derived state
Connector minimization boundary
```

---

# 46. Maturity Assessment

The following concepts are now considered sufficiently stable for implementation-oriented design:

```text
ConnectedSource

Connector boundary

Observation envelope

Typed Observation payloads

Service Candidate Detection

ServiceIdentifier

Entity Resolution states

Evidence Classification boundary

Evidence Aggregation boundary

Relationship Assessment boundary

Progressive Permission

Provider independence

Provenance

Local-first processing

UNKNOWN / UNRESOLVED / AMBIGUOUS states

RelationshipStatus / TemporalStatus separation
```

The following concepts remain intentionally provisional:

```text
Account

Organization

Service granularity

Service Registry lifecycle

Evidence taxonomy details

Evidence lifecycle transition rules

CollectionRun

Persistence model

Service Graph technology

Confidence

advanced AI usage
```

---

## 47. Path Toward Implementation

Draft v0.3 completes the first Identity and Service Discovery architecture-consolidation cycle.

The project progression has reached:

```text
Architecture v0.1
       |
       v
SCN-001 Gmail
       |
       v
Architecture v0.2
       |
       v
SCN-002 Password Manager
       |
       v
Domain Model v0.2
       |
       v
Software Contracts v0.1
       |
       v
Consistency Review
       |
       v
Architecture v0.3
       |
       v
Domain Model v0.3
       |
       v
Contract Alignment
       |
       v
README Alignment
       |
       v
IMPLEMENTATION MODEL
       |
       v
Gmail Vertical MVP
       |
       v
Empirical Validation
       |
       v
Architecture Refinement
```

The following Discovery design activities are now complete:

```text
Architecture consolidation
        ✓

Domain Model consolidation
        ✓

Software Contract alignment
        ✓

Repository entry-point alignment
        ✓
```

The seven Discovery contracts are aligned with the consolidated Architecture and Domain Model:

```text
01 Connector Contract

02 Observation Contract

03 Service Candidate Detector Contract

04 Entity Resolver Contract

05 Evidence Classifier Contract

06 Evidence Aggregator Contract

07 Relationship Assessor Contract
```

No additional Discovery processing contract is currently required.

The next design phase is the:

```text
IMPLEMENTATION MODEL
```

Its purpose is to translate the consolidated conceptual architecture into concrete, implementable software boundaries without changing the Domain responsibilities established by this architecture.

The Implementation Model should define, at minimum:

```text
package structure

dependency direction

Domain entities

Domain value objects

Enums and controlled vocabularies

Python Protocols or abstract interfaces

typed Observation payloads

Processing Result objects

repository interfaces

ServiceRegistry interface

Evidence lifecycle implementation

assessment-policy boundaries

application orchestration

persistence boundaries

configuration and rule loading

testing boundaries
```

The Implementation Model must preserve the architectural distinctions already established, including:

```text
ConnectedSource != Connector

Observation != Evidence

CandidateIdentifier != ServiceIdentifier != Service

Normalization != Resolution

Evidence != Relationship

EvidenceAggregate != Authoritative Evidence

RelationshipStatus != TemporalStatus

Processing Result != Core Domain Entity
```

It must also preserve the dependency direction that keeps Provider-specific infrastructure outside the common Discovery Domain.

Conceptually:

```text
Provider Infrastructure
        |
        v
Connector / Infrastructure Adapters
        |
        v
Application Orchestration
        |
        v
Discovery Interfaces and Domain Model
```

The Implementation Model must not collapse the architecture into Provider-specific application logic.

After the Implementation Model is defined, the first executable vertical slice should be:

```text
Gmail Vertical MVP
```

Conceptually:

```text
Gmail
  |
  v
GmailConnector
  |
  v
EMAIL_MESSAGE_METADATA Observation
  |
  +-------------------------+
  |                         |
  v                         v
Candidate Detection    Evidence Classification
  |                         |
  v                         v
ServiceIdentifier          Evidence
  |                         |
  v                         |
EntityResolver              |
  |                         |
  v                         |
Service --------------------+
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
Relationship
            |
            v
MVP Service Graph / Output
```

The Gmail Vertical MVP should validate the implementation against real source-derived behavior while preserving:

```text
metadata-first collection

Progressive Permission

Provider isolation

Connector minimization

explicit provenance

deterministic-first processing

UNKNOWN / UNRESOLVED / AMBIGUOUS states

EvidenceStatus lifecycle

RelationshipStatus / TemporalStatus separation

no numerical Confidence

local-first processing where practical

explainability
```

Architecture changes after this point should primarily be driven by implementation evidence, empirical validation or genuinely new cross-source requirements.

New abstractions should not be introduced in advance merely because they appear potentially useful.Draft v0.3.

In particular, Domain Model v0.3 should incorporate:

```text
Relationship
    |
    +-- User reference
    +-- Service reference
    +-- RelationshipStatus
    +-- TemporalStatus
    +-- Identity references
    +-- Evidence basis
    +-- Assessment provenance
```

and:

```text
Evidence
    |
    +-- EvidenceStatus
         |
         +-- ACTIVE
         +-- SUPERSEDED
         +-- REJECTED
```

Once these concepts are reflected consistently in the Domain Model, the seven existing software contracts should receive only the terminology and dependency alignment necessary to match the consolidated architecture.

No new processing component should be introduced unless implementation design or new empirical scenarios demonstrate that it is required.
