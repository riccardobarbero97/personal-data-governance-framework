# Personal Data Governance Framework

> Know who may have your data. Understand what they know. Take back control.

## Overview

Every day, people share personal information with dozens or even hundreds of digital services.

Email addresses, phone numbers, names, addresses, payment information, locations, interests, account activity, behavioral information and inferred attributes gradually become distributed across an ecosystem that most individuals can no longer see or understand.

The problem is simple:

> **We generate and share personal data continuously, but we do not have a practical way to understand who has it, what they know about us, and what we can do about it.**

The **Personal Data Governance Framework** explores a user-centric approach to solving this problem.

The long-term objective is to enable individuals to progressively discover, understand, map, monitor and govern their personal data footprint.

---

## The Idea

The framework starts from digital identities explicitly provided by the user.

For example:

```text
Email addresses
Phone numbers
Usernames
Google accounts
Apple accounts
Microsoft accounts
```

From these starting points, authorized discovery mechanisms can identify evidence of relationships with digital services.

For example:

```text
User
 │
 ▼
Identity
 │
 ▼
Discovery Sources
 │
 ├── Email
 ├── Identity Providers
 ├── Password Managers
 ├── Browser
 └── Manual Input
 │
 ▼
Evidence
 │
 ▼
Services
 │
 ▼
Relationships
```

A detected relationship does **not** mean that the framework automatically assumes which personal information a service holds.

Instead, discovery creates the foundation for subsequent stages.

---

## Long-Term Vision

The broader framework is currently envisioned as:

```text
IDENTITY
   │
   ▼
DISCOVER
   │
   ▼
REQUEST
   │
   ▼
INGEST
   │
   ▼
UNDERSTAND
   │
   ▼
MAP
   │
   ▼
MONITOR
   │
   ▼
ACT
```

### Identity

Define the digital identities belonging to the user.

### Discover

Identify services and organizations with which those identities appear to have or have had relationships.

### Request

Determine how the user can obtain the personal data held by an identified organization.

Possible mechanisms may include:

- account data exports;
- privacy portals;
- APIs;
- data portability mechanisms;
- data subject access requests;
- other supported mechanisms.

### Ingest

Process information returned by different services and convert heterogeneous formats into a common internal representation.

### Understand

Identify and classify personal information contained in the acquired data.

### Map

Build a navigable model connecting:

```text
Person
   ↕
Identity
   ↕
Service
   ↕
Personal Data
```

This should eventually allow questions such as:

> Which organizations know my phone number?

or:

> What information does this organization appear to hold about me?

### Monitor

Continuously detect changes to the user's observable digital footprint.

### Act

Help the user understand and, where appropriate, exercise available controls over their personal information.

---

## Observed Footprint, Not Absolute Truth

The framework does not attempt to claim that it can discover every piece of personal information that exists about an individual.

That would not be technically realistic.

Instead, the framework builds an:

> **Observed Personal Data Footprint**

Every conclusion should distinguish between:

- observed facts;
- supporting evidence;
- inferred relationships;
- confirmed information;
- unknown information.

Uncertainty is part of the data model rather than something the framework attempts to hide.

---

## Privacy by Design

A system designed to improve personal privacy should not become another centralized repository containing everything about a person.

For this reason, the project is being designed around a **local-first** principle.

Where technically practical:

```text
Raw Personal Data
        │
        ▼
 Local Processing
        │
        ▼
Structured Evidence
        │
        ▼
Minimum Necessary Storage
```

Sensitive source data should remain on the user's device whenever possible.

External processing should be deliberate, transparent and controllable by the user.

---

## AI

Artificial intelligence may become an important component of the framework, but it is not intended to replace deterministic software unnecessarily.

Potential AI-assisted capabilities include:

- evidence classification;
- service identification;
- entity resolution;
- personal-data extraction;
- understanding heterogeneous data exports;
- adapting to changing data-access procedures;
- reasoning across multiple evidence sources.

The framework is intended to remain **AI-provider independent**.

Future implementations should be capable of supporting:

```text
Local models
Self-hosted models
Free models
Commercial APIs
User-provided AI providers
Deterministic fallbacks
```

The user should not be locked into a specific AI vendor.

---

## Architecture

The framework is intentionally modular.

Conceptually:

```text
                    ┌───────────────────┐
                    │      Identity     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │     Discovery     │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Relationship Graph│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Data Acquisition  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Data Understanding│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Personal Data Graph│
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Monitoring &      │
                    │ Governance        │
                    └───────────────────┘
```

The exact architecture is still being designed and will evolve as individual use cases are tested.

---

## Current Focus

The project is currently in the **design and validation phase**.

The first component being defined is the **Identity & Service Discovery layer**.

Its initial problem is:

> Given one or more digital identities provided by a user, how can we reliably and explainably discover services with which that person has or has had a relationship?

The first concrete scenario being analyzed is:

> A user connects a Gmail account containing several years of email history. How can the framework determine which digital services that person uses or has used without incorrectly treating every email sender as an account relationship?

---

## Documentation

Current design documents:

- docs/01-identity-and-service-discovery.md

Additional architecture documents will be added as the project evolves.

---

## Project Status

**Experimental / Early Design**

This repository currently contains architecture and design work.

APIs, interfaces, data models and implementation details should be considered unstable until the core concepts have been validated through concrete use cases.

---

## Licensing

The intended licensing model is:

- permitted non-commercial use: free;
- commercial use: separate commercial license required.

The final license has not yet been selected.

Until explicit licensing terms are added to this repository, no additional rights should be assumed beyond those provided by applicable copyright law.

---

## Guiding Principle

The project is built around a simple idea:

> **People should be able to understand where their personal data goes, what others know about them, and what control they have over it.**
