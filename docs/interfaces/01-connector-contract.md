# Connector Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md` - Draft v0.3  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md` - Draft v0.3  
**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for Connectors used by the Identity and Service Discovery capability of the Personal Data Governance Framework.

A Connector isolates provider-specific integration logic from the common Discovery Core.

The objective is to allow the framework to support:

- multiple SourceTypes;
- multiple Providers;
- multiple ConnectedSource instances;
- multiple instances using the same Connector implementation;
- capability-specific permissions;
- independent source lifecycles;

without requiring provider-specific logic inside downstream Discovery components.

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
IdentityProviderConnector
```

All compatible Connectors should expose a common behavioral contract while remaining free to implement provider-specific authorization, retrieval and synchronization internally.

---

## 2. Design Goal

The Discovery Core should not need to know:

```text
How Gmail authentication works

How Microsoft authentication works

How a password manager stores records

Which API a Provider exposes

How provider pagination works

How provider-specific tokens are refreshed

Which provider object represents a message

Which provider object represents a credential entry

How provider-specific synchronization state is encoded
```

Instead, the Discovery Core should be able to ask a Connector questions such as:

```text
Who are you?

What SourceType and Provider do you support?

What capabilities do you support?

What permissions does a capability require?

What is the authorization state of this ConnectedSource?

Collect Observations for this capability.

Was collection complete?

Can collection continue later?

What errors or warnings occurred?
```

The Connector Contract defines this boundary.

---

## 3. Architectural Position

A Connector exists between a particular ConnectedSource and an external Provider.

```text
CONNECTED SOURCE
       |
       v
    CONNECTOR
       |
       v
EXTERNAL PROVIDER
```

Information returned by the Provider crosses the Connector boundary only after source-specific selection, normalization and minimization.

```text
EXTERNAL PROVIDER
       |
       v
    CONNECTOR
       |
       | Provider and security boundary
       |
       v
   OBSERVATIONS
       |
       v
DISCOVERY CORE
```

The Connector is responsible for communicating with the external source.

The Discovery Core is responsible for interpreting the resulting Observations.

Therefore:

```text
CONNECTOR != DISCOVERY ENGINE
```

```text
CONNECTOR != SERVICE CANDIDATE DETECTOR
```

```text
CONNECTOR != ENTITY RESOLVER
```

```text
CONNECTOR != EVIDENCE CLASSIFIER
```

```text
CONNECTOR != RELATIONSHIP ASSESSOR
```

The Connector must not absorb downstream responsibilities merely because it has privileged access to the source.

---

## 4. Core Responsibilities

A Connector should be responsible for the following categories of behavior:

```text
Identity
Capability Discovery
Authorization
Permission Analysis
Collection
Source Interaction
Representation Normalization
Data Minimization
Observation Creation
Synchronization
Error Reporting
Revocation
Disconnection
```

Not every Provider supports every operation in the same way.

The contract must therefore allow unsupported capabilities to be represented explicitly.

---

## 5. Connector Identity

Every Connector implementation must identify itself through a descriptor.

Conceptually:

```text
ConnectorDescriptor

- connector_id
- source_type
- provider
- version
```

Example:

```text
connector_id:
gmail

source_type:
EMAIL

provider:
GOOGLE

version:
1
```

Another Connector may expose:

```text
connector_id:
outlook

source_type:
EMAIL

provider:
MICROSOFT

version:
1
```

A password-manager Connector may expose:

```text
connector_id:
password-manager-x

source_type:
PASSWORD_MANAGER

provider:
PROVIDER_X

version:
1
```

The exact Provider vocabulary remains open.

---

## 6. SourceType

The Connector must expose the general SourceType it supports.

Initial categories may include:

```text
EMAIL
PASSWORD_MANAGER
BROWSER
IDENTITY_PROVIDER
MANUAL
```

These categories must remain extensible.

Provider names and SourceTypes must not be conflated.

For example:

```text
GMAIL
```

is not a SourceType.

It is a provider-specific product or integration associated with:

```text
EMAIL
```

Conceptually:

```text
SourceType
    |
    +-- EMAIL
    |     |
    |     +-- GmailConnector
    |     +-- OutlookConnector
    |     +-- ICloudMailConnector
    |     +-- ProtonMailConnector
    |
    +-- PASSWORD_MANAGER
          |
          +-- ProviderAConnector
          +-- ProviderBConnector
```

---

## 7. Connector Implementation and ConnectedSource

A Connector implementation and a ConnectedSource are different concepts.

For example:

```text
GmailConnector
```

represents reusable provider-specific integration behavior.

The User may connect:

```text
personal@gmail.com
```

and:

```text
oldaddress@gmail.com
```

through the same Connector implementation.

Conceptually:

```text
                    GmailConnector
                    /            \
                   /              \
                  v                v
         ConnectedSource A   ConnectedSource B
         Personal Gmail      Old Gmail
```

The software design must support multiple simultaneously active Connected Sources using the same Connector implementation.

A Connector must not assume:

```text
one Provider = one User connection
```

---

## 8. ConnectedSource Identity

Every connected or authorized source instance must have an internal framework identifier.

Conceptually:

```text
ConnectedSource

- id
- user_reference
- connector_reference
- source_type
- provider
- display_name
- external_account_reference
- connection_state
- authorization_state
```

Example:

```text
id:
source_001

connector_reference:
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

Sensitive external identifiers may require:

- minimization;
- encryption;
- hashing;
- indirect secure references;
- restricted persistence.

The Domain Model is the authoritative source for the `ConnectedSource` definition.

---

## 9. Capabilities

A Connector must explicitly advertise the capabilities it supports.

The Discovery Core must not infer capabilities based only on SourceType or Provider.

Conceptually:

```text
get_capabilities()
```

may return capabilities such as:

```text
SERVICE_DISCOVERY_METADATA
COLLECT_CONTENT
COLLECT_ATTACHMENTS
INCREMENTAL_SYNC
IDENTITY_REFERENCE
SEARCH
REVOCATION
```

Capabilities should represent meaningful framework operations rather than mirror provider APIs unnecessarily.

---

## 9.1 Why Capability Discovery Matters

Two email Connectors may expose different capabilities.

Example:

```text
GmailConnector

metadata collection     YES
content collection      YES
incremental sync        YES
attachments             OPTIONAL
```

while another Provider may expose:

```text
ProviderConnector

metadata collection     YES
content collection      NO
incremental sync        NO
attachments             NO
```

The Discovery Engine must therefore ask:

```text
Does this Connector support the requested capability
for this ConnectedSource?
```

rather than assume:

```text
This is EMAIL, therefore every email operation exists.
```

---

## 10. Capability Descriptor

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

supports_incremental_collection:
true
```

The exact implementation remains open.

Capability availability may need to be evaluated for a specific ConnectedSource rather than only for the Connector implementation.

---

## 11. Progressive Permission Contract

Connectors must support Progressive Permission.

The framework should be able to determine:

```text
Capability
     |
     v
Required Information
     |
     v
Required Permission
```

before requesting unnecessary source access.

Conceptually:

```text
get_permission_requirements(
    connected_source,
    capability
)
```

should allow the application to understand what access is required.

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

The final enumeration remains open.

---

## 11.2 No Silent Permission Escalation

A Connector must never silently expand source permissions because a collection operation encounters insufficient information.

The expected flow is:

```text
collect()
   |
   v
Existing Permission Sufficient?
       /          \
     yes           no
      |             |
      v             v
  continue      return
                PERMISSION_REQUIRED
                     |
                     v
              Application Layer
                     |
                     v
                    User
```

The Connector reports the permission requirement.

The application layer decides how to explain and request it.

The Connector does not autonomously authorize broader access.

---

## 12. Authorization Boundary

Connectors are responsible for Provider-specific authorization mechanics.

Possible mechanisms include:

```text
OAuth 2.0
API Tokens
Local Application Authorization
Operating-System Permission
File Access
Provider-Specific Authorization
```

The common contract should expose authorization state without requiring the Discovery Core to understand provider-specific authentication flows.

Conceptually:

```text
get_authorization_status(
    connected_source
)
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

Connection state and authorization state may remain separate Domain concepts.

---

## 13. Authorization Request

A Connector should be able to describe the authorization required for a capability before access is requested.

Conceptually:

```text
prepare_authorization(
    connected_source,
    capability
)
```

should produce information sufficient for the application layer to explain:

```text
What access is required?

Why is it required?

Which capability needs it?

What information may be collected?

What sensitivity level is involved?

Does existing authorization already cover it?
```

The Connector Contract must not assume that every authorization flow is OAuth-based.

---

## 14. Credentials

Authentication credentials belong to the Connector and secure credential-storage boundary.

Downstream Discovery components must not require direct access to provider credentials.

The intended architecture is:

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
      +--> raw source object --> Discovery Core
```

Credential storage and secret-management implementation remain outside this contract.

The boundary requirement is:

> Components consuming preserved Observations must not require provider credentials merely to process or reinterpret those Observations.

---

## 15. Collection Request

Information collection must occur through an explicit, capability-specific request.

Conceptually:

```text
CollectionRequest

- connected_source_id
- capability
- permission_context
- continuation
- limit
- options
```

Not every field is necessarily required in the final implementation.

The important principles are:

```text
Collection is intentional.

Collection targets exactly one ConnectedSource.

Collection is capability-specific.

Collection does not mean "retrieve everything."
```

---

## 16. Collect Operation

The central Connector operation is conceptually:

```text
collect(request)
    ->
CollectionResult
```

The Connector receives a request describing:

- the ConnectedSource;
- the capability;
- the current authorization or permission context;
- optional continuation information;
- collection-specific options.

It returns:

```text
Observations
+
Collection Status
+
Warnings
+
Errors
+
Continuation Information
+
Collection Metadata
```

The Connector must not return raw provider objects directly to the Discovery Core.

---

## 17. Observation Contract

The primary successful output of collection is one or more framework Observations.

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

Every resulting Observation must reference exactly one ConnectedSource.

---

## 17.1 Common Observation Envelope

The Observation Contract defines the common envelope as conceptually containing:

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

The Connector must not force all source structures into one universal flat representation.

The preferred direction is:

```text
Common Observation Envelope
          +
Typed Source-Specific Payload
```

---

## 18. Source Reference

Observations should retain a stable source reference where technically possible and safe.

Examples include:

```text
Gmail message identifier

Outlook message reference

Password-manager record identifier

Browser-history entry identifier
```

A source reference may support:

- deduplication;
- incremental synchronization;
- source updates;
- reprocessing;
- debugging;
- traceability.

Source references must not expose unnecessary secrets.

The safe identity context is normally:

```text
ConnectedSourceId
        +
SourceReference
```

rather than SourceReference alone.

---

## 19. Observation Minimization

A Connector must minimize information before creating Observations where reasonably possible.

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
Observation            discarded,
                       isolated or
                       never retrieved
```

A password-manager Connector provides a clear example:

```text
Record
 |
 +-- title ----------+
 +-- username -------+--> Observation
 +-- URI ------------+
 |
 +-- password -------X
 +-- OTP seed -------X
 +-- recovery code --X
 +-- private key ----X
```

The Discovery Core must not receive secrets it does not need.

---

## 20. Collection Result

Collection must return more than a list of Observations.

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

The Discovery Engine must be able to determine whether collection was complete.

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

This distinction is required because:

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

## 21. Partial Collection

Connectors must represent partial processing explicitly.

Example:

```text
10,000 source records expected

4,000 processed

Provider API became unavailable
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

The Discovery Core must distinguish incomplete source coverage from absence of Evidence.

---

## 22. Continuation

Large sources may require incremental retrieval or pagination.

The Connector should provide opaque continuation information.

Conceptually:

```text
CollectionResult

status:
PARTIAL

continuation:
<opaque connector state>
```

followed by:

```text
CollectionRequest

continuation:
<opaque connector state>
```

The Discovery Core must not need to interpret:

```text
Gmail page tokens
Microsoft continuation links
Provider-specific cursors
Local file offsets
```

These details should remain internal to the relevant Connector or synchronization layer.

---

## 23. Incremental Synchronization

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
Only New or Changed Information
```

A Connector supporting this capability should advertise it explicitly.

The common contract must not assume that every Provider supports incremental synchronization.

---

## 23.1 Synchronization State

Provider-specific synchronization state should remain opaque to the Discovery Core where practical.

Conceptually:

```text
SyncState

connector-owned opaque value
```

This prevents Provider-specific synchronization concepts from leaking into the common Discovery Domain.

The future application model must determine whether synchronization state belongs to:

- ConnectedSource;
- Connector-owned storage;
- a synchronization repository;
- a CollectionRun record;
- another application component.

---

## 24. Idempotency

Repeated collection must not create uncontrolled duplicate Observations.

For the same source record:

```text
collect()
collect()
collect()
```

should not produce three unrelated Domain facts when the Provider is exposing the same unchanged record.

Connectors should provide stable source references where supported.

Deduplication responsibility may ultimately be shared between:

```text
Connector
Observation Repository
Synchronization Layer
```

The exact ownership remains open.

---

## 25. Error Contract

Connector errors should be represented using provider-independent categories where practical.

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

Provider diagnostics may be preserved separately for debugging.

The Discovery Core should not need to understand Provider-specific error codes to know that:

- authorization expired;
- access was revoked;
- collection was rate-limited;
- the source was unavailable;
- the capability was unsupported.

---

## 26. Errors vs Domain Uncertainty

Connector errors and Domain uncertainty are different.

```text
Connector could not access source
```

is a Connector or collection failure.

```text
Observation collected successfully
but Service could not be identified
```

is an Entity Resolution outcome.

```text
Observation collected successfully
but meaning could not be determined
```

is an Evidence Classification outcome.

Therefore:

```text
CONNECTOR ERROR
      !=
UNRESOLVED ENTITY
      !=
UNKNOWN EVIDENCE
      !=
UNKNOWN RELATIONSHIP
```

This prevents integration failures from being represented as Domain uncertainty.

---

## 27. Unsupported Capabilities

A Connector must be allowed to report:

```text
UNSUPPORTED
```

For example, a Provider may support metadata-based Service Discovery but not:

- content collection;
- attachment collection;
- incremental synchronization;
- revocation through the integration.

The framework must adapt to capabilities actually available.

A Connector must not pretend to support a capability merely to conform to the interface.

---

## 28. Revocation

The Connector should detect or process source-authorization revocation where technically possible.

Conceptually:

```text
AUTHORIZED
    |
    v
REVOKED
```

After revocation:

```text
new collection
```

must stop.

However:

```text
Revoke Authorization
```

must not automatically mean:

```text
Delete Observations
Delete Evidence
Delete Relationships
```

These are separate lifecycle decisions.

---

## 29. Disconnect

The application must be able to disconnect one particular ConnectedSource.

Example:

```text
User

+-- Personal Gmail     KEEP
+-- Old Gmail          DISCONNECT
+-- Work Outlook       KEEP
```

The framework must manage connection lifecycle per ConnectedSource rather than per Connector implementation.

Disconnecting `Old Gmail` must not disconnect:

- Personal Gmail;
- Work Outlook;
- every source using GmailConnector.

---

## 30. Multiple Connected Sources

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

All resulting Observations enter the same provider-independent Discovery Core.

---

## 31. Provider Independence

Downstream components should receive framework concepts rather than provider-specific representations.

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

Provider branching should remain concentrated primarily inside:

- Connector implementations;
- Connector registration;
- Provider configuration;
- authorization adapters.

---

## 32. Capability-Specific Collection

The Connector Contract must not expose one unrestricted operation equivalent to:

```text
give_me_everything()
```

Instead:

```text
collect(capability)
```

must express the framework purpose.

For example:

```text
SERVICE_DISCOVERY_METADATA
```

may justify different information and permissions from:

```text
PERSONAL_DATA_ACQUISITION
```

even if both capabilities use the same Provider and ConnectedSource.

This is necessary for Progressive Permission and data minimization.

---

## 33. Connector Contract Summary

The initial conceptual Connector interface includes:

```text
Connector

+ get_descriptor()

+ get_capabilities(connected_source)

+ get_authorization_status(connected_source)

+ get_permission_requirements(
      connected_source,
      capability
  )

+ prepare_authorization(
      connected_source,
      capability
  )

+ collect(request)

+ disconnect(connected_source)
```

Some Connectors may also support:

```text
+ refresh_authorization(connected_source)

+ revoke(connected_source)
```

Incremental collection should normally be expressed through capability and request context rather than requiring an entirely separate Provider-specific interface.

The exact method structure will be finalized during implementation design.

---

## 34. Conceptual Contract

A language-independent representation is:

```text
interface Connector {

    ConnectorDescriptor getDescriptor()

    CapabilitySet getCapabilities(
        ConnectedSource connectedSource
    )

    AuthorizationStatus getAuthorizationStatus(
        ConnectedSource connectedSource
    )

    PermissionRequirements getPermissionRequirements(
        ConnectedSource connectedSource,
        Capability capability
    )

    AuthorizationRequest prepareAuthorization(
        ConnectedSource connectedSource,
        Capability capability
    )

    CollectionResult collect(
        CollectionRequest request
    )

    DisconnectResult disconnect(
        ConnectedSource connectedSource
    )
}
```

This is pseudocode.

It is not the final Python interface.

---

## 35. Collection Contract

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
        |
        +-- Collection Metadata
```

At no point should the common Discovery Engine require raw Provider-specific API objects.

---

## 36. Security Invariants

### CON-INV-001

A Connector must not expose source credentials to downstream Discovery components.

---

### CON-INV-002

A Connector must not silently request broader permissions than required by the selected capability.

---

### CON-INV-003

A Connector must not report a partial collection as complete.

---

### CON-INV-004

Source-specific errors must not be confused with Domain uncertainty.

---

### CON-INV-005

A Connector should minimize source information before producing Observations where technically practical.

---

### CON-INV-006

Authentication secrets unnecessary for Service Discovery must not become normal Observations.

---

### CON-INV-007

A Connector must preserve enough source provenance to support traceability where technically possible.

---

### CON-INV-008

Multiple Connected Sources using the same Connector implementation must coexist independently.

---

### CON-INV-009

Disconnecting one ConnectedSource must not implicitly disconnect another ConnectedSource using the same Provider or Connector.

---

### CON-INV-010

The absence of returned Observations must not be interpreted as complete absence of relevant source information unless collection completed successfully.

---

### CON-INV-011

Provider-specific pagination and synchronization details should not leak into the common Discovery Domain unless they have meaningful framework semantics.

---

### CON-INV-012

The Discovery Core must not depend on one specific Connector implementation.

---

### CON-INV-013

Every collection request must identify exactly one ConnectedSource.

---

### CON-INV-014

Every Observation produced by a Connector must reference the ConnectedSource from which it originated.

---

### CON-INV-015

A Connector must not assign canonical Service conclusions.

---

### CON-INV-016

A Connector must not assign final Evidence semantics unless a future source-specific contract explicitly demonstrates that doing so is required and does not violate the common Discovery boundaries.

---

### CON-INV-017

A Connector must not assign Relationship conclusions.

---

### CON-INV-018

Connector minimization must preserve the information required by the requested capability while excluding unnecessary sensitive information.

---

## 37. Gmail Example

Conceptually:

```text
User chooses:
Connect Gmail
      |
      v
GmailConnector
      |
      v
Create or select:
ConnectedSource = Personal Gmail
      |
      v
getCapabilities(
    Personal Gmail
)
      |
      v
SERVICE_DISCOVERY_METADATA supported
      |
      v
getPermissionRequirements(
    Personal Gmail,
    SERVICE_DISCOVERY_METADATA
)
      |
      v
Minimum Gmail authorization
      |
      v
User authorizes
      |
      v
collect(
    connected_source = Personal Gmail,
    capability = SERVICE_DISCOVERY_METADATA
)
      |
      v
Gmail API
      |
      v
Connector selection,
normalization and minimization
      |
      v
EMAIL_MESSAGE_METADATA Observations
      |
      v
Discovery Core
```

The Discovery Core processes the resulting Observations without depending directly on Gmail API objects.

---

## 38. Additional Email Provider Example

A second email provider fits the same architecture:

```text
User chooses:
Connect Outlook
      |
      v
OutlookConnector
      |
      v
ConnectedSource:
Work Outlook
      |
      v
getCapabilities()
      |
      v
getPermissionRequirements()
      |
      v
Microsoft-specific authorization
      |
      v
collect(
    SERVICE_DISCOVERY_METADATA
)
      |
      v
Microsoft API
      |
      v
EMAIL_MESSAGE_METADATA Observations
      |
      v
Same Discovery Core
```

Gmail and Outlook may produce the same ObservationType when their normalized framework semantics are compatible.

Provider differences remain primarily inside the respective Connectors.

---

## 39. Password Manager Example

Conceptually:

```text
User chooses:
Connect Password Manager
      |
      v
PasswordManagerConnector
      |
      v
ConnectedSource:
Primary Vault
      |
      v
getCapabilities()
      |
      v
SERVICE_DISCOVERY_METADATA
      |
      v
Permission analysis
      |
      v
Authorized metadata access
      |
      v
Password Manager
      |
      v
Connector minimization
   /             \
metadata         secrets
  |                 |
  v                 X
Observation
  |
  v
Discovery Core
```

The same collection contract is therefore usable for structurally different sources.

The password value, OTP seed and recovery codes do not enter ordinary Service Discovery Observations.

---

## 40. ConnectedSource Alignment

`ConnectedSource` is now a Core Domain Entity.

The distinction between:

```text
Connector Implementation
```

and:

```text
A particular source instance connected by a User
```

is part of the consolidated Discovery Domain Model.

This distinction is required to support:

- multiple accounts using the same Provider;
- multiple Providers of the same SourceType;
- multiple password managers;
- independent authorization state;
- independent permission state;
- independent synchronization state;
- per-source collection;
- per-source revocation;
- per-source disconnection;
- Observation provenance.

Conceptually:

```text
Connector Implementation
        |
        +-- ConnectedSource A
        |
        +-- ConnectedSource B
        |
        +-- ConnectedSource C
```

The Connector represents provider-specific integration behavior.

The ConnectedSource represents a particular source instance connected by the User.

This is no longer a candidate finding.

It is a consolidated Domain dependency.

---

## 41. ConnectedSource Contract Dependency

The Connector Contract depends on the `ConnectedSource` Core Domain Entity defined by the Discovery Domain Model.

A Connector must operate on one specific ConnectedSource context when performing source-specific operations.

Conceptually:

```text
ConnectedSource
      |
      v
Connector
      |
      v
Collection
```

The Connector may use ConnectedSource information such as:

```text
internal source identity
SourceType
Provider
connector reference
external account reference
connection state
authorization state
```

subject to data-minimization and security requirements.

Authorization credentials remain outside ordinary ConnectedSource Domain attributes.

The preferred boundary is:

```text
ConnectedSource
      |
      v
Credential Reference
      |
      v
Secure Credential Storage
```

not:

```text
ConnectedSource
 |
 +-- access_token
 +-- refresh_token
 +-- password
```

The Domain Model is authoritative for ConnectedSource structure and lifecycle semantics.

The Connector Contract defines how Connector behavior consumes that source context.

---

## 42. Open Questions

### Connector Registration

- How are Connector implementations discovered?
- Static registration?
- Plugin registry?
- Dependency injection?
- Package-based discovery?
- Another mechanism?
- How are Connector versions selected?

This should be decided during application architecture design.

### ConnectedSource

- Which authorization states belong in the Domain Model?
- Which states belong exclusively inside the Connector implementation?
- How should external account identifiers be protected?
- Where should opaque synchronization state be stored?
- How should locally imported sources be represented?
- How should manual sources be represented when no external authorization exists?

### Capabilities

- What is the minimum capability vocabulary?
- Should capabilities represent technical operations or User-facing framework capabilities?
- Can Connectors dynamically enable or disable capabilities?
- Can capability availability differ between Connected Sources using the same Connector?
- How are capability versions managed?

### Permissions

- What is the common representation of Provider-specific permissions?
- Should the core understand concrete OAuth scopes?
- Should Connectors expose abstract framework permission requirements?
- How should permission changes over time be represented?
- How are capability-specific permission upgrades explained to the User?

### Authorization

- Which authorization responsibilities belong to the Connector?
- Which belong to the application UI?
- How are browser redirects represented?
- How are local authorization flows represented?
- How are authorization failures surfaced?
- Which component owns secure credential storage?

### Observations

- Which Observation Types belong to the initial implementation?
- How are typed payloads represented?
- How are payload schemas registered?
- How are schema versions negotiated?
- Should producer Connector ID and version be mandatory Observation provenance?

### Collection

- Should `collect()` return a complete collection or a batch?
- Should collection also support streaming?
- Who controls batch size?
- How should collection cancellation work?
- How are partial batches materialized safely?
- Is a CollectionRun application concept required?

### Synchronization

- Should incremental synchronization use the same `collect()` operation?
- Where is synchronization state stored?
- How is synchronization restarted after failure?
- How are deleted or modified source records represented?
- How is synchronization state migrated across Connector versions?

### Secrets

- Which component owns secure credential storage?
- How are credential references represented?
- How are secret fields prevented from entering logs?
- How are Connector implementations prevented from accidentally exposing source secrets?
- How should memory containing retrieved secrets be handled?
- How are secret fields excluded from diagnostics?

### Errors

- Which errors belong to the common Connector error taxonomy?
- Which Provider diagnostics should be retained?
- Which errors are retryable?
- Who decides whether and when retries occur?
- How are repeated failures surfaced without corrupting previous valid information?

---

## 43. Decision Alignment

The Connector Contract is aligned with the consolidated Architecture Decisions.

### D-017 - Multiple Connected Source Instances

The framework supports multiple independent Connected Sources, including multiple sources using the same Connector implementation.

---

### D-018 - Connector Is a Data-Minimization Boundary

Provider information unnecessary for the requested capability should not cross the Connector boundary where technically practical.

---

### D-019 - Provider-Neutral Observations

Equivalent source semantics from different Providers should produce equivalent Observation Types where their framework semantics are compatible.

---

### Existing Connector Decisions Preserved

The following contract decisions remain valid:

```text
Capability-aware Connectors

Provider details remain behind Connectors

Progressive Permission

Credential isolation

Partial collection is explicit

Provider-independent errors

Opaque continuation state

Independent ConnectedSource lifecycle
```

---

## 44. Current Contract Baseline

The current minimum Connector contract is:

```text
Connector

- identifies itself;

- receives one ConnectedSource context;

- advertises capabilities available for that source;

- describes capability-specific permission requirements;

- exposes authorization state;

- prepares Provider-specific authorization;

- performs capability-specific collection;

- minimizes source data;

- returns framework Observations;

- reports complete, partial or failed collection;

- preserves continuation state when required;

- supports incremental collection where advertised;

- supports independent source instances;

- supports source-specific disconnection;

- preserves Provider-independent errors and warnings.
```

The contract must not require:

```text
AI

specific database technology

specific cloud provider

specific OAuth provider

specific Discovery Source type

specific UI technology

specific graph technology
```

---

## 45. Downstream Contract Dependencies

The Connector output enters the following Discovery pipeline:

```text
Connector
    |
    v
Observation
   /       \
  /         \
 v           v
Service      Evidence
Candidate    Classification
Detector
```

The Connector must therefore comply with the Observation Contract but must not perform downstream semantic responsibilities.

The current contract dependency order remains:

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
```

while Evidence Classification operates as an independent branch from the same Observation:

```text
Observation
   /       \
  v         v
Candidate   Evidence
Detection   Classification
```

The results later converge through Evidence Aggregation and Relationship Assessment.

The Connector Contract is now aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- the parallel Entity Resolution and Evidence Classification model;
- the consolidated ConnectedSource Core Domain Entity;
- the Connector minimization boundary.

No further Connector-domain abstraction is required before implementation-oriented interface design.
