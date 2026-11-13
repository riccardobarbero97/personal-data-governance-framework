# Entity Resolver Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md`  
**Related Interfaces:**  
- `docs/interfaces/01-connector-contract.md`
- `docs/interfaces/02-observation-contract.md`
- `docs/interfaces/03-service-candidate-detector-contract.md`

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `EntityResolver` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Entity Resolver determines whether one or more candidate technical identifiers can be associated with a canonical `Service`.

Conceptually:

```text
Observation
      |
      v
Service Candidate Detection
      |
      v
Candidate Identifier
      |
      v
Entity Resolver
      |
  +---+------------+
  |                |
  v                v
Resolved       Unresolved
  |
  v
Service
```

In ambiguous cases:

```text
Candidate Identifier
      |
      v
Entity Resolver
      |
      v
AMBIGUOUS
```

The Entity Resolver answers:

> Which canonical Service, if any, does this observed identifier appear to represent?

It does not determine:

- whether the User has a confirmed account;
- what the Observation means semantically;
- what Evidence Type should be assigned;
- the strength of the Relationship;
- what personal data the Service currently holds.

---

## 2. Architectural Position

The Entity Resolver operates after Service Candidate Detection and before Service-level Evidence aggregation and Relationship Assessment.

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
ENTITY RESOLVER
      |
  +---+---+
  |       |
  v       v
Service   Unresolved
  |
  v
Downstream Discovery
```

Evidence Classification may operate independently on the underlying Observation.

Therefore the broader pipeline may be represented as:

```text
                    Observation
                    /         \
                   /           \
                  v             v
        Candidate Detection   Evidence Classification
                  |             |
                  v             v
        CandidateIdentifier   Evidence
                  |
                  v
          Entity Resolution
                  |
                  v
               Service
                  \             /
                   \           /
                    v         v
                 Aggregation
                      |
                      v
              Relationship Assessment
```

Entity Resolution and Evidence Classification answer different questions.

---

## 3. Fundamental Boundary

The core distinction is:

```text
IDENTIFIER != SERVICE
```

Examples of identifiers include:

```text
spotify.com
accounts.spotify.com
no-reply@spotify.com
https://accounts.spotify.com/login
provider-specific application identifier
```

A canonical Service may be:

```text
Spotify
```

The Entity Resolver is responsible for determining whether such identifiers refer to that Service.

---

## 4. Entity Resolution Is Not Candidate Detection

Candidate Detection asks:

> Is this Observation sufficiently relevant to Service Discovery?

Entity Resolution asks:

> Which canonical Service does the relevant identifier represent?

Example:

```text
Observation:
URI = https://accounts.spotify.com

Candidate Detection:
CANDIDATE

Candidate Identifier:
accounts.spotify.com

Entity Resolution:
Spotify
```

Therefore:

```text
CANDIDATE
    !=
RESOLVED
```

An Observation may be a valid Service candidate while Entity Resolution remains unsuccessful.

---

## 5. Entity Resolution Is Not Evidence Classification

Consider:

```text
From:
no-reply@spotify.com

Subject:
Verify your email address
```

Entity Resolution may answer:

```text
spotify.com
    ->
Spotify
```

Evidence Classification may answer:

```text
Verify your email address
    ->
ACCOUNT_VERIFICATION
```

Neither result substitutes for the other.

Therefore:

```text
SERVICE IDENTITY
       !=
EVIDENCE SEMANTICS
```

---

## 6. Entity Resolution Is Not Relationship Assessment

Resolving:

```text
spotify.com
    ->
Spotify
```

does not mean:

```text
User has confirmed active Spotify account
```

It means only:

> The observed identifier has been associated with the canonical Service `Spotify`.

Therefore:

```text
RESOLVED SERVICE
       !=
CONFIRMED RELATIONSHIP
```

Relationship semantics remain downstream.

---

## 7. Input Contract

The Entity Resolver receives one or more candidate identifiers generated from a Service-relevant Observation.

Conceptually:

```text
resolve(
    identifiers,
    context
)
    ->
ResolutionResult
```

The minimum identifier representation is conceptually:

```text
CandidateIdentifier

- type
- value
- source_attribute
```

Examples:

```text
type:
EMAIL_DOMAIN

value:
spotify.com
```

or:

```text
type:
HOSTNAME

value:
accounts.spotify.com
```

---

## 8. Candidate Identifier Types

Potential identifier types include:

```text
DOMAIN
HOSTNAME
URL
EMAIL_ADDRESS
EMAIL_DOMAIN
DISPLAY_NAME
PROVIDER_SPECIFIC
```

The final taxonomy remains open.

The Entity Resolver must not assume that every identifier is a domain.

Future sources may provide identifiers such as:

```text
application IDs
OAuth client identifiers
package names
mobile application identifiers
merchant identifiers
organization identifiers
provider-specific service references
```

The contract must remain extensible.

---

## 9. Original Identifier

The original Candidate Identifier must remain preserved.

Example:

```text
Original Identifier:
accounts.spotify.com
```

may be normalized to:

```text
Normalized Identifier:
spotify.com
```

and ultimately resolved to:

```text
Service:
Spotify
```

The original value must not be destructively replaced.

Conceptually:

```text
Original Identifier
       |
       v
Normalization
       |
       v
Normalized Identifier
       |
       v
Resolution
       |
       v
Canonical Service
```

This provenance is required for explainability and reprocessing.

---

## 10. Normalization

Entity Resolution may require technical normalization before canonical Service matching.

Examples include:

```text
lowercase normalization

URL -> hostname

hostname -> registrable domain

known alias normalization

internationalized domain handling

trailing-dot normalization
```

Normalization must remain deterministic where practical.

For example:

```text
HTTPS://ACCOUNTS.SPOTIFY.COM/login
```

may be normalized through explicit parsing rather than AI.

---

## 11. Normalization Is Not Resolution

Normalization and Entity Resolution are separate conceptual operations.

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
NORMALIZED IDENTIFIER
        !=
CANONICAL SERVICE
```

The distinction should remain visible in resolution provenance.

---

## 12. Domain Normalization

Domain-like identifiers require standards-aware normalization.

The framework must not naïvely assume:

```text
last two labels = registrable domain
```

because public suffix structures vary.

For example, implementations should eventually use an appropriate Public Suffix List-aware mechanism when determining registrable domains.

The contract does not prescribe a specific library.

The requirement is:

> Domain normalization must use domain semantics rather than naïve string splitting.

---

## 13. Resolution Sources

Entity Resolution may use multiple resolution sources or strategies.

Potential sources include:

```text
deterministic normalization
known Service mappings
local Service registry
known aliases
previously resolved Services
curated mappings
user corrections
external reference datasets
AI-assisted semantic resolution
```

Not every implementation must support every strategy.

The resolution method used must remain traceable.

---

## 14. Local Service Registry

A future implementation may maintain a local Service registry.

Conceptually:

```text
Service Registry

Spotify
 |
 +-- spotify.com
 +-- accounts.spotify.com
 +-- open.spotify.com

GitHub
 |
 +-- github.com
 +-- api.github.com
```

The Entity Resolver may query this registry.

The persistence technology and maintenance process remain undefined.

---

## 15. Known Alias Resolution

Some Services may use identifiers that cannot be resolved through simple domain normalization alone.

Conceptually:

```text
Identifier A
Identifier B
Identifier C
      |
      v
Known Alias Mapping
      |
      v
Canonical Service
```

Alias mappings should be explicit and versionable where they materially affect resolution outcomes.

---

## 16. Multiple Identifiers

One resolution request may include multiple Candidate Identifiers derived from the same Observation.

Example:

```text
sender domain:
mailer.example.net

reply-to domain:
service.example.com
```

or:

```text
URI 1:
https://example.com

URI 2:
https://login.example.com
```

The resolver should therefore support:

```text
List<CandidateIdentifier>
```

rather than requiring exactly one identifier.

---

## 17. Consistent Identifiers

If multiple identifiers independently point to the same canonical Service:

```text
spotify.com
accounts.spotify.com
open.spotify.com
        |
        v
Spotify
```

the resolver may return:

```text
RESOLVED
Service = Spotify
```

while preserving the contributing identifiers.

---

## 18. Conflicting Identifiers

Multiple Candidate Identifiers may suggest different Services.

Example:

```text
sender domain:
email-platform.example

display name:
Example Shop

link domain:
example-shop.com
```

The resolver must not arbitrarily choose the first identifier.

Possible outcomes include:

```text
RESOLVED
```

when rules reliably establish which identifier represents the Service,

or:

```text
AMBIGUOUS
```

when multiple plausible Service identities remain.

---

## 19. Resolution Status

The minimum domain resolution states are:

```text
RESOLVED

UNRESOLVED

AMBIGUOUS
```

These describe successful execution of the resolver.

They do not describe technical processing success.

---

## 20. RESOLVED

`RESOLVED` means that the resolver has enough information under the active resolution strategy to associate the input identifiers with one canonical Service.

Conceptually:

```text
spotify.com
    |
    v
RESOLVED
    |
    v
Spotify
```

This does not mean the User has a confirmed Relationship with Spotify.

---

## 21. UNRESOLVED

`UNRESOLVED` means that processing succeeded but no canonical Service could be reliably identified.

Example:

```text
old-unknown-domain.example
        |
        v
UNRESOLVED
```

The identifier must remain available.

No fabricated Service should be created merely to avoid an unresolved state.

---

## 22. AMBIGUOUS

`AMBIGUOUS` means that multiple plausible canonical Services remain and the resolver cannot safely select one.

Conceptually:

```text
Identifier
    |
    +--> Service A
    |
    +--> Service B
    |
    v
AMBIGUOUS
```

Ambiguity is a valid domain state.

The resolver should preserve the candidate Services where useful.

---

## 23. Processing Status

Domain resolution status must remain separate from technical processing status.

Conceptually:

```text
processing_status:

SUCCESS
UNSUPPORTED
FAILED
```

and, when processing succeeds:

```text
resolution_status:

RESOLVED
UNRESOLVED
AMBIGUOUS
```

For example:

```text
processing_status:
SUCCESS

resolution_status:
UNRESOLVED
```

means:

> The resolver worked correctly, but it could not identify the Service.

This is fundamentally different from:

```text
processing_status:
FAILED
```

---

## 24. Resolution Result

The initial conceptual result is:

```text
ResolutionResult

- input_identifiers
- normalized_identifiers
- processing_status
- resolution_status
- resolved_service
- alternative_services
- method
- reason_codes
- resolver_version
- provenance
```

This remains implementation-independent.

---

## 25. Resolved Service

When:

```text
resolution_status:
RESOLVED
```

the result should reference a canonical `Service`.

Conceptually:

```text
resolved_service:
service_spotify
```

The resolver should prefer returning a Service identity rather than embedding a duplicate Service representation inside every ResolutionResult.

The exact persistence model remains undefined.

---

## 26. Alternative Services

For:

```text
AMBIGUOUS
```

the result may expose multiple candidate Services.

Conceptually:

```text
alternative_services:

- service_a
- service_b
```

The order must not automatically imply probabilistic ranking unless ranking semantics are explicitly defined.

Draft v0.1 does not introduce numerical probabilities.

---

## 27. No Arbitrary Confidence

The Entity Resolver should not initially generate scores such as:

```text
Spotify = 0.91
```

without a defined and calibrated meaning.

The preferred initial model is:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

plus:

```text
method
reason codes
provenance
```

This prevents false precision.

---

## 28. Resolution Method

The result should identify how resolution occurred.

Potential conceptual methods include:

```text
DIRECT_MAPPING
DOMAIN_NORMALIZATION
ALIAS_MAPPING
LOCAL_REGISTRY
USER_CORRECTION
AI
COMPOSITE
```

The final taxonomy remains open.

Most straightforward technical mappings should remain deterministic.

---

## 29. Reason Codes

Entity Resolution should preserve structured reasons for its result.

Potential reason codes may include:

```text
EXACT_IDENTIFIER_MATCH

NORMALIZED_DOMAIN_MATCH

KNOWN_ALIAS

MULTIPLE_MATCHES

NO_MATCH

SHARED_INFRASTRUCTURE

INSUFFICIENT_INFORMATION

HISTORICAL_IDENTIFIER

USER_CONFIRMED

CONFLICTING_IDENTIFIERS
```

These are illustrative.

The final vocabulary should evolve through implementation and real data.

---

## 30. Explainability

The framework should be able to explain:

> Why did you associate this identifier with this Service?

For example:

```text
The identifier accounts.spotify.com was associated with Spotify because:

- the hostname was normalized using domain-aware rules;
- the normalized domain was spotify.com;
- spotify.com is mapped to the canonical Service Spotify.
```

Or:

```text
The identifier could not be resolved because no known Service mapping
corresponded to the normalized identifier.
```

Resolution must therefore remain explainable.

---

## 31. Cross-Source Resolution

One of the primary responsibilities of Entity Resolution is to allow identifiers from independent Connected Sources to converge on one canonical Service.

Conceptually:

```text
Personal Gmail
      |
      v
no-reply@spotify.com
      |
      v
spotify.com
      |
      +-----------------------+
                              |
                              v
                           Spotify
                              ^
                              |
      +-----------------------+
      |
accounts.spotify.com
      ^
      |
Primary Password Manager
```

The framework should not create:

```text
SpotifyFromGmail
```

and:

```text
SpotifyFromPasswordManager
```

when both identifiers represent the same canonical Service.

---

## 32. Cross-Provider Resolution

The same principle applies when observations come from multiple providers of the same SourceType.

Example:

```text
Gmail Observation
      |
      v
spotify.com
      |
      +--------------+
                     |
                     v
                  Spotify
                     ^
                     |
      +--------------+
      |
spotify.com
      ^
      |
Outlook Observation
```

Provider identity must not cause canonical Service duplication.

---

## 33. Same Identifier, Different Sources

Observing the same identifier from multiple Connected Sources may strengthen downstream Relationship context.

However, Entity Resolution itself should not necessarily produce a different Service only because the identifier was observed repeatedly.

Conceptually:

```text
spotify.com
from Gmail

spotify.com
from Outlook

spotify.com
from Password Manager
        |
        v
same canonical Service
```

Source diversity belongs primarily to Evidence Aggregation and Relationship Assessment.

---

## 34. Shared Infrastructure

An identifier may belong to an infrastructure provider rather than the Service with which the User has a meaningful Relationship.

Examples may include:

```text
transactional email providers
cloud providers
identity platforms
payment processors
customer-support systems
marketing platforms
CDNs
```

The Entity Resolver must not naïvely resolve every observed infrastructure domain as the relevant Service.

For example:

```text
mail-delivery-provider.example
```

may technically own the sending infrastructure but not represent the business relationship being discovered.

Possible outcomes include:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

until additional context identifies the actual Service.

---

## 35. Infrastructure Can Also Be a Service

An infrastructure provider may itself legitimately be a Service used by the User.

For example, context may sometimes indicate a direct Relationship with:

```text
cloud provider
payment Service
identity provider
```

Therefore the rule cannot simply be:

```text
Infrastructure Provider
       ->
Never a Service
```

Resolution must remain contextual.

---

## 36. Service vs Organization

Entity Resolution in this contract targets:

```text
Service
```

not necessarily:

```text
Organization
```

For example:

```text
Service A
Service B
       |
       v
Organization X
```

may represent different Services operated by one Organization.

The resolver must not automatically collapse all Services belonging to the same corporate parent.

Therefore:

```text
SAME ORGANIZATION
      !=
SAME SERVICE
```

Organization resolution may become a separate future capability.

---

## 37. Service vs Brand

Brands may also differ from canonical Services.

Conceptually:

```text
Organization
    |
    v
Brand
    |
    v
Service
```

or other structures may eventually be necessary.

Draft v0.1 does not define this model.

The Entity Resolver should avoid introducing implicit Organization or Brand semantics that the Domain Model has not yet formalized.

---

## 38. Rebranding

Services may change identifiers or names over time.

For example:

```text
Historical Identifier
        |
        v
Old Service Name
        |
        v
Rebranding
        |
        v
Current Service Name
```

A historical identifier may still resolve to a current canonical Service if the mapping is known and justified.

However, historical provenance must remain preserved.

The framework should be able to distinguish:

```text
Observed historical identifier
```

from:

```text
Current canonical Service
```

---

## 39. Acquisition

A Service may be acquired by another Organization.

Acquisition does not necessarily imply:

```text
old Service
    =
new owner's other Services
```

Entity Resolution therefore must not automatically merge Services merely because corporate ownership changes.

Service identity and Organization ownership remain separate concepts.

---

## 40. Service Split

A Service may also split into multiple products or Services over time.

Historical identifiers may therefore be ambiguous.

Possible outcome:

```text
AMBIGUOUS
```

may be preferable to rewriting historical evidence into a currently convenient structure.

---

## 41. Multiple Domains

A single Service may legitimately use multiple domains.

Example:

```text
domain-a.example
domain-b.example
login.example.net
      |
      v
Same Service
```

Entity Resolution must support many identifiers resolving to one Service.

---

## 42. One Domain, Multiple Services

The reverse may also occur.

A single organizational domain may host multiple distinct Services.

Conceptually:

```text
example.com/service-a
example.com/service-b
```

Therefore:

```text
DOMAIN
   !=
UNIVERSAL UNIQUE SERVICE KEY
```

Future identifier types may need to preserve more context than registrable domain alone.

---

## 43. URLs

URLs may contain more Service-identifying information than hostnames.

For example:

```text
platform.example.com/product-a
```

and:

```text
platform.example.com/product-b
```

may represent different Services.

The resolver must therefore not always discard URL path semantics before determining whether they matter.

Normalization strategy may depend on identifier type and known resolution rules.

---

## 44. Email Addresses

Email addresses may provide useful identifiers.

For example:

```text
billing@spotify.com
```

may contribute:

```text
EMAIL_DOMAIN:
spotify.com
```

The local part:

```text
billing
```

may also sometimes contain useful context.

However, Entity Resolution should not assume that local parts have universal semantics.

Domain-based and address-based resolution should remain distinguishable.

---

## 45. Display Names

An Observation may contain:

```text
display_name:
Spotify
```

Display names may help resolution but are weaker identifiers than stable technical identifiers because they may be:

- spoofed;
- generic;
- localized;
- renamed;
- non-unique.

The resolver may therefore use display names as supporting context without automatically treating them as canonical identifiers.

---

## 46. Provider-Specific Identifiers

Some sources may provide strong provider-specific identifiers.

Examples may eventually include:

```text
OAuth client ID
application ID
package identifier
merchant identifier
password-manager application reference
```

These may be useful for resolution.

The common resolver contract should therefore support extensible identifier types.

---

## 47. User Corrections

User corrections may provide authoritative local guidance for future resolution.

Example:

```text
Framework:
example.net -> Service A

User:
This actually belongs to Service B.
```

A correction should not rewrite the historical Observation.

Instead:

```text
Original Identifier
       |
       v
Automated Resolution
       |
       v
User Correction
       |
       v
Current Resolution
```

The correction itself requires provenance.

---

## 48. User Correction Priority

If User corrections are supported, the architecture must define their precedence.

A plausible future policy is:

```text
Explicit User Correction
        >
Automated Resolution
```

for the local User's Service Graph.

However, Draft v0.1 does not formalize precedence rules.

This remains a domain-policy decision.

---

## 49. Manual Service Creation

If the resolver cannot identify a Service, the User may eventually be allowed to create or confirm one manually.

For example:

```text
Identifier:
oldwebsite.example

Resolver:
UNRESOLVED

User:
"This was Old Website."
```

This may produce a new canonical Service or mapping.

The exact workflow remains outside this contract.

---

## 50. AI-Assisted Resolution

AI may eventually assist with semantically ambiguous Entity Resolution.

Example:

```text
display name:
My Music Service

domain:
UNKNOWN

other non-secret metadata:
...
```

AI may provide useful interpretation where deterministic data is insufficient.

However:

```text
AI != default resolver
```

and:

```text
AI output != automatically trusted canonical Service
```

AI-assisted resolution must preserve method provenance.

---

## 51. AI Input Minimization

If AI assists resolution, it should receive only the minimum information necessary.

For example, there is generally no reason to provide:

```text
entire email body
password
full browsing history
```

to resolve:

```text
accounts.spotify.com
```

AI must respect the authorization and privacy boundary of existing Observations.

---

## 52. AI Unavailable

Entity Resolution must continue functioning when AI is:

- disabled;
- unavailable;
- unsupported;
- rejected by the User;
- incompatible with privacy requirements.

The correct fallback may be:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

rather than global failure.

---

## 53. External Reference Data

Resolution may eventually use external reference datasets.

Examples might include:

```text
domain registries
curated Service catalogs
public corporate mappings
application registries
```

External references introduce concerns around:

- availability;
- privacy;
- licensing;
- freshness;
- trust;
- versioning.

The resolver contract must not require an external remote lookup for routine operation.

---

## 54. Local-First Resolution

Basic Entity Resolution should operate locally where practical.

Potential local resources include:

```text
normalization rules
local Service registry
known aliases
user corrections
cached reference data
```

This supports:

- privacy;
- availability;
- reproducibility;
- performance;
- offline operation.

Remote enrichment may remain optional.

---

## 55. Resolution Context

The resolver may require an explicit context.

Conceptually:

```text
ResolutionContext

- known_services
- local_aliases
- user_corrections
- resolution_rules
- reference_data
- policy
```

The context must not contain provider credentials.

It should contain only information necessary for resolution.

---

## 56. Identity Information

Entity Resolution identifies Services.

It should not require User identity information unless that information is genuinely necessary to disambiguate Service identity.

For example:

```text
personal@gmail.com
```

should not generally influence whether:

```text
spotify.com
```

represents Spotify.

This separation reduces unnecessary personal-data exposure.

---

## 57. Resolution Stability

Identical:

```text
identifiers
+
resolution context
+
resolver version
```

should ideally produce the same result.

This supports reproducibility.

Conceptually:

```text
resolve(X, Context v1, Resolver v1)
        |
        v
same result
```

across repeated executions unless underlying referenced data changes.

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

---

## 59. Resolver Version

Each ResolutionResult should identify the resolver version where practical.

Example:

```text
resolver_version:
1
```

This enables later reprocessing.

For example:

```text
Resolver v1:
UNRESOLVED

Resolver v2:
RESOLVED -> Spotify
```

The original Observation and identifier remain unchanged.

---

## 60. Re-Resolution

Preserved Candidate Identifiers should support later re-resolution.

Conceptually:

```text
CandidateIdentifier
       |
       +--> Resolver v1
       |        |
       |        v
       |    UNRESOLVED
       |
       +--> Resolver v2
                |
                v
             RESOLVED
                |
                v
             Service
```

A previously unresolved identifier should not require retrieving the external source again if sufficient minimized provenance was preserved.

---

## 61. Changed Resolution

A new resolver version may produce a different result.

Example:

```text
Resolver v1:
example.com -> Service A

Resolver v2:
example.com -> Service B
```

The framework must not silently overwrite historical provenance.

It should be possible to determine:

```text
what changed
which resolver produced each result
which result is current
```

The exact versioning model remains undefined.

---

## 62. Service Merge

Two canonical Services may later be discovered to represent the same actual Service.

Conceptually:

```text
Service A
Service B
    |
    v
Merge Decision
    |
    v
Service C
```

Entity Resolution must support future Service consolidation without rewriting original Observations.

The exact Service merge lifecycle belongs to future domain design.

---

## 63. Service Split

The reverse may occur.

A previously unified Service may need to be split when evidence indicates that identifiers actually represent different Services.

Again, original Observations and Resolution provenance must allow reassessment.

---

## 64. Resolution Result Persistence

Resolution results may need to be persisted for:

- explainability;
- performance;
- auditing;
- reprocessing comparison;
- user correction;
- Service merge/split handling.

However, the contract does not require one persistence strategy.

A lightweight implementation may initially recompute deterministic resolution where inexpensive.

---

## 65. Invalid Identifier

Malformed identifiers must not automatically become:

```text
UNRESOLVED
```

if the actual problem is invalid input.

For example:

```text
URL:
http://[invalid
```

may represent a processing or normalization error.

Therefore:

```text
INVALID INPUT
       !=
UNRESOLVED
```

Processing state and domain state remain separate.

---

## 66. Unsupported Identifier Type

The resolver may receive an identifier type it does not support.

Example:

```text
type:
FUTURE_APPLICATION_IDENTIFIER
```

This should produce a processing outcome such as:

```text
UNSUPPORTED
```

rather than:

```text
UNRESOLVED
```

because the resolver has not actually evaluated the identifier semantically.

---

## 67. Resolver Failure

Technical failures may include:

```text
internal error
corrupt Service registry
reference-data failure
external enrichment failure
unexpected input
```

These should remain separate from:

```text
UNRESOLVED
```

or:

```text
AMBIGUOUS
```

A conceptual result therefore requires both:

```text
processing_status
```

and:

```text
resolution_status
```

---

## 68. Batch Resolution

An implementation may resolve multiple requests in batches.

Conceptually:

```text
resolve_many(requests)
```

may improve performance.

However, each ResolutionRequest must retain its independently traceable ResolutionResult.

Batch execution must not destroy provenance.

---

## 69. Canonical Service Creation

The resolver contract does not assume that every successfully interpreted identifier already has a canonical Service in storage.

A case may arise where:

```text
identifier clearly represents a Service
```

but:

```text
no canonical Service entity exists yet
```

This creates an important separation between:

```text
resolution
```

and potentially:

```text
Service creation / registration
```

Draft v0.1 does not yet define which component creates new canonical Services.

---

## 70. Existing vs New Services

A future ResolutionResult may need to distinguish:

```text
MATCHED_EXISTING_SERVICE
```

from:

```text
NEW_SERVICE_CANDIDATE
```

However, introducing this distinction now may prematurely mix Entity Resolution with Service registry lifecycle.

Draft v0.1 therefore leaves Service creation as an open question.

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

The resolver should not need the complete Observation when Candidate Identifiers and permitted context are sufficient.

This supports data minimization.

---

## 72. Minimum Necessary Input

Entity Resolution should consume the minimum information required.

For example:

```text
accounts.spotify.com
```

may be sufficient.

The resolver should not automatically receive:

```text
email subject
message body
password-manager username
User email addresses
```

unless they materially contribute to resolving Service identity.

This creates another privacy boundary.

---

## 73. Context Escalation

If basic identifiers are insufficient, additional already-authorized Observation information may sometimes help.

However, the resolver must not directly request new provider permissions.

Conceptually:

```text
Resolver
   |
   X
OAuth permission escalation
```

The resolver operates inside the information boundary already provided by the Discovery pipeline.

If additional source information is required, a higher-level capability may determine whether Progressive Permission is justified.

---

## 74. Language-Independent Contract

The initial conceptual interface is:

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

## 75. Resolution Request Contract

Conceptually:

```text
ResolutionRequest {

    ObservationId observationId

    List<CandidateIdentifier> candidateIdentifiers

    ResolutionContext context
}
```

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

---

## 77. Entity Resolver Invariants

### ER-INV-001

The resolver must operate on framework Candidate Identifiers rather than raw provider objects.

---

### ER-INV-002

The original Candidate Identifiers must remain traceable after normalization.

---

### ER-INV-003

Normalization must not be treated as equivalent to canonical Service Resolution.

---

### ER-INV-004

`RESOLVED` must reference one canonical Service.

---

### ER-INV-005

`UNRESOLVED` must not result in a fabricated Service.

---

### ER-INV-006

`AMBIGUOUS` must remain a valid result when multiple plausible Services exist.

---

### ER-INV-007

Technical processing failure must remain distinct from domain `UNRESOLVED`.

---

### ER-INV-008

Unsupported identifier types must remain distinguishable from `UNRESOLVED`.

---

### ER-INV-009

Entity Resolution must remain distinct from Evidence Classification.

---

### ER-INV-010

Entity Resolution must remain distinct from Relationship Assessment.

---

### ER-INV-011

A resolved Service must not imply a confirmed User Relationship.

---

### ER-INV-012

Provider identity must not create provider-specific copies of canonical Services.

---

### ER-INV-013

Identifiers from multiple Connected Sources may resolve to the same Service.

---

### ER-INV-014

Multiple identifiers may resolve to one canonical Service.

---

### ER-INV-015

A single technical domain must not be assumed to uniquely identify one Service in all contexts.

---

### ER-INV-016

Service identity and Organization identity must remain distinct.

---

### ER-INV-017

Resolution must preserve enough provenance to support explanation and reprocessing.

---

### ER-INV-018

The resolver must not require provider credentials.

---

### ER-INV-019

The resolver must not silently request additional provider permissions.

---

### ER-INV-020

Deterministic resolution should be preferred when sufficient.

---

### ER-INV-021

AI availability must not be required for basic resolution.

---

### ER-INV-022

No arbitrary numerical Confidence score is required in Draft v0.1.

---

### ER-INV-023

User corrections must not require destructive rewriting of source Observations.

---

### ER-INV-024

Re-resolution must not require source retrieval when preserved identifiers are sufficient.

---

### ER-INV-025

Service merges or splits must not destroy original identifier provenance.

---

## 78. Gmail Resolution Example

Input:

```text
Observation:
observation_001

Candidate Identifier:
EMAIL_DOMAIN = spotify.com
```

Resolution:

```text
spotify.com
    |
    v
Exact / known domain mapping
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
DIRECT_MAPPING

reason_codes:
- EXACT_IDENTIFIER_MATCH
```

This result says nothing yet about the meaning of the email.

---

## 79. Password Manager Resolution Example

Input:

```text
Observation:
observation_002

Candidate Identifier:
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
Service registry
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

The Gmail and Password Manager Observations now converge on the same canonical Service.

---

## 80. Unresolved Example

Input:

```text
Candidate Identifier:
DOMAIN = old-unknown-service.example
```

Result:

```text
processing_status:
SUCCESS

resolution_status:
UNRESOLVED

resolved_service:
NONE

reason_codes:
- NO_MATCH
```

The identifier remains available for future re-resolution.

---

## 81. Ambiguous Example

Input:

```text
Candidate Identifiers:

DISPLAY_NAME = Example
DOMAIN = shared-platform.example
```

Resolution finds:

```text
Service A
Service B
```

but cannot safely choose one.

Result:

```text
processing_status:
SUCCESS

resolution_status:
AMBIGUOUS

alternative_services:
- service_a
- service_b

reason_codes:
- MULTIPLE_MATCHES
```

No arbitrary Service is selected.

---

## 82. Shared Infrastructure Example

Input:

```text
Candidate Identifier:
EMAIL_DOMAIN = mail-platform.example
```

Additional context indicates that the domain is shared by many unrelated Services.

Possible result:

```text
processing_status:
SUCCESS

resolution_status:
UNRESOLVED

reason_codes:
- SHARED_INFRASTRUCTURE
```

This prevents infrastructure from automatically becoming the discovered Service.

---

## 83. Historical Identifier Example

Input:

```text
DOMAIN:
oldbrand.example
```

Local registry contains:

```text
oldbrand.example
      |
      v
historical identifier
      |
      v
Current Service:
Service X
```

Result:

```text
processing_status:
SUCCESS

resolution_status:
RESOLVED

resolved_service:
service_x

reason_codes:
- HISTORICAL_IDENTIFIER
```

The original identifier remains preserved.

---

## 84. User-Corrected Example

Historical automated result:

```text
example.net
    ->
Service A
```

User correction:

```text
example.net
    ->
Service B
```

A later resolution may use:

```text
method:
USER_CORRECTION
```

while retaining the original automated result for provenance.

---

## 85. Multi-Source Example

```text
Personal Gmail
      |
      v
EMAIL_DOMAIN
spotify.com
      |
      +-------------------+
                          |
                          v
                       Spotify
                          ^
                          |
      +-------------------+
      |
HOSTNAME
accounts.spotify.com
      ^
      |
Primary Password Manager
```

Both paths produce:

```text
ServiceReference:
service_spotify
```

while retaining separate Observation and ConnectedSource provenance.

---

## 86. Open Questions

### Candidate Identifiers

- Is the current CandidateIdentifier representation sufficient?
- Which identifier types are necessary initially?
- Should URLs remain full URLs or be decomposed before resolution?
- Should display names be Candidate Identifiers or contextual attributes?

### Normalization

- Which normalization belongs to Candidate Detection?
- Which belongs to Entity Resolution?
- Should normalization be represented as its own versioned component?
- How should internationalized domains be handled?
- How should public suffix data be versioned?

### Service Registry

- Do we need a local Service Registry?
- What creates its initial records?
- How are entries updated?
- Can Users add Services?
- Can Connectors contribute mappings?
- How are incorrect mappings corrected?

### Service Creation

- Who creates a new canonical Service when no existing Service matches?
- Entity Resolver?
- Separate Service Registry component?
- User confirmation?
- Another workflow?

### Multiple Services

- Can one ResolutionRequest legitimately resolve to multiple Services?
- Or must that always be represented as `AMBIGUOUS`?
- How should platform/container Services be represented?

### Product vs Service

- Is a product always a Service?
- Should `accounts.google.com` resolve to Google, Google Account, or another Service?
- At what granularity should canonical Services exist?

### Organization

- When should Services be linked to Organizations?
- Should Organization Resolution become a separate contract?
- How will Legal Data Controllers relate to canonical Services?

### Cross-Source Context

- Should the Resolver use previously observed source diversity?
- Or should source diversity remain entirely downstream in Relationship Assessment?

### User Corrections

- How are corrections stored?
- Are they global or local to one User?
- Which corrections can override curated mappings?
- How are accidental corrections reversed?

### AI

- Which unresolved cases actually justify AI-assisted resolution?
- Should AI propose candidates rather than directly resolve?
- Should User confirmation be required for some AI-generated mappings?

### External Datasets

- Which external datasets are suitable?
- What licensing restrictions apply?
- How are stale mappings detected?
- How can resolution remain functional offline?

### Persistence

- Should ResolutionResult be persisted?
- Should only mappings be persisted?
- Should every resolver version retain historical results?
- How are superseded results represented?

### Service Merge and Split

- Which component performs merges?
- How are affected Relationships recalculated?
- How are user corrections preserved?
- How are historical identifiers reassigned safely?

### Confidence

- Do we ever need numerical Entity Resolution Confidence?
- Would explicit statuses and reasons remain sufficient?
- If Confidence is added, how will it be calibrated?

---

## 87. Findings from Contract Design

### Finding 1 - ServiceIdentifier Is Strongly Validated

The Entity Resolver Contract confirms that `ServiceIdentifier` is not merely a conceptual convenience.

The framework requires an explicit representation between:

```text
Observation
```

and:

```text
Service
```

Therefore the Domain Model decision to represent ServiceIdentifier is reinforced.

---

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

---

### Finding 3 - UNRESOLVED and AMBIGUOUS Are Necessary

A simple:

```text
Service or null
```

response would lose important semantics.

The resolver needs:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

as distinct outcomes.

---

### Finding 4 - Resolution Must Be Cross-Source

Entity Resolution belongs to the common Discovery Core rather than individual Connectors.

Otherwise:

```text
Gmail
```

and:

```text
Password Manager
```

could independently create duplicate representations of the same Service.

---

### Finding 5 - Service Registry Lifecycle Is Not Yet Defined

The Resolver can match Candidate Identifiers to existing canonical Services.

However, the project has not yet determined:

> Who creates a canonical Service when no existing Service is available?

This must remain an explicit open question rather than being hidden inside the Resolver.

---

### Finding 6 - Service Granularity Requires Validation

Questions such as:

```text
Google
vs
Google Account
vs
Gmail
```

demonstrate that canonical Service identity requires a defined granularity model.

The Entity Resolver Contract should not decide that question implicitly.

---

### Finding 7 - Resolution Provenance Is Required

Because mappings can change through:

```text
new rules
new registry data
rebranding
user correction
Service merge
Service split
```

resolution must remain traceable and reprocessable.

---

## 88. Decision Candidates

### Candidate Decision - Explicit Resolution States

```text
Entity Resolution must explicitly distinguish RESOLVED, UNRESOLVED and
AMBIGUOUS outcomes.

A failure to identify one canonical Service must not cause fabricated
resolution.
```

---

### Candidate Decision - Normalization Is Not Resolution

```text
Technical identifier normalization and canonical Service Resolution are
distinct operations and their provenance should remain distinguishable.
```

---

### Candidate Decision - Resolution Is Cross-Source

```text
Canonical Service Resolution should operate in the common Discovery Core
rather than being implemented independently inside source Connectors.

Equivalent identifiers from different Connected Sources should be able to
resolve to the same canonical Service.
```

---

### Candidate Decision - Provider Independence

```text
Provider identity must not cause duplicate canonical Services.

Service identity should remain independent from which Connected Source
produced the supporting identifier.
```

---

### Candidate Decision - No Arbitrary Resolution Confidence

```text
Draft v0.1 should use explicit resolution states, methods and reason codes
rather than uncalibrated numerical Entity Resolution Confidence values.
```

---

### Candidate Decision - Re-Resolution Supported

```text
Preserved Service Identifiers should support later re-resolution without
requiring source retrieval when existing minimized information is sufficient.
```

---

## 89. Current Contract Baseline

The initial Entity Resolver contract is:

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
original identifiers preserved
normalization traceable
provider-independent resolution
cross-source Service convergence
explicit unresolved state
explicit ambiguous state
no fabricated Service
no Relationship conclusion
no Evidence conclusion
no arbitrary numerical Confidence
deterministic-first operation
optional AI assistance
re-resolution support
user-correction compatibility
```

---

## 90. Next Interface Contract

The Discovery pipeline now has contracts for:

```text
Connector
      |
      v
Observation
      |
      v
ServiceCandidateDetector
      |
      v
EntityResolver
```

The next interface contract should define:

```text
EvidenceClassifier
```

Its responsibility is:

> Given an Observation, determine what semantic Evidence, if any, that Observation provides about the User-Service Relationship.

The next contract should establish:

```text
Observation
      |
      v
EvidenceClassifier
      |
  +---+-----------+
  |               |
  v               v
Evidence        UNKNOWN
```

and formalize:

- Evidence Types;
- deterministic classification;
- AI-assisted classification;
- classification provenance;
- multiple Evidence items from one Observation;
- UNKNOWN;
- unsupported Observation Types;
- classification failures;
- reclassification;
- source-specific versus common Evidence taxonomy.

The Entity Resolver should remain independent from those semantic classification concerns.
