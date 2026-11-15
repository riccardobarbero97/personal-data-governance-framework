# Evidence Aggregator Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md` - Draft v0.3  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md` - Draft v0.3  
**Related Interfaces:**
- `docs/interfaces/01-connector-contract.md`
- `docs/interfaces/02-observation-contract.md`
- `docs/interfaces/03-service-candidate-detector-contract.md`
- `docs/interfaces/04-entity-resolver-contract.md`
- `docs/interfaces/05-evidence-classifier-contract.md`

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `EvidenceAggregator` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Evidence Aggregator combines individual Evidence items into a structured representation suitable for Relationship Assessment.

Conceptually:

```text
ACTIVE Evidence A
ACTIVE Evidence B
ACTIVE Evidence C
        |
        v
Evidence Aggregator
        |
        v
Evidence Aggregate
[Derived View]
        |
        v
Relationship Assessor
```

Its purpose is not to determine whether a Relationship is:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

or whether its temporal state is:

```text
UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

Its responsibility is narrower:

> Given the currently accepted Evidence associated with a Service or unresolved discovery context, what structured body of Evidence is available for Relationship Assessment?

The Aggregator must preserve individual Evidence and its provenance while deriving useful information such as:

- EvidenceTypes;
- Evidence counts;
- source diversity;
- ConnectedSource diversity;
- temporal distribution;
- Identity references;
- conflicting Evidence;
- coverage context;
- duplicate handling;
- unresolved information.

The consolidated Domain Model classifies `EvidenceAggregate` as a Derived View rather than a Core Domain Entity.

---

## 2. Architectural Position

The Evidence Aggregator operates after individual Evidence has been classified and relevant ServiceIdentifiers have been resolved where possible.

Conceptually:

```text
                         Observation
                         /         \
                        /           \
                       v             v
             Entity Resolution   Evidence Classification
                       |             |
                       v             v
                    Service        Evidence
                       \             /
                        \           /
                         v         v
                    EVIDENCE AGGREGATOR
                            |
                            v
                     Evidence Aggregate
                      [Derived View]
                            |
                            v
                   Relationship Assessor
                            |
                            v
                       Relationship
```

The Aggregator brings together two different kinds of output:

```text
What Service is involved?
```

and:

```text
What currently accepted Evidence has been observed?
```

without deciding the final Relationship state.

---

## 3. Fundamental Boundary

The central architectural distinction is:

```text
EVIDENCE AGGREGATION
        !=
RELATIONSHIP ASSESSMENT
```

For example, the Aggregator may produce:

```text
Service:
Spotify

Evidence Summary:
ACCOUNT_VERIFICATION       1
SUBSCRIPTION               4
PAYMENT                   12
MARKETING                 30
PASSWORD_MANAGER_ENTRY     1

Source Types:
EMAIL
PASSWORD_MANAGER

First Observed:
2021-05-10

Last Observed:
2026-08-14
```

It must not itself conclude:

```text
RelationshipStatus:
ESTABLISHED

TemporalStatus:
CURRENTLY_OBSERVED
```

Those conclusions belong to `RelationshipAssessor`.

---

## 4. Why Aggregation Exists

Without aggregation, Relationship Assessment would need to reason directly over an unstructured collection of individual Evidence items.

For example:

```text
Evidence 1
Evidence 2
Evidence 3
Evidence 4
...
Evidence 150
```

The Aggregator creates a structured view:

```text
150 individual Evidence items
           |
           v
      aggregation
           |
           v
Service:
Spotify

EvidenceTypes:
ACCOUNT_VERIFICATION       1
PAYMENT                    15
SUBSCRIPTION                8
MARKETING                 125
PASSWORD_MANAGER_ENTRY      1

ConnectedSources:
2

SourceTypes:
2

Timeline:
2020 -> 2026
```

The authoritative Evidence remains available.

The Aggregate is a derived view over that Evidence.

---

## 5. Aggregation Does Not Replace Evidence

The Aggregator must not collapse individual Evidence into an irreversible summary.

Therefore:

```text
AGGREGATE
    !=
REPLACEMENT FOR EVIDENCE
```

The relationship:

```text
EvidenceAggregate
       |
       +-- Evidence A
       +-- Evidence B
       +-- Evidence C
```

must remain reconstructable.

This is required for:

- explainability;
- reassessment;
- debugging;
- reclassification;
- source deletion;
- source revocation;
- Entity re-resolution;
- User correction.

This is now a consolidated architectural decision:

```text
D-021 - Evidence Aggregates Are Derived State
```

---

## 6. Input Contract

The Aggregator should receive explicitly identified Evidence and relevant context.

Conceptually:

```text
aggregate(
    request
)
    ->
AggregationResult
```

The request may contain:

```text
AggregationRequest

- aggregation_scope
- service_reference
- unresolved_identifier_reference
- identity_references
- evidence_items
- context
```

The exact implementation remains open.

Evidence lifecycle must be respected before semantic summaries are calculated.

---

## 7. Service-Oriented Aggregation

The primary aggregation boundary is the canonical Service.

Conceptually:

```text
Service
   |
   +-- ACTIVE Evidence A
   +-- ACTIVE Evidence B
   +-- ACTIVE Evidence C
```

For example:

```text
Spotify
 |
 +-- Gmail ACCOUNT_VERIFICATION
 +-- Gmail SUBSCRIPTION
 +-- Gmail PAYMENT
 +-- Password Manager PASSWORD_MANAGER_ENTRY
```

This creates a coherent Service-level Evidence context.

---

## 8. Why Service Is the Primary Boundary

The final Discovery objective is to identify Relationships between the User and Services.

Therefore aggregation around:

```text
Service
```

is more useful than aggregation around:

```text
Provider
Connector
ObservationType
ConnectedSource
```

Those concepts remain provenance dimensions.

They should not define separate canonical Relationships merely because Evidence originated from different sources.

---

## 9. Identity-Aware Aggregation

Aggregation must also preserve relevant Identity information.

For example:

```text
Spotify
 |
 +-- ACCOUNT_VERIFICATION
 |      identity: personal@example.com
 |
 +-- PASSWORD_MANAGER_ENTRY
 |      identity: personal@example.com
 |
 +-- PASSWORD_MANAGER_ENTRY
        identity: oldmail@example.net
```

The Aggregator must not automatically merge:

```text
personal@example.com
```

and:

```text
oldmail@example.net
```

into one Identity.

The Aggregate should retain Identity references associated with its Evidence.

---

## 10. User-Level vs Identity-Level Aggregation

The consolidated Domain Model now defines the primary Relationship as:

```text
User -> Relationship -> Service
```

Relevant Identity Seeds remain associated with the Relationship and its Evidence basis.

Therefore Service-level aggregation is primarily intended to support the User-Service Relationship.

At the same time, Identity information must remain preserved so that the framework can answer questions such as:

> Which Services were associated with `oldmail@example.net`?

Conceptually:

```text
User-level Service Evidence
        +
Identity references
```

must coexist.

A separate:

```text
IdentityServiceAssociation
```

remains a Candidate Domain Concept.

The Aggregator must not create that concept implicitly.

---

## 11. Account Candidate Concept

Scenario 002 exposed the possible future concept:

```text
Account
```

For example:

```text
Spotify
 |
 +-- Account using personal@example.com
 |
 +-- Account using oldmail@example.net
```

The Aggregator must not invent Account entities merely because multiple Identity references exist.

Until Account is formally introduced:

```text
Identity-specific Evidence
        !=
Confirmed separate Accounts
```

The Aggregate should preserve the distinction without making the inference.

---

## 12. Resolved-Service Evidence

The normal aggregation case is:

```text
ACTIVE Evidence
    +
Resolved Service
    |
    v
Service-Level Aggregate
```

Example:

```text
Evidence:
ACCOUNT_VERIFICATION

EvidenceStatus:
ACTIVE

Service:
Spotify
```

can contribute to:

```text
Spotify EvidenceAggregate
```

---

## 13. Unresolved-Service Evidence

Evidence may exist while Entity Resolution remains:

```text
UNRESOLVED
```

For example:

```text
Evidence:
PAYMENT

Identifier:
unknown-service.example

Service:
UNRESOLVED
```

This Evidence must not disappear.

The Aggregator must support unresolved aggregation contexts.

Conceptually:

```text
Unresolved Service Context
        |
        +-- ServiceIdentifier
        |
        +-- ACTIVE Evidence
```

This allows later re-resolution.

---

## 14. Ambiguous-Service Evidence

Entity Resolution may also return:

```text
AMBIGUOUS
```

In that case, Evidence must not be arbitrarily assigned to one canonical Service.

Conceptually:

```text
Evidence
   |
   v
Ambiguous Service Context
   |
   +-- Candidate Service A
   |
   +-- Candidate Service B
```

The Evidence may remain outside canonical Service Aggregates until ambiguity is resolved.

---

## 15. No Evidence Loss During Resolution Failure

The following must never happen:

```text
Evidence
    |
Entity Resolver
    |
 UNRESOLVED
    |
    X
Evidence discarded
```

The correct behavior is:

```text
Evidence
    |
    v
Unresolved Aggregation Context
```

The framework should preserve useful semantic information even before canonical Service identity is known.

---

## 16. Aggregation Request

The initial conceptual request is:

```text
AggregationRequest

- aggregation_scope
- service_reference
- unresolved_identifier_reference
- identity_references
- evidence_items
- context
```

Not all fields apply simultaneously.

The exact structure remains implementation-dependent.

---

## 17. Aggregation Scope

The aggregation request should identify the logical scope.

Potential scopes include:

```text
SERVICE
UNRESOLVED_SERVICE_CANDIDATE
AMBIGUOUS_SERVICE_CANDIDATE
```

Additional scopes may emerge later.

For the current Discovery workflow:

```text
SERVICE
```

is the primary case.

---

## 18. Aggregation Result

The initial conceptual result is:

```text
AggregationResult

- processing_status
- aggregation_status
- aggregate
- aggregator_version
```

where:

```text
EvidenceAggregate
```

contains the semantic derived view.

The consolidated Domain Model distinguishes:

```text
AggregationResult
=
Processing Result
```

from:

```text
EvidenceAggregate
=
Derived View
```

The exact software representation remains open.

---

## 19. Processing Status

Technical processing state must remain separate from Domain aggregation state.

Potential processing states include:

```text
SUCCESS
UNSUPPORTED
FAILED
```

A processing failure must not silently produce an empty EvidenceAggregate.

---

## 20. Aggregation Status

Potential Domain states may include:

```text
AGGREGATED
EMPTY
PARTIAL
```

### AGGREGATED

One or more eligible Evidence items were successfully aggregated.

### EMPTY

The request contained no Evidence eligible under the active aggregation policy.

### PARTIAL

Some Evidence could be aggregated while other eligible Evidence could not be processed.

The final taxonomy remains open.

---

## 21. Empty Aggregate

An empty Aggregate must not be interpreted as:

```text
No Relationship exists.
```

It means only:

```text
No usable Evidence is currently present
under this aggregation scope and policy.
```

The absence of Evidence is not proof of absence of a Relationship.

---

## 22. Evidence References

Every Aggregate must preserve references to the Evidence items from which it was derived.

Conceptually:

```text
EvidenceAggregate
 |
 +-- evidence_001
 +-- evidence_002
 +-- evidence_003
```

Summary values must remain reproducible from underlying eligible Evidence where practical.

---

## 23. Evidence Summary

The Aggregate should provide counts grouped by EvidenceType.

Example:

```text
EvidenceSummary

ACCOUNT_VERIFICATION       1
PASSWORD_RESET             2
SECURITY_NOTIFICATION      3
SUBSCRIPTION               5
PAYMENT                   12
MARKETING                 40
PASSWORD_MANAGER_ENTRY     1
```

This is a summary.

It does not assign relative strength.

For the default current Discovery view, these counts should normally be derived from:

```text
ACTIVE Evidence
```

only.

---

## 24. Evidence Frequency Is Not Evidence Strength

The Aggregator must preserve the distinction:

```text
COUNT != STRENGTH
```

For example:

```text
100 MARKETING
```

must not automatically outweigh:

```text
1 ACCOUNT_VERIFICATION
```

The Aggregator reports frequency.

The RelationshipAssessor determines semantic importance.

---

## 25. No Implicit Weighting

The Aggregator must not calculate hidden formulas such as:

```text
ACCOUNT_VERIFICATION * 0.8
+
PAYMENT * 0.6
+
MARKETING * 0.1
```

unless such weighting is explicitly defined by a future Relationship Assessment model.

Draft v0.1 contains no Evidence weight model.

---

## 26. No Aggregate Confidence

Numerical Confidence is outside the initial Discovery model.

The Aggregator must not produce arbitrary outputs such as:

```text
aggregate_confidence:
0.93
```

The Aggregate is a structured representation of currently eligible Evidence.

The framework instead preserves:

- EvidenceTypes;
- counts;
- provenance;
- source diversity;
- temporal semantics;
- conflicts;
- coverage.

This aligns with:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

---

## 27. Source Summary

The Aggregate should preserve which ConnectedSources contributed Evidence.

Example:

```text
ConnectedSources:

Personal Gmail
Primary Password Manager
Work Outlook
```

Conceptually, the summary may include:

```text
connected_source_count
source_types
providers
evidence_count_by_connected_source
evidence_count_by_source_type
```

These values describe provenance diversity.

They do not independently determine Relationship strength.

---

## 28. SourceType Diversity

Example:

```text
EMAIL
PASSWORD_MANAGER
```

represents two structurally different source categories.

The Aggregator may expose:

```text
source_types:
- EMAIL
- PASSWORD_MANAGER
```

This may later help Relationship Assessment distinguish:

```text
many emails from one mailbox
```

from:

```text
independent Evidence from email and password manager
```

---

## 29. ConnectedSource Diversity

Evidence from:

```text
Personal Gmail
Old Gmail
```

represents two ConnectedSources.

However, both may belong to:

```text
SourceType:
EMAIL
```

Therefore the Aggregate should distinguish:

```text
ConnectedSource diversity
```

from:

```text
SourceType diversity
```

---

## 30. Provider Diversity

Evidence may also originate from different Providers.

Example:

```text
Google / Gmail
Microsoft / Outlook
Provider A / Password Manager
```

Provider diversity may be useful provenance.

However:

```text
Provider diversity
       !=
Independent semantic proof
```

Relationship Assessment may later decide whether this matters.

---

## 31. Source Independence

The Aggregator must not create different aggregate schemas for:

```text
Gmail Evidence
Outlook Evidence
Password Manager Evidence
Browser Evidence
```

The intended architecture is:

```text
Evidence from Gmail --------+
                            |
Evidence from Outlook ------+
                            |
Evidence from Password -----+--> EvidenceAggregator
Manager                     |           |
                            |           v
Evidence from Browser ------+    Common EvidenceAggregate
```

Provider-specific details remain in Evidence and Observation provenance.

---

## 32. Temporal Summary

The Aggregate should preserve temporal information derived from Evidence and supporting Observations.

Potential summary information includes:

```text
first_observed
last_observed
evidence_type_first_observed
evidence_type_last_observed
timeline
typed_temporal_values
```

The exact structure remains open.

---

## 33. Temporal Semantics Must Be Preserved

Temporal aggregation must not erase source semantics.

For example:

```text
Email Message Time:
2025-01-01
```

and:

```text
Password Manager Record Modified:
2025-01-01
```

cannot automatically be interpreted as equivalent Service activity events.

The Aggregate may preserve both timestamps but must retain their temporal semantics.

---

## 34. First Observed

`first_observed` should mean:

> Earliest relevant temporal value available under explicitly defined aggregation semantics.

This definition must be used carefully.

It must not silently become:

```text
Account creation date
```

because the earliest observed Evidence may simply represent:

```text
oldest Evidence currently available
```

---

## 35. Last Observed

Similarly:

```text
last_observed
```

must not automatically mean:

```text
last Service usage
```

It means only the latest relevant Observation under the aggregation semantics.

For example:

```text
Password Manager Record Modified
```

may not represent actual Service use.

---

## 36. Evidence Timeline

The Aggregate may expose a semantic Evidence timeline.

Example:

```text
2021
ACCOUNT_VERIFICATION

2022
SUBSCRIPTION

2023
PAYMENT

2024
ACCOUNT_DELETION

2026
MARKETING
```

The RelationshipAssessor may then reason about historical state.

The Aggregator itself must not interpret this timeline as:

```text
account deleted but reopened
```

without sufficient Evidence.

---

## 37. Historical Evidence

Historical Evidence must remain available to aggregation when it is still ACTIVE.

For example:

```text
ACCOUNT_CREATION
ACCOUNT_VERIFICATION
ACCOUNT_DELETION
```

should not be discarded merely because the Evidence refers to historical events.

The distinction is important:

```text
historical semantic event
        !=
SUPERSEDED Evidence
```

An `ACCOUNT_VERIFICATION` Evidence item from 2021 may still be:

```text
ACTIVE
```

because it is still the currently accepted interpretation of that historical Observation.

Therefore:

```text
historical Evidence semantics
```

and:

```text
Evidence lifecycle state
```

must remain distinct.

---

## 38. Evidence Ordering

Evidence may be ordered temporally where source semantics support it.

However, an Aggregator must not imply causal ordering merely because timestamps are ordered.

For example:

```text
A before B
```

does not necessarily mean:

```text
A caused B
```

Aggregation provides sequence.

Relationship reasoning provides interpretation.

---

## 39. Conflicting Evidence

Evidence may conflict.

Example:

```text
ACCOUNT_DELETION
```

followed by:

```text
AUTHENTICATION
```

Possible interpretations include:

```text
account recreated
deletion did not complete
different account
misclassified Evidence
timestamp semantics differ
shared account
```

The Aggregator must preserve the conflict.

It must not decide the explanation.

---

## 40. Conflict Summary

An Aggregate may expose:

```text
ConflictSummary
```

with information such as:

```text
potential_conflicts:
- ACCOUNT_DELETION followed by AUTHENTICATION
```

However, conflict detection must be based on explicit rules rather than arbitrary semantic speculation.

Draft v0.1 allows conflict reporting but does not define a complete conflict taxonomy.

---

## 41. Conflicting Evidence Must Not Be Discarded

The Aggregator must not resolve conflicts by deleting or ignoring one Evidence item.

Conceptually:

```text
Evidence A
    +
Evidence B
    |
    v
Conflict
```

not:

```text
Evidence A
    +
Evidence B
    |
choose one
    |
discard other
```

Both remain traceable.

---

## 42. Duplicate Observations vs Duplicate Evidence

Technical duplication can occur at multiple layers.

For example:

```text
same email imported twice
```

may produce duplicate Observations.

Repeated classification may produce duplicate Evidence.

The Aggregator must not blindly count every Evidence record as an independent semantic event.

---

## 43. Evidence Deduplication

The Aggregator may require a concept of logical Evidence uniqueness.

Possible factors include:

```text
supporting Observation
EvidenceType
classifier version
semantic event identity
source reference
EvidenceStatus
```

The exact deduplication model remains open.

The requirement is:

> Technical duplication must not artificially inflate Evidence frequency.

---

## 44. Deduplication Must Preserve Provenance

If two Evidence items are recognized as duplicates:

```text
Evidence A
Evidence B
    |
    v
same logical event
```

their provenance should not necessarily be deleted.

A future Aggregate may represent:

```text
logical event count:
1

supporting Evidence records:
2
```

if this distinction becomes necessary.

---

## 45. Cross-Source Similarity Is Not Duplication

Evidence from independent sources describing related events must not automatically be deduplicated.

Example:

```text
Gmail:
PAYMENT

Financial Source:
PAYMENT
```

may represent the same underlying transaction or two separate semantic Observations.

Without a reliable correlation mechanism, they should remain independently traceable.

Therefore:

```text
similar semantics
      !=
duplicate Evidence
```

---

## 46. Classification Version Duplicates

Suppose the same Observation is processed by:

```text
Classifier v1
Classifier v2
```

and both produce:

```text
PAYMENT
```

The Aggregator should not necessarily count this as two separate payment events.

The Evidence lifecycle provides an explicit mechanism for determining which interpretation participates in the current view.

For example:

```text
Classifier v1 Evidence:
PAYMENT
SUPERSEDED

Classifier v2 Evidence:
PAYMENT
ACTIVE
```

produces one current semantic contribution.

Classification history and current semantic Evidence count must remain distinguishable.

---

## 47. Current vs Superseded Evidence

The consolidated Domain Model defines:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

These lifecycle states are no longer a future candidate.

For the default current aggregation policy:

```text
ACTIVE
    -> include

SUPERSEDED
    -> exclude

REJECTED
    -> exclude
```

Conceptually:

```text
Evidence
 |
 +-- ACTIVE --------+
 |                  |
 |                  v
 |             Current Aggregate
 |
 +-- SUPERSEDED --> provenance/history
 |
 +-- REJECTED ----> provenance/history
```

Historical classification provenance remains available without artificially increasing current Evidence.

---

## 48. User-Corrected Evidence

If the User corrects:

```text
MARKETING
```

to:

```text
NEWSLETTER
```

the Aggregate should reflect the currently accepted Evidence semantics while preserving correction provenance.

For example:

```text
MARKETING
SUPERSEDED

NEWSLETTER
ACTIVE
```

results in:

```text
Current Aggregate:
NEWSLETTER = 1
MARKETING = 0
```

assuming no other independent ACTIVE MARKETING Evidence exists.

If the original interpretation was explicitly invalidated rather than replaced, it may instead be:

```text
REJECTED
```

according to Evidence lifecycle policy.

---

## 49. Evidence Validity Filtering

Aggregation uses explicit Evidence lifecycle state.

Conceptually:

```text
Evidence
 |
 +-- ACTIVE
 |
 +-- SUPERSEDED
 |
 +-- REJECTED
```

The default current Discovery aggregation policy consumes:

```text
ACTIVE
```

Evidence.

`SUPERSEDED` and `REJECTED` Evidence remain available for provenance or specifically requested historical/audit views.

This filtering is controlled by:

```text
EvidenceStatePolicy
```

within the AggregationContext.

The lifecycle semantics belong to the consolidated Domain Model.

The exact software implementation belongs to the Implementation Model.

---

## 50. Evidence from Multiple Identities

One Service may be associated with Evidence involving multiple IdentitySeeds.

Example:

```text
Spotify
 |
 +-- personal@gmail.com
 |
 +-- oldmail@example.net
```

The Aggregate must retain both.

It must not automatically conclude:

```text
two Accounts
```

or:

```text
same Account
```

These remain separate interpretation questions.

---

## 51. Unassociated Identity Evidence

Some Evidence may not be safely linked to a known IdentitySeed.

Example:

```text
Password Manager username:
old-address@example.com
```

where the address has not been confirmed as a User IdentitySeed.

The Aggregate may preserve:

```text
unassociated identity reference
```

rather than fabricating an Identity relationship.

---

## 52. Identity Completeness

An Aggregate should not require every Evidence item to have an Identity reference.

Valid state:

```text
Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION

Identity:
personal@example.com

Evidence:
MARKETING

Identity:
UNKNOWN
```

Both may belong to the Service-level Aggregate.

---

## 53. Aggregation Context

The Aggregator may require explicitly versioned policy or rules.

Conceptually:

```text
AggregationContext

- deduplication_policy
- evidence_state_policy
- temporal_policy
- conflict_policy
- aggregation_version
```

The context must not contain Provider credentials.

For the default current Discovery view:

```text
evidence_state_policy:

ACTIVE      -> include
SUPERSEDED  -> exclude
REJECTED    -> exclude
```

Historical or audit views may intentionally use different policies.

Such deviations must be explicit.

---

## 54. Deterministic Aggregation

Aggregation should be deterministic where practical.

Given the same:

```text
eligible Evidence set
+
AggregationContext
+
AggregatorVersion
```

the same Aggregate should be produced.

This improves:

- reproducibility;
- debugging;
- testing;
- reassessment.

---

## 55. AI Boundary

Basic Evidence Aggregation should not require AI.

Operations such as:

```text
group by Service
filter by EvidenceStatus
count EvidenceTypes
list ConnectedSources
calculate first/last observed
preserve Identity references
detect exact duplicates
```

are deterministic.

AI should not be used simply because a collection of Evidence exists.

---

## 56. AI for Complex Correlation

Future cases may require semantic correlation.

For example:

```text
Evidence from email
+
Evidence from financial transaction
+
Evidence from privacy export
```

may need richer interpretation.

However, such reasoning should not automatically become part of the basic EvidenceAggregator.

A separate correlation or advanced reasoning capability may eventually be more appropriate.

Draft v0.1 keeps aggregation deterministic-first.

---

## 57. No Permission Escalation

The Aggregator operates only on already available Evidence and provenance.

It must not request additional ConnectedSource permissions.

Conceptually:

```text
EvidenceAggregator
       |
       X
request Gmail body access
```

If more information is needed, that decision belongs to a higher-level capability.

---

## 58. Local-First

Evidence Aggregation should execute locally where technically practical.

The input may reveal highly sensitive information about the User's digital history.

There is no default justification for transmitting the complete Evidence graph to a remote service simply to:

```text
count
group
filter
sort
summarize
```

---

## 59. Aggregator Version

The result should identify the Aggregator version where practical.

Conceptually:

```text
aggregator_version:
1
```

This supports re-aggregation as logic evolves.

---

## 60. Re-Aggregation

Preserved individual Evidence should allow later re-aggregation.

Conceptually:

```text
Evidence Set
    |
    +--> Aggregator v1
    |         |
    |         v
    |    Aggregate v1
    |
    +--> Aggregator v2
              |
              v
         Aggregate v2
```

Individual Evidence remains unchanged unless separately reclassified or its lifecycle state changes.

---

## 61. Triggering Re-Aggregation

Re-aggregation may be required when:

```text
new ACTIVE Evidence arrives
Evidence is deleted
Evidence becomes SUPERSEDED
Evidence becomes REJECTED
Evidence is reclassified
Service Resolution changes
User correction occurs
ConnectedSource data is removed
Identity association changes
deduplication logic changes
aggregation policy changes
Service merge occurs
Service split occurs
```

The exact event mechanism remains an implementation concern.

---

## 62. Entity Re-Resolution

Suppose Evidence initially belongs to:

```text
Unresolved Candidate A
```

and later Entity Resolution determines:

```text
Candidate A
    ->
Spotify
```

The Evidence should then become eligible for the Spotify Aggregate.

Conceptually:

```text
Unresolved Evidence
        |
        v
Re-resolution
        |
        v
Resolved Service
        |
        v
Re-aggregation
```

No source retrieval should be required if preserved information is sufficient.

---

## 63. Service Merge

If:

```text
Service A
```

and:

```text
Service B
```

are later merged into:

```text
Service C
```

their EvidenceAggregates must be recalculable.

The Aggregator should not store irreversible summary state that prevents reconstructing the combined Evidence context.

---

## 64. Service Split

Similarly, a Service split may require redistribution of Evidence based on preserved identifier and Observation provenance.

This reinforces:

```text
EvidenceAggregate
=
Derived View
```

which must remain reconstructable from authoritative Evidence.

---

## 65. Aggregation Persistence

An EvidenceAggregate may be:

```text
computed on demand
```

or:

```text
materialized and persisted
```

The contract does not choose between these strategies.

Materialization may improve performance.

On-demand computation may reduce synchronization complexity.

Regardless of persistence:

```text
EvidenceAggregate
```

remains:

```text
Derived View
```

and not:

```text
Core Domain Entity
```

---

## 66. Aggregate Identity

If materialized, an Aggregate may require stable identity or a deterministic cache/materialization key.

Potential conceptual identity may derive from:

```text
Aggregation Scope
+
Service Reference
+
Identity Scope
+
Aggregation Policy Version
+
Aggregator Version
```

The exact identity model remains undefined.

Persistence identity must not transform EvidenceAggregate into authoritative Domain state.

---

## 67. Aggregate Is Derived State

An EvidenceAggregate must always be considered derived state.

Therefore:

```text
EvidenceAggregate
       |
       v
can be rebuilt
       |
       v
from authoritative eligible Evidence
```

where preserved Evidence remains available.

The Aggregate must not become the sole source of semantic provenance.

This is formalized by:

```text
D-021 - Evidence Aggregates Are Derived State
```

---

## 68. Aggregate Deletion

Deleting a materialized Aggregate should not delete underlying Evidence.

Conceptually:

```text
Delete Aggregate
     |
     v
Evidence remains
```

The Aggregate can later be rebuilt.

---

## 69. Evidence Deletion

Deleting Evidence is different.

Conceptually:

```text
Delete Evidence
      |
      v
Affected Aggregates
      |
      v
Recalculate
      |
      v
Affected Relationships
      |
      v
Reassess
```

The exact orchestration remains outside this contract.

---

## 70. ConnectedSource Removal

Suppose a User deletes all retained information from:

```text
Personal Gmail
```

Evidence derived exclusively from that ConnectedSource may need to be deleted or invalidated according to lifecycle policy.

The Aggregate must then be recomputed from remaining ACTIVE Evidence.

Example:

```text
Before:

Spotify
 |
 +-- Gmail ACCOUNT_VERIFICATION
 +-- Gmail PAYMENT
 +-- Password Manager Entry
```

After Gmail-derived Evidence removal:

```text
Spotify
 |
 +-- Password Manager Entry
```

The Relationship may still exist but requires reassessment.

---

## 71. Partial Evidence Sets

Aggregation may sometimes operate over incomplete source coverage.

For example:

```text
ConnectedSource A:
COMPLETE

ConnectedSource B:
PARTIAL

ConnectedSource C:
FAILED
```

The Aggregate should not claim:

```text
complete Evidence footprint
```

merely because aggregation succeeded over available Evidence.

---

## 72. Coverage Metadata

EvidenceAggregate may include a `CoverageSummary` when reliable collection context is available.

Conceptually:

```text
CoverageSummary

ConnectedSource A = COMPLETE
ConnectedSource B = PARTIAL
ConnectedSource C = FAILED
```

Collection completeness originates upstream.

The Aggregator may summarize it when relevant but must not invent it.

The consolidated Domain Model classifies `CoverageSummary` as:

```text
Derived Processing Context
```

rather than a Core Domain Entity.

---

## 73. Aggregate Completeness

The framework cannot normally know:

```text
All Evidence that could possibly exist
```

because Discovery itself is incomplete.

Therefore an Aggregate must not claim absolute completeness.

At most it can describe known coverage relative to:

```text
configured ConnectedSources
+
available collection/synchronization context
```

---

## 74. Cross-Source Example

Input Evidence:

```text
Evidence 1
Type:
ACCOUNT_VERIFICATION
Status:
ACTIVE
Source:
Personal Gmail

Evidence 2
Type:
SUBSCRIPTION
Status:
ACTIVE
Source:
Personal Gmail

Evidence 3
Type:
PAYMENT
Status:
ACTIVE
Source:
Personal Gmail

Evidence 4
Type:
PASSWORD_MANAGER_ENTRY
Status:
ACTIVE
Source:
Primary Password Manager
```

All resolve to:

```text
Spotify
```

Possible Aggregate:

```text
Service:
Spotify

EvidenceSummary:
ACCOUNT_VERIFICATION      1
SUBSCRIPTION              1
PAYMENT                   1
PASSWORD_MANAGER_ENTRY    1

ConnectedSources:
2

SourceTypes:
EMAIL
PASSWORD_MANAGER

IdentityReferences:
personal@example.com
```

The Aggregate still does not assign:

```text
RelationshipStatus:
ESTABLISHED
```

That remains Relationship Assessment responsibility.

---

## 75. Single-Source High-Volume Example

Input:

```text
Spotify

Gmail:
150 ACTIVE MARKETING Evidence items
```

Aggregate:

```text
EvidenceSummary:
MARKETING 150

ConnectedSources:
1

SourceTypes:
EMAIL
```

The Aggregator must not transform this into:

```text
strong Relationship
```

simply because Evidence count is high.

---

## 76. Multi-Source Low-Volume Example

Input:

```text
Spotify

Gmail:
1 ACTIVE ACCOUNT_VERIFICATION

Password Manager:
1 ACTIVE PASSWORD_MANAGER_ENTRY
```

Aggregate:

```text
EvidenceSummary:

ACCOUNT_VERIFICATION      1
PASSWORD_MANAGER_ENTRY    1

ConnectedSources:
2

SourceTypes:
EMAIL
PASSWORD_MANAGER
```

The RelationshipAssessor may later consider this differently from 150 marketing emails.

The Aggregator itself does not assign that meaning.

---

## 77. Historical Example

Input ACTIVE Evidence:

```text
2021 ACCOUNT_CREATION
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

Aggregate:

```text
EvidenceTypes:

ACCOUNT_CREATION
ACCOUNT_VERIFICATION
PAYMENT
ACCOUNT_DELETION

FirstObserved:
2021

LastRelevantEvidence:
2024

Timeline:
preserved
```

The Aggregator does not conclude:

```text
TemporalStatus:
HISTORICAL
```

although it provides the information needed for Relationship Assessment.

---

## 78. Conflicting Example

Input:

```text
2024 ACCOUNT_DELETION
ACTIVE

2026 AUTHENTICATION
ACTIVE
```

Aggregate:

```text
EvidenceSummary:

ACCOUNT_DELETION 1
AUTHENTICATION   1

Conflict:
potential temporal-semantic inconsistency
```

The Aggregator does not decide whether:

```text
account was recreated
```

or:

```text
deletion was ineffective
```

or another explanation applies.

---

## 79. Multiple Identity Example

Input:

```text
Spotify

Evidence 1:
PASSWORD_MANAGER_ENTRY
Status:
ACTIVE
Identity:
personal@example.com

Evidence 2:
PASSWORD_MANAGER_ENTRY
Status:
ACTIVE
Identity:
oldmail@example.net
```

Aggregate:

```text
Service:
Spotify

IdentityReferences:
- personal@example.com
- oldmail@example.net

EvidenceSummary:
PASSWORD_MANAGER_ENTRY 2
```

The Aggregator must not infer:

```text
Two Spotify Accounts
```

because Account remains a Candidate Domain Concept.

---

## 80. Unresolved Example

Input:

```text
Evidence:
PAYMENT

Status:
ACTIVE

ServiceIdentifier:
unknownservice.example

Resolution:
UNRESOLVED
```

Possible Aggregate:

```text
Scope:
UNRESOLVED_SERVICE_CANDIDATE

Identifier:
unknownservice.example

EvidenceSummary:
PAYMENT 1
```

Later re-resolution may move this Evidence into a canonical Service Aggregate.

---

## 81. Ambiguous Example

Input:

```text
Evidence:
SUBSCRIPTION

Status:
ACTIVE

Resolution:
AMBIGUOUS

Possible Services:
Service A
Service B
```

The Evidence should remain:

```text
Ambiguous Service Context
```

rather than being counted in both Service Aggregates as though both mappings were true.

---

## 82. Processing Failure

If an internal aggregation failure occurs:

```text
processing_status:
FAILED
```

must remain distinct from:

```text
aggregation_status:
EMPTY
```

An empty Aggregate is a Domain condition.

A failed aggregation is a technical condition.

---

## 83. Unsupported Evidence Version

If the Aggregator receives an Evidence format or version it cannot understand:

```text
processing_status:
UNSUPPORTED
```

should be possible.

The framework must not silently ignore unsupported eligible Evidence and present the remaining Aggregate as complete.

---

## 84. Batch Aggregation

An implementation may aggregate multiple Service contexts in one execution.

Conceptually:

```text
aggregate_many(...)
```

may process:

```text
Spotify
GitHub
Netflix
Amazon
```

together.

Each aggregation scope must still receive an independently traceable AggregationResult and EvidenceAggregate.

---

## 85. Streaming Aggregation

Large Evidence sets may eventually benefit from streaming or incremental aggregation.

Conceptually:

```text
Existing Aggregate
       +
New Evidence
       |
       v
Updated Aggregate
```

However, incremental updates must produce the same logical result as rebuilding the Aggregate from authoritative current Evidence under the same Aggregator version and policy.

---

## 86. Incremental Consistency

If:

```text
Aggregate(Evidence A + Evidence B)
```

differs semantically from:

```text
Aggregate(Evidence A)
then add Evidence B
```

under the same:

```text
EvidenceStatePolicy
DeduplicationPolicy
TemporalPolicy
ConflictPolicy
AggregatorVersion
```

the implementation contains an aggregation consistency problem.

The contract expects deterministic equivalence where practical.

---

## 87. Aggregation Context

The conceptual context may be:

```text
AggregationContext {

    DeduplicationPolicy deduplicationPolicy

    TemporalPolicy temporalPolicy

    EvidenceStatePolicy evidenceStatePolicy

    ConflictPolicy conflictPolicy

    AggregatorVersion aggregatorVersion
}
```

The default `EvidenceStatePolicy` for the current Discovery view is conceptually:

```text
ACTIVE:
INCLUDE

SUPERSEDED:
EXCLUDE

REJECTED:
EXCLUDE
```

This is pseudocode.

The exact implementation remains open.

---

## 88. Language-Independent Contract

The initial conceptual interface is:

```text
interface EvidenceAggregator {

    AggregationResult aggregate(
        AggregationRequest request
    )
}
```

This is pseudocode.

It is not the final Python interface.

---

## 89. Aggregation Request Contract

Conceptually:

```text
AggregationRequest {

    AggregationScope scope

    Optional<ServiceReference> serviceReference

    Optional<UnresolvedIdentifierReference> unresolvedReference

    List<IdentityReference> identityReferences

    List<EvidenceReference> evidenceItems

    AggregationContext context
}
```

Evidence references may include lifecycle states, or the application layer may resolve them before Aggregator invocation.

The exact application boundary remains an Implementation Model decision.

---

## 90. Aggregation Result Contract

Conceptually:

```text
AggregationResult {

    ProcessingStatus processingStatus

    Optional<AggregationStatus> aggregationStatus

    Optional<EvidenceAggregate> aggregate

    AggregatorVersion aggregatorVersion
}
```

`AggregationResult` is classified as:

```text
Processing Result
```

It describes execution of the aggregation operation.

`EvidenceAggregate` is classified as:

```text
Derived View
```

It represents the structured semantic result.

Therefore:

```text
AggregationResult
        !=
EvidenceAggregate
```

---

## 91. EvidenceSummary Contract

Conceptually:

```text
EvidenceSummary {

    totalEvidenceCount

    evidenceCountByType

    activeEvidenceTypes
}
```

For the default current Discovery view:

```text
totalEvidenceCount
```

and:

```text
evidenceCountByType
```

refer to Evidence eligible under the active EvidenceStatePolicy, normally ACTIVE Evidence only.

Historical classification interpretations remain available through Evidence provenance rather than being mixed into current semantic counts.

---

## 92. SourceSummary Contract

Conceptually:

```text
SourceSummary {

    connectedSourceCount

    sourceTypes

    providers

    evidenceCountByConnectedSource

    evidenceCountBySourceType
}
```

Provider information may be omitted when unnecessary.

The summary should remain privacy-minimized.

---

## 93. TemporalSummary Contract

Conceptually:

```text
TemporalSummary {

    firstObserved

    lastObserved

    evidenceTimeline

    typedTemporalValues
}
```

Temporal values must preserve their semantics.

Historical event time and Evidence lifecycle state must not be conflated.

---

## 94. ConflictSummary Contract

Conceptually:

```text
ConflictSummary {

    hasPotentialConflicts

    conflictTypes

    involvedEvidenceReferences
}
```

The final conflict taxonomy remains open.

ConflictSummary must describe detected conflicts without inventing their explanation.

---

## 95. Evidence Aggregator Invariants

### EA-INV-001

The Aggregator must operate on framework Evidence rather than raw Provider objects.

### EA-INV-002

Aggregation must not destructively replace individual Evidence.

### EA-INV-003

Every Aggregate must remain traceable to its contributing Evidence.

### EA-INV-004

Evidence frequency must not be interpreted as Evidence strength.

### EA-INV-005

The Aggregator must not assign RelationshipStatus.

### EA-INV-006

The Aggregator must not assign numerical Relationship Confidence.

### EA-INV-007

Evidence from multiple ConnectedSources may contribute to one Service Aggregate.

### EA-INV-008

Evidence from multiple SourceTypes may contribute to one Service Aggregate.

### EA-INV-009

Provider identity must not create separate canonical Service Aggregates.

### EA-INV-010

Identity references must not be discarded during Service-level aggregation.

### EA-INV-011

Multiple Identity references must not automatically imply multiple Accounts.

### EA-INV-012

Evidence without a known Identity reference may still participate in Service-level aggregation.

### EA-INV-013

Unresolved-Service Evidence must not be discarded.

### EA-INV-014

Ambiguous-Service Evidence must not be arbitrarily assigned to one Service.

### EA-INV-015

Ambiguous Evidence must not be duplicated across all possible Services as though each resolution were true.

### EA-INV-016

Technical duplicate Evidence must not artificially increase semantic Evidence frequency.

### EA-INV-017

Similar Evidence from independent sources must not automatically be treated as duplicates.

### EA-INV-018

Conflicting Evidence must remain preserved.

### EA-INV-019

The Aggregator must not resolve Evidence conflicts by silently deleting one side.

### EA-INV-020

Temporal aggregation must preserve source-specific temporal semantics.

### EA-INV-021

`first_observed` must not automatically be interpreted as account creation.

### EA-INV-022

`last_observed` must not automatically be interpreted as last Service usage.

### EA-INV-023

Historical Evidence must not be discarded merely because later Evidence exists.

### EA-INV-024

The Aggregator must not request additional source permissions.

### EA-INV-025

Provider credentials must not be required by the Aggregator.

### EA-INV-026

Basic aggregation must not require AI.

### EA-INV-027

Re-aggregation must not require source retrieval when preserved Evidence is sufficient.

### EA-INV-028

Service merge or split operations must remain compatible with rebuilding Aggregates from underlying Evidence.

### EA-INV-029

Deleting a materialized Aggregate must not delete underlying Evidence.

### EA-INV-030

Deleting or invalidating underlying Evidence must trigger eventual Aggregate reassessment where affected.

### EA-INV-031

Processing failure must remain distinguishable from an EMPTY EvidenceAggregate.

### EA-INV-032

An Aggregate must not claim perfect completeness of the User's real-world Evidence footprint.

### EA-INV-033

Aggregation should be deterministic for the same eligible Evidence set, context and Aggregator version where practical.

### EA-INV-034

Incremental aggregation and full rebuild should produce logically equivalent results under the same rules where practical.

### EA-INV-035

Current Discovery aggregation should normally consume only ACTIVE Evidence.

### EA-INV-036

SUPERSEDED Evidence must not contribute to current semantic Evidence counts under the default current-view policy.

### EA-INV-037

REJECTED Evidence must not contribute to current Relationship Assessment.

### EA-INV-038

Historical or audit aggregation including non-ACTIVE Evidence must require an explicit EvidenceStatePolicy.

### EA-INV-039

Evidence lifecycle state and temporal semantics must remain distinct.

### EA-INV-040

EvidenceAggregate must remain classified as a Derived View even when materialized or persisted.

### EA-INV-041

AggregationResult must remain classified as a Processing Result even when persisted.

### EA-INV-042

Deleting an EvidenceAggregate must not change authoritative Evidence lifecycle state.

---

## 96. Complete Gmail + Password Manager Example

Suppose Service Resolution has produced:

```text
Service:
Spotify
```

Evidence Classification and lifecycle management have produced:

```text
Evidence 001

Type:
ACCOUNT_VERIFICATION

Status:
ACTIVE

ConnectedSource:
Personal Gmail

Identity:
personal@example.com

Observed:
2021-03-10
```

```text
Evidence 002

Type:
SUBSCRIPTION

Status:
ACTIVE

ConnectedSource:
Personal Gmail

Identity:
personal@example.com

Observed:
2021-03-11
```

```text
Evidence 003

Type:
PAYMENT

Status:
ACTIVE

ConnectedSource:
Personal Gmail

Identity:
personal@example.com

Observed:
2021-03-11
```

```text
Evidence 004

Type:
PASSWORD_MANAGER_ENTRY

Status:
ACTIVE

ConnectedSource:
Primary Password Manager

Identity:
personal@example.com

TemporalSemantics:
SOURCE_RECORD_MODIFIED

Observed:
2025-08-20
```

Suppose an older classification also remains:

```text
Evidence 005

Type:
MARKETING

Status:
SUPERSEDED

ConnectedSource:
Personal Gmail
```

The default current Aggregate should use Evidence 001-004 and exclude Evidence 005.

Conceptually:

```text
Service:
Spotify

Current Evidence Count:
4

EvidenceSummary:

ACCOUNT_VERIFICATION       1
SUBSCRIPTION               1
PAYMENT                    1
PASSWORD_MANAGER_ENTRY     1

MARKETING:
not counted in current view

IdentityReferences:
personal@example.com

ConnectedSourceCount:
2

SourceTypes:
EMAIL
PASSWORD_MANAGER

Temporal Information:

2021-03-10 EMAIL EVENT
2021-03-11 EMAIL EVENT
2021-03-11 EMAIL EVENT
2025-08-20 PASSWORD MANAGER RECORD MODIFIED
```

It must not produce:

```text
RelationshipStatus:
ESTABLISHED
```

nor:

```text
AccountActive:
true
```

Those interpretations belong downstream.

---

## 97. Open Questions

### Aggregation Scope

The primary Relationship is now User-Service and Service remains the primary aggregation boundary.

The remaining questions are:

- Are separate Identity-level derived views necessary?
- Should User-level and Identity-filtered views coexist?
- How should unresolved Service candidates be grouped?
- When would `IdentityServiceAssociation` become necessary?

### Evidence Lifecycle

The Domain Model now defines:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

The remaining questions are:

- What exact EvidenceStatus transitions are permitted?
- Can REJECTED Evidence become ACTIVE again?
- When should Evidence become SUPERSEDED rather than REJECTED?
- How should User-corrected Evidence affect automated Evidence?
- How should historical/audit Aggregates request non-ACTIVE Evidence?
- How is EvidenceStatePolicy versioned?

### Deduplication

- What defines one logical Evidence event?
- Should duplicate Observations be removed before Evidence Classification?
- Should the Aggregator own semantic deduplication?
- How should source imports and migrations be handled?
- How should multiple classifications of one Observation interact with Evidence lifecycle?

### Temporal Model

- Is one `first_observed` and `last_observed` value sufficiently precise?
- Should temporal values always retain typed semantics?
- Should an Aggregate expose multiple temporal dimensions?
- How should missing or uncertain timestamps be represented?
- How should historical event semantics remain distinct from EvidenceStatus?

### Conflicts

- Which Evidence combinations qualify as conflicts?
- Is ACCOUNT_DELETION followed by AUTHENTICATION always a conflict?
- Should the Aggregator only expose raw chronology and leave more conflict interpretation downstream?
- Is a dedicated conflict detector eventually necessary?

### Source Diversity

- Should source diversity remain only descriptive?
- Which SourceType distinctions are useful to Relationship Assessment?
- How should multiple email accounts compare with multiple structurally different SourceTypes?

### Identity

- Which Identity-filtered Aggregate views are necessary?
- How should unverified observed identities participate?
- How should aliases affect Identity summaries?
- When is `IdentityServiceAssociation` necessary?

### Account

- Does aggregation eventually provide enough Evidence to justify introducing Account?
- Could multiple Identity-specific Evidence clusters reveal separate Accounts?
- Should that remain a downstream inference rather than Aggregation responsibility?

### Service Resolution

- What happens when Entity Resolution changes after Aggregation?
- How is Evidence moved between Aggregates?
- How are ambiguous candidates represented efficiently?
- How do Service merge and split operations invalidate materialized Aggregates?

### Persistence

- Should Aggregates be materialized?
- What is the cache/materialization identity?
- How are materialized Aggregates invalidated?
- Should they be rebuilt on demand?
- What scale would justify incremental materialization?
- Where is AggregatorVersion stored?

### Completeness

- How should ConnectedSource collection completeness be reflected?
- Should Relationship Assessment receive CoverageSummary through EvidenceAggregate?
- Can EvidenceAggregate completeness ever be meaningfully defined?
- Is CollectionRun required for reliable coverage semantics?

### AI

- Is there any justified use of AI in basic aggregation?
- Should semantic event correlation become a separate future capability rather than part of EvidenceAggregator?

### Confidence

Numerical Aggregate Confidence is outside the initial Discovery baseline.

The remaining question is whether any later aggregate-level metric can be clearly defined and empirically validated without duplicating Relationship Assessment semantics.

---

## 98. Findings from Contract Design

### Finding 1 - Aggregates Are Derived State

An EvidenceAggregate is not authoritative source information.

It must remain reconstructable from individual Evidence.

The consolidated Domain Model now formally classifies:

```text
EvidenceAggregate
```

as:

```text
Derived View
```

This is also captured by:

```text
D-021 - Evidence Aggregates Are Derived State
```

Materialization does not change that classification.

### Finding 2 - Service Is the Primary Aggregation Boundary, but Identity Must Be Preserved

The current Domain is Service-oriented:

> Which Services appear connected to me?

The primary Relationship is:

```text
User -> Service
```

Therefore Service is the natural primary aggregation boundary.

Identity references must remain inside the Aggregate because Identity-oriented queries and possible future Account semantics may depend on them.

### Finding 3 - Unresolved Evidence Requires an Aggregation Path

Evidence semantics may be known before Service identity is resolved.

The system therefore requires an unresolved aggregation context rather than discarding such Evidence.

### Finding 4 - Source Diversity and Evidence Frequency Are Different Dimensions

These situations are structurally different:

```text
100 Evidence items
from one Gmail account
```

and:

```text
2 Evidence items
from Gmail and Password Manager
```

The Aggregate should describe both dimensions independently.

It must not decide which represents the stronger Relationship.

### Finding 5 - Evidence Lifecycle Is Now a Consolidated Dependency

Reclassification and User correction require control over which Evidence represents the currently accepted semantic interpretation.

The Domain Model now defines:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

Therefore the default current Aggregate should consume ACTIVE Evidence only.

SUPERSEDED and REJECTED Evidence remain provenance/history unless an explicit aggregation policy requests them.

### Finding 6 - Account Remains a Candidate Concept

Identity-aware aggregation again exposes cases such as:

```text
Spotify

personal@example.com

oldmail@example.net
```

but still does not prove that two separate Accounts exist.

The Account abstraction therefore remains a Candidate Domain Concept.

### Finding 7 - Basic Aggregation Does Not Need AI

Grouping, filtering Evidence lifecycle, counting, provenance preservation, source diversity and temporal summarization are deterministic operations.

Any future semantic correlation requiring richer reasoning should be justified separately rather than inserted into the base Aggregator.

### Finding 8 - AggregationResult and EvidenceAggregate Have Different Roles

The consolidated Domain Model distinguishes:

```text
AggregationResult
=
Processing Result
```

from:

```text
EvidenceAggregate
=
Derived View
```

The former represents execution.

The latter represents derived semantic state.

### Finding 9 - Historical Event Semantics and Historical Evidence Versions Are Different

An ACTIVE Evidence item may describe an event from years ago.

A SUPERSEDED Evidence item may describe a recently collected Observation.

Therefore:

```text
event time
        !=
Evidence lifecycle state
```

and must remain independently represented.

---

## 99. Architecture Alignment and Remaining Decision Candidates

### Architecture Alignment - Aggregate Is Derived State

EvidenceAggregates are Derived Views based on authoritative Evidence.

They must remain reconstructable where underlying Evidence is retained.

This is formalized by:

```text
D-021 - Evidence Aggregates Are Derived State
```

### Architecture Alignment - Service-Level Aggregation with Identity Preservation

Service is the primary Evidence aggregation boundary for Service Discovery.

The primary Relationship is User-Service.

Identity references associated with Evidence remain preserved inside the Aggregate.

### Architecture Alignment - Evidence Lifecycle Filtering

The default current Discovery Aggregate consumes:

```text
ACTIVE Evidence
```

while:

```text
SUPERSEDED Evidence
REJECTED Evidence
```

are excluded from current semantic counts.

Historical or audit views may use separate explicit policy.

### Architecture Alignment - Evidence Frequency Is Descriptive

Evidence frequency is represented descriptively.

It must not automatically determine Relationship strength.

### Architecture Alignment - Preserve Source Diversity

Evidence Aggregation preserves:

```text
ConnectedSource
SourceType
Provider provenance where relevant
```

so Relationship Assessment can distinguish repeated observations from structurally different source support.

### Architecture Alignment - Preserve Unresolved Evidence

Evidence associated with unresolved or ambiguous Service candidates must not be discarded solely because canonical Entity Resolution is incomplete.

### Architecture Alignment - Aggregator Does Not Assess Relationship

EvidenceAggregator structures Evidence for Relationship Assessment.

It does not assign:

```text
RelationshipStatus
```

or:

```text
TemporalStatus
```

and does not calculate arbitrary numerical Confidence.

### Architecture Alignment - Deterministic Aggregation

Basic Evidence Aggregation remains deterministic and local-first where technically practical.

AI is not required for:

```text
filtering
grouping
counting
sorting
provenance preservation
temporal summarization
```

### Architecture Alignment - No Numerical Confidence

Numerical Aggregate Confidence is outside the initial Discovery baseline.

This is consistent with:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

### Remaining Decision Candidate - Materialized vs On-Demand Aggregate

EvidenceAggregate semantics are now defined as derived state.

The Implementation Model must still determine whether Aggregates are:

```text
computed on demand
```

or:

```text
materialized
```

for the initial implementation.

### Remaining Decision Candidate - Semantic Deduplication

Technical deduplication requirements are clear.

The exact boundary for semantic event deduplication remains unresolved and should be validated against real Gmail data during the Vertical MVP.

---

## 100. Current Contract Baseline

The aligned EvidenceAggregator contract is:

```text
Evidence
Evidence
Evidence
    |
    v
EvidenceStatePolicy
    |
    +-- ACTIVE -------> include
    |
    +-- SUPERSEDED ---> exclude from current view
    |
    +-- REJECTED -----> exclude from current view
    |
    v
AggregationRequest
    |
    v
EvidenceAggregator
    |
    v
AggregationResult
[Processing Result]
    |
    v
EvidenceAggregate
[Derived View]
    |
    +-- scope
    |
    +-- service_reference
    |
    +-- identity_references
    |
    +-- evidence_references
    |
    +-- EvidenceSummary
    |
    +-- SourceSummary
    |
    +-- TemporalSummary
    |
    +-- ConflictSummary
    |
    +-- CoverageSummary
    |
    +-- aggregator_version
```

with the guarantees:

```text
individual Evidence preserved

ACTIVE Evidence used by default for current aggregation

SUPERSEDED Evidence excluded from current semantic counts

REJECTED Evidence excluded from current assessment

Evidence lifecycle distinct from temporal semantics

Service-oriented aggregation

User-Service orientation

Identity provenance preserved

cross-source Evidence supported

source diversity preserved

Evidence frequency represented descriptively

temporal semantics preserved

conflicting Evidence retained

unresolved Evidence retained

ambiguous Evidence not arbitrarily assigned

no RelationshipStatus conclusion

no TemporalStatus conclusion

no numerical Confidence

deterministic-first operation

no Provider credentials

no permission escalation

re-aggregation supported

D-021 derived-state semantics

EvidenceAggregate classified as Derived View

AggregationResult classified as Processing Result
```

---

## 101. Downstream Contract

The next contract in the Discovery pipeline is:

```text
RelationshipAssessor
```

and has already been defined in:

```text
docs/interfaces/07-relationship-assessor-contract.md
```

The consolidated dependency is:

```text
                         Observation
                         /         \
                        /           \
                       v             v
        ServiceCandidateDetector   EvidenceClassifier
                       |             |
                       v             v
            CandidateIdentifier   EvidenceCandidate
                       |             |
                       v             v
              ServiceIdentifier    Evidence
                       |             |
                       v             |
                EntityResolver      |
                       |             |
                       v             |
                    Service          |
                       \             /
                        \           /
                         v         v
                    EvidenceAggregator
                            |
                            v
                    EvidenceAggregate
                     [Derived View]
                            |
                            v
                   RelationshipAssessor
                            |
                            v
              RelationshipAssessmentResult
                            |
                            v
                     Application Layer
                            |
                            v
                       Relationship
```

For the default current Discovery path:

```text
Evidence
   |
   v
EvidenceStatus
   |
   +-- ACTIVE ------+
   |                |
   |                v
   |          EvidenceAggregator
   |                |
   |                v
   |         EvidenceAggregate
   |                |
   |                v
   |      RelationshipAssessor
   |
   +-- SUPERSEDED --> provenance/history
   |
   +-- REJECTED ----> provenance/history
```

The RelationshipAssessor consumes the structured Aggregate and determines:

```text
RelationshipStatus

UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

independently from:

```text
TemporalStatus

UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

The EvidenceAggregator must not assign either dimension.

The Evidence Aggregator Contract is now aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- EvidenceStatus as a consolidated lifecycle concept;
- ACTIVE / SUPERSEDED / REJECTED semantics;
- ACTIVE-only default current aggregation;
- User-Service as the primary Relationship orientation;
- Identity preservation within the aggregation context;
- D-021 EvidenceAggregate derived-state semantics;
- AggregationResult as a Processing Result;
- CoverageSummary as Derived Processing Context;
- D-023 exclusion of numerical Confidence;
- deterministic-first Discovery;
- the parallel Entity Resolution / Evidence Classification model.

No additional Evidence Aggregation abstraction is required before the Implementation Model phase.
