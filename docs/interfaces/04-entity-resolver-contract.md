# Entity Resolver Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md` - Draft v0.3  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md` - Draft v0.3  
**Related Interfaces:**
- `docs/interfaces/01-connector-contract.md`
- `docs/interfaces/02-observation-contract.md`
- `docs/interfaces/03-service-candidate-detector-contract.md`

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `EntityResolver` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Entity Resolver attempts to associate one or more technical Service identifiers with a canonical `Service`.

Conceptually:

```text
CandidateIdentifier
        |
        v
ServiceIdentifier
        |
        v
EntityResolver
        |
   +----+---------+
   |              |
   v              v
RESOLVED      UNRESOLVED
   |
   v
Service
```

An additional outcome exists when more than one canonical Service remains plausible:

```text
AMBIGUOUS
```

The Entity Resolver answers:

> Which canonical Service, if any, does this identifier appear to represent?

It does not determine:

- whether an Observation is relevant to Service Discovery;
- what semantic Evidence an Observation represents;
- whether the User has a meaningful Relationship with the Service;
- whether an Account exists;
- which personal data a Service currently holds.

---

## 2. Architectural Position

The Entity Resolver operates after Service Candidate Detection.

Conceptually:

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
ENTITY RESOLVER
      |
  +---+----------------+
  |         |          |
  v         v          v
RESOLVED UNRESOLVED AMBIGUOUS
  |
  v
Service
```

Evidence Classification operates independently from this branch:

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
           ServiceIdentifier
                   |
                   v
           Entity Resolution
```

Therefore Entity Resolution must not depend on successful Evidence Classification.

---

## 3. Core Question

The Resolver answers:

> What canonical Service does this technical identifier represent?

It does not answer:

> Is this Observation relevant?

That belongs to Service Candidate Detection.

It does not answer:

> What does this Observation mean?

That belongs to Evidence Classification.

It does not answer:

> What does the complete body of Evidence imply about the User-Service Relationship?

That belongs to Relationship Assessment.

---

## 4. Fundamental Distinction

The central distinction is:

```text
IDENTIFIER != SERVICE
```

For example:

```text
spotify.com
```

is a technical identifier.

```text
Spotify
```

is a canonical Service.

Likewise:

```text
accounts.spotify.com
```

and:

```text
https://accounts.spotify.com/login
```

are technical identifiers.

They must not automatically become separate canonical Services.

---

## 5. Candidate Is Not Resolved

A Candidate Observation may remain unresolved.

For example:

```text
Observation:
Password Manager Entry

URI:
https://old-service.example
```

may produce:

```text
CandidateStatus:
CANDIDATE

ResolutionStatus:
UNRESOLVED
```

Therefore:

```text
CANDIDATE != RESOLVED
```

The failure to resolve a Service must not retroactively invalidate the candidate.

---

## 6. Entity Resolution Is Not Relationship Assessment

Resolving:

```text
spotify.com
    |
    v
Spotify
```

does not mean:

```text
User has an ESTABLISHED Spotify Relationship
```

It means only:

> The observed identifier has been associated with the canonical Service Spotify.

Therefore:

```text
RESOLVED SERVICE
       !=
ESTABLISHED RELATIONSHIP
```

A successful Entity Resolution does not determine:

```text
RelationshipStatus
```

or:

```text
TemporalStatus
```

Those conclusions belong to Relationship Assessment.

---

## 7. Input Contract

Conceptually:

```text
resolve(
    request
)
    ->
ResolutionResult
```

A request should provide:

```text
ResolutionRequest

- observation_id
- candidate_identifiers
- context
```

The Resolver should not require the complete Observation when CandidateIdentifiers and explicitly permitted context are sufficient.

This supports data minimization.

---

## 8. CandidateIdentifier

`CandidateIdentifier` represents an identifier produced by Service Candidate Detection.

Conceptually:

```text
CandidateIdentifier

- type
- value
- source_attribute
```

Examples include:

```text
EMAIL_DOMAIN:
spotify.com
```

```text
HOSTNAME:
accounts.spotify.com
```

```text
URL:
https://accounts.spotify.com/login
```

A CandidateIdentifier is not a canonical Service.

---

### 8.1 CandidateIdentifier and ServiceIdentifier

The consolidated Domain Model distinguishes between:

```text
CandidateIdentifier
```

and:

```text
ServiceIdentifier
```

`CandidateIdentifier` is an interface-level processing representation produced by Service Candidate Detection.

`ServiceIdentifier` is the Domain Value Concept used when an identifier and its provenance, normalization or resolution history become part of retained Discovery state.

Conceptually:

```text
Observation
      |
      v
ServiceCandidateDetector
      |
      v
CandidateIdentifier
[processing representation]
      |
      v
ServiceIdentifier
[Domain Value Concept]
      |
      v
EntityResolver
```

The exact materialization boundary between CandidateIdentifier and ServiceIdentifier remains an Implementation Model decision.

Therefore:

```text
CandidateIdentifier
        !=
ServiceIdentifier
        !=
Service
```

in terms of software role, even when CandidateIdentifier and ServiceIdentifier carry the same technical value.

---

## 9. Identifier Types

Potential initial identifier types include:

```text
DOMAIN
HOSTNAME
URL
EMAIL_ADDRESS
EMAIL_DOMAIN
DISPLAY_NAME
PROVIDER_SPECIFIC
```

Future sources may justify additional types such as:

```text
OAuth application ID
mobile application package ID
merchant identifier
application identifier
source-specific Service reference
```

The vocabulary must remain extensible.

---

## 10. Original Identifier Preservation

The Resolver must preserve the original observed identifier.

Conceptually:

```text
Original Identifier
        |
        v
Normalized Identifier
        |
        v
Canonical Service
```

Resolution must not destructively replace:

```text
accounts.spotify.com
```

with:

```text
Spotify
```

without retaining the original value and transformation provenance.

---

## 11. Normalization

Entity Resolution may use deterministic normalization before canonical lookup.

Examples include:

```text
URL
  |
  v
Hostname
```

```text
accounts.spotify.com
        |
        v
spotify.com
```

Potential operations include:

- scheme removal;
- hostname extraction;
- case normalization;
- port removal;
- registrable-domain extraction;
- internationalized-domain handling;
- known alias normalization.

Normalization rules must remain explicit and testable.

---

## 12. Normalization Is Not Resolution

The framework must distinguish:

```text
accounts.spotify.com
        |
        v
spotify.com
```

from:

```text
spotify.com
        |
        v
Spotify
```

The first is technical normalization.

The second is semantic Entity Resolution.

Therefore:

```text
NORMALIZATION != RESOLUTION
```

Both transformations should remain explainable.

---

## 13. Domain Normalization

Domain processing must use domain semantics rather than naïve string manipulation.

For example:

```text
service.example.co.uk
```

must not be treated as though:

```text
co.uk
```

were the canonical Service domain.

Implementation may therefore require a Public Suffix List-aware mechanism.

The specific library or reference dataset belongs to the Implementation Model.

---

## 14. Service Registry

The consolidated Domain Model recognizes a `ServiceRegistry` boundary as necessary for managing canonical Services and their known identifiers.

The Service Registry is classified as:

```text
Application / Repository Boundary
```

rather than a Core Domain Entity.

Conceptually:

```text
EntityResolver
      |
      v
ServiceRegistry
      |
      +-- Service
      |      |
      |      +-- ServiceIdentifier
      |      +-- ServiceIdentifier
      |
      +-- Service
```

The Entity Resolver may query the Service Registry during resolution.

The Service Registry may eventually provide access to:

```text
canonical Services
known ServiceIdentifiers
aliases
historical identifiers
User corrections
Service mappings
```

However, the Entity Resolver does not automatically own:

- Service persistence;
- creation of new canonical Services;
- Service merge;
- Service split;
- Service Registry lifecycle;
- registry synchronization;
- registry governance.

The exact persistence technology and Service Registry interface remain undefined.

The Implementation Model must establish this boundary before the first executable EntityResolver is implemented.

---

## 15. Exact Identifier Match

The strongest deterministic resolution mechanism may be a known exact mapping.

Example:

```text
spotify.com
      |
      v
ServiceRegistry
      |
      v
Spotify
```

Possible method:

```text
EXACT_IDENTIFIER_MATCH
```

A known exact match may justify:

```text
ResolutionStatus:
RESOLVED
```

provided registry semantics are reliable.

---

## 16. Normalized Identifier Match

Resolution may also occur after normalization.

Example:

```text
accounts.spotify.com
        |
        v
spotify.com
        |
        v
Spotify
```

Possible method:

```text
DOMAIN_NORMALIZATION
```

Normalization steps must remain traceable.

---

## 17. Alias Mapping

A Service may have multiple identifiers or historical aliases.

Example:

```text
old-service.example
new-service.example
```

may both map to:

```text
Service X
```

when a known mapping supports that conclusion.

Alias mappings should belong to explicit reference information rather than hidden string heuristics.

---

## 18. Resolution Status

The minimum resolution model is:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

These are semantic resolution outcomes.

They remain separate from technical processing state.

---

## 19. RESOLVED

`RESOLVED` means that the Resolver has identified one canonical Service under the active resolution rules and Registry state.

Conceptually:

```text
ResolutionStatus:
RESOLVED

ResolvedService:
Spotify
```

The Resolver must preserve the Evidence supporting that mapping.

---

## 20. UNRESOLVED

`UNRESOLVED` means that no canonical Service can currently be identified with sufficient justification.

Example:

```text
Identifier:
old-service.example

ResolutionStatus:
UNRESOLVED
```

This is valid.

The Resolver must not fabricate a Service merely to avoid an unresolved state.

---

## 21. AMBIGUOUS

`AMBIGUOUS` means that more than one plausible canonical Service remains and the Resolver cannot safely choose one.

Example:

```text
Identifier:
shared-platform.example

Possible Services:
Service A
Service B
```

Result:

```text
ResolutionStatus:
AMBIGUOUS
```

The alternatives may be preserved for later re-resolution or User review.

---

## 22. Processing Status

Technical processing state should remain separate.

Conceptually:

```text
ProcessingStatus

SUCCESS
UNSUPPORTED
FAILED
```

Thus:

```text
processing_status:
SUCCESS

resolution_status:
UNRESOLVED
```

means the Resolver worked correctly.

By contrast:

```text
processing_status:
FAILED
```

means the resolution operation itself could not complete.

---

## 23. Unsupported Identifier Type

A Resolver may receive an identifier type it cannot process.

Example:

```text
IdentifierType:
FUTURE_PROVIDER_IDENTIFIER
```

Possible result:

```text
processing_status:
UNSUPPORTED
```

This must remain distinct from:

```text
resolution_status:
UNRESOLVED
```

Unsupported means:

> I cannot process this identifier type.

Unresolved means:

> I processed the identifier but could not identify a Service.

---

## 24. Resolution Result

The Resolver must return a structured result.

Conceptually:

```text
ResolutionResult

- observation_id
- input_identifiers
- normalized_identifiers
- processing_status
- resolution_status
- resolved_service
- alternative_services
- method
- reason_codes
- resolver_version
```

This result must preserve enough provenance to explain the mapping.

---

### 24.1 Domain Classification

The consolidated Domain Model classifies `ResolutionResult` as:

```text
Processing Result / Value Object
```

rather than a Core Domain Entity.

It may still be persisted when required for:

- provenance;
- explainability;
- historical comparison;
- User correction;
- re-resolution;
- debugging;
- Service merge or split analysis.

Persistence does not make the ResolutionResult the authoritative representation of the Service.

Therefore:

```text
ResolutionResult != Service
```

---

## 25. Resolution Method

Potential conceptual methods include:

```text
EXACT_IDENTIFIER_MATCH
DOMAIN_NORMALIZATION
KNOWN_ALIAS
SERVICE_REGISTRY
USER_CORRECTION
AI
COMPOSITE
```

The exact vocabulary remains open.

The method should support explainability.

---

## 26. Reason Codes

Potential reason codes include:

```text
EXACT_IDENTIFIER_MATCH
NORMALIZED_DOMAIN_MATCH
KNOWN_ALIAS
NO_MATCH
MULTIPLE_MATCHES
SHARED_INFRASTRUCTURE
INSUFFICIENT_INFORMATION
HISTORICAL_IDENTIFIER
USER_CONFIRMED
CONFLICTING_IDENTIFIERS
```

These are illustrative.

The final taxonomy should emerge from implementation and validation.

---

## 27. Numerical Confidence Is Outside the Initial Discovery Model

The consolidated Discovery Architecture explicitly excludes numerical Confidence from the initial Entity Resolution baseline.

The Entity Resolver therefore uses:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

together with:

```text
resolution method
reason codes
normalization provenance
resolver version
alternative Services
```

rather than values such as:

```text
Spotify = 0.91
```

A numerical Resolution Confidence may be reconsidered only if future empirical validation demonstrates that:

- its semantics can be defined precisely;
- representative validation data exists;
- calibration is possible;
- the score provides measurable User value.

This aligns with:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

---

## 28. Cross-Source Resolution

The same canonical Service may be supported by identifiers from different ConnectedSources.

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

The framework must not create:

```text
Spotify-from-Gmail

Spotify-from-Password-Manager
```

as separate canonical Services.

---

## 29. Provider Independence

Service identity must remain independent from which Provider generated the identifier.

For example:

```text
Gmail Observation
Outlook Observation
Password Manager Observation
Browser Observation
```

may all contribute identifiers resolving to one Service.

Provider identity is provenance, not canonical Service identity.

---

## 30. Multiple Identifiers

One Service may have many identifiers.

Example:

```text
Spotify
 |
 +-- spotify.com
 +-- accounts.spotify.com
 +-- open.spotify.com
 +-- no-reply@spotify.com
```

The registry and Resolver must support many-to-one identifier-to-Service mappings.

---

## 31. Conflicting Identifiers

One Observation may expose multiple identifiers suggesting different entities.

For example:

```text
sender domain:
mailer-platform.example

link domain:
example-service.com

display name:
Example Service
```

The Resolver must not choose arbitrarily.

Possible outcomes include:

```text
RESOLVED
```

when explicit rules safely identify the intended Service;

```text
AMBIGUOUS
```

when multiple plausible Services remain;

or:

```text
UNRESOLVED
```

when insufficient information exists.

---

## 32. Shared Infrastructure

Services may use shared infrastructure such as:

```text
transactional email providers
customer-support platforms
cloud hosting
CDNs
payment processors
authentication providers
marketing platforms
```

An infrastructure identifier may not represent the Service relevant to the User.

The Resolver must not automatically convert every technical infrastructure Provider into the discovered Service.

---

## 33. Infrastructure Can Still Be a Service

The previous rule does not mean infrastructure Providers can never be discovered Services.

For example, the User may independently have a direct Relationship with:

```text
Cloudflare
AWS
Stripe
GitHub
```

depending on context.

Therefore:

```text
INFRASTRUCTURE
        !=
ALWAYS NOT A SERVICE
```

Resolution must consider the specific identifier context.

---

## 34. Service Versus Organization

The Resolver resolves canonical `Service` identity.

It must not silently collapse:

```text
Service
Organization
Brand
Legal Data Controller
```

into one object.

For example:

```text
YouTube
Google Drive
Gmail
```

may ultimately belong to one Organization while remaining distinct Services.

Therefore:

```text
SERVICE != ORGANIZATION
```

---

## 35. Service Versus Brand

A Brand may operate multiple Services.

A Service may also be rebranded without meaning that every historical Relationship should be rewritten as though the old Brand never existed.

The current contract resolves Services.

A dedicated Brand model remains outside the initial Discovery Domain.

---

## 36. Service Granularity

The most difficult unresolved Entity Resolution question is canonical Service granularity.

For example:

```text
Google
Google Account
Gmail
```

could represent:

- one Service;
- three Services;
- an Organization plus two Services;
- another hierarchy.

The Resolver must not answer this implicitly through technical-domain normalization.

Service granularity requires explicit Registry policy and empirical validation.

---

## 37. Product Versus Service

A product name may or may not correspond directly to the canonical Service unit used by the framework.

For example:

```text
Microsoft 365
Outlook
OneDrive
Microsoft Account
```

may require different canonical boundaries.

Draft v0.1 does not define a universal Product-to-Service ontology.

---

## 38. One Domain, Multiple Services

One domain may support multiple Services.

Therefore:

```text
one domain
      !=
one Service
```

Examples may arise through:

```text
shared corporate domains
platform hosting
multi-product portals
identity infrastructure
```

Entity Resolution cannot rely exclusively on registrable domain in every case.

---

## 39. Multiple Domains, One Service

Conversely:

```text
multiple domains
       !=
multiple Services
```

One Service may use:

- authentication domains;
- application domains;
- transactional domains;
- historical domains;
- regional domains.

The Resolver must support known many-to-one mappings.

---

## 40. URL Path Semantics

In some cases the URL path may contain Service-level information.

For example:

```text
platform.example/service-a
platform.example/service-b
```

may indicate different logical Services despite sharing one hostname.

The initial Resolver should avoid assuming that:

```text
hostname alone
```

is sufficient in every case.

Whether path-aware resolution is required for the first MVP remains open.

---

## 41. Email Local-Part Semantics

Email addresses contain both:

```text
local-part
@
domain
```

For many cases the domain is the useful Service identifier.

However:

```text
billing@service.example
security@service.example
newsletter@service.example
```

may carry contextual information.

The local part may support explanation or downstream classification.

It should not automatically create separate Service identities.

---

## 42. Display Names

Observed display names may contribute context.

Example:

```text
Spotify <no-reply@mailer.example>
```

The display name may suggest:

```text
Spotify
```

while the technical sender belongs to an intermediary.

Display names are weaker and potentially spoofable.

They must not automatically override stronger identifier provenance.

---

## 43. Provider-Specific Identifiers

Some sources may provide identifiers such as:

```text
application ID
merchant ID
OAuth client
password-manager application identifier
mobile package ID
```

These may be valuable for deterministic resolution.

Provider-specific identifier semantics should remain behind explicit identifier types rather than being encoded as arbitrary strings.

---

## 44. Historical Identifiers

Services change domains and identifiers.

The Registry may therefore need:

```text
Current Identifier

Historical Identifier

Alias
```

Example:

```text
old-service.example
        |
        v
Service X
```

The historical identifier must remain preserved.

---

## 45. Rebranding

A Service may change its public name while remaining the same canonical Service under explicit Registry policy.

For example:

```text
Old Brand
     |
     v
New Brand
```

must not automatically require a new Service entity.

But rebranding semantics should be explicit rather than guessed dynamically.

---

## 46. Acquisitions

Organization acquisition does not automatically mean Service identity merger.

Example:

```text
Organization B acquires Service A
```

does not imply:

```text
Service A = Organization B
```

or:

```text
Service A = every other Service operated by Organization B
```

Entity Resolution must preserve Service-level identity.

---

## 47. Service Merge

Two previously distinct canonical Services may later be determined to represent the same Service.

A Service merge must preserve:

- original identifiers;
- resolution history;
- Evidence;
- User corrections;
- Relationship reassessment capability.

The EntityResolver itself does not own merge lifecycle.

---

## 48. Service Split

The inverse may occur.

A previously broad Service may later require splitting into multiple canonical Services.

The framework must preserve enough provenance to redistribute:

- ServiceIdentifiers;
- Evidence;
- Relationships;

according to explicit correction or Registry rules.

The EntityResolver itself does not own split lifecycle.

---

## 49. Manual Service Creation

If the Resolver cannot identify an existing canonical Service, the User may eventually be allowed to propose or confirm a new Service.

For example:

```text
Identifier:
oldwebsite.example

Resolver:
UNRESOLVED

User:
"This was Old Website."
```

However, Service creation does not belong directly to the Entity Resolver.

The consolidated Domain Model assigns Service Registry lifecycle to an:

```text
Application / Repository Boundary
```

Therefore a possible future flow is:

```text
UNRESOLVED identifier
        |
        v
Application-Level Service Creation Workflow
        |
     +--+----------------+
     |                   |
     v                   v
Create Service       Remain Unresolved
     |
     v
Register Identifier
     |
     v
Re-Resolution
```

The exact Service creation process remains outside this contract.

---

## 50. User Corrections

Users may eventually correct resolution conclusions.

Example:

```text
Framework:
example.com -> Service A

User:
This actually belongs to Service B.
```

The original automated ResolutionResult must remain preserved.

A corrected mapping may use:

```text
ResolutionMethod:
USER_CORRECTION
```

according to explicit policy.

---

## 51. User Correction Priority

A User correction may be strong local information.

However, the framework must eventually define how corrections interact with:

- curated Registry mappings;
- later Registry updates;
- Service merge/split;
- automated re-resolution.

Draft v0.1 does not define a universal precedence hierarchy.

---

## 52. Correction Provenance

User corrections must remain attributable to:

```text
User
timestamp
previous result
corrected result
```

where practical.

Corrections must not destructively erase the previous automated conclusion.

---

## 53. Deterministic First

Entity Resolution should prefer deterministic methods where they safely solve the problem.

Examples include:

```text
exact identifier lookup
domain normalization
known aliases
historical mappings
User corrections
```

AI should not replace reliable deterministic Registry lookup.

---

## 54. AI-Assisted Resolution

AI may eventually assist when:

- identifiers are incomplete;
- display names are ambiguous;
- historical Services lack known mappings;
- unusual metadata provides semantic hints.

AI should normally propose possible mappings rather than fabricate canonical identities without supporting information.

---

## 55. AI Is Optional

Entity Resolution must continue functioning without AI.

If AI is:

- unavailable;
- disabled;
- incompatible with privacy policy;

valid outcomes remain:

```text
UNRESOLVED
AMBIGUOUS
```

This is graceful degradation.

---

## 56. AI Input Minimization

AI-assisted Entity Resolution must receive only information necessary for resolution.

It must not automatically receive:

- complete email content;
- password values;
- unrelated User identities;
- full mailbox history;
- Provider credentials.

The same local-first and Progressive Permission boundaries apply.

---

## 57. External Reference Data

Resolution may use external or curated datasets.

Potential examples include:

```text
Public Suffix List
local Service mappings
curated Service Registry
known domain aliases
historical-domain datasets
```

External reference data introduces concerns such as:

- licensing;
- freshness;
- reproducibility;
- offline operation;
- privacy.

The initial implementation should introduce reference datasets only when justified.

---

## 58. Reference Data Versioning

If resolution relies on mutable reference data, reproducibility may require preserving its version.

Conceptually:

```text
Resolver Version:
2

Service Registry Version:
2026-11
```

Draft v0.1 does not require a specific versioning implementation.

However, materially changing resolution inputs should eventually remain traceable.

Service Registry versioning is distinct from Resolver versioning.

A change to the Service Registry may alter resolution results even when the Resolver implementation itself has not changed.

---

## 59. Resolver Version

The Resolver result should identify the Resolver version where practical.

Conceptually:

```text
resolver_version:
1
```

This supports re-resolution and comparison when resolution logic changes.

---

## 60. Re-Resolution

Preserved identifiers should support later re-resolution.

Conceptually:

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
           Spotify
```

Source retrieval should not be required if preserved minimized identifier information is sufficient.

---

## 61. Changed Resolution

A later Resolver may disagree with an earlier result.

Example:

```text
Resolver v1:
Service A

Resolver v2:
Service B
```

The framework must preserve enough provenance to understand:

- previous mapping;
- current mapping;
- Resolver version;
- supporting identifier;
- reason for reassessment where available.

Current canonical association and historical ResolutionResults are separate concerns.

---

## 62. Re-Resolution and Evidence

Evidence may already exist when Service resolution changes.

Conceptually:

```text
Evidence:
PAYMENT

Old resolution:
UNRESOLVED

New resolution:
Spotify
```

The Evidence may then become associated with the resolved Service without reclassifying the Observation if Evidence semantics remain unchanged.

---

## 63. Re-Resolution and Aggregates

Resolution changes may require:

```text
old Aggregate invalidation
        |
        v
Evidence reassociation
        |
        v
new Aggregate
        |
        v
Relationship reassessment
```

The Resolver does not own this orchestration.

The application layer does.

---

## 64. Resolution Result Persistence

ResolutionResults may need to be persisted for:

- explainability;
- performance;
- auditing;
- reprocessing comparison;
- User correction;
- Service merge/split handling.

However, the contract does not require one persistence strategy.

A lightweight implementation may initially recompute deterministic resolution where inexpensive.

Persisting ResolutionResult does not change its Domain classification.

It remains:

```text
Processing Result / Value Object
```

rather than:

```text
Core Domain Entity
```

---

## 65. Resolution Stability

A canonical Service mapping should not change arbitrarily between identical resolution runs.

Given the same:

```text
identifier
resolution context
Resolver version
Registry version
```

the result should be deterministic where practical.

This is important for reproducibility.

---

## 66. Statelessness

Where practical, Entity Resolution should behave as a function of:

```text
Identifiers
+
ResolutionContext
+
ResolverVersion
+
ServiceRegistry state
```

Implicit mutable state should be minimized.

Repository and Registry dependencies should remain explicit.

---

## 67. Batch Resolution

An implementation may resolve multiple identifier groups together.

Conceptually:

```text
resolve_many(...)
```

may improve performance.

Each request must still receive independently traceable:

```text
ResolutionResult
```

Batch processing must not destroy provenance.

---

## 68. Minimum Necessary Input

The Resolver should consume the minimum information required for resolution.

For example, a domain identifier may not require:

```text
message body
full password-manager entry
all source metadata
```

to resolve:

```text
spotify.com -> Spotify
```

This follows data minimization.

---

## 69. Canonical Service Creation Boundary

The Entity Resolver contract does not assume that every successfully interpreted identifier already has a canonical Service in the Service Registry.

A case may arise where:

```text
identifier appears to represent a legitimate Service
```

but:

```text
no matching canonical Service exists
```

This creates a separation between:

```text
resolution
```

and:

```text
Service creation / registration
```

The Entity Resolver answers:

> Does this identifier resolve to an existing canonical Service?

The application layer separately determines:

> Should a new canonical Service be created?

Conceptually:

```text
Candidate Identifier
        |
        v
EntityResolver
        |
        v
NO EXISTING SERVICE
        |
        v
Application-Level Workflow
       / \
      /   \
     v     v
 create   remain
 Service  unresolved
     |
     v
ServiceRegistry
     |
     v
re-resolution
```

The Implementation Model must define this workflow.

---

## 70. Existing vs New Services

A future application workflow may need to distinguish:

```text
MATCHED_EXISTING_SERVICE
```

from:

```text
NEW_SERVICE_CANDIDATE
```

However, this distinction should not be introduced directly into ResolutionStatus.

The canonical Entity Resolution states remain:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

`NEW_SERVICE_CANDIDATE` is an application-level interpretation of an unresolved but apparently legitimate candidate.

---

## 71. Resolution Request

The conceptual request is:

```text
ResolutionRequest

- observation_id
- candidate_identifiers
- context
```

The `observation_id` preserves traceability.

The Resolver should not need the complete Observation when identifiers and permitted context are sufficient.

The CandidateIdentifiers may correspond to transient representations of Domain ServiceIdentifiers.

The Implementation Model must determine where:

```text
CandidateIdentifier
        |
        v
ServiceIdentifier
```

materialization occurs.

---

## 72. Resolution Context

Conceptually:

```text
ResolutionContext

- ServiceRegistry
- normalization_policy
- reference_data
- user_corrections
- resolution_policy
- optional_ai_policy
```

The context must not contain:

- Provider credentials;
- unrestricted raw source data;
- unrelated User information.

The exact structure remains open.

---

## 73. Context Escalation

If available identifiers are insufficient, the Resolver should normally return:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

It must not independently escalate source permissions.

A higher-level application workflow may decide whether additional authorized information is justified.

---

## 74. Language-Independent Interface

Conceptually:

```text
interface EntityResolver {

    ResolutionResult resolve(
        ResolutionRequest request
    )
}
```

This is pseudocode.

It is not the final Python interface.

---

## 75. ServiceRegistry Dependency

The Resolver depends on a ServiceRegistry abstraction rather than a concrete persistence technology.

Conceptually:

```text
interface ServiceRegistry {

    ServiceMatches findByIdentifier(
        ServiceIdentifier identifier
    )
}
```

This is illustrative.

The actual ServiceRegistry contract belongs to the Implementation Model rather than a new Discovery processing contract.

---

## 76. Resolution Result Contract

Conceptually:

```text
ResolutionResult {

    ObservationId observationId

    List<CandidateIdentifier> inputIdentifiers

    List<NormalizedIdentifier> normalizedIdentifiers

    ProcessingStatus processingStatus

    Optional<ResolutionStatus> resolutionStatus

    Optional<ServiceReference> resolvedService

    List<ServiceReference> alternativeServices

    ResolutionMethod method

    List<ReasonCode> reasonCodes

    ResolverVersion resolverVersion
}
```

This is conceptual pseudocode.

`ResolutionResult` remains a:

```text
Processing Result / Value Object
```

`resolvedService` contains a reference to the canonical Domain Service.

---

## 77. Entity Resolver Invariants

### ER-INV-001

The Resolver must operate on framework identifiers rather than raw Provider objects.

### ER-INV-002

Original identifiers must remain traceable after normalization and resolution.

### ER-INV-003

Normalization and Entity Resolution must remain distinguishable.

### ER-INV-004

RESOLVED must reference one canonical Service.

### ER-INV-005

UNRESOLVED must not cause creation of a fabricated Service.

### ER-INV-006

AMBIGUOUS must remain a valid outcome.

### ER-INV-007

Processing failure must remain distinguishable from UNRESOLVED.

### ER-INV-008

Unsupported identifier type must remain distinguishable from UNRESOLVED.

### ER-INV-009

Entity Resolution must remain independent from Evidence Classification.

### ER-INV-010

A resolved Service must not imply current personal-data possession.

### ER-INV-011

A resolved Service must not imply an ESTABLISHED User-Service Relationship.

### ER-INV-012

Provider identity must not create Provider-specific copies of canonical Services.

### ER-INV-013

Multiple identifiers may resolve to one Service.

### ER-INV-014

One identifier must not be assumed to identify one Service in every context.

### ER-INV-015

Service and Organization must remain distinct concepts.

### ER-INV-016

Provider credentials must not be required by the Resolver.

### ER-INV-017

The Resolver must not request additional source permissions directly.

### ER-INV-018

Deterministic resolution should be preferred when sufficient.

### ER-INV-019

AI must remain optional.

### ER-INV-020

AI must not fabricate a Service when available information is insufficient.

### ER-INV-021

Resolution results must remain explainable through identifiers, mappings and provenance.

### ER-INV-022

Numerical Entity Resolution Confidence is outside the initial Discovery model.

### ER-INV-023

Re-resolution must not require destructive modification of preserved identifiers.

### ER-INV-024

Service merge and split operations must preserve resolution provenance.

### ER-INV-025

User correction must not destructively erase previous automated ResolutionResults.

### ER-INV-026

ResolutionResult must remain distinguishable from the canonical Service it references.

### ER-INV-027

Persistence of a ResolutionResult must not change its classification as a Processing Result / Value Object.

### ER-INV-028

The Entity Resolver must not create canonical Services as an implicit side effect of ordinary resolution.

### ER-INV-029

Service creation, Service merge and Service split lifecycle must remain outside normal Entity Resolver responsibility.

### ER-INV-030

The Entity Resolver may depend on a ServiceRegistry boundary but must not depend on its concrete persistence technology.

### ER-INV-031

CandidateIdentifier and ServiceIdentifier must remain distinguishable from canonical Service identity.

---

## 78. Gmail Resolution Example

Input:

```text
Observation:
observation_001

CandidateIdentifier:
EMAIL_DOMAIN = spotify.com
```

Resolution:

```text
spotify.com
      |
      v
ServiceRegistry lookup
      |
      v
Spotify
```

Possible result:

```text
processing_status:
SUCCESS

resolution_status:
RESOLVED

resolved_service:
service_spotify

method:
EXACT_IDENTIFIER_MATCH
```

The Resolver does not classify the Observation as ACCOUNT_VERIFICATION.

---

## 79. Password Manager Resolution Example

Input:

```text
Observation:
observation_002

CandidateIdentifier:
HOSTNAME = accounts.spotify.com
```

Resolution:

```text
accounts.spotify.com
       |
       v
Domain normalization
       |
       v
spotify.com
       |
       v
ServiceRegistry lookup
       |
       v
Spotify
```

Possible result:

```text
processing_status:
SUCCESS

resolution_status:
RESOLVED

normalized_identifier:
spotify.com

resolved_service:
service_spotify

method:
DOMAIN_NORMALIZATION
```

The Gmail and Password Manager Observations converge on the same canonical Service.

---

## 80. Unresolved Example

Input:

```text
Identifier:
old-service.example
```

No Registry mapping exists.

Result:

```text
processing_status:
SUCCESS

resolution_status:
UNRESOLVED

reason_codes:
- NO_MATCH
```

No Service is fabricated.

---

## 81. Ambiguous Example

Input:

```text
Identifier:
shared-login.example
```

Registry/context exposes:

```text
Service A
Service B
```

but neither can safely be selected.

Result:

```text
processing_status:
SUCCESS

resolution_status:
AMBIGUOUS

alternative_services:
- service_a
- service_b
```

---

## 82. Shared Infrastructure Example

Input:

```text
sender domain:
mailer-platform.example

display:
Example Shop
```

The technical domain belongs to shared transactional infrastructure.

The Resolver must not automatically produce:

```text
Service:
Mailer Platform
```

nor:

```text
Service:
Example Shop
```

without sufficient mapping information.

Possible result:

```text
UNRESOLVED
```

with:

```text
reason:
SHARED_INFRASTRUCTURE
```

---

## 83. Historical Identifier Example

Input:

```text
old-brand.example
```

ServiceRegistry contains an explicit historical mapping:

```text
old-brand.example
        |
        v
Service X
```

Possible result:

```text
RESOLVED
```

while preserving:

```text
original_identifier:
old-brand.example
```

The historical identifier is not overwritten.

---

## 84. Conflicting-Identifier Example

Input:

```text
EMAIL_DOMAIN:
mailer-platform.example

URL_HOSTNAME:
example-service.com
```

If context does not safely establish which identifier represents the relevant Service:

```text
resolution_status:
AMBIGUOUS
```

or:

```text
UNRESOLVED
```

is preferable to arbitrary selection.

---

## 85. User-Corrected Resolution Example

Initial result:

```text
example.com
    ->
Service A
```

User correction:

```text
example.com
    ->
Service B
```

The framework preserves:

```text
automated ResolutionResult
```

and:

```text
User correction provenance
```

The current mapping may use:

```text
method:
USER_CORRECTION
```

under explicit correction policy.

---

## 86. Open Questions

### Candidate Identifiers

- Is the current CandidateIdentifier representation sufficient?
- Which identifier types are necessary initially?
- Should URLs remain full URLs or be decomposed before resolution?
- Should display names be CandidateIdentifiers or contextual attributes?
- At which application boundary should CandidateIdentifier become ServiceIdentifier?

### Normalization

- Which normalization belongs to Candidate Detection?
- Which belongs to Entity Resolution?
- Should normalization be represented as its own versioned component?
- How should internationalized domains be handled?
- How should Public Suffix List data be versioned?

### Service Registry

The consolidated Domain Model already recognizes the need for a ServiceRegistry boundary.

The remaining questions are:

- What is the initial ServiceRegistry implementation?
- Is the Registry entirely local?
- Which canonical Services populate the initial Registry?
- How are ServiceIdentifier mappings stored?
- How are aliases represented?
- How are historical identifiers represented?
- How are Registry entries versioned?
- Can Users add or correct Services?
- Can Connectors contribute candidate mappings?
- Which component validates contributed mappings?
- How are incorrect mappings corrected?
- How are Service merge and split operations represented?
- Which repository technology should back the Registry?

### Service Creation

Service creation is explicitly outside EntityResolver responsibility.

The remaining questions are:

- Which application component decides whether a new canonical Service should be created?
- Which Evidence is sufficient to propose a new Service?
- Is User confirmation required?
- Can deterministic reference data create a Service automatically?
- Can AI only propose a Service candidate?
- How is a new Service registered in ServiceRegistry?
- How are initial ServiceIdentifiers attached?
- How is accidental Service creation reversed?

### Multiple Services

- Can one ResolutionRequest legitimately resolve to multiple Services?
- Or must that always be represented as AMBIGUOUS?
- How should platform/container Services be represented?

### Product vs Service

- Is a product always a Service?
- Should `accounts.google.com` resolve to Google, Google Account or another Service?
- At what granularity should canonical Services exist?

### Organization

- When should Services be linked to Organizations?
- Should Organization Resolution become a separate capability?
- How will Legal Data Controllers relate to canonical Services?

### Cross-Source Context

- Should the Resolver use previously observed source diversity?
- Or should source diversity remain downstream in Relationship Assessment?

### User Corrections

- How are corrections stored?
- Are they global or local to one User?
- Which corrections can override curated mappings?
- How are accidental corrections reversed?

### AI

- Which unresolved cases justify AI-assisted resolution?
- Should AI propose candidates rather than directly resolve?
- Should User confirmation be required for some AI-generated mappings?

### External Datasets

- Which external datasets are suitable?
- What licensing restrictions apply?
- How are stale mappings detected?
- How can resolution remain functional offline?

### Persistence

- Should ResolutionResult be persisted?
- Should only Registry mappings be persisted?
- Should every Resolver version retain historical results?
- How are superseded Results represented?

### Service Merge and Split

- Which component performs merges?
- How are affected Relationships recalculated?
- How are User corrections preserved?
- How are historical identifiers reassigned safely?

### Confidence

Numerical Entity Resolution Confidence is outside the initial Discovery baseline.

If reconsidered in a future version:

- what exactly will it measure?
- how will it be calibrated?
- what validation dataset will be used?
- how will Users interpret it?
- how will it differ from RESOLVED / UNRESOLVED / AMBIGUOUS?

---

## 87. Findings from Contract Design

### Finding 1 - ServiceIdentifier Is Strongly Validated

The framework requires an explicit representation between:

```text
Observation
```

and:

```text
Service
```

The consolidated Domain Model classifies ServiceIdentifier as a Domain Value Concept.

CandidateIdentifier remains the upstream processing representation.

```text
CandidateIdentifier
        |
        v
ServiceIdentifier
        |
        v
Service
```

### Finding 2 - Normalization and Resolution Are Different

The pipeline must distinguish:

```text
accounts.spotify.com
        |
        v
spotify.com
```

from:

```text
spotify.com
        |
        v
Spotify
```

The first transforms technical representation.

The second establishes canonical Service identity.

### Finding 3 - UNRESOLVED and AMBIGUOUS Are Necessary

A simple:

```text
Service or null
```

response loses important semantics.

The Resolver requires:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

as distinct outcomes.

### Finding 4 - Resolution Must Be Cross-Source

Entity Resolution belongs to the common Discovery Core rather than individual Connectors.

Otherwise different sources could create duplicate representations of the same Service.

### Finding 5 - Service Registry Boundary Is Required but Its Lifecycle Is Not Yet Defined

The Resolver requires canonical Service and ServiceIdentifier information.

The consolidated Domain Model therefore recognizes:

```text
ServiceRegistry
```

as an:

```text
Application / Repository Boundary
```

Its concrete persistence, creation, mapping-governance and merge/split workflows remain open.

### Finding 6 - Service Granularity Requires Validation

Questions such as:

```text
Google
vs
Google Account
vs
Gmail
```

demonstrate that canonical Service identity requires explicit granularity policy.

The Resolver must not decide that policy implicitly.

### Finding 7 - Resolution Provenance Is Required

Mappings may change through:

```text
new rules
new Registry data
rebranding
User correction
Service merge
Service split
```

Resolution must therefore remain traceable and reprocessable.

### Finding 8 - ResolutionResult Is a Processing Result

The Domain Model classifies:

```text
ResolutionResult
```

as:

```text
Processing Result / Value Object
```

It may be persisted for provenance without becoming a Core Domain Entity.

### Finding 9 - Service Creation Is an Application-Level Workflow

Entity Resolution and canonical Service creation are separate responsibilities.

An unresolved but legitimate candidate may require an application-level workflow before a new canonical Service exists.

---

## 88. Architecture Alignment and Remaining Decision Candidates

### Architecture Alignment - Explicit Resolution States

Entity Resolution distinguishes:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

A failure to identify one canonical Service must not produce fabricated resolution.

### Architecture Alignment - Normalization Is Not Resolution

```text
NORMALIZATION != RESOLUTION
```

Both operations remain independently traceable.

### Architecture Alignment - Resolution Is Cross-Source

Equivalent identifiers from different ConnectedSources may resolve to the same canonical Service.

### Architecture Alignment - Provider Independence

Service identity is independent from which Provider supplied the identifier.

### Architecture Alignment - No Numerical Resolution Confidence

Numerical Entity Resolution Confidence is outside the initial Discovery baseline.

This follows:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

### Architecture Alignment - Re-Resolution Supported

Preserved ServiceIdentifiers support later re-resolution without source retrieval when retained information is sufficient.

### Remaining Decision Candidate - Service Creation Workflow

The Implementation Model must define the workflow through which:

```text
unresolved legitimate Service candidate
        |
        v
new canonical Service
```

may occur.

### Remaining Decision Candidate - Service Granularity

The Resolver does not determine whether abstractions such as:

```text
Google
Google Account
Gmail
```

represent one or several canonical Services.

That remains empirically unresolved.

---

## 89. Current Contract Baseline

The aligned Entity Resolver Contract is:

```text
ResolutionRequest
      |
      +-- observation_id
      |
      +-- candidate_identifiers
      |
      +-- resolution_context
      |
      v
EntityResolver
      |
      +------> ServiceRegistry
      |       [Application / Repository Boundary]
      |
      v
ResolutionResult
      |
      +-- processing_status
      |
      +-- resolution_status
      |
      +-- normalized_identifiers
      |
      +-- resolved_service
      |
      +-- alternative_services
      |
      +-- method
      |
      +-- reason_codes
      |
      +-- resolver_version
```

with the guarantees:

```text
CandidateIdentifier / ServiceIdentifier distinction

original identifiers preserved

normalization traceable

NORMALIZATION != RESOLUTION

Provider-independent resolution

cross-source Service convergence

RESOLVED / UNRESOLVED / AMBIGUOUS

no fabricated Service

no Relationship conclusion

no Evidence conclusion

no numerical Confidence

deterministic-first operation

optional AI assistance

ServiceRegistry boundary explicit

Service creation outside EntityResolver

ResolutionResult classified as Processing Result / Value Object

re-resolution supported

User-correction compatibility
```

---

## 90. Downstream Contract

The next semantic contract is:

```text
EvidenceClassifier
```

defined in:

```text
docs/interfaces/05-evidence-classifier-contract.md
```

However, Evidence Classification is not sequentially dependent on successful Entity Resolution.

The consolidated architecture is:

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
           ServiceIdentifier
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

Therefore:

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

The Entity Resolver Contract is aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- ServiceIdentifier as a Domain Value Concept;
- ResolutionResult as a Processing Result / Value Object;
- ServiceRegistry as an Application / Repository Boundary;
- explicit RESOLVED / UNRESOLVED / AMBIGUOUS states;
- normalization/resolution separation;
- resolution/Service-creation separation;
- numerical Confidence excluded from the initial baseline;
- parallel Entity Resolution / Evidence Classification;
- deterministic-first and local-first principles;
- User-correction and re-resolution compatibility.

No additional Entity Resolution processing abstraction is required before the Implementation Model phase.
