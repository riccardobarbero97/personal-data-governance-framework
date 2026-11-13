# Connector Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md`  
**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for Connectors used by the Identity and Service Discovery capability of the Personal Data Governance Framework.

A Connector isolates provider-specific integration logic from the common Discovery Core.

The objective is to allow the framework to support multiple source types, multiple providers and multiple connected source instances without requiring provider-specific logic inside downstream discovery components.

Conceptually:

```text
External Provider
       |
       v
Provider-Specific Connector
       |
       v
Common Connector Contract
       |
       v
Observations
       |
       v
Discovery Core
```

Examples may eventually include:

```text
GmailConnector
OutlookConnector
ICloudMailConnector
ProtonMailConnector
PasswordManagerConnector
BrowserConnector
```

All compatible Connectors should expose a common behavioral contract while remaining free to implement provider-specific authorization, retrieval and synchronization internally.

---

# 2. Design Goal

The Discovery Core should not need to know:

```text
How Gmail authentication works
How Microsoft authentication works
How a password manager stores records
Which API a provider exposes
How pagination works
How provider-specific tokens are refreshed
Which provider-specific object represents a message
Which provider-specific object represents a credential entry
```

Instead, the core should be able to ask a Connector questions such as:

```text
Who are you?

What capabilities do you support?

What permissions do you require?

Are you currently authorized?

Collect observations for this capability.

What was the result?

Can collection continue later?
```

The Connector Contract defines this boundary.

---

# 3. Architectural Position

A Connector exists between an external Discovery Source and the common Discovery Domain.

```text
DISCOVERY SOURCE
       |
       v
    CONNECTOR
       |
       | Provider boundary
       |
       v
   OBSERVATIONS
       |
       v
DISCOVERY CORE
```

The Connector is responsible for communicating with the external source.

The Discovery Core is responsible for interpreting the Observations.

Therefore:

```text
CONNECTOR != DISCOVERY ENGINE
```

and:

```text
CONNECTOR != EVIDENCE CLASSIFIER
```

and:

```text
CONNECTOR != ENTITY RESOLVER
```

The Connector should not absorb responsibilities belonging to downstream discovery components merely because it has access to the source.

---

# 4. Core Responsibilities

A Connector should be responsible for the following categories of behavior:

```text
Identity
Capabilities
Authorization
Permissions
Collection
Minimization
Observation Creation
Synchronization
Error Reporting
Revocation
```

Not every provider will support every behavior in the same way.

The contract must allow providers to declare unsupported capabilities explicitly.

---

# 5. Connector Identity

Every Connector implementation must identify itself.

Conceptually:

```text
ConnectorDescriptor

- connector_id
- connector_type
- provider
- version
```

Example:

```text
connector_id: gmail
connector_type: EMAIL
provider: GOOGLE
version: 1
```

Another Connector might expose:

```text
connector_id: outlook
connector_type: EMAIL
provider: MICROSOFT
version: 1
```

A password-manager Connector might expose:

```text
connector_id: password-manager-x
connector_type: PASSWORD_MANAGER
provider: PROVIDER_X
version: 1
```

The exact enumeration of providers is not yet defined.

---

# 6. Connector Type

The Connector should expose the category of Discovery Source it supports.

Initial categories may include:

```text
EMAIL
PASSWORD_MANAGER
BROWSER
IDENTITY_PROVIDER
MANUAL
```

These categories must remain extensible.

Provider names and source types must not be conflated.

For example:

```text
GMAIL
```

is not a source type.

It is a provider-specific implementation of:

```text
EMAIL
```

Conceptually:

```text
Source Type
    |
    +-- EMAIL
    |     |
    |     +-- Gmail
    |     +-- Outlook
    |     +-- iCloud Mail
    |     +-- Proton Mail
    |
    +-- PASSWORD_MANAGER
          |
          +-- Provider A
          +-- Provider B
```

---

# 7. Connector Instance

A Connector implementation and a Connector instance are different concepts.

For example:

```text
GmailConnector
```

represents provider-specific integration behavior.

The User may connect:

```text
personal@gmail.com
```

and:

```text
oldaddress@gmail.com
```

using the same Connector implementation.

Conceptually:

```text
                 GmailConnector
                    /       \
                   /         \
                  v           v
        Connection A       Connection B
        user@gmail.com     old@gmail.com
```

The software design must therefore support multiple active instances of the same Connector implementation.

A provider-specific Connector must not assume:

```text
one provider = one user connection
```

---

# 8. Connected Source Identity

Each authorized source instance should have an internal framework identifier.

Conceptually:

```text
ConnectedSource

- id
- connector_id
- source_type
- provider
- display_name
- external_account_reference
- state
```

Example:

```text
id:
source_001

connector_id:
gmail

source_type:
EMAIL

provider:
GOOGLE

display_name:
Personal Gmail

external_account_reference:
user@gmail.com
```

This example is conceptual.

Sensitive external identifiers may require minimization or protection in the persistent implementation.

---

# 9. Capabilities

A Connector must explicitly advertise the capabilities it supports.

The Discovery Core must not infer capabilities based only on provider type.

Conceptually:

```text
get_capabilities()
```

could return capabilities such as:

```text
COLLECT_METADATA
COLLECT_CONTENT
COLLECT_ATTACHMENTS
INCREMENTAL_SYNC
IDENTITY_REFERENCE
SEARCH
REVOCATION
```

However, capabilities should describe meaningful framework operations rather than mirror provider APIs unnecessarily.

---

## 9.1 Why Capability Discovery Matters

Two email Connectors may support different functionality.

Conceptually:

```text
GmailConnector

metadata collection     YES
content collection      YES
incremental sync        YES
attachments             OPTIONAL
```

while another provider could expose:

```text
ProviderConnector

metadata collection     YES
content collection      NO
incremental sync        NO
attachments             NO
```

The Discovery Engine must therefore ask:

```text
Does this Connector support the capability?
```

rather than assuming:

```text
This is email, therefore this operation exists.
```

---

# 10. Capability Descriptor

A capability should expose enough information for the framework to reason about its availability and requirements.

Conceptually:

```text
CapabilityDescriptor

- capability
- supported
- permission_requirements
- sensitivity
- requires_user_authorization
- supports_incremental_collection
```

Example:

```text
capability:
SERVICE_DISCOVERY_METADATA

supported:
true

sensitivity:
METADATA

requires_user_authorization:
true
```

The precise structure remains implementation-dependent.

---

# 11. Progressive Permission Contract

Connectors must support the architectural principle of Progressive Permission.

The Discovery Core should be able to determine:

```text
Capability
     |
     v
Required Data
     |
     v
Required Permission
```

before requesting unnecessary access.

Conceptually:

```text
get_permission_requirements(capability)
```

should allow the framework to understand what additional access is required.

---

## 11.1 Permission States

The contract should support states conceptually equivalent to:

```text
NOT_REQUIRED
NOT_GRANTED
GRANTED
INSUFFICIENT
REVOKED
UNKNOWN
```

The final enumeration remains to be defined.

---

## 11.2 No Silent Permission Escalation

A Connector must never silently expand source permissions because a collection operation encounters insufficient information.

The expected flow is:

```text
collect()
   |
   v
Existing Permission Sufficient?
       /        \
     yes         no
      |           |
      v           v
  continue     return
              PERMISSION_REQUIRED
                   |
                   v
             Discovery Core
                   |
                   v
                User
```

The Connector reports the requirement.

The application decides how to present the request to the User.

---

# 12. Authorization Boundary

Connectors are responsible for provider-specific authorization mechanics.

Examples may eventually include:

```text
OAuth 2.0
API Tokens
Local Application Authorization
File Access
Operating-System Permission
Provider-Specific Authorization
```

These are implementation details of individual Connectors.

The common contract should expose authorization state without forcing the Discovery Core to understand provider-specific authentication flows.

Conceptually:

```text
get_authorization_status()
```

may return:

```text
AUTHORIZED
NOT_AUTHORIZED
EXPIRED
REVOKED
INSUFFICIENT
ERROR
```

---

# 13. Authorization Request

A Connector should be able to describe the authorization required for a capability before access is requested.

Conceptually:

```text
prepare_authorization(capability)
```

should produce information sufficient for the application layer to explain:

```text
What access is required?

Why is it required?

Which capability needs it?

What sensitivity level is involved?
```

The Connector Contract should not assume that every authorization flow is OAuth-based.

---

# 14. Credentials

Authentication credentials belong to the Connector boundary.

Downstream components must not require direct access to provider credentials.

Conceptually:

```text
                      +--> access token
                      |
External Provider --> Connector
                      |
                      +--> Observations --> Discovery Core
```

not:

```text
External Provider
      |
      +--> access token --> Discovery Core
      |
      +--> raw source data --> Discovery Core
```

Credential storage and secret-management implementation remain outside the current contract.

The boundary requirement is:

> Components consuming Observations should not need provider credentials merely to process previously collected information.

---

# 15. Collection Request

The Discovery Core should collect information through an explicit Collection Request.

Conceptually:

```text
CollectionRequest

- connected_source_id
- capability
- permission_context
- cursor
- limit
- options
```

Not every field is necessarily required in the final implementation.

The important principle is that collection should be intentional and capability-specific.

---

# 16. Collect Operation

The central Connector behavior is conceptually:

```text
collect(request)
    ->
CollectionResult
```

The Connector receives a request describing the capability to execute.

It returns:

```text
Observations
+
Collection State
+
Errors / Warnings
+
Continuation Information
```

It should not return raw provider objects directly to the Discovery Core.

---

# 17. Observation Contract

The primary output of successful Connector collection is one or more framework Observations.

Conceptually:

```text
Connector
    |
    v
CollectionResult
    |
    +-- Observation
    |
    +-- Observation
    |
    +-- Observation
```

The Connector translates provider-specific information into the common Observation boundary.

---

## 17.1 Common Observation Envelope

The exact Observation schema remains part of Domain Model refinement.

However, Connectors should produce an envelope conceptually containing:

```text
Observation

- id
- connected_source_id
- source_reference
- observation_type
- observed_at
- collected_at
- attributes
- provenance
```

The Connector should not be required to convert all source-specific information into a single universal flat schema.

Instead:

```text
Common Observation Envelope
          +
Source-Specific Attributes
```

is currently the preferred direction.

---

# 18. Source Reference

Observations should retain a source reference where this can be done safely.

Examples:

```text
Gmail message identifier
Password-manager record identifier
Browser-history entry identifier
```

This may allow:

- deduplication;
- incremental synchronization;
- reprocessing;
- traceability;
- source updates.

The source reference should not expose unnecessary secrets.

---

# 19. Observation Minimization

A Connector must minimize information before creating Observations where reasonably possible.

The intended pattern is:

```text
Provider Object
      |
      v
Connector Boundary
      |
 +----+------------------+
 |                       |
 v                       v
Required              Unnecessary
Information           Sensitive Data
 |                       |
 v                       X
Observation             discarded /
                        isolated
```

A password-manager Connector provides the clearest example:

```text
Record
 |
 +-- title ---------+
 +-- username ------+--> Observation
 +-- URI -----------+
 |
 +-- password ------X
 +-- OTP seed ------X
 +-- recovery code -X
```

The Discovery Core should not receive secrets it does not need.

---

# 20. Collection Result

Collection must return more than a list of Observations.

The Discovery Engine needs to know whether the operation was complete.

Conceptually:

```text
CollectionResult

- observations
- status
- continuation
- warnings
- errors
- collection_metadata
```

---

## 20.1 Collection Status

Potential states include:

```text
COMPLETE
PARTIAL
PERMISSION_REQUIRED
AUTHORIZATION_REQUIRED
UNSUPPORTED
FAILED
CANCELLED
```

The final enumeration remains open.

This is important because:

```text
observations = []
```

does not necessarily mean:

```text
No relevant information exists.
```

It may mean:

```text
The Connector could not complete collection.
```

---

# 21. Partial Collection

Connectors must represent partial processing explicitly.

Example:

```text
10,000 source records expected

4,000 processed

remote API unavailable
```

The correct result is:

```text
status:
PARTIAL
```

not:

```text
status:
COMPLETE

observations:
4,000 records
```

The Discovery Core must be able to distinguish incomplete source coverage from absence of evidence.

---

# 22. Continuation

Large sources may require incremental retrieval.

The Connector should be able to provide opaque continuation information.

Conceptually:

```text
CollectionResult

status:
PARTIAL

continuation:
<opaque connector state>
```

followed later by:

```text
CollectionRequest

continuation:
<opaque connector state>
```

The Discovery Core should not need to interpret provider-specific pagination tokens.

This permits:

```text
Gmail page tokens
Microsoft continuation links
provider-specific cursors
local-file offsets
```

to remain internal to Connector implementations.

---

# 23. Incremental Synchronization

Some Connectors may support incremental synchronization.

Conceptually:

```text
Initial Collection
       |
       v
Synchronization State
       |
       v
Later Collection
       |
       v
Only New / Changed Information
```

A Connector that supports this capability should expose it explicitly.

The common contract must not assume that all providers support incremental synchronization.

---

## 23.1 Synchronization State

Provider-specific synchronization state should ideally remain opaque to the Discovery Core.

Conceptually:

```text
SyncState

connector-owned opaque value
```

This prevents provider-specific concepts from leaking into the common domain.

---

# 24. Idempotency

Repeated collection should not create uncontrolled duplicate Observations.

For the same source record:

```text
collect()
collect()
collect()
```

should not necessarily produce:

```text
Observation A
Observation B
Observation C
```

as unrelated domain facts.

Connectors should provide stable source references where supported.

Deduplication responsibilities may ultimately be shared between:

```text
Connector
Observation Store
Synchronization Layer
```

The exact ownership remains open.

---

# 25. Error Contract

Connector errors should be represented in provider-independent categories where possible.

Potential common errors include:

```text
AUTHORIZATION_REQUIRED
PERMISSION_REQUIRED
AUTHORIZATION_EXPIRED
ACCESS_REVOKED
RATE_LIMITED
SOURCE_UNAVAILABLE
UNSUPPORTED_CAPABILITY
INVALID_SOURCE_RESPONSE
TEMPORARY_FAILURE
PERMANENT_FAILURE
```

Provider-specific diagnostic information may also be retained separately for debugging.

The Discovery Core should not need to understand:

```text
Google-specific error codes
Microsoft-specific exceptions
Password-manager-specific errors
```

to know that collection was rate-limited or authorization expired.

---

# 26. Errors vs Domain Uncertainty

Connector errors and discovery uncertainty are different.

For example:

```text
Connector:
Could not access source
```

is a Connector failure.

Whereas:

```text
Observation collected successfully
but Service could not be identified
```

is an Entity Resolution outcome.

Similarly:

```text
Observation collected successfully
but meaning is ambiguous
```

is an Evidence Classification outcome.

Therefore:

```text
CONNECTOR ERROR
      !=
UNRESOLVED ENTITY
      !=
UNKNOWN EVIDENCE
```

This separation prevents integration failures from being incorrectly represented as domain uncertainty.

---

# 27. Unsupported Capabilities

A Connector must be allowed to say:

```text
UNSUPPORTED
```

For example, one email provider may allow metadata-based discovery but not expose an appropriate incremental synchronization mechanism.

The framework should degrade according to the capability actually available.

A Connector should not fake support for a capability merely to conform to the interface.

---

# 28. Revocation

The Connector should support detecting or processing revocation where technically possible.

Conceptually:

```text
CONNECTED
    |
    v
REVOKED
```

After revocation:

```text
new collection
```

must stop.

However, revocation must not automatically imply:

```text
Delete Observations
Delete Evidence
Delete Relationships
```

Those are separate lifecycle decisions.

---

# 29. Disconnect

The application should be able to disconnect a specific Connected Source.

Example:

```text
User

+-- Gmail A        KEEP
+-- Gmail B        DISCONNECT
+-- Outlook        KEEP
```

The framework must therefore manage connection lifecycle per source instance rather than per Connector implementation.

Disconnecting:

```text
Gmail B
```

must not disconnect:

```text
Gmail A
```

or every source using the `GmailConnector`.

---

# 30. Multiple Connector Instances

The contract must support:

```text
GmailConnector
      |
      +-- ConnectedSource A
      |
      +-- ConnectedSource B
      |
      +-- ConnectedSource C
```

as well as:

```text
OutlookConnector
      |
      +-- ConnectedSource D
```

and:

```text
PasswordManagerConnector
      |
      +-- ConnectedSource E
```

All resulting Observations enter the same Discovery Core.

---

# 31. Provider Independence

Downstream discovery components should receive framework concepts rather than provider-specific representations.

The desired architecture is:

```text
Gmail -------- GmailConnector --------+
                                      |
Outlook ------ OutlookConnector ------+
                                      |
iCloud ------- ICloudConnector -------+--> Observations
                                      |         |
Proton ------- ProtonConnector -------+         v
                                      |    Discovery Core
PasswordMgr -- PasswordConnector -----+
```

not:

```text
if provider == Gmail:
    ...

elif provider == Outlook:
    ...

elif provider == Proton:
    ...
```

throughout the Discovery Engine.

Provider branching should remain concentrated primarily inside Connector implementations and Connector registration/configuration.

---

# 32. Capability-Specific Collection

The Connector Contract should not expose one unrestricted operation conceptually equivalent to:

```text
give_me_everything()
```

Instead:

```text
collect(capability)
```

should express what the framework is trying to accomplish.

For example:

```text
SERVICE_DISCOVERY_METADATA
```

may justify different access from a future capability such as:

```text
PERSONAL_DATA_ACQUISITION
```

even when both use the same external provider.

This is necessary for Progressive Permission.

---

# 33. Connector Contract Summary

The initial conceptual interface is:

```text
Connector

+ get_descriptor()
+ get_capabilities()
+ get_authorization_status()
+ get_permission_requirements(capability)
+ prepare_authorization(capability)
+ collect(request)
+ disconnect()
```

Some Connectors may additionally support:

```text
+ refresh_authorization()
+ incremental_collect()
+ revoke()
```

Whether these remain independent operations or become part of broader commands will be determined during implementation design.

---

# 34. Conceptual Contract

A language-independent representation of the contract is:

```text
interface Connector {

    ConnectorDescriptor getDescriptor()

    CapabilitySet getCapabilities()

    AuthorizationStatus getAuthorizationStatus()

    PermissionRequirements getPermissionRequirements(
        Capability capability
    )

    AuthorizationRequest prepareAuthorization(
        Capability capability
    )

    CollectionResult collect(
        CollectionRequest request
    )

    DisconnectResult disconnect()
}
```

This is intentionally pseudocode.

It is not yet the final Python interface.

---

# 35. Collection Contract

Conceptually:

```text
CollectionRequest
        |
        v
     Connector
        |
        v
CollectionResult
        |
        +-- Observations
        |
        +-- Status
        |
        +-- Continuation
        |
        +-- Warnings
        |
        +-- Errors
```

At no point should the common Discovery Engine require raw provider-specific API objects.

---

# 36. Security Invariants

The Connector Contract should enforce the following invariants.

### CON-INV-001

A Connector must not expose source credentials to downstream discovery components.

---

### CON-INV-002

A Connector must not silently request broader permissions than required by the selected capability.

---

### CON-INV-003

A Connector must not report a partial collection as complete.

---

### CON-INV-004

Source-specific errors should not be confused with domain uncertainty.

---

### CON-INV-005

A Connector should minimize source data before producing Observations where reasonably possible.

---

### CON-INV-006

Authentication secrets unnecessary for Service Discovery must not become normal Observations.

---

### CON-INV-007

A Connector must preserve enough source provenance to support traceability where technically possible.

---

### CON-INV-008

Multiple instances of the same Connector implementation must coexist independently.

---

### CON-INV-009

Disconnecting one Connected Source must not implicitly disconnect another Connected Source using the same provider.

---

### CON-INV-010

The absence of returned Observations must not be interpreted as complete absence of relevant source information unless collection completed successfully.

---

### CON-INV-011

Provider-specific pagination and synchronization details should not leak into the common Discovery Domain unless they have meaningful domain semantics.

---

### CON-INV-012

The Discovery Core must not depend on one specific Connector implementation.

---

# 37. Gmail Example

Conceptually:

```text
User chooses:
Connect Gmail
      |
      v
GmailConnector
      |
      v
getCapabilities()
      |
      v
SERVICE_DISCOVERY_METADATA supported
      |
      v
getPermissionRequirements()
      |
      v
Minimum Gmail authorization
      |
      v
User Authorizes
      |
      v
collect(
    SERVICE_DISCOVERY_METADATA
)
      |
      v
Gmail API
      |
      v
Connector Minimization
      |
      v
Observations
      |
      v
Discovery Core
```

The Discovery Core processes Gmail Observations without depending directly on Gmail API objects.

---

# 38. Second Email Provider Example

A second email provider should fit the same architecture:

```text
User chooses:
Connect Additional Email Provider
      |
      v
ProviderConnector
      |
      v
getCapabilities()
      |
      v
getPermissionRequirements()
      |
      v
Provider-Specific Authorization
      |
      v
collect(
    SERVICE_DISCOVERY_METADATA
)
      |
      v
Provider API / Integration
      |
      v
Observations
      |
      v
Same Discovery Core
```

The differences remain primarily inside the Connector.

---

# 39. Password Manager Example

Conceptually:

```text
User chooses:
Connect Password Manager
      |
      v
PasswordManagerConnector
      |
      v
getCapabilities()
      |
      v
SERVICE_DISCOVERY_METADATA
      |
      v
Permission Analysis
      |
      v
Metadata Access
      |
      v
Password Manager
      |
      v
Connector Minimization
   /           \
metadata       secrets
  |              |
  v              X
Observation
  |
  v
Discovery Core
```

The same `collect()` contract is therefore usable for structurally different Discovery Sources.

---

# 40. ConnectedSource Finding

Designing the Connector Contract provides stronger evidence that the candidate Domain Concept:

```text
ConnectedSource
```

is necessary.

The system must distinguish between:

```text
Connector Implementation
```

and:

```text
A particular source instance connected by a User.
```

Without this distinction, the framework cannot cleanly represent:

- multiple Gmail accounts;
- multiple email providers;
- multiple password managers;
- independent authorization states;
- independent synchronization states;
- per-source revocation;
- per-source collection history.

Therefore this document recommends promoting:

```text
ConnectedSource
```

from:

```text
Candidate Domain Concept
```

to:

```text
Core Domain Concept
```

subject to final review of the Discovery Domain Model.

---

# 41. Proposed ConnectedSource Concept

Conceptually:

```text
ConnectedSource

- id
- connector_id
- source_type
- provider
- display_name
- external_account_reference
- authorization_state
- connection_state
- created_at
```

Synchronization state may or may not belong directly to this entity.

Secret authorization material must not be stored directly as ordinary ConnectedSource attributes.

Instead:

```text
ConnectedSource
      |
      v
Credential Reference
      |
      v
Secure Credential Storage
```

should be considered during security architecture design.

---

# 42. Open Questions

## Connector Registration

- How are available Connector implementations discovered?
- Static registration?
- Plugin registry?
- Dependency injection?
- Package-based discovery?
- Another mechanism?

This should be decided during application architecture design.

---

## ConnectedSource

- Should `ConnectedSource` now be promoted into the core Domain Model?
- Which authorization state belongs in the domain?
- Which state belongs exclusively inside the Connector implementation?
- How should external account identifiers be protected?

---

## Capabilities

- What is the minimum capability vocabulary?
- Should capabilities represent technical operations or user-facing framework capabilities?
- Can Connectors dynamically enable and disable capabilities?

---

## Permissions

- What is the common representation of provider-specific permissions?
- Should the core understand concrete OAuth scopes?
- Should the Connector expose only an abstract sensitivity level?
- How should permission changes over time be handled?

---

## Authorization

- Which parts of authorization belong to the Connector?
- Which belong to the application UI?
- How should browser redirects or local authorization flows be represented?
- How should authorization failures be surfaced?

---

## Observations

- What exact common structure should every Connector produce?
- How should typed source-specific attributes be represented?
- How should schema versions be handled?

---

## Collection

- Should `collect()` return all available Observations or stream them?
- How should very large sources be processed?
- Should batching be controlled by the Connector or the application?
- How should collection cancellation work?

---

## Synchronization

- Should incremental collection be a separate method?
- Or should it be controlled through `CollectionRequest`?
- Where is synchronization state stored?
- How is synchronization restarted after failure?

---

## Secrets

- Which component owns secure credential storage?
- How are authorization tokens referenced?
- How are secret fields prevented from entering logs?
- How are Connector implementations prevented from accidentally exposing source secrets downstream?

---

## Errors

- Which errors belong to a common Connector error taxonomy?
- Which provider diagnostics should be preserved?
- Which errors are retryable?
- Who decides whether a retry occurs?

---

# 43. Decision Candidates

The Connector Contract suggests several decisions that should be evaluated for incorporation into the architecture.

### Candidate Decision - Multiple Source Instances

```text
The framework must support multiple simultaneously connected source instances,
including multiple instances using the same Connector implementation.
```

---

### Candidate Decision - Capability-Aware Connectors

```text
Connectors must explicitly advertise supported capabilities rather than having
the Discovery Core infer capabilities from the provider or source type.
```

---

### Candidate Decision - Connector Minimization Boundary

```text
Connectors should minimize source-specific information before exposing
Observations to the common Discovery Core.

Information unnecessary for the requested capability should not cross the
Connector boundary where technically practical.
```

---

### Candidate Decision - Provider Details Remain Behind Connectors

```text
Provider-specific APIs, pagination models, authorization protocols and
source object models should remain isolated behind Connector implementations
wherever reasonably possible.
```

---

# 44. Current Contract Baseline

The current minimum Connector contract is:

```text
Connector

    identify itself

    advertise capabilities

    describe permission requirements

    expose authorization state

    prepare authorization

    perform capability-specific collection

    return framework Observations

    report complete / partial / failed collection

    preserve continuation state when required

    support independent source instances

    support disconnection
```

The contract must not require:

```text
AI
specific database technology
specific cloud provider
specific OAuth provider
specific Discovery Source type
specific UI technology
```

---

# 45. Next Interface Contracts

After the Connector Contract is sufficiently stable, the next software contracts should be defined in dependency order.

Recommended order:

```text
01 Connector Contract
        |
        v
02 Observation Contract
        |
        v
03 Service Candidate Detector Contract
        |
        v
04 Entity Resolver Contract
        |
        v
05 Evidence Classifier Contract
        |
        v
06 Evidence Aggregator Contract
        |
        v
07 Relationship Assessor Contract
```

This sequence follows the Discovery pipeline and allows each downstream contract to depend only on concepts already defined upstream.

The immediate next step should be the Observation Contract because every Connector must produce Observations and every subsequent discovery component depends on them.
