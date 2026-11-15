# Scenario 002 - Password Manager Service Discovery

**Status:** Draft  
**Scenario ID:** SCN-002  
**Domain:** Identity and Service Discovery  
**Source:** Password Manager  
**Primary Capability:** Service Discovery  
**Architecture Under Test:** Identity & Service Discovery Draft v0.2  

---
> **Historical Validation Note**
>
> This scenario is a historical architecture-validation artifact.
>
> It was intentionally executed against:
>
> ```text
> Identity & Service Discovery
> Draft v0.2
> ```
>
> Its purpose was to test whether the architecture derived primarily from Gmail Service Discovery remained valid when applied to a structurally different and significantly more sensitive source: a Password Manager.
>
> The comparison described by this scenario has since been completed.
>
> Its findings contributed directly to:
>
> ```text
> Architecture Draft v0.3
>        |
>        v
> Domain Model Draft v0.3
>        |
>        v
> aligned Discovery software contracts
> ```
>
> In particular, the scenario helped validate or expose concepts that are now part of the consolidated Discovery baseline, including:
>
> ```text
> ConnectedSource
>
> Connector as a data-minimization boundary
>
> provider-neutral Observations
>
> typed Observation payloads
>
> Candidate Detection
>
> ServiceIdentifier
>
> cross-source Entity Resolution
>
> independent Entity Resolution and Evidence Classification
>
> Evidence lifecycle
>
> User-Service Relationship
>
> multiple Identity references
>
> source-aware temporal semantics
>
> Progressive Permission
>
> deterministic-first processing
> ```
>
> Questions raised in this scenario about concepts such as:
>
> ```text
> Account
> Relationship cardinality
> sensitive-field filtering
> cross-source Evidence
> ```
>
> were subsequently evaluated during the Domain Model and software-contract design cycle.
>
> The consolidated model currently defines:
>
> ```text
> User
>   |
>   v
> Relationship
>   |
>   v
> Service
> ```
>
> while preserving relevant Identity references.
>
> `Account` remains a Candidate Domain Concept rather than a Core Domain Entity.
>
> The scenario's final section describing a future comparison with Architecture Draft v0.2 should therefore be understood as part of the historical design sequence rather than as the repository's current next step.
>
> The current normative references are:
>
> ```text
> docs/architecture/01-identity-and-service-discovery.md
>
> docs/domain/01-discovery-domain-model.md
>
> docs/interfaces/
> ```
>
> This scenario should be preserved as evidence of:
>
> ```text
> what was tested
>        |
>        v
> which questions emerged
>        |
>        v
> how the architecture evolved
> ```
>
> rather than rewritten to make its original validation context appear as though it had always targeted Architecture Draft v0.3.
---

## 1. Purpose

This scenario tests whether the Identity and Service Discovery architecture defined in Draft v0.2 remains valid when applied to a Discovery Source that is structurally different from email.

Scenario 001 tested Gmail, where discovery begins primarily from messages and communication metadata.

A password manager presents a different structure.

Instead of:

```text
Message
  |
  v
Sender
  |
  v
Domain
  |
  v
Service Candidate
```

the source may expose information conceptually similar to:

```text
Credential Entry
      |
      v
Website / URI
      |
      v
Domain
      |
      v
Service Candidate
```

The objective of this scenario is therefore not simply to add password-manager support.

Its primary objective is to test whether the abstractions introduced after Scenario 001 are genuinely source-independent.

Specifically, this scenario tests:

- Connector;
- Observation;
- Service Candidate Detection;
- Entity Resolution;
- Evidence Classification;
- Evidence Aggregation;
- Relationship Assessment;
- Progressive Permission;
- provenance preservation;
- uncertainty;
- Service Graph integration.

A particularly important constraint is:

> Service Discovery should not require access to password values.

The framework needs evidence that a relationship with a Service may exist or may have existed.

It does not need the secret used to authenticate to that Service.

---

## 2. User Scenario

The user connects a supported password manager containing credential entries accumulated over several years.

The password manager may contain entries associated with:

- currently active accounts;
- abandoned accounts;
- historical accounts;
- duplicate credentials;
- multiple accounts for the same Service;
- different identities used with the same Service;
- obsolete domains;
- mobile applications;
- manually created records;
- automatically-generated records;
- credentials whose associated Service can no longer be identified.

A conceptual password-manager entry might contain information such as:

```text
Title:
Spotify

Username:
user@example.com

Website:
https://accounts.spotify.com

Password:
********
```

For Service Discovery, the password value itself is unnecessary.

The framework should attempt to discover:

```text
Service:
Spotify

Observed Identifier:
accounts.spotify.com

Associated Identity:
user@example.com

Evidence:
PASSWORD_MANAGER_ENTRY
```

without retrieving, analyzing or persisting:

```text
Password:
********
```

The system must aggregate multiple relevant entries rather than treating each password-manager record as an independent Service.

---

## 3. Scope

Scenario 002 covers:

- explicit authorization to access a password-manager source;
- source capability discovery;
- retrieval of non-secret metadata where supported;
- translation of source-specific entries into Observations;
- URL and domain normalization;
- Service Candidate Detection;
- Entity Resolution;
- Evidence Classification;
- Evidence Aggregation;
- association with known Identity Seeds where possible;
- historical relationship discovery;
- duplicate handling;
- uncertainty;
- provenance;
- Progressive Permission;
- Service Graph integration.

Scenario 002 does not attempt to solve:

- password extraction;
- password-strength analysis;
- password reuse detection;
- compromised-password detection;
- credential rotation;
- automatic login;
- automated password changes;
- secret synchronization;
- password sharing;
- account deletion;
- personal-data acquisition from discovered Services.

These may represent useful security or governance capabilities, but they are not required for Service Discovery.

---

## 4. Security Boundary

Password managers contain authentication secrets.

The password manager must therefore be considered a highly sensitive Discovery Source.

The central security rule for this scenario is:

```text
SERVICE DISCOVERY DOES NOT REQUIRE PASSWORD VALUES
```

A Connector should retrieve only the minimum non-secret information necessary to identify potential Service Relationships.

Conceptually:

```text
Password Manager Entry
        |
        +-- Title ----------------+
        |                         |
        +-- Username -------------+--> Discovery Observation
        |                         |
        +-- Website / URI --------+
        |
        +-- Password ------------ X
                                   \
                                    Not required
                                    for discovery
```

The exact metadata available depends on the password manager and the authorization mechanism provided by that product.

Scenario 002 therefore defines required semantics rather than assuming a universal password-manager API.

---

## 5. Password Manager as a Discovery Source

A Password Manager is the external Discovery Source.

Communication with it should occur through a source-specific Connector.

Conceptually:

```text
Password Manager
       |
       v
Password Manager Connector
       |
       v
Framework Observations
```

Possible implementations may eventually include Connectors for products that expose appropriate authorized integration mechanisms.

The core Discovery Engine must not depend on a particular password-manager vendor.

---

## 6. Connector

A password-manager Connector is responsible for interactions specific to the external source.

Its responsibilities may include:

- requesting authorization;
- determining available capabilities;
- retrieving authorized entry metadata;
- handling pagination or batching where applicable;
- handling source-specific errors;
- translating entries into framework Observations;
- preventing unnecessary secret retrieval;
- preserving source identifiers required for provenance.

The conceptual boundary is:

```text
Vendor-Specific Representation
           |
           v
      Connector
           |
           v
Framework Observation
```

Downstream components should not need to understand vendor-specific password-manager objects.

---

## 7. Progressive Permission

Scenario 002 provides a strong test of Progressive Permission because the source may expose substantially more sensitive information than Service Discovery requires.

The preferred permission model is:

```text
No Access
    |
    v
Non-Secret Metadata Access
    |
    v
Service Discovery
```

Access to authentication secrets must not occur merely because the external source is a password manager.

The general rule is:

> Access sensitivity should be determined by the capability being performed, not by everything technically available from the connected source.

For Service Discovery:

```text
Required:
- useful record identifier
- title or label where available
- associated website / URI where available
- username or identity reference where necessary and authorized
- relevant timestamps where available

Not Required:
- password value
- secret notes unrelated to discovery
- recovery codes
- private keys
- one-time-password secrets
```

The exact fields depend on individual providers.

The principle does not.

---

## 8. Observation Creation

A password-manager entry should be translated into an Observation without immediately assuming its meaning.

Example source entry:

```text
Title:
Spotify

Username:
riccardo@example.com

Website:
https://accounts.spotify.com
```

may generate a conceptual Observation such as:

```json
{
  "source": "password_manager",
  "source_record_id": "record_123",
  "title": "Spotify",
  "username": "riccardo@example.com",
  "uri": "https://accounts.spotify.com",
  "observed_domain": "accounts.spotify.com"
}
```

No password field is present.

At this point the framework knows only that an authorized source contains a record with these characteristics.

Therefore:

```text
OBSERVATION != EVIDENCE
```

continues to hold.

This directly tests an architectural distinction introduced in Draft v0.2.

---

## 9. Identity Association

Password-manager entries frequently contain usernames.

Some usernames may correspond to Identity Seeds already declared by the user.

Example:

```text
Identity Seeds:

personal@example.com
oldmail@example.net
```

Password-manager Observation:

```text
Username:
personal@example.com
```

The framework may therefore associate the Observation with:

```text
identity_001
```

without treating the username itself as proof of ownership.

Conceptually:

```text
Observation Username
        |
        v
Identity Matching
        |
   +----+----+
   |         |
 match     no match
   |         |
   v         v
Existing   Unassociated
Identity   Identifier
```

An unmatched username is not necessarily invalid.

It may represent:

- an old email address;
- a username rather than an email;
- another identity belonging to the user;
- a shared credential;
- another person's account;
- obsolete information;
- incorrect information.

Scenario 002 does not define automatic creation of new Identity Seeds from password-manager usernames.

That remains an Open Question.

---

## 10. Service Candidate Detection

Password-manager records are structurally different from email communication.

A credential-like record generally provides stronger initial evidence of an account-related interaction than a generic email or website visit.

However, not every password-manager record necessarily represents a conventional online Service.

Possible entries may include:

```text
Wi-Fi passwords
Router credentials
Local applications
Database credentials
Server credentials
Software licenses
Secure notes
Internal systems
Shared credentials
Test accounts
Archived records
```

Service Candidate Detection must therefore still exist.

Conceptually:

```text
Password Manager Observation
          |
          v
  Candidate Detection
        /     \
      yes      no
       |        |
       v        v
    Entity     Ignore for
   Resolution  this capability
```

This validates that Candidate Detection is useful beyond email.

---

## 11. Identifier Extraction

For web Services, a URI may provide useful technical identifiers.

Example:

```text
https://accounts.spotify.com/login
```

may produce:

```text
Hostname:
accounts.spotify.com
```

and a normalized domain candidate:

```text
spotify.com
```

Conceptually:

```text
URI
 |
 v
Hostname Extraction
 |
 v
Domain Normalization
 |
 v
Observed Identifier
```

This operation should be deterministic.

An AI model is not required to parse a URL.

This supports the architectural principle:

> Deterministic operations should remain deterministic.

---

## 12. Entity Resolution

Entity Resolution attempts to associate observed identifiers with canonical Services.

Example:

```text
Title:
Spotify

URI:
https://accounts.spotify.com

Observed Domain:
spotify.com
        |
        v
Entity Resolution
        |
        v
Spotify
```

Multiple entries may resolve to the same Service.

For example:

```text
https://spotify.com
https://accounts.spotify.com
https://open.spotify.com
        |
        v
     Spotify
```

This validates:

```text
DOMAIN != SERVICE
```

in a second, structurally different source.

---

## 13. Cross-Source Entity Resolution

One of the most important objectives of Scenario 002 is to determine whether evidence from different Discovery Sources can converge on the same Service.

Scenario 001 may have produced:

```text
Gmail Observation
      |
      v
spotify.com
      |
      v
Spotify
```

Scenario 002 may independently produce:

```text
Password Manager Observation
      |
      v
accounts.spotify.com
      |
      v
Spotify
```

These should not create:

```text
Spotify-from-Gmail

Spotify-from-Password-Manager
```

as unrelated canonical Services.

Instead:

```text
            Spotify
           /       \
          /         \
         v           v
   Gmail Evidence   Password Manager Evidence
```

This represents the first explicit test of multi-source convergence in the architecture.

---

## 14. Resolution Provenance

Cross-source Entity Resolution must not destroy source-specific information.

The framework should preserve:

```text
Source:
Password Manager

Original URI:
https://accounts.spotify.com/login

Observed Hostname:
accounts.spotify.com

Normalized Domain:
spotify.com

Resolved Service:
Spotify
```

Similarly, Gmail-derived identifiers remain independently preserved.

The canonical Service is therefore supported by multiple independently traceable observations.

---

## 15. Evidence Classification

A password-manager record should produce Evidence describing what the record implies.

An initial scenario-specific category may be:

```text
PASSWORD_MANAGER_ENTRY
```

Conceptually:

```text
Password Manager Observation
          |
          v
   Evidence Classifier
          |
          v
PASSWORD_MANAGER_ENTRY
```

The scenario-specific taxonomy is deliberately minimal.

The important architectural test is whether:

```text
Observation
     |
     v
Evidence Classification
     |
     v
Evidence
```

remains useful outside Gmail.

---

## 16. Is Classification Necessary?

Scenario 002 exposes an important architectural question.

A password-manager record may have less semantic ambiguity than an email subject.

For example:

```text
Entry
Title: Spotify
URI: accounts.spotify.com
Username: user@example.com
```

does not require an LLM to determine that the source contains a password-manager record associated with Spotify.

Evidence Classification may therefore be almost deterministic:

```text
Valid Service-Oriented Password Manager Record
                  |
                  v
       PASSWORD_MANAGER_ENTRY
```

This does not invalidate the Evidence Classifier abstraction.

Instead, it demonstrates that different Connectors may require different classification complexity.

For Gmail:

```text
Rules
  +
possible AI
```

may be required.

For password-manager metadata:

```text
Deterministic classification
```

may be sufficient for most observations.

This is desirable.

The architecture should not force AI into a pipeline that does not need it.

---

## 17. Evidence Semantics

A password-manager entry may represent relatively significant evidence of a Service Relationship.

However, it does not prove:

- that the account is still active;
- that the credentials still work;
- that the user created the account;
- that the user owns the account;
- that the Service still exists;
- that the associated username still belongs to the user;
- that the Service currently holds specific personal data.

Therefore:

```text
PASSWORD_MANAGER_ENTRY
        !=
CONFIRMED CURRENT ACCOUNT
```

and:

```text
PASSWORD_MANAGER_ENTRY
        !=
CURRENT DATA POSSESSION
```

Evidence remains Evidence.

---

## 18. Evidence Aggregation

A password manager may contain multiple entries for the same Service.

Example:

```text
Spotify - old account
Spotify
Spotify Family
accounts.spotify.com
```

These must not automatically become four distinct Service Relationships.

Conceptually:

```text
Entry A ----+
            |
Entry B ----+
            |
Entry C ----+--> Spotify --> Aggregated Evidence
            |
Entry D ----+
```

Aggregation must preserve the fact that multiple entries existed while avoiding artificial duplication of canonical Services.

---

## 19. Multiple Identities for the Same Service

The password manager may contain:

```text
Spotify
Username: personal@example.com
```

and:

```text
Spotify
Username: oldmail@example.net
```

Both may resolve to:

```text
Spotify
```

while being associated with different Identity Seeds.

Conceptually:

```text
personal@example.com ----+
                         |
                         v
                      Spotify
                         ^
                         |
oldmail@example.net -----+
```

The framework must not automatically assume that multiple usernames represent duplicate records.

They may represent:

- multiple accounts;
- migrated accounts;
- aliases;
- historical identities;
- shared accounts;
- duplicates.

Scenario 002 therefore tests the relationship between:

```text
Identity
Service
Relationship
```

more strongly than Scenario 001.

---

## 20. Historical Records

Password managers often retain credentials for Services that are no longer used.

An entry may therefore represent:

```text
Current Relationship
```

or:

```text
Historical Relationship
```

or:

```text
Unknown Relationship State
```

The existence of the record alone does not establish which state applies.

For example:

```text
Password Manager Entry Created: 2018
Last Modified: 2019
```

may suggest historical context, but modification timestamps cannot necessarily be interpreted as account activity.

The framework must distinguish:

```text
Source Record Timestamp
```

from:

```text
Service Activity Timestamp
```

unless the source semantics justify that interpretation.

This is an important provenance requirement.

---

## 21. Duplicate Records

Password managers may contain duplicate records because of:

- manual duplication;
- imports;
- migration between password managers;
- duplicate account creation;
- multiple URI variants;
- synchronization artifacts.

Duplicate detection must not destructively remove provenance.

For example:

```text
Record A
Record B
        |
        v
Potential Duplicate
        |
        v
Same Service
```

does not necessarily imply:

```text
Record A = Record B
```

The framework may aggregate their Service-level effect while retaining independent source records.

---

## 22. Shared Credentials

A password-manager entry may represent an account used by multiple people.

Examples could include:

```text
Family streaming account
Shared household account
Shared administrative account
Shared subscription
```

The presence of the credential in the user's password manager does not independently prove exclusive ownership.

Therefore:

```text
Stored Credential
       !=
Exclusive User Account
```

The framework should preserve uncertainty rather than fabricating ownership semantics.

---

## 23. Non-Web Credentials

Not every credential contains a useful web domain.

Examples:

```text
Local Application
Database
Router
NAS
VPN
Internal Server
Desktop Software
```

A record may therefore contain:

```text
Title:
Home Router

Username:
admin

URI:
192.168.1.1
```

This should not necessarily become a digital Service in the Personal Data Governance Service Graph.

Candidate Detection must be able to exclude records that are outside the current capability.

This provides another validation for keeping:

```text
Observation
```

separate from:

```text
Service Candidate
```

---

## 24. Missing URI

An entry may contain:

```text
Title:
Example Service

Username:
user@example.com

URI:
UNKNOWN
```

Entity Resolution may then use the title or other available metadata.

However, the system must be allowed to return:

```text
resolution_status = UNRESOLVED
```

if available information is insufficient.

The framework must not invent a domain or Service.

---

## 25. Obsolete Domains

A password-manager record may reference a domain that:

- no longer exists;
- redirects to another domain;
- belonged to an acquired Service;
- was replaced after rebranding.

Example:

```text
old-service.example
```

may historically correspond to a Service now located elsewhere.

The original identifier must remain preserved even if Entity Resolution maps it to a current canonical Service.

Conceptually:

```text
Historical Identifier
         |
         v
Entity Resolution
         |
         v
Current Canonical Service
```

without:

```text
Historical Identifier
         X
      deleted
```

---

## 26. AI Boundary

Scenario 002 provides an additional test of the principle:

> Use AI for ambiguity, not for everything.

Most routine processing in this scenario should be deterministic.

For example:

```text
URL parsing
Hostname extraction
Domain normalization
Identity matching
Known-Service lookup
Evidence classification for standard entries
```

should not require AI when deterministic logic is sufficient.

AI-assisted processing might become useful for unusual cases such as:

```text
Title:
My Music Account

URI:
UNKNOWN
```

when other non-secret metadata is available but ambiguous.

Even in such cases:

- AI must receive only the minimum necessary information;
- password values must not be provided;
- an unresolved outcome remains valid.

Scenario 002 therefore reinforces rather than weakens the deterministic-first architecture.

---

## 27. Relationship Assessment

Relationship Assessment considers accumulated Evidence associated with a Service.

For example:

```text
Service:
Spotify

Evidence:
PASSWORD_MANAGER_ENTRY
```

may indicate a likely historical or current account-style relationship.

If Scenario 001 has already produced:

```text
ACCOUNT_VERIFICATION
SUBSCRIPTION
PAYMENT
```

for the same Service, the combined representation becomes:

```text
                     Spotify
                        |
        +---------------+---------------+
        |                               |
        v                               v
   Gmail Evidence              Password Manager Evidence
        |                               |
 ACCOUNT_VERIFICATION           PASSWORD_MANAGER_ENTRY
 SUBSCRIPTION
 PAYMENT
```

This is stronger multi-source context than either source alone.

However, Scenario 002 still does not define a numerical Confidence score.

---

## 28. Cross-Source Evidence

Scenario 002 introduces the first direct test of Evidence convergence.

Conceptually:

```text
GmailConnector
      |
      v
Observations
      |
      v
Evidence
      |
      +-------------------+
                          |
                          v
                       Spotify
                          ^
                          |
      +-------------------+
      |
PasswordManagerConnector
      |
      v
Observations
      |
      v
Evidence
```

The framework should preserve:

```text
Source-specific provenance
```

while producing:

```text
Shared canonical Service identity
```

This is one of the central architectural requirements of the Personal Data Governance Framework.

---

## 29. Expected Output

A simplified Service-level output might be:

```json
{
  "service": {
    "name": "Spotify",
    "canonical_domain": "spotify.com",
    "resolution_status": "RESOLVED"
  },
  "observations": [
    {
      "source": "password_manager",
      "observed_domain": "accounts.spotify.com",
      "identity_reference": "identity_001"
    }
  ],
  "evidence": [
    {
      "source": "password_manager",
      "type": "PASSWORD_MANAGER_ENTRY",
      "classification_method": "RULE"
    }
  ],
  "relationship": {
    "status": "DISCOVERED"
  }
}
```

If evidence from Scenario 001 also exists:

```json
{
  "service": {
    "name": "Spotify",
    "canonical_domain": "spotify.com"
  },
  "evidence_sources": [
    "gmail",
    "password_manager"
  ]
}
```

These structures are illustrative.

They do not define the final persistent schema.

---

## 30. Explainability

The framework should be able to answer:

> Why was this Service discovered from my password manager?

For example:

```text
Spotify was discovered because:

- an authorized Password Manager Connector exposed a credential record;
- the record contained the URI accounts.spotify.com;
- accounts.spotify.com was normalized and resolved to Spotify;
- the record generated PASSWORD_MANAGER_ENTRY Evidence;
- no password value was required for this discovery.
```

If Gmail also supports the Relationship:

```text
Additional independent Evidence was found through Gmail.
```

The explanation should preserve source distinctions.

---

## 31. Privacy Requirements

### 31.1 Do Not Retrieve Secrets Without Need

Service Discovery should not retrieve:

```text
Password values
OTP seeds
Recovery codes
Private keys
Secret tokens
```

unless a separate future capability explicitly requires them and can justify that access.

---

### 31.2 Minimize Identity Exposure

Usernames may themselves be personal data.

If an entry can be resolved to a Service without persisting the full username, the framework should evaluate whether a minimized representation can be retained instead.

The final persistence strategy remains an Open Question.

---

### 31.3 Local-First Processing

Password-manager metadata should be processed locally where technically practical.

The default architecture should not transmit credential metadata to remote infrastructure merely for convenience.

---

### 31.4 AI Restrictions

Authentication secrets must not be transmitted to AI systems for Service Discovery.

If AI assists with ambiguous entity resolution, the input should be limited to non-secret information necessary for that task.

---

### 31.5 Connector Isolation

The component capable of communicating with the password manager should remain isolated from downstream components.

Conceptually:

```text
Password Manager
      |
      v
Privileged Connector Boundary
      |
      v
Minimized Observation
      |
      v
Discovery Engine
```

This minimizes the number of components exposed to sensitive source data.

---

## 32. Failure Modes

### 32.1 Authorization Denied

If the user denies access:

```text
Password Manager Discovery = unavailable
```

Other Discovery Sources continue functioning.

---

### 32.2 Insufficient Source Capability

A password manager may not expose the metadata required for discovery through a supported integration mechanism.

The framework must not assume that every password-manager product can support the same Connector capabilities.

Expected result:

```text
Capability Unsupported
```

rather than bypassing security boundaries.

---

### 32.3 Secret-Only Interface

If a source cannot provide the necessary metadata without also exposing unnecessary secret values, the architecture should evaluate whether the Connector can safely isolate and discard those secrets before releasing Observations downstream.

If this cannot be done safely, the source may be unsuitable for this discovery capability.

---

### 32.4 Entity Resolution Failure

Example:

```text
Title:
Old Account

URI:
UNKNOWN
```

Expected result:

```text
resolution_status = UNRESOLVED
```

---

### 32.5 Identity Matching Failure

A username does not correspond to any known Identity Seed.

Expected behavior:

```text
identity_reference = UNRESOLVED
```

The Observation may still contribute to Service Discovery without automatically creating a new Identity Seed.

---

### 32.6 Duplicate Ambiguity

Two similar records cannot safely be determined to represent:

```text
duplicate records
```

or:

```text
different accounts
```

They should remain independently traceable.

---

### 32.7 Partial Collection

If only part of the password-manager data is available:

```text
Analysis Status:
PARTIAL
```

must remain distinguishable from:

```text
Analysis Status:
COMPLETE
```

---

### 32.8 AI Unavailable

Routine discovery should continue deterministically.

Ambiguous observations may remain unresolved.

---

## 33. Architectural Validation

Scenario 002 evaluates several abstractions introduced or refined in Draft v0.2.

### 33.1 Connector

**Result:** Supported by the scenario.

Password-manager-specific authorization and retrieval can remain isolated behind a Connector.

---

### 33.2 Observation

**Result:** Supported by the scenario.

A credential record can produce a non-secret Observation before semantic interpretation.

This demonstrates that Observation is not specific to email messages.

---

### 33.3 Service Candidate Detection

**Result:** Supported by the scenario.

Not every password-manager entry represents an external digital Service relevant to Personal Data Governance.

Candidate Detection therefore remains useful.

---

### 33.4 Entity Resolution

**Result:** Supported by the scenario.

URIs, hostnames and other identifiers must still be normalized and mapped to canonical Services.

This reinforces:

```text
DOMAIN != SERVICE
```

---

### 33.5 Evidence Classification

**Result:** Supported, but with lower expected complexity than Gmail.

A password-manager record can generally be classified deterministically.

This demonstrates that the classifier abstraction can support source-specific strategies without requiring AI.

---

### 33.6 Evidence Aggregation

**Result:** Supported by the scenario.

Multiple records may correspond to one Service and should not create duplicate Service identities.

---

### 33.7 Relationship Assessment

**Result:** Supported by the scenario.

The presence of a credential record suggests a Relationship but does not independently prove current account status or current data possession.

---

### 33.8 Progressive Permission

**Result:** Strongly supported by the scenario.

The source contains information substantially more sensitive than Service Discovery requires.

The framework therefore benefits from capability-specific minimum access.

---

### 33.9 Provenance

**Result:** Strongly supported by the scenario.

Source record, URI, normalized identifier, resolved Service and Evidence must remain distinguishable.

---

### 33.10 AI for Ambiguity

**Result:** Supported by the scenario.

Routine password-manager discovery provides a concrete example where most of the pipeline should remain deterministic.

AI remains optional.

---

## 34. New Architectural Questions Exposed by Scenario 002

Scenario 002 does not currently invalidate the Draft v0.2 architecture.

However, it exposes several questions requiring further consideration.

### OQ-002-001 - Identity Matching

Should usernames discovered inside authorized sources be allowed to become candidate Identity Seeds?

For example:

```text
Known Identity Seeds:
user@gmail.com

Discovered Password Manager Username:
old-address@example.com
```

Should the framework:

```text
A. Preserve it only as an observed identifier
B. Suggest it to the user as a possible Identity Seed
C. Automatically create a new Identity Seed
```

Automatic creation may create incorrect identity assumptions.

---

### OQ-002-002 - Relationship Cardinality

How should multiple accounts with the same Service be represented?

Example:

```text
Spotify
  |
  +-- personal@example.com
  |
  +-- oldmail@example.net
```

Should this produce:

```text
one Service
two Relationships
```

or another model?

---

### OQ-002-003 - Service vs Account

Scenario 002 exposes a distinction that may become architecturally important:

```text
Service
   |
   v
Account
   |
   v
Identity
```

Draft v0.2 currently models primarily:

```text
Identity
   |
   v
Relationship
   |
   v
Service
```

Additional scenarios are required before deciding whether `Account` should become a first-class domain concept.

---

### OQ-002-004 - Sensitive Field Filtering

Should Connectors be responsible for ensuring that secret fields never leave the Connector boundary?

Conceptually:

```text
Source Record
    |
    v
Connector
    |
    +-- Secret Fields -> discard / isolate
    |
    v
Minimized Observation
```

This may become a general Connector security responsibility.

---

### OQ-002-005 - Cross-Source Relationship Assessment

How should Evidence from structurally different sources be combined?

Example:

```text
Gmail:
ACCOUNT_VERIFICATION

Password Manager:
PASSWORD_MANAGER_ENTRY
```

The architecture supports aggregation, but does not yet define how the combination should affect Relationship state.

---

### OQ-002-006 - Source Record Age

What temporal meaning should be assigned to source-specific timestamps?

A password-manager modification timestamp may describe:

```text
record modification
```

rather than:

```text
last Service activity
```

Temporal semantics must remain source-aware.

---

### OQ-002-007 - Shared Accounts

How should the framework represent a credential that may belong to:

```text
user
household
family
team
another person
```

without incorrectly attributing ownership?

---

## 35. Acceptance Criteria

Scenario 002 is considered architecturally supported when the framework can demonstrate the following behavior.

### Authorization

- [ ] Password-manager access requires explicit user authorization.
- [ ] Service Discovery does not require password values.
- [ ] The Connector requests only information necessary for discovery where supported by the source.
- [ ] Denying password-manager access does not prevent other Discovery Sources from operating.

### Connector

- [ ] Source-specific behavior remains inside the password-manager Connector.
- [ ] The Connector can produce framework Observations.
- [ ] Downstream components do not require vendor-specific password-manager objects.
- [ ] Secret fields do not become part of normal discovery Observations.

### Observation

- [ ] A password-manager record can produce an Observation without exposing a password value.
- [ ] Observation provenance remains available.
- [ ] Source timestamps retain their original semantics.

### Candidate Detection

- [ ] Web Service credentials can become Service candidates.
- [ ] Local, infrastructure or otherwise irrelevant credentials do not automatically become Personal Data Governance Services.

### Entity Resolution

- [ ] URIs can be deterministically parsed.
- [ ] Multiple URI variants can resolve to the same Service.
- [ ] Entity Resolution can return `UNRESOLVED`.
- [ ] Gmail-derived and password-manager-derived identifiers can potentially converge on the same Service.
- [ ] Original identifiers remain available after resolution.

### Identity

- [ ] Known usernames can be associated with existing Identity Seeds where justified.
- [ ] Unknown usernames do not automatically become verified Identity Seeds.
- [ ] Multiple identities can potentially relate to the same Service.

### Evidence

- [ ] A password-manager Observation can generate appropriate Evidence.
- [ ] Evidence Classification can operate deterministically.
- [ ] Password-manager Evidence does not automatically imply a currently active account.
- [ ] Evidence does not automatically imply current personal-data possession.

### Aggregation

- [ ] Multiple records for the same Service do not automatically create duplicate canonical Services.
- [ ] Duplicate handling preserves provenance.
- [ ] Evidence from multiple Discovery Sources remains distinguishable.

### Privacy and Security

- [ ] Password values are not required by the discovery pipeline.
- [ ] OTP secrets are not required.
- [ ] Recovery codes are not required.
- [ ] Secret values are not transmitted to AI for Service Discovery.
- [ ] Sensitive-source processing follows Progressive Permission.
- [ ] Connector boundaries minimize downstream exposure.

### Architecture

- [ ] `Connector` remains source-independent.
- [ ] `Observation` remains source-independent.
- [ ] `Service Candidate Detection` remains useful.
- [ ] `Entity Resolution` remains source-independent.
- [ ] `Evidence Classification` can use different strategies depending on the source.
- [ ] `Evidence Aggregation` supports cross-source Evidence.
- [ ] `Relationship Assessment` remains distinct from Evidence Classification.
- [ ] The final result can contribute to the same Service Graph used by Scenario 001.

---

## 36. Scenario Result

Scenario 002 tests whether the Draft v0.2 pipeline survives a source fundamentally different from Gmail.

The resulting conceptual pipeline is:

```text
Password Manager
       |
       v
Password Manager Connector
       |
       v
Minimized Non-Secret Observations
       |
       v
Service Candidate Detection
       |
       v
Identifier Extraction
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

This scenario reinforces the following architectural boundaries:

```text
SOURCE != CONNECTOR

SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

EVIDENCE != RELATIONSHIP

DOMAIN != SERVICE

RELATIONSHIP != CURRENT DATA POSSESSION
```

It also introduces an important security boundary:

```text
SOURCE SECRET
     !=
DISCOVERY OBSERVATION
```

For Password Manager Service Discovery, authentication secrets are not part of the required discovery data.

---

## 37. Preliminary Architectural Finding

Scenario 002 does not currently expose a contradiction that requires abandoning the Draft v0.2 architecture.

Instead, it provides preliminary support for the architecture's source-independent structure.

In particular:

```text
Gmail
  |
  v
GmailConnector
  |
  v
Observations
      \
       \
        +--> Shared Discovery Pipeline --> Service Graph
       /
      /
Password Manager
  |
  v
PasswordManagerConnector
  |
  v
Observations
```

The most significant new design question exposed by Scenario 002 is the possible distinction between:

```text
Identity
Service
Account
Relationship
```

A password-manager source makes the concept of an individual account more visible than Gmail alone.

However, Scenario 002 by itself does not provide sufficient evidence to introduce `Account` as a new first-class domain entity.

That decision should remain open until additional scenarios determine whether the concept is required across the framework rather than only useful for password-manager data.

---

## 38. Next Step

Scenario 002 should now be compared with:

```text
docs/architecture/01-identity-and-service-discovery.md
Draft v0.2
```

The comparison should determine whether:

```text
A. Draft v0.2 survives unchanged
```

or:

```text
B. Scenario 002 exposes a general architectural requirement
   that justifies Draft v0.3
```

Implementation-specific interfaces should not be finalized until this comparison has been completed.

The primary point requiring further architectural evaluation is:

```text
Does the framework need Account as a first-class concept?
```

That question should be decided based on cross-scenario requirements rather than introducing the abstraction prematurely.
