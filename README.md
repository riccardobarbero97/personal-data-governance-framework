# Personal Data Governance Framework

> Know who may have your data. Understand what they know. Take back control.

## Overview

Every day, people share personal information with dozens or hundreds of digital Services.

Email addresses, phone numbers, names, physical addresses, payment information, locations, interests, Account activity, behavioral information and inferred attributes gradually become distributed across an ecosystem that most individuals can no longer see or understand.

The problem is simple:

> We continuously generate and share personal data, but we do not have a practical way to understand who may have it, what they may know about us and what we can do about it.

The **Personal Data Governance Framework** explores a User-centric and privacy-conscious approach to this problem.

Its long-term objective is to help individuals progressively:

```text
discover
understand
map
monitor
and govern
```

their observable personal-data footprint.

The project does not claim that it can reconstruct every piece of personal information held about a person.

Instead, it builds an evidence-based representation of what can be observed through sources explicitly authorized by the User.

---

## Core Idea

The framework starts from digital identities and source connections explicitly provided or authorized by the User.

Examples of Identity Seeds may include:

- email addresses;
- phone numbers;
- usernames;
- Google Accounts;
- Apple Accounts;
- Microsoft Accounts;
- other identifiers explicitly confirmed by the User.

The User may also authorize one or more ConnectedSources, such as:

- Gmail accounts;
- Outlook accounts;
- Password Managers;
- browser profiles;
- Identity Providers;
- manual input;
- future authorized sources.

These sources produce minimized Observations that can be interpreted as Evidence of possible current or historical Relationships with digital Services.

Conceptually:

```text
User
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

The output is an:

> **Observed Digital Relationship Graph**

It represents Services with which the User appears to have or have had a meaningful digital Relationship, together with the Evidence supporting that conclusion.

---

## Observed Footprint, Not Absolute Truth

The framework does not attempt to reconstruct an objective and complete digital footprint.

That would not be technically realistic.

Instead:

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

A discovered Relationship does not prove:

- that an Account currently exists;
- that an Account is still active;
- that credentials still work;
- that the Service currently holds specific personal data;
- that the Service has deleted or retained any particular information;
- that the framework has discovered every relevant Service.

Every conclusion must remain relative to the information currently available to the framework.

The architecture therefore preserves distinctions between:

```text
Observed information
Interpretation
Technical identifier
Resolved Service
Evidence
Relationship assessment
Unknown information
Processing failure
```

Uncertainty is part of the Domain Model rather than something the framework attempts to hide.

Valid outcomes include:

```text
CandidateStatus:
UNKNOWN

ResolutionStatus:
UNRESOLVED

ResolutionStatus:
AMBIGUOUS

ClassificationStatus:
UNKNOWN

RelationshipStatus:
UNKNOWN

TemporalStatus:
UNKNOWN
```

The system should prefer an explicit unknown state over an unsupported conclusion.

---

## Long-Term Vision

The broader framework is envisioned as:

```text
IDENTITY
   |
   v
DISCOVER
   |
   v
REQUEST
   |
   v
INGEST
   |
   v
UNDERSTAND
   |
   v
MAP
   |
   v
MONITOR
   |
   v
ACT
```

### Identity

Define and confirm the digital identities belonging to the User.

### Discover

Identify Services and Organizations with which the User appears to have or have had Relationships.

### Request

Determine how the User can obtain personal data held by an identified Organization or Service.

Possible mechanisms may include:

- Account data exports;
- privacy portals;
- APIs;
- data portability mechanisms;
- Data Subject Access Requests;
- other supported acquisition mechanisms.

### Ingest

Process information returned by different Services and convert heterogeneous source formats into a common internal representation.

### Understand

Identify, normalize and classify personal information contained in acquired data.

### Map

Build a navigable representation connecting:

```text
User
  ↕
Identity
  ↕
Service
  ↕
Personal Data
```

This should eventually support questions such as:

> Which Organizations appear to know my phone number?

or:

> What information does this Service appear to hold about me?

### Monitor

Detect changes to the User's observable digital footprint over time.

### Act

Help the User understand and, where appropriate, exercise available controls over personal information.

---

## Current Scope

The current project scope is:

> **Identity and Service Discovery**

The capability addresses the following question:

> Given one or more digital identities declared by a User and one or more explicitly authorized sources, which digital Services appear to have or have had a Relationship with that User?

The current scope is limited to discovering and explaining observable Service Relationships.

It does not yet implement:

- personal-data acquisition from discovered Services;
- Data Subject Access Request automation;
- privacy-portal automation;
- Account deletion;
- complete analysis of personal-data exports;
- Personal Data Graph construction;
- continuous monitoring;
- governance actions.

These belong to later framework capabilities.

---

## Discovery Architecture

The consolidated Discovery architecture is based on the following boundaries:

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

These distinctions prevent:

- Provider-specific concepts from leaking into the Discovery Core;
- collected information from being confused with interpretation;
- technical identifiers from automatically becoming canonical Services;
- Evidence from being treated as confirmed fact;
- Relationships from being interpreted as active Accounts;
- historical events from being mistaken for current Account activity;
- technical failures from being represented as Domain uncertainty.

---

## Core Domain Model

The current Core Domain Entities are:

```text
User

IdentitySeed

ConnectedSource

Observation

Service

Evidence

Relationship
```

Supporting Domain Value and Classification Concepts include:

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

The primary Domain and integration processes are:

```text
Connector

ServiceCandidateDetector

EntityResolver

EvidenceClassifier

EvidenceAggregator

RelationshipAssessor
```

Concepts still under evaluation include:

```text
Account

Organization

Brand

LegalDataController

IdentityServiceAssociation

CollectionRun

RelationshipAssessmentHistory
```

These concepts will not be promoted solely because they appear useful in one scenario.

They require cross-scenario or implementation evidence.

---

## Relationship Model

The primary Relationship is modeled between:

```text
User
  |
  v
Relationship
  |
  v
Service
```

Relevant Identity references remain preserved inside:

- Evidence;
- EvidenceAggregate;
- Relationship.

This allows the framework to answer:

> Which Services appear connected to me?

while retaining enough information to support questions such as:

> Which Services were associated with `oldmail@example.net`?

Multiple Identity references do not automatically imply multiple Accounts.

---

## Relationship Status

Relationship support is represented through:

```text
RelationshipStatus

UNKNOWN

OBSERVED

ESTABLISHED

REJECTED
```

### UNKNOWN

Available Evidence is insufficient to justify a stronger Relationship conclusion.

### OBSERVED

Interaction or communication with the Service has been observed, but Evidence does not justify the stronger ESTABLISHED state.

### ESTABLISHED

Available Evidence provides a justified basis for concluding that a meaningful Relationship existed.

### REJECTED

The apparent Relationship should not currently be attributed to the User.

Rejection requires explicit provenance.

---

## Temporal Status

Temporal interpretation is represented independently through:

```text
TemporalStatus

UNKNOWN

CURRENTLY_OBSERVED

HISTORICAL
```

This supports combinations such as:

```text
ESTABLISHED + HISTORICAL

ESTABLISHED + UNKNOWN

OBSERVED + CURRENTLY_OBSERVED

REJECTED + UNKNOWN
```

A Relationship may therefore be strongly supported while its current status remains unknown.

---

## Evidence Lifecycle

Evidence interpretations have an explicit lifecycle:

```text
EvidenceStatus

ACTIVE

SUPERSEDED

REJECTED
```

### ACTIVE

The Evidence represents a currently accepted semantic interpretation.

### SUPERSEDED

The Evidence has been replaced by a newer accepted interpretation but remains available for provenance.

### REJECTED

The Evidence interpretation has been explicitly invalidated.

The default current Discovery view normally uses:

```text
ACTIVE Evidence
```

while preserving SUPERSEDED and REJECTED Evidence for provenance, historical analysis and User correction.

Evidence lifecycle state is distinct from temporal meaning.

An ACTIVE Evidence item may describe a historical event.

---

## Privacy by Design

A system intended to improve personal privacy should not become another centralized repository containing everything about a person.

The project is therefore designed around:

```text
Local-First Processing

Data Minimization

Least Privilege

Progressive Permission

Provider Isolation

Explicit Provenance
```

Where technically practical:

```text
External Source
      |
      v
Privileged Connector
      |
      v
Select / Normalize / Minimize
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

Sensitive source information should remain on the User's device whenever practical.

External processing should be deliberate, transparent and controllable by the User.

---

## Connector as a Security Boundary

A Connector isolates Provider-specific integration logic and privileged source access.

Conceptually:

```text
Highly Sensitive Source
         |
         v
      Connector
         |
    +----+----+
    |         |
 required   unnecessary
   data      sensitive data
    |         |
    v         X
Observation
```

For example, a Password Manager source may expose:

```text
title
username
URI
password
OTP seed
recovery codes
private keys
```

while Service Discovery may require only:

```text
title
username reference
URI
non-secret timestamps
```

Secrets unnecessary for Discovery should not cross the Connector boundary.

---

## Progressive Permission

Connecting a source must not automatically grant every framework capability access to all information available through that source.

The general permission model is:

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

No component may silently escalate Provider permissions.

For Gmail Service Discovery, metadata and message content should remain separate capabilities.

Basic Service Discovery must not require attachment access.

---

## Provider Independence

Core Discovery components must not depend on one specific Provider.

The intended model is:

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

Equivalent source semantics should use Provider-neutral ObservationTypes where possible.

For example:

```text
Gmail ---------+
               |
Outlook -------+
               |
iCloud --------+--> EMAIL_MESSAGE_METADATA
               |
Proton --------+
```

Provider-specific authentication, pagination, synchronization and error handling remain primarily behind Connectors.

---

## Deterministic First

Operations that can be implemented reliably and deterministically should remain deterministic.

Examples include:

- email-address parsing;
- URL parsing;
- hostname extraction;
- Public Suffix List-aware domain normalization;
- known Service mapping lookup;
- Evidence counting;
- temporal sorting;
- Evidence lifecycle filtering;
- rule-based classification;
- Relationship policy evaluation.

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

AI is an optional strategy available to selected components.

AI is not the Discovery architecture itself.

---

## AI Principles

Artificial intelligence may support selected capabilities such as:

- ambiguous Evidence Classification;
- multilingual semantic interpretation;
- ambiguous Entity Resolution;
- complex explanations;
- later personal-data extraction;
- interpretation of heterogeneous data exports.

The framework remains AI-Provider independent.

Potential future configurations may support:

- local models;
- self-hosted models;
- open models;
- commercial APIs;
- User-provided AI Providers;
- deterministic-only operation.

AI must not be required for basic deterministic Discovery.

If AI is unavailable:

```text
deterministic processing continues
```

and unresolved information remains explicit.

AI input must follow:

- data minimization;
- existing authorization boundaries;
- sensitivity policy;
- local-first preferences;
- no secret disclosure;
- no silent permission escalation.

---

## No Numerical Confidence in the Initial Model

The initial Discovery model does not use arbitrary numerical Confidence values such as:

```text
candidate_confidence = 0.78

resolution_confidence = 0.91

relationship_confidence = 0.87
```

The framework instead uses explicit states, provenance and explanations.

Examples include:

```text
CandidateStatus:
CANDIDATE / NOT_CANDIDATE / UNKNOWN
```

```text
ResolutionStatus:
RESOLVED / UNRESOLVED / AMBIGUOUS
```

```text
ClassificationStatus:
CLASSIFIED / UNKNOWN
```

```text
RelationshipStatus:
UNKNOWN / OBSERVED / ESTABLISHED / REJECTED
```

```text
TemporalStatus:
UNKNOWN / CURRENTLY_OBSERVED / HISTORICAL
```

A numerical Confidence model may be reconsidered only if:

- its semantics are precisely defined;
- representative validation data exists;
- calibration is possible;
- it provides measurable value to the User.

---

## Current Validation Scenarios

The architecture and Domain Model have been validated conceptually against two structurally different Discovery scenarios.

### Scenario 001: Gmail Service Discovery

The User connects a Gmail account containing several years of email history.

The framework attempts to identify Services through authorized email metadata without treating every sender as an Account Relationship.

The scenario validates:

- Gmail Connector isolation;
- metadata-first Discovery;
- Progressive Permission;
- email Observation creation;
- sender and domain extraction;
- Candidate Detection;
- Entity Resolution;
- Evidence Classification;
- multilingual ambiguity;
- Evidence Aggregation;
- historical Relationships;
- explainability;
- partial collection;
- graceful degradation when AI is unavailable.

Document:

```text
docs/scenarios/001-gmail-service-discovery.md
```

### Scenario 002: Password Manager Service Discovery

The User connects or imports an authorized Password Manager source.

The framework attempts to discover Services from minimized non-secret metadata such as:

```text
title
username reference
URI
record timestamps
```

without requiring:

```text
password values
OTP seeds
recovery codes
private keys
secret tokens
```

The scenario validates:

- source-independent Connector boundaries;
- non-email ObservationTypes;
- sensitive-source minimization;
- deterministic URL and hostname processing;
- cross-source Service convergence;
- Password Manager Evidence;
- multiple Identity references;
- source-specific temporal semantics;
- historical credential records;
- unresolved Services;
- Account remaining a Candidate Domain Concept.

Document:

```text
docs/scenarios/002-password-manager-service-discovery.md
```

---

## Software Contracts

The initial Discovery pipeline is documented through seven aligned software contracts.

### 01. Connector Contract

Defines the Provider-specific integration and security boundary.

Key responsibilities include:

- capability discovery;
- authorization;
- permission analysis;
- collection;
- minimization;
- Observation creation;
- continuation;
- partial collection;
- Provider-independent errors;
- independent ConnectedSource lifecycle.

```text
docs/interfaces/01-connector-contract.md
```

### 02. Observation Contract

Defines the Provider-independent source-derived representation:

```text
Common Observation Envelope
            +
Typed Payload
```

Observation is a Core Domain Entity and belongs to exactly one ConnectedSource.

```text
docs/interfaces/02-observation-contract.md
```

### 03. Service Candidate Detector Contract

Determines whether an Observation should participate in Service Discovery.

It distinguishes:

```text
CANDIDATE
NOT_CANDIDATE
UNKNOWN
```

without assigning a canonical Service.

```text
docs/interfaces/03-service-candidate-detector-contract.md
```

### 04. Entity Resolver Contract

Maps ServiceIdentifiers to canonical Services.

It supports:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

and preserves the distinction:

```text
NORMALIZATION != RESOLUTION
```

The EntityResolver may depend on a ServiceRegistry boundary but does not implicitly own canonical Service creation.

```text
docs/interfaces/04-entity-resolver-contract.md
```

### 05. Evidence Classifier Contract

Interprets Observations and creates semantic Evidence candidates.

It supports:

- deterministic-first classification;
- optional AI escalation;
- multilingual input;
- zero, one or multiple Evidence items;
- UNKNOWN classification;
- reclassification;
- EvidenceStatus lifecycle;
- User correction.

```text
docs/interfaces/05-evidence-classifier-contract.md
```

### 06. Evidence Aggregator Contract

Builds a structured, rebuildable EvidenceAggregate from current Evidence.

The default current view normally includes:

```text
ACTIVE Evidence
```

and excludes:

```text
SUPERSEDED Evidence
REJECTED Evidence
```

EvidenceAggregate is a Derived View rather than authoritative Domain state.

```text
docs/interfaces/06-evidence-aggregator-contract.md
```

### 07. Relationship Assessor Contract

Interprets an EvidenceAggregate and produces a RelationshipAssessmentResult.

It determines:

```text
RelationshipStatus
+
TemporalStatus
+
Evidence basis
+
Reason codes
+
Warnings
```

The application layer may then create or update the current User-Service Relationship.

```text
docs/interfaces/07-relationship-assessor-contract.md
```

---

### Documentation Structure

The current documentation set is organized as:

```text
docs/
├── architecture/
│   └── 01-identity-and-service-discovery.md
│
├── domain/
│   └── 01-discovery-domain-model.md
│
├── implementation/
│   └── 01-discovery-implementation-model.md
│
├── scenarios/
│   ├── 001-gmail-service-discovery.md
│   └── 002-password-manager-service-discovery.md
│
└── interfaces/
    ├── 01-connector-contract.md
    ├── 02-observation-contract.md
    ├── 03-service-candidate-detector-contract.md
    ├── 04-entity-resolver-contract.md
    ├── 05-evidence-classifier-contract.md
    ├── 06-evidence-aggregator-contract.md
    └── 07-relationship-assessor-contract.md
```

The documentation has four different normative roles:

```text
Architecture
    |
    v
defines system responsibilities and boundaries

Domain Model
    |
    v
defines Domain semantics and classifications

Software Contracts
    |
    v
define behavioral processing boundaries

Implementation Model
    |
    v
defines the initial executable software representation
```

The scenarios remain historical validation artifacts showing how the architecture evolved through empirical design questions.

Current normative implementation guidance is defined by:

```text
docs/implementation/01-discovery-implementation-model.md
```

## Key Architecture Decisions

The current Discovery architecture includes the following decisions.

### Evidence-Based Discovery

A discovered Service does not imply that it currently holds personal data.

Discovery identifies observable Evidence of current or historical Relationships.

### Multiple Discovery Sources

No individual source defines the complete User footprint.

Multiple SourceTypes and multiple ConnectedSources may contribute to the same canonical Service.

### Unknown Is Valid

Unknown, unresolved and ambiguous outcomes must remain explicitly representable.

### Local-First

Sensitive information should be processed locally whenever technically practical.

### Explainability

Relationships must remain explainable through Evidence and provenance.

### Discovery and Acquisition Are Separate

Discovering a Service and obtaining personal data from that Service are separate capabilities.

### Provider-Independent AI

The framework must not depend on one AI Provider.

### Deterministic Processing First

AI must not replace reliable deterministic processing unnecessarily.

### Progressive Permission

Additional access requires an explicit capability need and User authorization.

### Preserve Source Provenance

Derived conclusions must remain traceable to their supporting Observations and processing history.

### Multiple ConnectedSource Instances

The User may connect multiple independent source instances, including multiple instances using the same Provider and Connector implementation.

### Connector as Data-Minimization Boundary

Provider information unnecessary for the requested capability should not cross the Connector boundary.

### Provider-Neutral ObservationTypes

Equivalent source semantics should use equivalent framework ObservationTypes where practical.

### Parallel Resolution and Classification

Entity Resolution and Evidence Classification are independent processing branches.

Either may succeed while the other remains unresolved.

### EvidenceAggregates Are Derived State

Aggregates must remain reconstructable from authoritative Evidence where Evidence is retained.

### Separate Relationship and Temporal Status

Relationship support and temporal interpretation are separate dimensions.

### No Numerical Confidence Initially

The initial Discovery model uses explicit states, provenance and explanations rather than uncalibrated numerical scores.

---

## Failure Model

Technical failures must remain separate from valid Domain uncertainty.

For example:

```text
Connector failure
       !=
No Observations found
```

```text
Candidate Detector failure
       !=
NOT_CANDIDATE
```

```text
Entity Resolver failure
       !=
UNRESOLVED
```

```text
Evidence Classifier failure
       !=
UNKNOWN
```

```text
Evidence Aggregator failure
       !=
EMPTY
```

```text
Relationship Assessor failure
       !=
RelationshipStatus.UNKNOWN
```

This distinction is preserved throughout the Discovery pipeline.

---

### Current Project Status

The project has completed its first Discovery architecture, Domain and implementation-design consolidation cycle.

Current status:

```text
1. Architecture v0.3
   COMPLETE

2. Domain Model v0.3
   COMPLETE

3. Contract Alignment
   COMPLETE

   01 Connector
   02 Observation
   03 ServiceCandidateDetector
   04 EntityResolver
   05 EvidenceClassifier
   06 EvidenceAggregator
   07 RelationshipAssessor

4. README and Repository Consistency
   COMPLETE

5. Implementation Model v0.1
   COMPLETE

6. Python Project Skeleton
   NEXT

7. Gmail Vertical MVP
   PLANNED
```

The project has therefore completed the transition from:

```text
conceptual architecture
```

through:

```text
implementation-oriented design
```

and is now ready to begin:

```text
executable implementation
```

No production-ready Discovery engine is currently claimed.

The Architecture, Domain Model, contracts and Implementation Model remain experimental and may evolve when executable code and real Gmail-derived data expose validated requirements or inconsistencies.

At this stage, new abstractions should primarily be introduced in response to:

```text
implementation evidence

test results

empirical Gmail behavior

privacy constraints

or new validated cross-source requirements
```

rather than speculative design.

### Next Step: Python Project Skeleton

The Discovery Implementation Model is now defined.

The next repository phase is executable implementation.

The first step is to create the Python project skeleton described by:

```text
docs/implementation/01-discovery-implementation-model.md
```

The initial structure should follow the implementation-model boundaries:

```text
src/
└── personal_data_governance/
    │
    ├── domain/
    │   ├── entities/
    │   ├── values/
    │   ├── enums/
    │   └── views/
    │
    ├── application/
    │   ├── ports/
    │   ├── values/
    │   ├── results/
    │   └── services/
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

The implementation begins with:

```text
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
Ports / Protocols
        |
        v
In-Memory Repositories
        |
        v
ServiceRegistry
        |
        v
Deterministic Discovery Components
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

The initial executable architecture is intentionally:

```text
Python
+
modular monolith
+
ports and adapters
+
typed Domain model
+
in-memory infrastructure first
+
deterministic-first Discovery
```

The initial implementation does not require:

```text
microservices

graph database

remote persistence

remote AI

production synchronization

Account Entity

Organization Entity

numerical Confidence
```

The purpose of the Python skeleton is to make the established boundaries executable before introducing Gmail-specific integration complexity.

## First Vertical Implementation: Gmail Discovery MVP

After the Implementation Model, the first executable vertical slice will be:

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

The MVP should validate the architecture using real Gmail-derived data while preserving:

- metadata-first collection;
- Progressive Permission;
- Provider isolation;
- data minimization;
- deterministic-first processing;
- UNKNOWN, UNRESOLVED and AMBIGUOUS states;
- EvidenceStatus lifecycle;
- RelationshipStatus and TemporalStatus separation;
- no arbitrary numerical Confidence;
- explainability;
- provenance;
- local-first behavior where practical.

---

## Implementation Principles

The implementation should not collapse the architecture into:

```text
Gmail
  |
  v
one large script
  |
  v
Service list
```

Provider-specific logic should remain behind Connector boundaries.

Domain processes should operate on common framework concepts.

The dependency direction should remain conceptually:

```text
Infrastructure
      |
      v
Application
      |
      v
Domain abstractions
```

Provider APIs and persistence technologies should depend on framework interfaces rather than forcing the Domain to depend on Provider-specific implementations.

---

## Non-Goals of the Initial MVP

The Gmail Vertical MVP is not expected to solve:

- full mailbox semantic understanding;
- message attachment analysis;
- automatic Account deletion;
- automated Data Subject Access Requests;
- production-scale continuous synchronization;
- final Service ontology;
- final Organization model;
- final Account model;
- final Service Graph persistence technology;
- complete multilingual classification;
- complete Evidence taxonomy;
- numerical Confidence;
- production-grade AI integration;
- support for every email Provider.

The objective is to validate one complete architectural path end to end.

---

## Guiding Principles

The project follows several guiding principles:

```text
Evidence before inference

Unknown is valid

Deterministic first

Local-first processing

Minimum necessary access

Progressive Permission

Provider independence

Source provenance

Explainable conclusions

No fabricated certainty

No unnecessary secrets

Derived state remains rebuildable

Implementation evidence before new abstractions
```

---

## Licensing

The intended licensing model is:

- permitted non-commercial use: free;
- commercial use: subject to a separate commercial licence.

The final licence has not yet been selected.

Until explicit licensing terms are added to the repository, no additional rights should be assumed beyond those provided by applicable copyright law.

Contributors and users should review the final licence before using the project outside personal evaluation or authorized development activities.

---

### Repository Maturity

**Status: Experimental / Implementation-Ready**

The repository currently contains:

- consolidated Architecture v0.3;
- consolidated Domain Model v0.3;
- two historical validation scenarios;
- seven aligned software contracts;
- Discovery Implementation Model v0.1;
- explicit Python package and dependency boundaries;
- initial Domain-type representations;
- Processing Result boundaries;
- repository and ServiceRegistry ports;
- Evidence lifecycle implementation semantics;
- resolved, unresolved and ambiguous aggregation semantics;
- initial deterministic Gmail Vertical MVP strategy.

The repository does not yet contain a production-ready Discovery engine.

The next maturity transition is:

```text
Implementation-Ready
        |
        v
Executable Vertical Slice
```

through the Gmail Vertical MVP.

The first implementation is intended to validate whether:

```text
Architecture v0.3

+

Domain Model v0.3

+

Discovery Contracts v0.1

+

Implementation Model v0.1
```

survive contact with executable code and real source-derived behavior.

Interfaces, policies and implementation choices may still change when implementation evidence demonstrates a concrete need.

Architectural changes should not be introduced solely for hypothetical future requirements.

## Guiding Principle

The project is built around a simple idea:

> **People should be able to understand where their personal data goes, what others may know about them and what control they have.**

The framework should help build that understanding without becoming another unnecessary holder of the User's complete digital life.
