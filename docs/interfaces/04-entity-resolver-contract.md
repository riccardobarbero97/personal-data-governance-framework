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

## IMPORTANT ALIGNMENT RULE

All sections of the original Draft v0.1 Entity Resolver Contract remain unchanged except for the explicit replacements and additions below.

The resulting contract retains the complete original 90-section structure, examples, edge cases, invariants, findings and open questions.

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

The Entity Resolver Contract must support both the transient processing representation and the Domain representation without conflating either with the canonical Service itself.

Therefore:

```text
CandidateIdentifier
        !=
ServiceIdentifier
        !=
Service
```

in terms of software role, even when CandidateIdentifier and ServiceIdentifier contain the same technical value.

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

Conceptually:

```text
EntityResolver
      |
      v
ResolutionResult
[Processing Result]
      |
      +-- resolved Service reference
      |
      +-- normalization provenance
      |
      +-- resolution provenance
```

while:

```text
Service
```

remains the canonical Core Domain Entity.

Therefore:

```text
ResolutionResult != Service
```

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

Explicit resolution states are preferred over uncalibrated numerical pseudo-precision.

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

User confirmation may participate in that workflow.

The exact Service creation process remains outside this contract.

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

Materially relevant Registry and reference-data versions should therefore remain traceable where practical.

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

The persistence decision should be driven by provenance, performance and reprocessing requirements.

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

This creates an important separation between:

```text
resolution
```

and:

```text
Service creation / registration
```

The consolidated Domain Model intentionally leaves Service creation outside the Entity Resolver.

The Entity Resolver answers:

> Does this identifier resolve to an existing canonical Service?

The application layer must separately determine:

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

The Implementation Model must define this application workflow before unresolved-but-valid Service candidates can result in canonical Service creation.

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

However, this distinction should not be introduced directly into `ResolutionStatus`.

The canonical Entity Resolution states remain:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

A potential `NEW_SERVICE_CANDIDATE` is an application-level interpretation of an unresolved but apparently legitimate Service candidate.

This prevents Entity Resolution from becoming coupled to Service Registry lifecycle.

Draft v0.1 therefore keeps Service creation outside the core Resolver status model.

---

## 71. Resolution Request

The conceptual request remains:

```text
ResolutionRequest

- observation_id
- candidate_identifiers
- context
```

The `observation_id` preserves traceability.

The Resolver should not need the complete Observation when CandidateIdentifiers and permitted context are sufficient.

This supports data minimization.

The CandidateIdentifiers contained in the request may correspond to transient processing representations of Domain ServiceIdentifiers.

The Implementation Model must determine whether:

```text
CandidateIdentifier
        |
        v
ServiceIdentifier
```

materialization occurs:

- before calling the Resolver;
- inside an application orchestration layer;
- after successful normalization;
- when persistence becomes necessary.

The Entity Resolver Contract does not depend on one specific persistence choice.

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

`resolvedService` contains a reference to the canonical Domain `Service`.

It must not contain an independently authoritative duplicate representation of that Service.

---

## 77. Entity Resolver Invariants

The existing invariants `ER-INV-001` through `ER-INV-010` remain unchanged.

### ER-INV-011

A resolved Service must not imply an `ESTABLISHED` User-Service Relationship.

The existing invariants `ER-INV-012` through `ER-INV-021` remain unchanged.

### ER-INV-022

Numerical Entity Resolution Confidence is outside the initial Discovery model.

The existing invariants `ER-INV-023` through `ER-INV-025` remain unchanged.

### ER-INV-026

`ResolutionResult` must remain distinguishable from the canonical `Service` it references.

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

The Gmail and Password Manager Observations now converge on the same canonical Service.

---

## 86. Open Questions

All original Open Questions remain valid except where a decision has already been consolidated by Architecture v0.3 or Domain Model v0.3.

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

Service creation is now explicitly outside EntityResolver responsibility.

The remaining questions are:

- Which application component decides whether a new canonical Service should be created?
- Which Evidence is sufficient to propose a new Service?
- Is User confirmation required?
- Can deterministic reference data create a Service automatically?
- Can AI only propose a Service candidate, or may it participate in creation?
- How is the new Service registered in ServiceRegistry?
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
- Should every Resolver version retain historical results?
- How are superseded Results represented?

### Service Merge and Split

- Which component performs merges?
- How are affected Relationships recalculated?
- How are User corrections preserved?
- How are historical identifiers reassigned safely?

### Confidence

Numerical Entity Resolution Confidence is outside the initial Discovery baseline.

The remaining question is whether later empirical validation demonstrates a justified need for it.

If Confidence is introduced in a future version:

- what exactly will it measure?
- how will it be calibrated?
- what validation dataset will be used?
- how will Users interpret it?
- how will it differ from `RESOLVED / UNRESOLVED / AMBIGUOUS`?

---

## 87. Findings from Contract Design

### Finding 1 - ServiceIdentifier Is Strongly Validated

The Entity Resolver Contract confirms that ServiceIdentifier is not merely a conceptual convenience.

The framework requires an explicit representation between:

```text
Observation
```

and:

```text
Service
```

The consolidated Domain Model classifies `ServiceIdentifier` as a Domain Value Concept.

`CandidateIdentifier` remains the processing representation produced upstream.

This confirms:

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

response would lose important semantics.

The Resolver requires:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

as distinct outcomes.

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

### Finding 5 - Service Registry Boundary Is Required but Its Lifecycle Is Not Yet Defined

The Entity Resolver requires access to canonical Service and ServiceIdentifier information.

The consolidated Domain Model therefore recognizes:

```text
ServiceRegistry
```

as an:

```text
Application / Repository Boundary
```

However, the project has not yet determined:

- its concrete persistence model;
- how initial Services are created;
- who may add canonical Services;
- how mappings are governed;
- how Service merge and split operations work.

These responsibilities must remain explicit rather than being hidden inside EntityResolver.

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

The Entity Resolver Contract must not decide that question implicitly.

### Finding 7 - Resolution Provenance Is Required

Because mappings can change through:

```text
new rules
new Registry data
rebranding
User correction
Service merge
Service split
```

resolution must remain traceable and reprocessable.

### Finding 8 - ResolutionResult Is a Processing Result

The consolidated Domain Model classifies:

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

An unresolved but apparently legitimate Service candidate may require a later application-level workflow before a new canonical Service exists.

---

## 88. Architecture Alignment and Remaining Decision Candidates

### Architecture Alignment - Explicit Resolution States

Entity Resolution explicitly distinguishes:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

A failure to identify one canonical Service must not result in fabricated resolution.

This is part of the consolidated Architecture v0.3 baseline.

### Architecture Alignment - Normalization Is Not Resolution

Technical identifier normalization and canonical Service Resolution are distinct operations.

Their provenance must remain distinguishable.

This is one of the consolidated architectural boundaries:

```text
NORMALIZATION != RESOLUTION
```

### Architecture Alignment - Resolution Is Cross-Source

Canonical Service Resolution belongs to the common Discovery Core.

Equivalent identifiers from different Connected Sources may resolve to the same canonical Service.

Provider identity must not create source-specific Service copies.

### Architecture Alignment - Provider Independence

Service identity remains independent from which ConnectedSource or Provider produced the supporting identifier.

This is consistent with the consolidated Provider-independent Discovery Architecture.

### Architecture Alignment - No Numerical Resolution Confidence

Numerical Entity Resolution Confidence is outside the initial Discovery baseline.

The Resolver uses:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

plus structured provenance.

This is covered by:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

### Architecture Alignment - Re-Resolution Supported

Preserved ServiceIdentifiers should support later re-resolution without requiring source retrieval when existing minimized information is sufficient.

This follows the consolidated provenance and reprocessing architecture.

### Remaining Decision Candidate - Service Creation Workflow

The Entity Resolver does not create canonical Services directly.

The Implementation Model must define the separate workflow through which:

```text
unresolved legitimate Service candidate
        |
        v
new canonical Service
```

may occur.

### Remaining Decision Candidate - Service Granularity

The Resolver Contract intentionally does not determine whether abstractions such as:

```text
Google
Google Account
Gmail
```

should be modeled as one or multiple canonical Services.

That policy remains to be validated empirically.

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

no numerical Confidence in the initial baseline

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

The next semantic contract in the Discovery Architecture is:

```text
EvidenceClassifier
```

and has already been defined in:

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

The Entity Resolver Contract is now aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- ServiceIdentifier as a Domain Value Concept;
- ResolutionResult as a Processing Result / Value Object;
- ServiceRegistry as an Application / Repository Boundary;
- explicit `RESOLVED / UNRESOLVED / AMBIGUOUS` states;
- the separation between normalization and resolution;
- the separation between resolution and Service creation;
- the exclusion of numerical Confidence from the initial Discovery baseline;
- the parallel Entity Resolution / Evidence Classification architecture.

No additional Entity Resolution abstraction is required before the Implementation Model phase.
