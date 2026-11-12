# Identity & Service Discovery

**Status:** Draft v0.1  
**Scope:** Identity and service discovery  
**Last updated:** November 2026

---

## 1. Purpose

The first problem addressed by the framework is:

> Given one or more digital identities provided by a user, which services and organizations may hold, or may have held, personal data related to that user?

The objective of this module is not yet to determine exactly what personal data each organization currently holds.

Its objective is to discover and document evidence of digital relationships between the user and external services.

The fundamental discovery model is:

```text
Identity Seed
    ↓
Discovery Source
    ↓
Evidence
    ↓
Service
    ↓
Relationship
```

The output of this process becomes the starting point for subsequent modules of the framework that may:

1. determine how personal data can be obtained from each identified service;
2. request or retrieve that data;
3. ingest and normalize the returned information;
4. classify personal data;
5. build a personal data graph;
6. continuously monitor changes;
7. help the user exercise control over personal data.

This document focuses exclusively on the first part of that process: **Identity and Service Discovery**.

---

# 2. Design Principles

## 2.1 Evidence before inference

The framework must distinguish between:

- what has been directly observed;
- what has been inferred;
- what has been confirmed;
- what remains unknown.

For example, detecting an email from a service does not prove that the service currently stores personal data about the user.

The framework should therefore preserve the evidence behind every conclusion.

---

## 2.2 Unknown is a valid state

The framework must not invent information to fill knowledge gaps.

For example:

```text
Service: Spotify
Relationship: Probable
Personal data held: UNKNOWN
```

`UNKNOWN` is an explicit and valid state.

Absence of information must not be confused with absence of data.

---

## 2.3 Multiple independent discovery sources

No single discovery source should be considered sufficient to reconstruct a person's complete digital footprint.

For this reason, the framework should support multiple independent discovery mechanisms.

For example:

```text
Email
Password Manager
Browser
Identity Provider
Manual Input
        │
        ▼
  Discovery Engine
```

Evidence obtained from different sources may then be correlated.

---

## 2.4 Explainability

Every discovered relationship should be traceable to the evidence that caused the framework to identify it.

The user should be able to ask:

> Why do you think I have or had a relationship with this organization?

The framework should be able to answer with the actual evidence supporting that conclusion.

---

## 2.5 Local-first and privacy by design

The framework itself must not unnecessarily become another centralized repository containing highly sensitive information about the user.

Whenever technically practical:

- raw personal data should be processed locally;
- only the minimum required information should be persisted;
- external transmission should require an explicit purpose;
- credentials and authorization tokens should be isolated from discovered personal information;
- external AI providers should not automatically receive raw personal data.

The framework should minimize the personal information it collects about the person it is attempting to protect.

---

# 3. Identity Seed

An `Identity Seed` is an identifier or digital account declared by the user as belonging to them and used as a starting point for discovery.

Possible Identity Seeds include:

- email addresses;
- phone numbers;
- usernames;
- Google accounts;
- Apple accounts;
- Microsoft accounts;
- other supported digital identities.

Example:

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
│
├── personal@gmail.com
├── work@example.com
├── oldmail@example.net
├── +39XXXXXXXXXX
└── username123
```

These identities may represent different portions of the same person's digital history.

---

## 3.1 Identity Seeds are starting points

An Identity Seed is not necessarily information that should automatically be searched publicly on the Internet.

Its primary purpose is to provide a starting point from which authorized discovery processes may begin.

For example, the user may authorize the framework to inspect a mailbox associated with one of their email addresses.

The framework may then use that authorized source to discover services with which the user has interacted.

---

# 4. Discovery Source

A `Discovery Source` is an authorized source from which the framework can obtain evidence about relationships between the user and external services.

Different Discovery Sources may provide different strengths and types of evidence.

---

## 4.1 Email

Potential providers include:

- Gmail;
- Outlook;
- other supported email providers.

Email may contain evidence such as:

- account verification messages;
- welcome messages;
- password resets;
- OTP or authentication codes;
- login notifications;
- security notifications;
- purchase confirmations;
- invoices;
- subscriptions;
- newsletters;
- privacy notifications;
- account changes;
- account deletion messages.

For example:

```text
"Verify your Spotify account"
```

may constitute evidence that a relationship existed between an identity and Spotify.

However, receiving an email must not automatically be interpreted as proof of an active account.

---

## 4.2 Identity Providers

Identity providers may expose relationships created through authentication mechanisms such as:

- Sign in with Google;
- Sign in with Apple;
- Microsoft identity;
- OAuth;
- OpenID Connect;
- other supported authentication relationships.

For example, an application authorized through a Google account may provide evidence that the user established a relationship with that application.

---

## 4.3 Password Managers

A password manager may provide strong evidence that an account exists or existed for a particular service.

For example:

```text
netflix.com
username: personal@gmail.com
```

could constitute strong evidence of a relationship with Netflix.

Access to password-manager information must always require explicit user authorization.

Actual passwords should not be imported, persisted, or processed unless strictly necessary.

The framework primarily needs evidence of the relationship, not the user's credentials.

---

## 4.4 Browser Data

A browser may provide additional evidence through signals such as:

- browsing history;
- frequently visited domains;
- login-related information;
- bookmarks;
- locally stored site information;
- other supported browser signals.

However:

> Visiting a website does not imply having an account with that website.

Browser history alone should therefore normally constitute weaker evidence than an explicit account verification message or credential entry.

---

## 4.5 Manual User Input

The user must always be able to manually declare a relationship.

Example:

> I had an account on example.com using another email address in 2018.

Manual input is necessary because no automated discovery mechanism can guarantee complete reconstruction of a person's digital history.

The user may remember relationships that are no longer visible through any connected Discovery Source.

---

## 4.6 Future Discovery Sources

The framework should allow additional Discovery Sources to be implemented as independent connectors without redesigning the core system.

Conceptually:

```text
Discovery Source Interface
        │
        ├── Gmail Connector
        ├── Outlook Connector
        ├── Browser Connector
        ├── Password Manager Connector
        ├── Google Identity Connector
        ├── Apple Identity Connector
        └── Future Connectors
```

Each connector should produce evidence using a common internal representation.

---

# 5. Evidence

An `Evidence` is an observable element suggesting that a relationship exists or existed between an Identity Seed and a Service.

Example:

```json
{
  "id": "evidence_001",
  "identity_id": "identity_001",
  "source": "email",
  "evidence_type": "account_verification",
  "observed_domain": "spotify.com",
  "timestamp": "2025-10-01T13:42:00Z"
}
```

Evidence should preserve sufficient provenance to explain where the information came from.

---

## 5.1 Evidence is not Fact

Evidence may be misleading.

An email apparently associated with a service might represent:

- marketing communication;
- phishing;
- an old account;
- a deleted account;
- an email forwarding rule;
- an incorrectly entered email address;
- a service used by another person;
- communication unrelated to an account.

Therefore:

```text
Evidence ≠ Confirmed Relationship
```

and:

```text
Relationship ≠ Current Data Possession
```

These distinctions are fundamental to the framework.

---

## 5.2 Evidence provenance

Whenever possible, the framework should preserve:

```text
Evidence
├── Discovery Source
├── Original observation
├── Timestamp
├── Evidence type
├── Identity involved
├── Service/domain observed
└── Extraction method
```

This provenance allows relationships to remain auditable and explainable.

---

# 6. Service

A `Service` represents a normalized digital service, organization, or other potential data-holding entity.

Different observations may refer to the same underlying service.

For example:

```text
open.spotify.com
accounts.spotify.com
no-reply@spotify.com
spotify.com
```

may all resolve to:

```text
Spotify
```

This means that service discovery and service identification are separate problems.

---

## 6.1 Entity Resolution

A future `Entity Resolution Engine` should determine whether multiple observations refer to the same service or organization.

For example:

```text
Observed domains
      │
      ├── spotify.com
      ├── accounts.spotify.com
      └── open.spotify.com
             │
             ▼
      Entity Resolution
             │
             ▼
          Spotify
```

Entity resolution may become substantially more complicated for organizations operating:

- multiple brands;
- different regional domains;
- subsidiaries;
- acquired companies;
- multiple products;
- separate legal entities.

The framework must preserve original observations even after normalization so that entity-resolution decisions remain explainable.

---

# 7. Relationship

A `Relationship` represents the framework's current understanding that a particular identity is or was associated with a Service.

Example:

```json
{
  "identity_id": "identity_001",
  "service_id": "spotify",
  "status": "probable",
  "confidence": 0.91
}
```

Potential future relationship states may include:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
REJECTED
```

These states are provisional.

Their exact semantics should be refined after analysing real discovery scenarios.

---

# 8. Multiple Evidence Sources

Different Discovery Sources may independently identify the same Relationship.

Example:

```text
                         ┌── Gmail: registration email
                         │
User ───── Spotify ──────┼── Password Manager: credential
                         │
                         └── Google: OAuth relationship
```

Three independent observations support the same relationship.

This should generally increase confidence that the relationship actually exists or existed.

However, multiple pieces of evidence still must not automatically be interpreted as evidence of what personal data the Service currently possesses.

---

# 9. Confidence

Relationships should eventually carry a confidence assessment.

Potential representations include:

```text
CONFIRMED
HIGH
MEDIUM
LOW
```

or a numerical representation:

```text
0.00 → 1.00
```

The exact confidence algorithm is intentionally **not defined in Draft v0.1**.

For example, assigning arbitrary weights such as:

```text
registration email = +0.4
password manager = +0.5
browser visit = +0.1
```

would create a false sense of mathematical precision.

A confidence model should instead be developed after:

1. defining an Evidence taxonomy;
2. testing real examples;
3. analysing false positives;
4. analysing false negatives;
5. measuring the reliability of different evidence types;
6. testing combinations of independent evidence.

A confidence score must ultimately be explainable rather than merely numerical.

---

# 10. Discovery Engine

The `Discovery Engine` is the first major component of the framework.

## 10.1 Responsibility

Given:

- one or more Identity Seeds;
- one or more authorized Discovery Sources;

the Discovery Engine produces structured Evidence describing Services with which the user may have or have had a Relationship.

---

## 10.2 The Discovery Engine must not

The Discovery Engine must not:

- assume what personal data an organization currently holds;
- automatically send privacy requests;
- delete accounts;
- modify external data;
- claim that discovery is complete;
- silently perform consequential external actions.

These responsibilities belong to other components of the broader framework.

---

## 10.3 High-Level Architecture

```text
                         USER
                           │
                           ▼
                   Identity Manager
                           │
                           ▼
                 Discovery Sources
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
           Email         OAuth         Browser
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                     Evidence Store
                           │
                           ▼
                    Entity Resolution
                           │
                           ▼
                  Relationship Engine
                           │
                           ▼
                      Service Graph
```

Other Discovery Sources can later be connected to the same pipeline.

---

# 11. Expected Output

After discovery, the framework should eventually be capable of representing information such as:

```text
User
│
├── Google
│   ├── Relationship: CONFIRMED
│   ├── Evidence:
│   │   └── User-provided Google identity
│   └── Personal data held: UNKNOWN
│
├── Spotify
│   ├── Relationship: HIGH CONFIDENCE
│   ├── Evidence:
│   │   ├── Account registration email
│   │   ├── Billing email
│   │   └── Password manager entry
│   └── Personal data held: UNKNOWN
│
└── oldwebsite.example
    ├── Relationship: LOW CONFIDENCE
    ├── Evidence:
    │   └── Email received in 2018
    └── Personal data held: UNKNOWN
```

This output represents an:

> **Observed Digital Relationship Graph**

It does not represent a complete map of the user's personal data.

---

# 12. Relationship Graph

At a conceptual level, the Discovery Engine begins building a graph around the user.

For example:

```text
              Gmail
                │
                ▼
             Evidence
                │
                ▼
Netflix ◄───── User ─────► Spotify
  ▲                        ▲
  │                        │
Evidence                Evidence
  │                        │
  ▼                        ▼
Browser              Password Manager
```

Over time, this graph may become the foundation of a broader `Personal Data Graph`.

The distinction is important:

### Relationship Graph

Answers:

> Which services appear connected to me?

### Personal Data Graph

Will eventually answer:

> Which personal data does each service actually hold about me?

The first graph enables construction of the second.

---

# 13. Privacy and Security Requirements

This framework may eventually process exceptionally sensitive information, including:

- email metadata;
- potentially email content;
- account relationships;
- browsing information;
- authentication relationships;
- personal identifiers;
- exported personal datasets;
- historical digital activity.

This creates a fundamental architectural constraint:

> A privacy framework must not solve one privacy problem by creating a larger centralized privacy problem.

The default architectural assumption should therefore be:

## Local-first

Where technically practical:

```text
Raw Data
   │
   ▼
Local Processing
   │
   ▼
Structured Evidence
   │
   ▼
Minimum Necessary Persistence
```

Raw mailbox contents, complete browser histories, credentials, or exported personal datasets should not be transmitted to external infrastructure unless explicitly required and authorized.

---

## 13.1 AI implications

The same principle applies to artificial intelligence.

If AI is used for tasks such as:

- email classification;
- entity resolution;
- evidence classification;
- document understanding;
- anomaly detection;

the architecture should not assume that raw personal data can simply be sent to an external AI provider.

The AI layer should eventually support multiple providers, including:

```text
Local Model
Cloud Model A
Cloud Model B
User-provided Model
Rule-based fallback
```

Privacy requirements may determine which provider can be used for a particular operation.

The core framework should therefore remain independent from any single model or AI provider.

---

# 14. Non-Goals

## 14.1 Complete Discovery

The framework cannot guarantee discovery of every organization holding data about the user.

The real digital footprint is fundamentally unknown.

Therefore:

```text
Observed Footprint ≠ Complete Footprint
```

---

## 14.2 Current Data Possession

Historical Evidence of a Relationship does not prove that an organization still stores personal data.

For example:

```text
Account verification email from 2018
```

may demonstrate that a relationship probably existed in 2018.

It does not demonstrate what information the organization stores today.

---

## 14.3 Perfect Accuracy

Discovery processes can produce:

- false positives;
- false negatives;
- ambiguous relationships;
- conflicting evidence.

The system must explicitly support uncertainty.

---

## 14.4 Public Internet Discovery

Searching the public Internet for occurrences of information such as:

- phone numbers;
- email addresses;
- names;
- usernames;
- leaked information;
- public profiles;

is part of the broader goal of understanding a user's personal data footprint but represents a different technical problem.

It should therefore be designed as a separate module rather than silently mixed with Service Discovery.

---

## 14.5 Personal Data Acquisition

This document does not define how personal data is requested or retrieved from identified organizations.

For example:

```text
Service discovered
      │
      ▼
How can I obtain my data?
      │
      ├── API
      ├── Data export
      ├── Privacy portal
      ├── Access request
      ├── Email
      └── Other mechanism
```

That functionality belongs to a subsequent component of the framework.

---

# 15. Conceptual End-to-End Flow

The current project vision can therefore be summarized as:

```text
USER
 │
 ▼
IDENTITY SEEDS
 │
 ▼
DISCOVERY SOURCES
 │
 ▼
EVIDENCE COLLECTION
 │
 ▼
ENTITY RESOLUTION
 │
 ▼
RELATIONSHIP DISCOVERY
 │
 ▼
SERVICE GRAPH
 │
 ▼
DATA ACQUISITION
 │
 ▼
DATA INGESTION
 │
 ▼
PERSONAL DATA CLASSIFICATION
 │
 ▼
PERSONAL DATA GRAPH
 │
 ▼
MONITORING
 │
 ▼
GOVERNANCE ACTIONS
```

Only the following section of this pipeline is currently defined by this document:

```text
IDENTITY SEEDS
      ↓
DISCOVERY SOURCES
      ↓
EVIDENCE
      ↓
SERVICES
      ↓
RELATIONSHIPS
```

The remaining components will be designed separately.

---

# 16. Open Questions

The following questions remain deliberately unresolved.

### Identity

1. Which Identity Seed types should be supported?
2. How should Identity Seeds be verified?
3. How should multiple identities belonging to the same person be correlated?
4. Should identities ever be automatically discovered?

### Discovery

5. Which Discovery Sources should be implemented first?
6. What constitutes valid Evidence?
7. What Evidence categories are required?
8. How do we detect malicious Evidence such as phishing?
9. How do we distinguish marketing communication from an actual account relationship?

### Entity Resolution

10. How should multiple domains resolve to one organization?
11. How should brands and parent companies be represented?
12. Should a product and its legal data controller be separate entities?

### Relationships

13. How should active, historical, and unknown relationships be distinguished?
14. How should Evidence strength be classified?
15. How should false positives and false negatives be measured?
16. When can a Relationship be considered confirmed?

### Privacy

17. Which processing must occur locally?
18. Which information should be persisted?
19. How long should Evidence be retained?
20. How should authentication tokens be isolated?
21. What information, if any, can be sent to external AI providers?

### AI

22. Where does AI provide measurable value over deterministic logic?
23. Which tasks require an LLM?
24. Which tasks should remain deterministic?
25. How should local and remote AI providers be interchangeable?
26. How can AI-generated conclusions remain explainable?

### Completeness

27. How can discovery coverage be measured when the complete set of relationships is unknown?
28. How should the framework communicate uncertainty to the user?

---

# 17. Decision Log

## D-001 - Discovery is evidence-based

A detected Service does not imply that it currently holds personal data.

---

## D-002 - Multiple Discovery Sources

Email is one Discovery Source, not the foundation of the entire framework.

The architecture must support multiple sources.

---

## D-003 - Unknown is a valid state

Missing information must be represented as `UNKNOWN` rather than inferred without sufficient Evidence.

---

## D-004 - Local-first

Raw personal information should be processed locally whenever technically practical.

---

## D-005 - Explainability

Every discovered Relationship should be traceable to the Evidence supporting it.

---

## D-006 - Discovery and acquisition are separate concerns

Discovering that a Relationship exists and obtaining the personal data held by a Service are distinct framework responsibilities.

---

## D-007 - Commercial licensing

The project is intended to be freely available for permitted non-commercial use.

Commercial use will require a separate commercial license from the copyright holder.

Final licensing terms will be established before the first public release.

---

## D-008 - Provider-independent AI

The framework must not depend on one particular AI model or provider.

AI capabilities should eventually be exposed through interchangeable provider interfaces, allowing users to select local, free, commercial, or self-hosted models depending on their requirements.

---

## D-009 - AI is not a substitute for deterministic components

AI should be introduced when it provides measurable value for problems involving ambiguity, classification, extraction, reasoning, or adaptation.

Deterministic operations should remain deterministic when possible.

---

# 18. Next Design Exercise

The first real scenario used to challenge this model will be:

> A user connects a Gmail account containing several years of email history. How can the framework determine, with reasonable confidence and explainability, which digital services that person uses or has used?

The exercise will be used to validate:

- Identity Seeds;
- Discovery Sources;
- Evidence types;
- service identification;
- Entity Resolution;
- Relationship states;
- confidence modelling;
- privacy constraints;
- local processing;
- the role of AI;
- false-positive management;
- false-negative management;
- scalability.

The findings from this exercise will be incorporated into **Draft v0.2**.

---

# 19. Future Documents

This document defines only the first part of the framework.

At this stage, the expected design documentation may evolve approximately as follows:

```text
docs/
│
├── 01-identity-and-service-discovery.md
│
├── 02-personal-data-acquisition.md
│
├── 03-personal-data-model.md
│
├── 04-personal-data-graph.md
│
├── 05-ai-and-agent-architecture.md
│
├── 06-privacy-and-security-architecture.md
│
└── 07-continuous-monitoring-and-governance.md
```

These filenames and boundaries are provisional.

They will evolve as the framework architecture becomes better understood.
