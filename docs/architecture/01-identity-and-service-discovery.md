# Identity & Service Discovery

**Status:** Draft v0.2  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  

---

## 1. Purpose

The first problem addressed by the framework is:

> Given one or more digital identities provided by a user, which services and organizations may hold, or may have held, personal data related to that user?

The objective of this module is not to determine exactly what personal data each organization currently holds.

Its objective is to discover, normalize and document evidence of digital relationships between the user and external services.

The framework builds an observed representation of the user's digital relationships rather than claiming to reconstruct an objective and complete digital footprint.

The discovery process is based on the following conceptual model:

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

The output of this process becomes the starting point for subsequent modules that may:

- determine how personal data can be obtained from identified services;
- request or retrieve that data;
- ingest and normalize returned information;
- classify personal data;
- construct a Personal Data Graph;
- monitor changes;
- help the user exercise available controls over personal information.

This document focuses exclusively on **Identity and Service Discovery**.

---

## 2. Design Principles

### 2.1 Evidence Before Inference

The framework must distinguish between:

- what has been directly observed;
- what has been interpreted from an observation;
- what has been inferred from multiple pieces of evidence;
- what has been confirmed;
- what remains unknown.

For example, detecting an account-verification email associated with a service may provide significant evidence that a relationship existed.

It does not prove:

- that the relationship still exists;
- that an account is currently active;
- what personal data the service currently holds;
- that the evidence has been interpreted correctly.

The framework must therefore preserve the evidence behind every conclusion.

---

### 2.2 Unknown Is a Valid State

The framework must not invent information to fill knowledge gaps.

Unknown, unresolved and ambiguous states are valid outcomes.

For example:

```text
Observed Domain: example.com
Resolved Service: UNKNOWN
```

or:

```text
Observation:
"Important information about your account"

Evidence Type:
UNKNOWN
```

or:

```text
Service: Spotify
Relationship: DISCOVERED
Personal Data Held: UNKNOWN
```

Absence of information must not be confused with absence of data.

The framework should prefer uncertainty over fabricated certainty.

---

### 2.3 Multiple Independent Discovery Sources

No single Discovery Source should be considered sufficient to reconstruct a person's complete digital footprint.

The architecture must support multiple independent discovery mechanisms.

Examples may include:

```text
Email
Password Manager
Browser
Identity Provider
Manual Input
Other Authorized Sources
```

These sources may provide different types and strengths of evidence.

The same Service may eventually be supported by evidence originating from multiple independent sources.

---

### 2.4 Explainability

Every discovered Relationship should be traceable to the evidence supporting it.

The user should be able to ask:

> Why do you think I have or had a relationship with this Service?

The framework should be able to explain:

- which observations were collected;
- how those observations were interpreted;
- how identifiers were resolved;
- what evidence was produced;
- how the accumulated evidence contributed to the Relationship Assessment.

Explainability should not require exposing more raw personal information than necessary.

---

### 2.5 Local-First and Privacy by Design

A framework intended to improve personal privacy must not unnecessarily become another centralized repository containing highly sensitive information about the user.

Whenever technically practical:

- raw personal data should be processed locally;
- only the minimum required information should be persisted;
- external transmission should require an explicit purpose;
- credentials and authorization tokens should be isolated from discovered information;
- external AI providers should not automatically receive raw personal data;
- derived information should be preferred over unnecessary persistence of raw source data.

Conceptually:

```text
Raw Source Data
      |
      v
Local Processing
      |
      v
Observations / Evidence
      |
      v
Minimum Necessary Persistence
```

---

### 2.6 Progressive Permission

Access to a Discovery Source must be capability-driven.

Connecting a source must not automatically imply authorization to retrieve every category of information available from that source.

The framework should request the minimum level of access required for the requested capability.

If existing permissions are insufficient:

1. the framework identifies the additional information required;
2. explains why that information is required;
3. requests the minimum additional permission;
4. continues only if the user explicitly authorizes the operation.

Conceptually:

```text
Minimum Permission
        |
        v
Attempt Capability
        |
   +----+----+
   |         |
Enough    Insufficient
   |         |
   v         v
Continue   Explain Need
             |
             v
       Request Additional
          Permission
          /      \
       allow     deny
         |         |
         v         v
      Continue   Remain
                Unresolved
```

Permission escalation must never occur silently.

---

### 2.7 Preserve Provenance

Normalization and interpretation must not destroy the relationship between derived information and its source.

The framework should preserve sufficient provenance to determine:

```text
Source
  |
  v
Observation
  |
  v
Interpretation
  |
  v
Evidence
  |
  v
Relationship
```

This is required for:

- explainability;
- auditing;
- debugging;
- user correction;
- reclassification;
- entity re-resolution;
- future improvements to discovery logic.

---

### 2.8 Deterministic Processing Before AI

AI should not replace deterministic software unnecessarily.

Operations that can be performed reliably through explicit deterministic logic should remain deterministic.

AI should primarily be considered for ambiguity, semantic interpretation and other cases where deterministic approaches are insufficient or excessively brittle.

The general strategy is:

```text
Input
  |
  v
Deterministic Processing
  |
  +----------------+
  |                |
resolved        ambiguous
  |                |
  |                v
  |          AI when appropriate
  |                |
  +-------+--------+
          |
          v
        Result
```

AI should therefore be an optional capability rather than a foundational dependency of Service Discovery.

---

## 3. Identity Seed

An Identity Seed is an identifier or digital account declared by the user as belonging to them and used as a starting point for discovery.

Possible Identity Seeds include:

- email addresses;
- phone numbers;
- usernames;
- Google accounts;
- Apple accounts;
- Microsoft accounts;
- other supported digital identities.

Conceptually:

```json
{
  "id": "identity_001",
  "type": "email",
  "value": "user@example.com",
  "verified": true
}
```

A single person may provide multiple Identity Seeds.

For example:

```text
User
 |
 +-- personal@gmail.com
 |
 +-- work@example.com
 |
 +-- oldmail@example.net
 |
 +-- +39XXXXXXXXXX
 |
 +-- username123
```

These identities may represent different portions of the same person's digital history.

---

### 3.1 Identity Seeds Are Starting Points

An Identity Seed is not necessarily information that should automatically be searched publicly on the Internet.

Its primary purpose is to provide a starting point from which explicitly authorized discovery processes may begin.

For example, a user may authorize a Connector to inspect an email account associated with one of their Identity Seeds.

The framework may then use information available through that authorized source to discover possible relationships with external Services.

---

## 4. Discovery Source

A Discovery Source is a source from which the framework may obtain information relevant to discovering relationships between the user and external Services.

Examples include:

```text
Email Provider
Identity Provider
Password Manager
Browser
Manual Input
Other Authorized Source
```

Different Discovery Sources may provide different categories and strengths of information.

A Discovery Source is conceptually distinct from the software component used to communicate with it.

```text
Discovery Source
       |
       v
    Connector
       |
       v
  Observations
```

---

### 4.1 Email

Potential providers include:

- Gmail;
- Outlook;
- other supported email providers.

Email may contain observations associated with:

- account creation;
- account verification;
- authentication;
- password resets;
- security notifications;
- purchases;
- invoices;
- subscriptions;
- payments;
- newsletters;
- privacy notifications;
- account changes;
- account deletion.

Receiving an email must not automatically be interpreted as proof of an active account.

Email is one Discovery Source among several and must not define the core architecture of the framework.

---

### 4.2 Identity Providers

Identity providers may expose relationships created through mechanisms such as:

- Sign in with Google;
- Sign in with Apple;
- Microsoft identity;
- OAuth;
- OpenID Connect;
- other supported authentication relationships.

An authorized application relationship may provide evidence that the user established some form of relationship with an external Service.

---

### 4.3 Password Managers

A password manager may provide evidence that an account exists or existed for a particular Service.

For example:

```text
Domain:
netflix.com

Username:
personal@gmail.com
```

may constitute relatively significant evidence of a relationship with Netflix.

Access to password-manager information must require explicit user authorization.

The framework should not retrieve, import or persist actual passwords unless a future capability can demonstrate that doing so is strictly necessary.

Service Discovery primarily requires evidence of the relationship, not the user's credentials.

---

### 4.4 Browser Data

A browser may provide relevant observations through signals such as:

- browsing history;
- frequently visited domains;
- bookmarks;
- login-related information;
- locally stored site information;
- other supported browser signals.

However:

```text
Website Visit != Account Relationship
```

Browser observations alone may therefore indicate interaction without proving the existence of an account.

---

### 4.5 Manual User Input

The user must be able to manually declare relationships that automated discovery mechanisms cannot reconstruct.

Example:

```text
"I had an account on example.com using another email address in 2018."
```

Manual input is necessary because no automated discovery mechanism can guarantee complete reconstruction of a person's digital history.

Manual information should still retain provenance indicating that it was user-provided.

---

### 4.6 Future Discovery Sources

The architecture must allow additional Discovery Sources to be introduced without redesigning the core discovery pipeline.

For example:

```text
                   Connector Interface
                          |
          +---------------+---------------+
          |               |               |
          v               v               v
      Email           Browser       Password Manager
     Connector       Connector          Connector
          |               |               |
          +---------------+---------------+
                          |
                          v
                    Observations
```

Source-specific implementation details should remain inside the corresponding Connector whenever reasonably possible.

---

## 5. Connector

A Connector is a source-specific component responsible for communicating with a Discovery Source.

Its responsibilities may include:

- authorization;
- source API interaction;
- data retrieval;
- pagination;
- synchronization;
- source-specific error handling;
- translating source-specific information into framework Observations.

Conceptually:

```text
External Source
       |
       v
    Connector
       |
       v
  Observations
```

The Connector forms a boundary between external systems and the framework's core domain logic.

Downstream components should avoid depending directly on source-specific objects or APIs whenever reasonably possible.

For example:

```text
Gmail API Objects
       |
       v
 GmailConnector
       |
       v
Framework Observations
```

rather than:

```text
Gmail API Objects
       |
       +-----------------------------+
       |              |              |
       v              v              v
Entity Resolver   Classifier   Relationship Engine
```

The first design allows source-specific behavior to remain isolated.

---

### 5.1 Connector Authorization

A Connector must not assume that source connectivity implies unrestricted access.

Each capability should identify the minimum information it requires.

The Connector should request only the authorization required to obtain that information.

Authorization state and derived domain information must remain conceptually separate.

For example:

```text
Revoke Source Access
```

is not necessarily equivalent to:

```text
Delete Existing Observations
Delete Evidence
Delete Relationships
```

Lifecycle rules for derived information must be defined separately.

---

### 5.2 Connector Failure

Failure of an external source must not corrupt previously valid domain information.

Possible failures include:

- authorization expiration;
- permission denial;
- network failure;
- API unavailability;
- rate limiting;
- interrupted synchronization;
- malformed or unexpected source responses.

The framework must distinguish between:

```text
No information found
```

and:

```text
Source could not be completely analyzed
```

Incomplete discovery must not be presented as complete discovery.

---

## 6. Observation

An Observation represents information obtained from a Discovery Source before the framework assigns semantic meaning to it.

For example:

```text
Source:
Email

Sender:
no-reply@example.com

Subject:
Verify your email address

Observed At:
2026-01-01
```

is an Observation.

The interpretation:

```text
ACCOUNT_VERIFICATION
```

is Evidence.

Therefore:

```text
OBSERVATION != EVIDENCE
```

This distinction is fundamental.

Observations preserve what was detected.

Evidence represents what the framework currently believes that Observation means.

Separating the two allows future logic to:

- reclassify observations;
- improve deterministic rules;
- change AI models;
- correct mistakes;
- retry Entity Resolution;
- preserve historical source provenance.

---

### 6.1 Observation Provenance

An Observation should preserve sufficient information to identify:

- the originating Discovery Source;
- the Connector that produced it, where relevant;
- the Identity Seed involved, where applicable;
- when it was observed;
- useful source identifiers;
- relevant extracted attributes;
- collection or synchronization context.

The exact persistent schema remains an implementation decision.

---

## 7. Service Candidate Detection

Not every Observation indicates a relationship with a digital Service.

For example, an email source may contain:

- personal correspondence;
- generic email-provider addresses;
- mailing infrastructure;
- communication from individual employees;
- automated notifications;
- service-related communication.

Similarly, a browser source may contain websites the user visited only once without creating an account.

Service Candidate Detection determines whether an Observation should enter the Service Discovery pipeline.

Conceptually:

```text
Observation
     |
     v
Candidate Detection
    / \
   /   \
 yes    no
  |      |
  v      v
Entity   Not used for this
Resolution capability
```

An Observation ignored for Service Discovery may still be useful to another capability.

Candidate Detection therefore answers:

> Is this Observation relevant to the current Service Discovery capability?

It does not answer:

> Is this Observation globally useful?

---

## 8. Service

A Service represents a normalized digital service or product with which the user may have or have had a relationship.

Different technical identifiers may refer to the same Service.

For example:

```text
spotify.com
accounts.spotify.com
open.spotify.com
no-reply@spotify.com
        |
        v
     Spotify
```

The framework must distinguish between:

```text
Technical Identifier
```

and:

```text
Service Identity
```

Therefore:

```text
DOMAIN != SERVICE
```

More generally, Service identity and Organization identity must not automatically be treated as equivalent.

A company may operate multiple Services.

A Service may:

- use multiple domains;
- operate under multiple brands;
- change domains;
- change ownership;
- be renamed;
- use third-party infrastructure.

The exact model connecting Services, Brands, Organizations and legal data controllers remains to be defined.

---

## 9. Entity Resolution

Entity Resolution determines whether one or more observed identifiers correspond to the same underlying Service.

Conceptually:

```text
Observed Identifiers
        |
        +-- spotify.com
        |
        +-- accounts.spotify.com
        |
        +-- no-reply@spotify.com
        |
        v
Entity Resolution
        |
        v
     Spotify
```

Possible resolution signals may include:

- domains;
- hostnames;
- email addresses;
- URLs;
- display names;
- known service aliases;
- source-specific identifiers;
- previously resolved entities;
- other supporting information.

The exact resolution mechanism is intentionally not defined at this stage.

---

### 9.1 Resolution Provenance

Entity Resolution must preserve the relationship between:

```text
Observed Identifier
       |
       v
Normalized Identifier
       |
       v
Resolved Service
```

A resolved Service must not destructively replace the original Observation.

This allows the framework to support:

- explainability;
- re-resolution;
- user correction;
- improved normalization;
- evolving service mappings;
- debugging.

---

### 9.2 Unresolved Entities

Entity Resolution must be allowed to fail safely.

For example:

```json
{
  "observed_identifier": "example-service.net",
  "resolved_service": null,
  "resolution_status": "UNRESOLVED"
}
```

An unresolved identity is preferable to an incorrect confident association.

---

### 9.3 Shared Infrastructure

Technical infrastructure does not always identify the Service with which the user has a relationship.

Services may use third parties for:

- email delivery;
- authentication;
- cloud hosting;
- customer support;
- analytics;
- payment processing;
- marketing.

Entity Resolution must therefore avoid automatically converting infrastructure providers into user relationships without sufficient supporting evidence.

---

## 10. Evidence

Evidence represents the framework's semantic interpretation of an Observation in the context of Service Discovery.

Conceptually:

```text
Observation
     |
     v
Evidence Classification
     |
     v
Evidence
```

For example:

```text
Observation:

Subject:
"Verify your email address"
```

may produce:

```text
Evidence:

Type:
ACCOUNT_VERIFICATION
```

The precise Evidence Taxonomy may vary as additional discovery scenarios are tested.

The architecture requires that Evidence:

- has a semantic type;
- references its supporting Observation or Observations;
- retains provenance;
- may remain UNKNOWN;
- can be aggregated with other Evidence;
- can contribute to Relationship Assessment.

---

### 10.1 Evidence Is Not Fact

Evidence may be misleading or incomplete.

Depending on the Discovery Source, an Observation may represent:

- an old account;
- a deleted account;
- marketing communication;
- phishing;
- forwarded information;
- a guest purchase;
- activity by another person;
- an incorrectly entered identity;
- shared infrastructure;
- technical noise.

Therefore:

```text
EVIDENCE != CONFIRMED RELATIONSHIP
```

and:

```text
RELATIONSHIP != CURRENT DATA POSSESSION
```

These distinctions are fundamental.

---

### 10.2 Evidence Provenance

Evidence should preserve sufficient information to determine:

```text
Evidence
 |
 +-- Supporting Observation
 |
 +-- Discovery Source
 |
 +-- Evidence Type
 |
 +-- Classification Method
 |
 +-- Relevant Identity
 |
 +-- Relevant Service
 |
 +-- Temporal Information
```

The exact schema remains to be defined.

---

## 11. Evidence Classification

The Evidence Classifier interprets Observations and assigns semantic Evidence categories.

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

The classifier may use different strategies.

The initial architectural model is:

```text
                Observation
                     |
                     v
            Deterministic Rules
                     |
               +-----+-----+
               |           |
           resolved     ambiguous
               |           |
               |           v
               |      AI Classifier
               |      when appropriate
               |           |
               +-----+-----+
                     |
                     v
                  Evidence
```

---

### 11.1 Deterministic Classification

Clear and stable patterns should be processed deterministically whenever practical.

Advantages include:

- predictable behavior;
- explainability;
- reproducibility;
- testability;
- lower computational cost;
- reduced privacy exposure;
- independence from external AI systems.

Classification provenance should indicate that deterministic processing produced the result.

---

### 11.2 AI-Assisted Classification

AI may be introduced when deterministic processing cannot sufficiently resolve semantic ambiguity.

Potential uses may include:

- ambiguous natural-language observations;
- multilingual interpretation;
- complex semantic classification;
- heterogeneous source formats;
- cases where deterministic rules would become excessively brittle.

AI should receive only the minimum information necessary for the specific task.

AI-derived results must remain identifiable as such.

---

### 11.3 Classification Failure

Evidence Classification must not force a classification.

If available information is insufficient:

```text
Evidence Type:
UNKNOWN
```

is a valid result.

The original Observation must remain available.

---

## 12. Evidence Aggregation

Individual Evidence items should not automatically create independent Relationships.

For example:

```text
100 observations concerning one Service
```

must not produce:

```text
100 independent Service Relationships
```

Instead:

```text
Observations
     |
     v
Evidence
     |
     v
Evidence Aggregation
     |
     v
Service-Level Evidence
```

Aggregation may consider:

- Evidence type;
- Evidence frequency;
- temporal information;
- source diversity;
- provenance;
- duplicate detection;
- conflicting Evidence.

Frequency alone must not determine relationship strength.

For example:

```text
1 strong account-related Evidence item
```

may communicate different information from:

```text
100 generic marketing Evidence items
```

The framework must preserve enough information for Relationship Assessment without prematurely assigning arbitrary weights.

---

## 13. Relationship

A Relationship represents the framework's current assessment that a particular Identity or user is or was associated with a Service.

Relationship Assessment occurs after Evidence has been classified and aggregated.

Therefore:

```text
EVIDENCE != RELATIONSHIP
```

The conceptual process is:

```text
Evidence A
Evidence B
Evidence C
    |
    v
Evidence Aggregation
    |
    v
Relationship Assessment
    |
    v
Relationship
```

Potential relationship concepts may eventually include:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
REJECTED
```

These states remain provisional.

Their exact semantics should be defined only after additional scenarios and empirical testing.

---

### 13.1 Relationship Assessment

Relationship Assessment answers:

> What does the accumulated evidence suggest about the user's relationship with this Service?

This is distinct from Evidence Classification, which answers:

> What does this individual Observation mean?

For example:

```text
Evidence:

ACCOUNT_VERIFICATION
PASSWORD_RESET
SUBSCRIPTION
PAYMENT
```

may support a different assessment from:

```text
Evidence:

MARKETING
NEWSLETTER
```

The framework should analyze evidence collectively rather than treating all Evidence items as semantically equivalent.

---

### 13.2 Historical Relationships

A Service may remain relevant even after the user's apparent active relationship has ended.

For example:

```text
Account Creation
      |
      v
Account Activity
      |
      v
Account Deletion
```

still represents a historical digital relationship.

Historical Relationships matter because:

- data may remain subject to retention obligations;
- previous transactions may still exist;
- deletion evidence does not independently prove that all personal data has been erased;
- historical relationships remain part of the user's observable digital footprint.

Therefore:

```text
Current Relationship
```

and:

```text
Historical Relationship
```

must remain distinguishable concepts.

---

### 13.3 Temporal Information

Relationship interpretation requires temporal context.

For example:

```text
2021 Account Creation
2022 Purchase
2023 Payment
2024 Account Deletion
```

is different from:

```text
2021 Account Creation
2022 Purchase
2025 Authentication
2026 Security Notification
```

The architecture should therefore preserve enough temporal information to eventually support concepts such as:

```text
First Observed
Last Observed
Evidence Timeline
Historical State
```

The final temporal model remains to be defined.

---

## 14. Multiple Evidence Sources

Different Discovery Sources may independently provide Evidence related to the same Service.

For example:

```text
                         +-- Email
                         |
User -------- Spotify --+-- Password Manager
                         |
                         +-- Identity Provider
```

Multiple independent sources may strengthen the basis for believing that a Relationship exists or existed.

However:

```text
Multiple Sources != Proof of Current Data Possession
```

Source diversity should therefore contribute to Relationship Assessment without being interpreted as evidence about exactly what personal data a Service currently holds.

---

## 15. Confidence

Relationships may eventually carry a confidence assessment.

Potential representations could include qualitative states such as:

```text
HIGH
MEDIUM
LOW
```

or a numerical model.

However, the exact Confidence model remains intentionally undefined.

Arbitrary formulas such as:

```text
registration evidence = +0.4
password manager evidence = +0.5
browser evidence = +0.1
```

would create false mathematical precision.

Any Confidence model should be developed only after:

- a stable Evidence taxonomy exists;
- multiple real discovery scenarios have been tested;
- false positives have been measured;
- false negatives have been analyzed;
- Evidence reliability has been evaluated;
- combinations of independent sources have been tested;
- the meaning and calibration of Confidence have been defined.

A Confidence value must ultimately be explainable.

Until then, the architecture should preserve the information necessary to introduce Confidence later without requiring it now.

---

## 16. Discovery Engine

The Discovery Engine coordinates the Identity and Service Discovery process.

Given:

- one or more Identity Seeds;
- one or more authorized Discovery Sources;

the Discovery Engine produces structured information describing Services with which the user may have or may have had Relationships.

---

### 16.1 Responsibilities

The Discovery Engine coordinates:

```text
Identity Seeds
      |
      v
Connectors
      |
      v
Observations
      |
      v
Candidate Detection
      |
      v
Entity Resolution
      |
      v
Evidence Classification
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

Individual components should remain separable enough to allow their strategies and implementations to evolve independently.

---

### 16.2 The Discovery Engine Must Not

The Discovery Engine must not:

- assume what personal data an organization currently holds;
- automatically send privacy requests;
- automatically delete accounts;
- modify external user data;
- claim that discovery is complete;
- hide uncertainty;
- silently escalate source permissions;
- silently perform consequential external actions.

These responsibilities belong to other components of the broader framework.

---

### 16.3 High-Level Architecture

```text
                         USER
                           |
                           v
                   Identity Manager
                           |
                           v
                 Discovery Sources
                           |
           +---------------+---------------+
           |               |               |
           v               v               v
       Connector       Connector       Connector
           |               |               |
           +---------------+---------------+
                           |
                           v
                      Observations
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

This architecture is intended to remain independent of any specific Discovery Source.

---

## 17. Service Graph

The output of Identity and Service Discovery contributes to an observed graph of Services and Relationships associated with the user.

Conceptually:

```text
                   Evidence
                      |
                      v
              +---------------+
              |               |
              v               v
           Netflix           Spotify
              ^               ^
              |               |
          Relationship     Relationship
              ^               ^
              |               |
              +------ User ----+
```

Supporting Observations and Evidence may originate from multiple Discovery Sources.

The Service Graph should ultimately answer questions such as:

> Which Services appear to have or have had a relationship with me?

and:

> Why was this Service discovered?

The Service Graph does not claim to describe what personal data each Service currently possesses.

---

### 17.1 Service Graph and Personal Data Graph

The framework distinguishes between:

#### Service Graph

Answers:

> Which Services appear connected to me?

#### Personal Data Graph

Will eventually answer:

> Which personal data does each Service actually appear to hold about me?

The Service Graph provides a foundation for later Personal Data Acquisition and Personal Data Understanding capabilities.

---

## 18. Expected Output

After discovery, the framework should eventually be capable of representing information such as:

```text
User
 |
 +-- Service A
 |     |
 |     +-- Observed Identifiers
 |     |
 |     +-- Supporting Evidence
 |     |
 |     +-- First Observed
 |     |
 |     +-- Last Observed
 |     |
 |     +-- Relationship Assessment
 |     |
 |     +-- Personal Data Held: UNKNOWN
 |
 +-- Service B
       |
       +-- Observed Identifiers
       |
       +-- Supporting Evidence
       |
       +-- Relationship Assessment
       |
       +-- Personal Data Held: UNKNOWN
```

The exact persistent representation is intentionally undefined at this stage.

The important requirement is traceability:

```text
Source
   |
   v
Observation
   |
   v
Evidence
   |
   v
Aggregated Evidence
   |
   v
Relationship Assessment
   |
   v
Service
```

The output represents an **Observed Digital Relationship Graph**.

It does not represent a complete map of the user's personal data.

---

## 19. Privacy and Security Requirements

Identity and Service Discovery may process exceptionally sensitive information, including:

- email metadata;
- potentially email content;
- account relationships;
- browsing information;
- authentication relationships;
- personal identifiers;
- password-manager metadata;
- historical digital activity.

This creates a fundamental architectural constraint:

> A privacy framework must not solve one privacy problem by creating a larger centralized privacy problem.

---

### 19.1 Data Minimization

Only information necessary for a requested capability should be collected.

The existence of technical access to information does not independently justify collecting it.

---

### 19.2 Least Privilege

Connectors should request the narrowest permissions capable of supporting the requested capability.

Broad authorization should not be requested merely to simplify implementation or support hypothetical future capabilities.

---

### 19.3 Progressive Permission

If lower-privilege information is insufficient, additional access should be requested only when:

1. a specific capability requires it;
2. the required information can be explained;
3. the requested access is limited to what is necessary;
4. the user explicitly authorizes the operation.

---

### 19.4 Local-First Processing

Where technically practical:

```text
Raw Source Data
       |
       v
 Local Processing
       |
       v
Structured Observation
       |
       v
Structured Evidence
       |
       v
Minimum Necessary Persistence
```

Raw mailbox contents, complete browser histories, credentials or exported datasets should not be transmitted to external infrastructure by default.

---

### 19.5 External Processing

If information must leave the local environment, the architecture should make clear:

```text
What data leaves the environment
Why it is required
Where it is sent
How it is processed
What authorization permits it
```

External processing must be deliberate rather than implicit.

---

### 19.6 AI Implications

The same principles apply to AI-assisted processing.

The framework must not assume that raw personal information can be sent to an external AI provider.

The AI layer should eventually support interchangeable strategies such as:

```text
Deterministic Rules
Local Model
Self-Hosted Model
Remote Model
User-Provided Provider
```

The framework should remain independent of a single AI provider.

Privacy requirements may determine which AI strategy can be used for a specific operation.

---

### 19.7 Credential Isolation

Authorization credentials and access tokens must remain isolated from discovery information wherever reasonably possible.

Evidence Stores or Service Graph components should not require direct access to source credentials merely to interpret previously collected information.

---

### 19.8 Revocation and Data Lifecycle

Source authorization and derived information lifecycle are related but distinct concerns.

For example:

```text
Revoke Connector Authorization
Delete Connector Credentials
Delete Cached Source Data
Delete Observations
Delete Evidence
Delete Relationships
```

are not necessarily the same operation.

The exact lifecycle and deletion semantics remain to be defined by the broader privacy and security architecture.

---

## 20. AI Architecture within Discovery

AI may provide value to specific components of the Discovery Engine.

Potential applications include:

- Evidence Classification;
- Entity Resolution;
- ambiguous natural-language interpretation;
- heterogeneous data extraction;
- multilingual interpretation;
- reasoning across conflicting Evidence.

However, AI is not the Discovery Engine itself.

The architecture should therefore resemble:

```text
Discovery Component
        |
        +-- Deterministic Strategy
        |
        +-- AI-Assisted Strategy
        |
        +-- UNKNOWN / unresolved fallback
```

rather than:

```text
All Source Data
      |
      v
     LLM
      |
      v
Final Answer
```

The latter approach would reduce:

- explainability;
- determinism;
- privacy control;
- testability;
- graceful degradation.

---

### 20.1 AI for Ambiguity

The preferred pattern is:

```text
Deterministic Logic
        |
   +----+----+
   |         |
resolved   ambiguous
   |         |
   |         v
   |       AI
   |         |
   +----+----+
        |
        v
      Result
```

This principle should evolve based on empirical measurements rather than assumptions.

If testing demonstrates that AI provides measurable value in other areas, the architecture may evolve accordingly.

---

### 20.2 Graceful Degradation

Core Service Discovery must not require AI availability.

If an AI capability is:

- disabled;
- unavailable;
- unsupported;
- rejected by the user;
- incompatible with privacy requirements;

the deterministic pipeline should continue operating.

Unresolved information may remain:

```text
UNKNOWN
```

rather than preventing the whole pipeline from operating.

---

## 21. Non-Goals

### 21.1 Complete Discovery

The framework cannot guarantee discovery of every organization holding data about the user.

Therefore:

```text
Observed Footprint != Complete Footprint
```

Discovery coverage is inherently incomplete.

---

### 21.2 Current Data Possession

Historical evidence of a Relationship does not prove that a Service currently stores personal data.

For example:

```text
Account verification evidence from 2018
```

may support the conclusion that a relationship existed in 2018.

It does not establish what information the Service stores today.

---

### 21.3 Perfect Accuracy

Discovery may produce:

- false positives;
- false negatives;
- unresolved entities;
- ambiguous Evidence;
- conflicting Evidence;
- incorrect classifications.

The system must explicitly support uncertainty and correction.

---

### 21.4 Public Internet Discovery

Searching the public Internet for occurrences of:

- phone numbers;
- email addresses;
- names;
- usernames;
- leaked information;
- public profiles;

represents a different technical problem.

It should not be silently mixed with authorized Service Discovery.

---

### 21.5 Personal Data Acquisition

This document does not define how personal data should be requested or retrieved from identified Services.

Conceptually:

```text
Service Discovered
       |
       v
How Can I Obtain My Data?
       |
       +-- API
       |
       +-- Data Export
       |
       +-- Privacy Portal
       |
       +-- Access Request
       |
       +-- Other Mechanism
```

This belongs to a subsequent framework capability.

---

### 21.6 Final Confidence Model

This document does not define a final Confidence algorithm.

Confidence must be derived from empirical evidence rather than arbitrary weighting.

---

### 21.7 Final Persistent Schema

Examples in this document are conceptual.

They must not be interpreted as the final:

- database schema;
- object model;
- API schema;
- graph representation;
- class hierarchy.

These should be defined after additional architecture validation.

---

## 22. Architectural Boundaries

The current architecture establishes the following fundamental distinctions.

### 22.1 Source Is Not Connector

```text
SOURCE != CONNECTOR
```

A Source is the external system or information source.

A Connector is the component that communicates with it.

---

### 22.2 Source Is Not Observation

```text
SOURCE != OBSERVATION
```

A Source contains or exposes information.

An Observation represents specific information obtained from that Source.

---

### 22.3 Observation Is Not Evidence

```text
OBSERVATION != EVIDENCE
```

An Observation represents what was detected.

Evidence represents the framework's interpretation of that Observation.

---

### 22.4 Evidence Is Not Relationship

```text
EVIDENCE != RELATIONSHIP
```

Evidence represents supporting information.

A Relationship is assessed from one or more Evidence items.

---

### 22.5 Domain Is Not Service

```text
DOMAIN != SERVICE
```

A technical identifier such as a domain may contribute to identifying a Service, but it must not automatically be treated as the Service itself.

---

### 22.6 Service Is Not Organization

```text
SERVICE != ORGANIZATION
```

A Service may belong to an Organization.

An Organization may operate multiple Services.

The exact model connecting them remains unresolved.

---

### 22.7 Relationship Is Not Current Data Possession

```text
RELATIONSHIP != CURRENT DATA POSSESSION
```

Evidence that a relationship exists or existed does not establish which personal information a Service currently stores.

---

## 23. Conceptual End-to-End Flow

The broader project vision remains:

```text
USER
 |
 v
IDENTITY SEEDS
 |
 v
DISCOVERY
 |
 v
SERVICE GRAPH
 |
 v
DATA ACQUISITION
 |
 v
DATA INGESTION
 |
 v
PERSONAL DATA UNDERSTANDING
 |
 v
PERSONAL DATA GRAPH
 |
 v
MONITORING
 |
 v
GOVERNANCE ACTIONS
```

This document currently defines the Discovery portion in greater detail:

```text
IDENTITY SEEDS
      |
      v
DISCOVERY SOURCES
      |
      v
CONNECTORS
      |
      v
OBSERVATIONS
      |
      v
SERVICE CANDIDATE DETECTION
      |
      v
ENTITY RESOLUTION
      |
      v
EVIDENCE CLASSIFICATION
      |
      v
EVIDENCE
      |
      v
EVIDENCE AGGREGATION
      |
      v
RELATIONSHIP ASSESSMENT
      |
      v
SERVICE GRAPH
```

The remaining framework components will be designed separately.

---

## 24. Failure Model

The Discovery architecture should assume that components can fail independently.

Examples include:

```text
Connector Failure
Observation Collection Failure
Candidate Detection Failure
Entity Resolution Failure
Classification Failure
AI Unavailability
Partial Source Analysis
Conflicting Evidence
```

Failure should degrade gracefully whenever possible.

For example:

```text
Entity Resolution Failure
        |
        v
UNRESOLVED
```

rather than inventing a Service.

Similarly:

```text
Classification Failure
        |
        v
UNKNOWN
```

rather than forcing an Evidence type.

And:

```text
AI Unavailable
        |
        v
Continue Deterministic Processing
```

rather than failing the entire Discovery Engine.

---

## 25. Reprocessing and Evolution

Discovery logic will evolve.

Entity-resolution mappings may improve.

Evidence classifications may change.

New deterministic rules may be added.

AI models may improve or be replaced.

Service identities may change.

The architecture should therefore support controlled reprocessing where practical.

Conceptually:

```text
Preserved Observation
        |
        +------> Classifier v1
        |             |
        |             v
        |         Evidence v1
        |
        +------> Classifier v2
                      |
                      v
                  Evidence v2
```

Similarly:

```text
Observed Identifier
        |
        +------> Resolver v1
        |
        +------> Resolver v2
```

This requirement reinforces the need to preserve provenance and avoid destructive normalization.

---

## 26. User Correction

Automated discovery will not always be correct.

The architecture should therefore allow for future user correction.

Examples include:

```text
"This is not the same Service."

"I never had an account here."

"These two Services are actually the same."

"This Relationship was historical."

"This Observation belongs to someone else."
```

The exact correction mechanism is not defined in Draft v0.2.

However, preserving Observations, Evidence and resolution provenance is necessary to support it later.

User-provided corrections should themselves retain provenance rather than silently rewriting historical observations.

---

## 27. Measurement and Validation

Discovery quality cannot be evaluated only by counting detected Services.

Future implementations should support evaluation of outcomes such as:

```text
True Positive
False Positive
False Negative
Unresolved
Misclassified Evidence
Incorrect Entity Resolution
```

Relevant measurements may eventually include:

- precision;
- recall;
- Evidence Classification accuracy;
- Entity Resolution accuracy;
- UNKNOWN rate;
- deterministic-rule coverage;
- incremental value provided by AI;
- source-specific reliability.

These measurements should be introduced when sufficiently representative test data exists.

The architecture should not assign arbitrary accuracy targets before empirical evaluation.

---

## 28. Open Questions

The following questions remain deliberately unresolved.

### Identity

- Which Identity Seed types should be supported?
- How should Identity Seeds be verified?
- How should multiple identities belonging to the same person be correlated?
- Should identities ever be automatically discovered?

### Discovery Sources

- Which Discovery Sources should be implemented first?
- What source-specific permissions are required?
- How should partial discovery be represented?
- How should source synchronization work?
- Which sources can operate entirely locally?

### Connectors

- What should the common Connector interface expose?
- How should Connector capabilities be advertised?
- How should permission requirements be represented?
- How should incremental synchronization work?
- How should Connector state be persisted?

### Observations

- What is the minimum common Observation representation?
- Which source-specific fields should remain outside the common model?
- Which Observations should be persisted?
- How long should Observations be retained?
- When can raw source information be safely discarded?

### Service Candidate Detection

- Should candidate detection use source-specific or shared strategies?
- How should personal communication be distinguished from Service interactions?
- How should technical intermediaries be excluded?

### Entity Resolution

- How should multiple domains resolve to one Service?
- How should multiple Services belonging to one Organization be represented?
- How should Brands and parent Organizations be represented?
- Should a Service and its legal data controller be separate entities?
- Which information should be used for resolution?
- Should external datasets be used?
- When should AI assist Entity Resolution?

### Evidence

- What common Evidence categories are required across Discovery Sources?
- Which Evidence categories should remain source-specific?
- How should conflicting Evidence be represented?
- How should malicious or misleading Evidence be detected?

### Relationships

- How should active, historical and unknown Relationships be represented?
- When can a Relationship be considered confirmed?
- How should deleted accounts be represented?
- How should multiple identities relating to the same Service be represented?

### Confidence

- Is a numerical Confidence score necessary?
- Would qualitative states provide better explainability?
- How should Confidence be calibrated?
- How should Confidence change over time?
- How should contradictory Evidence affect Confidence?

### Privacy

- Which processing must occur locally?
- Which information should be persisted?
- How long should Observations and Evidence be retained?
- How should authorization tokens be isolated?
- What should happen to derived information when a Connector is disconnected?
- What information, if any, may be sent to external AI providers?

### AI

- Where does AI provide measurable value over deterministic logic?
- Which tasks benefit from an LLM?
- Which tasks should remain deterministic?
- How should local and remote AI strategies be interchangeable?
- How should AI-generated interpretations remain explainable?
- How should AI model changes affect historical classifications?

### Reprocessing

- When should historical Observations be reclassified?
- When should entity resolution be rerun?
- How should derived information be versioned?
- What happens when new logic produces a different conclusion?

### User Correction

- Which framework conclusions should users be able to correct?
- Should user corrections override automated conclusions?
- How should corrections affect future classification and resolution?
- How should correction provenance be represented?

### Completeness

- How can discovery coverage be measured when the complete set of Relationships is fundamentally unknown?
- How should partial scans be communicated?
- How should the framework communicate incompleteness to users?

---

## 29. Decision Log

### D-001 - Discovery Is Evidence-Based

A detected Service does not imply that it currently holds personal data.

Discovery identifies evidence of possible current or historical Relationships.

---

### D-002 - Multiple Discovery Sources

No single Discovery Source defines the framework.

The architecture must support multiple independent sources producing information that can contribute to the same Service Relationship.

---

### D-003 - Unknown Is a Valid State

Missing, ambiguous or unresolved information must be represented explicitly rather than inferred without sufficient Evidence.

This applies to:

- unresolved Services;
- unknown Evidence classifications;
- uncertain Relationships;
- incomplete source analysis.

---

### D-004 - Local-First

Raw personal information should be processed locally whenever technically practical.

External transmission must have an explicit purpose.

---

### D-005 - Explainability

Every discovered Relationship should be traceable to the Evidence supporting it.

The framework should be able to explain why a Service was discovered without unnecessarily exposing unrelated raw personal information.

---

### D-006 - Discovery and Acquisition Are Separate Concerns

Discovering that a Relationship exists and obtaining personal data held by a Service are distinct framework responsibilities.

---

### D-007 - Commercial Licensing

The project is intended to be freely available for permitted non-commercial use.

Commercial use will require a separate commercial license from the copyright holder.

Final licensing terms will be established before the first public release.

---

### D-008 - Provider-Independent AI

The framework must not depend on one particular AI model or provider.

AI capabilities should eventually support interchangeable strategies, including:

- local models;
- self-hosted models;
- remote providers;
- user-provided providers;
- deterministic alternatives where appropriate.

---

### D-009 - AI Is Not a Substitute for Deterministic Components

AI should be introduced when it provides measurable value for ambiguity, semantic interpretation, classification, extraction, reasoning or adaptation.

Operations that can be reliably performed deterministically should remain deterministic.

---

### D-010 - Progressive Permission

Connectors should request the minimum level of access required to perform a capability.

Access to more sensitive information should be requested only when lower-privilege data is insufficient and the user explicitly authorizes the operation.

---

### D-011 - AI for Ambiguity

Deterministic processing should be preferred when information can be reliably interpreted using explicit logic.

AI-assisted processing should primarily be used when deterministic processing cannot adequately resolve ambiguity and when the required input is available within the user's authorized permission boundary.

---

### D-012 - Preserve Source Provenance

Derived Service information must remain traceable to the Observations and Evidence from which it was produced.

Normalization, classification, aggregation and Entity Resolution must not destroy the provenance required to explain, correct or reprocess derived information.

---

### D-013 - Observation and Evidence Are Separate Concepts

Information collected from a Source must be represented independently from the framework's semantic interpretation of that information.

Therefore:

```text
OBSERVATION != EVIDENCE
```

This separation allows classification logic to evolve without destroying source provenance.

---

### D-014 - Evidence and Relationship Are Separate Concepts

Individual Evidence describes the meaning of one or more Observations.

A Relationship represents an assessment based on aggregated Evidence.

Therefore:

```text
EVIDENCE != RELATIONSHIP
```

Relationship Assessment must not be conflated with Evidence Classification.

---

### D-015 - Domain and Service Are Separate Concepts

Technical identifiers such as domains, URLs or email addresses must not automatically be treated as canonical Service identities.

Therefore:

```text
DOMAIN != SERVICE
```

Mapping observed identifiers to Services belongs to Entity Resolution.

---

### D-016 - Core Discovery Must Degrade Gracefully

Failure or unavailability of optional capabilities, including AI, must not prevent deterministic portions of Service Discovery from operating.

Unresolved states should remain explicit rather than causing fabricated conclusions.

---

## 30. Validation Status

Draft v0.2 incorporates architectural findings from the first concrete design scenario:

```text
SCN-001
Gmail Service Discovery
```

The scenario validated several concepts already present in Draft v0.1, including:

- evidence-based discovery;
- multiple Discovery Sources;
- Entity Resolution;
- uncertainty;
- explainability;
- local-first processing;
- provider-independent AI.

It also exposed architectural concepts that required explicit representation in Draft v0.2:

- Connectors as source-specific boundaries;
- Observations as distinct from Evidence;
- Service Candidate Detection;
- Evidence Classification;
- Evidence Aggregation;
- Relationship Assessment;
- Progressive Permission;
- explicit provenance preservation;
- deterministic-first classification;
- AI for ambiguity;
- graceful degradation;
- temporal awareness;
- support for reprocessing.

The architecture remains provisional.

A single source scenario is not sufficient to establish that the model is truly source-independent.

---

## 31. Next Design Exercise

The next architecture validation exercise should use a Discovery Source that is structurally different from email.

The objective is not yet to add another product feature.

The objective is to test whether the abstractions introduced in Draft v0.2 remain valid when the source does not consist of email messages.

A candidate scenario is:

```text
SCN-002
Password Manager Service Discovery
```

Conceptually:

```text
Password Manager
       |
       v
Password Manager Connector
       |
       v
Credential Metadata Observation
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
Evidence Aggregation
       |
       v
Relationship Assessment
       |
       v
Service Graph
```

The scenario should specifically test:

- whether `Connector` is sufficiently source-independent;
- whether the `Observation` abstraction works for non-email information;
- whether Evidence Classification remains useful;
- whether the distinction between technical identifier and Service remains valid;
- whether Progressive Permission works for highly sensitive sources;
- whether secret values such as passwords can remain completely outside the discovery pipeline;
- whether the same Service can eventually receive Evidence from independent sources;
- whether the current Relationship model remains valid.

Findings from this scenario should be used to determine whether Draft v0.2 can remain unchanged or requires another architectural revision before software interfaces are finalized.

---

## 32. Path Toward Implementation

Implementation should not begin by building the entire framework.

The current design process is:

```text
Architecture v0.1
       |
       v
Scenario 001
Gmail Service Discovery
       |
       v
Architecture v0.2
       |
       v
Additional Source-Independent
Architecture Validation
       |
       v
Domain Model
       |
       v
Software Interfaces
       |
       v
Vertical MVP
       |
       v
Measurement
       |
       v
Architecture Refinement
```

Once the architecture has survived sufficiently different scenarios, the next implementation steps should define:

1. the minimum Domain Model;
2. Connector interfaces;
3. Observation representation;
4. Entity Resolution interfaces;
5. Evidence Classification interfaces;
6. Evidence Aggregation;
7. Relationship Assessment;
8. persistence boundaries;
9. privacy and permission boundaries.

Only then should a source-specific vertical implementation be used to validate the complete pipeline in executable software.

---

## 33. Future Documents

This document defines only the Identity and Service Discovery portion of the framework.

The broader design documentation is currently expected to evolve approximately as follows:

```text
docs/
|
+-- architecture/
|   |
|   +-- 01-identity-and-service-discovery.md
|   |
|   +-- 02-personal-data-acquisition.md
|   |
|   +-- 03-personal-data-model.md
|   |
|   +-- 04-personal-data-graph.md
|   |
|   +-- 05-ai-and-agent-architecture.md
|   |
|   +-- 06-privacy-and-security-architecture.md
|   |
|   +-- 07-continuous-monitoring-and-governance.md
|
+-- scenarios/
    |
    +-- 001-gmail-service-discovery.md
    |
    +-- 002-...
```

These filenames and boundaries remain provisional.

They should evolve based on concrete architectural requirements rather than being considered fixed in advance.
