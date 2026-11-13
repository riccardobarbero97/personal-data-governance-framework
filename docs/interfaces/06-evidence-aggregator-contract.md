# Evidence Aggregator Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md`  
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
Evidence A
Evidence B
Evidence C
    |
    v
Evidence Aggregator
    |
    v
Evidence Aggregate
    |
    v
Relationship Assessor
```

Its purpose is not to determine whether a Relationship is:

```text
CONFIRMED
PROBABLE
HISTORICAL
ACTIVE
```

or any other final Relationship state.

Its responsibility is narrower:

> Given the Evidence currently associated with a Service and relevant Identity context, what structured body of Evidence is available for Relationship Assessment?

The aggregator must preserve the individual Evidence and its provenance while deriving useful aggregate information such as:

- Evidence Types;
- Evidence counts;
- source diversity;
- ConnectedSource diversity;
- temporal distribution;
- Identity references;
- conflicting Evidence;
- historical Evidence;
- duplicate handling;
- unresolved information.

---

## 2. Architectural Position

The Evidence Aggregator operates after individual Evidence has been classified and relevant Service identifiers have been resolved where possible.

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
                            |
                            v
                   Relationship Assessor
                            |
                            v
                       Relationship
```

The aggregator brings together two different kinds of output:

```text
What Service is involved?
```

and:

```text
What Evidence has been observed?
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

For example, the aggregator may produce:

```text
Service:
Spotify

Evidence Summary:
ACCOUNT_VERIFICATION    1
SUBSCRIPTION            4
PAYMENT                12
MARKETING              30
PASSWORD_MANAGER_ENTRY  1

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
Relationship:
CONFIRMED ACTIVE ACCOUNT
```

That belongs to the `RelationshipAssessor`.

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

The aggregator creates a structured view:

```text
150 individual Evidence items
           |
           v
      aggregation
           |
           v
Service:
Spotify

Evidence Types:
ACCOUNT_VERIFICATION  1
PAYMENT              15
SUBSCRIPTION          8
MARKETING           125
PASSWORD_MANAGER_ENTRY 1

Connected Sources:
2

Source Types:
2

Timeline:
2020 -> 2026
```

The original Evidence remains available.

The aggregate is a derived view over that Evidence.

---

## 5. Aggregation Does Not Replace Evidence

The aggregator must not collapse individual Evidence into an irreversible summary.

Therefore:

```text
AGGREGATE
    !=
REPLACEMENT FOR EVIDENCE
```

The relationship:

```text
Evidence Aggregate
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

---

## 6. Input Contract

The aggregator should receive explicitly identified Evidence and relevant context.

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

- service_reference
- identity_references
- evidence_items
- context
```

The exact implementation remains open.

---

## 7. Service-Oriented Aggregation

The primary aggregation boundary is currently the canonical `Service`.

Conceptually:

```text
Service
   |
   +-- Evidence A
   +-- Evidence B
   +-- Evidence C
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

The final Discovery objective is to identify Relationships between the User or their Identities and Services.

Therefore aggregation around:

```text
Service
```

is more useful than aggregation around:

```text
Provider
Connector
Observation Type
ConnectedSource
```

Those concepts remain provenance dimensions.

They should not define separate canonical Relationships merely because the Evidence originated from different sources.

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

The aggregator must not automatically merge:

```text
personal@example.com
```

and:

```text
oldmail@example.net
```

into one Identity.

The aggregate should retain the Identity references associated with its Evidence.

---

## 10. User-Level vs Identity-Level Aggregation

The Domain Model has not yet fully resolved whether a Relationship is fundamentally:

```text
User <-> Service
```

or:

```text
IdentitySeed <-> Service
```

or whether both views are required.

The aggregator must therefore avoid prematurely destroying Identity granularity.

A future Relationship Assessor may need:

```text
User-level Service Evidence

AND

Identity-level Service Evidence
```

The Evidence Aggregate should support both views where the underlying Evidence provides sufficient information.

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

The aggregator must not invent Account entities merely because multiple Identity references exist.

Until `Account` is formally introduced:

```text
Identity-specific Evidence
        !=
Confirmed separate Accounts
```

The aggregate should preserve the distinction without making the inference.

---

## 12. Resolved-Service Evidence

The normal aggregation case is:

```text
Evidence
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

Service:
Spotify
```

can contribute to:

```text
Spotify Evidence Aggregate
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

The aggregator must support unresolved aggregation contexts.

Conceptually:

```text
Unresolved Service Context
        |
        +-- Candidate Identifier
        |
        +-- Evidence
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

The Evidence may remain outside canonical Service aggregates until ambiguity is resolved.

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

The framework should preserve useful semantic information even before canonical identity is known.

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

For the current Discovery workflow, `SERVICE` is the primary case.

---

## 18. Aggregation Result

The initial conceptual result is:

```text
AggregationResult

- processing_status
- aggregation_status
- scope
- service_reference
- identity_references
- evidence_references
- evidence_summary
- source_summary
- temporal_summary
- conflict_summary
- aggregator_version
```

The exact representation remains open.

---

## 19. Processing Status

Technical processing state must remain separate from domain aggregation state.

Potential processing states include:

```text
SUCCESS
UNSUPPORTED
FAILED
```

A processing failure must not silently produce an empty Evidence Aggregate.

---

## 20. Aggregation Status

Potential domain states may include:

```text
AGGREGATED

EMPTY

PARTIAL
```

### AGGREGATED

One or more Evidence items were successfully aggregated.

### EMPTY

The request contained no usable Evidence.

### PARTIAL

Some Evidence could be aggregated while other items could not be processed.

The final taxonomy remains open.

---

## 21. Empty Aggregate

An empty aggregate must not be interpreted as:

```text
No Relationship exists.
```

It means only:

```text
No usable Evidence is currently present in this aggregation context.
```

The absence of Evidence is not proof of absence of a Relationship.

---

## 22. Evidence References

Every aggregate must preserve references to the Evidence items from which it was derived.

Conceptually:

```text
EvidenceAggregate
 |
 +-- evidence_001
 +-- evidence_002
 +-- evidence_003
```

Summary values must remain reproducible from the underlying Evidence where practical.

---

## 23. Evidence Summary

The aggregate should provide counts grouped by Evidence Type.

Example:

```text
Evidence Summary

ACCOUNT_VERIFICATION      1
PASSWORD_RESET            2
SECURITY_NOTIFICATION     3
SUBSCRIPTION              5
PAYMENT                  12
MARKETING                40
PASSWORD_MANAGER_ENTRY    1
```

This is a summary.

It does not assign relative strength.

---

## 24. Evidence Frequency Is Not Evidence Strength

The aggregator must preserve the distinction:

```text
COUNT
  !=
STRENGTH
```

For example:

```text
100 MARKETING
```

must not automatically outweigh:

```text
1 ACCOUNT_VERIFICATION
```

The aggregator reports frequency.

The Relationship Assessor determines semantic importance.

---

## 25. No Implicit Weighting

The aggregator must not calculate hidden formulas such as:

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

The aggregator must not produce arbitrary outputs such as:

```text
aggregate_confidence:
0.93
```

The aggregate is a structured representation of observed Evidence.

Confidence belongs, if introduced at all, to a later explicitly defined assessment model.

---

## 27. Source Summary

The aggregate should preserve which Connected Sources contributed Evidence.

Example:

```text
Connected Sources:

Personal Gmail
Primary Password Manager
Work Outlook
```

Conceptually, the summary may include:

```text
connected_source_count
source_type_count
provider_count
evidence_count_by_source
```

These values describe provenance diversity.

They do not independently determine Relationship strength.

---

## 28. Source Type Diversity

Example:

```text
EMAIL
PASSWORD_MANAGER
```

represents two structurally different source categories.

The aggregator may expose:

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

represents two Connected Sources.

However, both may belong to:

```text
SourceType:
EMAIL
```

Therefore the aggregate should distinguish:

```text
ConnectedSource diversity
```

from:

```text
SourceType diversity
```

---

## 30. Provider Diversity

Evidence may also originate from different providers.

Example:

```text
Google / Gmail
Microsoft / Outlook
Provider A / Password Manager
```

Provider diversity may be useful provenance.

However:

```text
provider diversity
       !=
independent semantic proof
```

The Relationship Assessor may eventually decide how much this matters.

---

## 31. Source Independence

The aggregator must not create different aggregate schemas for:

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
Evidence from Password -----+--> Evidence Aggregator
Manager                     |           |
                            |           v
Evidence from Browser ------+      Common Aggregate
```

Provider-specific details remain in Evidence and Observation provenance.

---

## 32. Temporal Summary

The aggregate should preserve temporal information derived from Evidence and supporting Observations.

Potential summary fields include:

```text
first_observed
last_observed
evidence_type_first_observed
evidence_type_last_observed
timeline
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

The aggregate may preserve both timestamps but must retain their temporal semantics.

---

## 34. First Observed

`first_observed` should mean:

> Earliest relevant temporal value available under explicitly defined aggregation semantics.

This definition must be used carefully.

It must not silently become:

```text
Account creation date
```

because the earliest observed Evidence may simply be:

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

It means only the latest relevant observation under the aggregation semantics.

For example:

```text
Password Manager Record Modified
```

may not represent actual Service use.

---

## 36. Evidence Timeline

The aggregate may expose a semantic Evidence timeline.

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

The Relationship Assessor may then reason about historical state.

The aggregator itself must not interpret this timeline as:

```text
account deleted but reopened
```

without sufficient Evidence.

---

## 37. Historical Evidence

Historical Evidence must remain included in aggregation.

For example:

```text
ACCOUNT_CREATION
ACCOUNT_VERIFICATION
ACCOUNT_DELETION
```

should not be discarded merely because:

```text
ACCOUNT_DELETION
```

appears later.

Historical Evidence remains part of the observed digital Relationship history.

---

## 38. Evidence Ordering

Evidence may be ordered temporally where source semantics support it.

However, an aggregator must not imply causal ordering merely because timestamps are ordered.

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

The aggregator must preserve the conflict.

It must not decide the explanation.

---

## 40. Conflict Summary

A future aggregate may expose:

```text
conflict_summary
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

The aggregator must not resolve conflicts by deleting or ignoring one Evidence item.

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

The aggregator must not blindly count every Evidence record as an independent semantic event.

---

## 43. Evidence Deduplication

The aggregator may require a concept of logical Evidence uniqueness.

Possible factors include:

```text
supporting Observation
Evidence Type
classifier version
semantic event identity
source reference
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

A future aggregate may represent:

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

may represent the same underlying transaction or two separate semantic observations.

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

The aggregator should not necessarily count this as two separate payment events.

Classification history and semantic Evidence count must remain distinguishable.

---

## 47. Current vs Superseded Evidence

If Evidence versioning is introduced, the aggregator may need to distinguish:

```text
CURRENT
SUPERSEDED
REJECTED
```

Evidence states.

For example:

```text
Classifier v1:
MARKETING

Classifier v2:
PRIVACY_NOTICE
```

Relationship Assessment should not necessarily consume both as simultaneous current interpretations.

The exact Evidence lifecycle remains an open Domain Model question.

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

the aggregate should reflect the current accepted Evidence semantics while preserving correction provenance.

The aggregator should not silently count both categories as independent semantic events if one supersedes the other.

---

## 49. Evidence Validity Filtering

Aggregation may require input Evidence state.

Conceptually:

```text
Evidence

- ACTIVE
- SUPERSEDED
- REJECTED
```

The Domain Model does not yet define these fields.

This contract therefore exposes a future requirement:

> Evidence lifecycle semantics may be necessary before production aggregation can be fully specified.

---

## 50. Evidence from Multiple Identities

One Service may be associated with Evidence involving multiple Identity Seeds.

Example:

```text
Spotify
 |
 +-- personal@gmail.com
 |
 +-- oldmail@example.net
```

The aggregate must retain both.

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

Some Evidence may not be safely linked to a known Identity Seed.

Example:

```text
Password Manager username:
old-address@example.com
```

where the address has not been confirmed as a User Identity Seed.

The aggregate may preserve:

```text
unassociated identity reference
```

rather than fabricating an Identity relationship.

---

## 52. Identity Completeness

An aggregate should not require every Evidence item to have an Identity reference.

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

Both may belong to the Service-level aggregate.

---

## 53. Aggregation Context

The aggregator may require explicitly versioned policy or rules.

Conceptually:

```text
AggregationContext

- deduplication_policy
- evidence_state_policy
- temporal_policy
- conflict_rules
- aggregation_version
```

This context must not contain provider credentials.

---

## 54. Deterministic Aggregation

Aggregation should be deterministic where practical.

Given the same:

```text
Evidence set
+
Aggregation Context
+
Aggregator Version
```

the same aggregate should be produced.

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
count Evidence Types
list Connected Sources
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

However, such reasoning should not automatically become part of the basic Evidence Aggregator.

A separate correlation or advanced reasoning capability may eventually be more appropriate.

Draft v0.1 keeps aggregation deterministic-first.

---

## 57. No Permission Escalation

The aggregator operates only on already available Evidence and provenance.

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

Individual Evidence remains unchanged unless separately reclassified.

---

## 61. Triggering Re-Aggregation

Re-aggregation may be required when:

```text
new Evidence arrives
Evidence is deleted
Evidence is reclassified
Service Resolution changes
User correction occurs
ConnectedSource data is removed
Identity association changes
deduplication logic changes
aggregation rules change
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

The Evidence should then become eligible for the Spotify aggregate.

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

their Evidence aggregates must be recalculable.

The aggregator should not store irreversible summary state that prevents reconstructing the combined Evidence context.

---

## 64. Service Split

Similarly, a Service split may require redistribution of Evidence based on preserved identifier and Observation provenance.

This reinforces:

```text
aggregate derived state
```

must remain reconstructable from:

```text
individual Evidence
```

---

## 65. Aggregation Persistence

An Evidence Aggregate may be:

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

The implementation should depend on scale and usage requirements.

---

## 66. Aggregate Identity

If persisted, an aggregate may require stable identity.

Potential conceptual identity:

```text
Aggregation Scope
+
Service Reference
+
Identity Scope
+
Aggregation Version
```

The exact identity model remains undefined.

---

## 67. Aggregate Is Derived State

An Evidence Aggregate must always be considered derived state.

Therefore:

```text
Evidence Aggregate
       |
       v
can be rebuilt
       |
       v
from authoritative Evidence inputs
```

where preserved Evidence remains available.

The aggregate must not become the sole source of semantic provenance.

---

## 68. Aggregate Deletion

Deleting a materialized aggregate should not delete underlying Evidence.

Conceptually:

```text
Delete Aggregate
     |
     v
Evidence remains
```

The aggregate can later be rebuilt.

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

The aggregate must then be recomputed from remaining Evidence.

Example:

```text
Before:

Spotify
 |
 +-- Gmail ACCOUNT_VERIFICATION
 +-- Gmail PAYMENT
 +-- Password Manager Entry

After Gmail evidence removal:

Spotify
 |
 +-- Password Manager Entry
```

The Relationship may still exist but require reassessment.

---

## 71. Partial Evidence Sets

Aggregation may sometimes operate over incomplete Evidence.

For example:

```text
ConnectedSource A:
complete

ConnectedSource B:
partial collection

ConnectedSource C:
temporarily unavailable
```

The aggregate should not claim:

```text
complete evidence footprint
```

merely because aggregation succeeded over available Evidence.

---

## 72. Coverage Metadata

A future Evidence Aggregate may need to expose coverage context.

Conceptually:

```text
coverage:

ConnectedSource A = COMPLETE
ConnectedSource B = PARTIAL
ConnectedSource C = FAILED
```

However, collection completeness originates upstream.

The aggregator may summarize it when relevant but must not invent it.

---

## 73. Aggregate Completeness

The framework cannot normally know:

```text
All Evidence that could possibly exist
```

because Discovery itself is incomplete.

Therefore an aggregate should not claim absolute completeness.

At most it can describe completeness relative to:

```text
configured Connected Sources
and
completed collection runs
```

---

## 74. Cross-Source Example

Input Evidence:

```text
Evidence 1
Type:
ACCOUNT_VERIFICATION
Source:
Personal Gmail

Evidence 2
Type:
SUBSCRIPTION
Source:
Personal Gmail

Evidence 3
Type:
PAYMENT
Source:
Personal Gmail

Evidence 4
Type:
PASSWORD_MANAGER_ENTRY
Source:
Primary Password Manager
```

All resolve to:

```text
Spotify
```

Possible aggregate:

```text
Service:
Spotify

Evidence Summary:
ACCOUNT_VERIFICATION      1
SUBSCRIPTION              1
PAYMENT                   1
PASSWORD_MANAGER_ENTRY    1

Connected Sources:
2

Source Types:
EMAIL
PASSWORD_MANAGER

Identity References:
personal@example.com
```

The aggregate still does not say:

```text
Relationship = CONFIRMED
```

---

## 75. Single-Source High-Volume Example

Input:

```text
Spotify

Gmail:
150 MARKETING
```

Aggregate:

```text
Evidence Summary:
MARKETING 150

Connected Sources:
1

Source Types:
EMAIL
```

The aggregator must not transform this into:

```text
strong Relationship
```

simply because the Evidence count is high.

---

## 76. Multi-Source Low-Volume Example

Input:

```text
Spotify

Gmail:
1 ACCOUNT_VERIFICATION

Password Manager:
1 PASSWORD_MANAGER_ENTRY
```

Aggregate:

```text
Evidence Summary:
ACCOUNT_VERIFICATION      1
PASSWORD_MANAGER_ENTRY    1

Connected Sources:
2

Source Types:
EMAIL
PASSWORD_MANAGER
```

The Relationship Assessor may later consider this differently from 150 marketing emails.

The aggregator itself does not assign that meaning.

---

## 77. Historical Example

Input:

```text
2021 ACCOUNT_CREATION
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

Aggregate:

```text
Evidence Types:
ACCOUNT_CREATION
ACCOUNT_VERIFICATION
PAYMENT
ACCOUNT_DELETION

First Observed:
2021

Last Relevant Evidence:
2024

Timeline:
preserved
```

The aggregator does not conclude:

```text
HISTORICAL
```

although it provides the information needed for the Relationship Assessor to consider that state.

---

## 78. Conflicting Example

Input:

```text
2024 ACCOUNT_DELETION
2026 AUTHENTICATION
```

Aggregate:

```text
Evidence Summary:
ACCOUNT_DELETION 1
AUTHENTICATION   1

Conflict:
potential temporal-semantic inconsistency
```

The aggregator does not decide whether:

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
Identity:
personal@example.com

Evidence 2:
PASSWORD_MANAGER_ENTRY
Identity:
oldmail@example.net
```

Aggregate:

```text
Service:
Spotify

Identity References:
- personal@example.com
- oldmail@example.net

Evidence Summary:
PASSWORD_MANAGER_ENTRY 2
```

The aggregator must not infer:

```text
Two Spotify Accounts
```

because `Account` is not yet a core Domain Entity.

---

## 80. Unresolved Example

Input:

```text
Evidence:
PAYMENT

Candidate Identifier:
unknownservice.example

Resolution:
UNRESOLVED
```

Possible aggregate:

```text
Scope:
UNRESOLVED_SERVICE_CANDIDATE

Identifier:
unknownservice.example

Evidence Summary:
PAYMENT 1
```

Later re-resolution may move this Evidence into a canonical Service aggregate.

---

## 81. Ambiguous Example

Input:

```text
Evidence:
SUBSCRIPTION

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

rather than being counted in both Service aggregates as if both were true.

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

An empty aggregate is a domain condition.

A failed aggregate is a technical condition.

---

## 83. Unsupported Evidence Version

If the aggregator receives an Evidence format it cannot understand:

```text
processing_status:
UNSUPPORTED
```

should be possible.

The framework must not silently ignore unsupported Evidence and present the remaining aggregate as complete.

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

Each Service must still receive an independently traceable aggregate.

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

However, incremental updates must produce the same logical result as rebuilding the aggregate from authoritative Evidence under the same Aggregator version and policy.

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

under the same rules, the implementation contains an aggregation consistency problem.

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

---

## 90. Aggregation Result Contract

Conceptually:

```text
AggregationResult {

    ProcessingStatus processingStatus

    Optional<AggregationStatus> aggregationStatus

    AggregationScope scope

    Optional<ServiceReference> serviceReference

    List<IdentityReference> identityReferences

    List<EvidenceReference> evidenceReferences

    EvidenceSummary evidenceSummary

    SourceSummary sourceSummary

    TemporalSummary temporalSummary

    ConflictSummary conflictSummary

    AggregatorVersion aggregatorVersion
}
```

---

## 91. Evidence Summary Contract

Conceptually:

```text
EvidenceSummary {

    totalEvidenceCount

    evidenceCountByType

    currentEvidenceTypes

    historicalEvidenceTypes
}
```

The distinction between current and historical Evidence remains dependent on future Evidence lifecycle semantics.

Therefore these fields are illustrative.

---

## 92. Source Summary Contract

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

## 93. Temporal Summary Contract

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

---

## 94. Conflict Summary Contract

Conceptually:

```text
ConflictSummary {

    hasPotentialConflicts

    conflictTypes

    involvedEvidenceReferences
}
```

The final conflict taxonomy remains open.

---

## 95. Evidence Aggregator Invariants

### EA-INV-001

The aggregator must operate on framework Evidence rather than raw provider objects.

---

### EA-INV-002

Aggregation must not destructively replace individual Evidence.

---

### EA-INV-003

Every aggregate must remain traceable to its contributing Evidence.

---

### EA-INV-004

Evidence frequency must not be interpreted as Evidence strength.

---

### EA-INV-005

The aggregator must not assign final Relationship state.

---

### EA-INV-006

The aggregator must not assign arbitrary numerical Relationship Confidence.

---

### EA-INV-007

Evidence from multiple Connected Sources may contribute to one Service aggregate.

---

### EA-INV-008

Evidence from multiple SourceTypes may contribute to one Service aggregate.

---

### EA-INV-009

Provider identity must not create separate canonical Service aggregates.

---

### EA-INV-010

Identity references must not be discarded during Service-level aggregation.

---

### EA-INV-011

Multiple Identity references must not automatically imply multiple Accounts.

---

### EA-INV-012

Evidence without a known Identity reference may still participate in Service-level aggregation.

---

### EA-INV-013

Unresolved-Service Evidence must not be discarded.

---

### EA-INV-014

Ambiguous-Service Evidence must not be arbitrarily assigned to one Service.

---

### EA-INV-015

Ambiguous Evidence must not be duplicated across all possible Services as if each resolution were true.

---

### EA-INV-016

Technical duplicate Evidence must not artificially increase semantic Evidence frequency.

---

### EA-INV-017

Similar Evidence from independent sources must not automatically be treated as duplicates.

---

### EA-INV-018

Conflicting Evidence must remain preserved.

---

### EA-INV-019

The aggregator must not resolve Evidence conflicts by silently deleting one side.

---

### EA-INV-020

Temporal aggregation must preserve source-specific temporal semantics.

---

### EA-INV-021

`first_observed` must not automatically be interpreted as account creation.

---

### EA-INV-022

`last_observed` must not automatically be interpreted as last Service usage.

---

### EA-INV-023

Historical Evidence must not be discarded merely because later Evidence exists.

---

### EA-INV-024

The aggregator must not request additional source permissions.

---

### EA-INV-025

Provider credentials must not be required by the aggregator.

---

### EA-INV-026

Basic aggregation must not require AI.

---

### EA-INV-027

Re-aggregation must not require source retrieval when preserved Evidence is sufficient.

---

### EA-INV-028

Service merge or split operations must remain compatible with rebuilding aggregates from underlying Evidence.

---

### EA-INV-029

Deleting a materialized aggregate must not delete underlying Evidence.

---

### EA-INV-030

Deleting or invalidating underlying Evidence must trigger eventual aggregate reassessment where affected.

---

### EA-INV-031

Processing failure must remain distinguishable from an empty Evidence aggregate.

---

### EA-INV-032

An aggregate must not claim perfect completeness of the User's real-world Evidence footprint.

---

### EA-INV-033

Aggregation should be deterministic for the same Evidence set, context and Aggregator version where practical.

---

### EA-INV-034

Incremental aggregation and full rebuild should produce logically equivalent results under the same rules where practical.

---

## 96. Complete Gmail + Password Manager Example

Suppose Service Resolution has produced:

```text
Service:
Spotify
```

Evidence Classification has produced:

```text
Evidence 001
Type:
ACCOUNT_VERIFICATION

Connected Source:
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

Connected Source:
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

Connected Source:
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

Connected Source:
Primary Password Manager

Identity:
personal@example.com

Temporal Semantics:
SOURCE_RECORD_MODIFIED

Observed:
2025-08-20
```

The aggregator may produce:

```text
Service:
Spotify

Evidence Count:
4

Evidence Summary:
ACCOUNT_VERIFICATION       1
SUBSCRIPTION               1
PAYMENT                    1
PASSWORD_MANAGER_ENTRY     1

Identity References:
personal@example.com

ConnectedSource Count:
2

Source Types:
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
Relationship:
CONFIRMED
```

or:

```text
Account Active:
true
```

Those interpretations belong downstream.

---

## 97. Open Questions

### Aggregation Scope

- Is Service the correct primary aggregation boundary?
- Should Identity-level aggregates exist separately?
- Should User-level and Identity-level aggregates coexist?
- How should unresolved Service candidates be grouped?

### Evidence Lifecycle

- Does Evidence require states such as `ACTIVE`, `SUPERSEDED`, `REJECTED`?
- How should reclassified Evidence be represented?
- Which Evidence versions participate in current aggregation?
- Should User-corrected Evidence supersede automated Evidence?

### Deduplication

- What defines one logical Evidence event?
- Should duplicate Observations be removed before Evidence Classification?
- Should the aggregator own semantic deduplication?
- How should source imports and migrations be handled?

### Temporal Model

- Is one `first_observed` and `last_observed` value sufficiently precise?
- Should temporal values always retain typed semantics?
- Should an aggregate expose multiple temporal dimensions?
- How should missing or uncertain timestamps be represented?

### Conflicts

- Which Evidence combinations qualify as conflicts?
- Is `ACCOUNT_DELETION` followed by `AUTHENTICATION` always a conflict?
- Should the aggregator only expose raw chronology and leave all conflict interpretation downstream?
- Is a dedicated conflict detector eventually necessary?

### Source Diversity

- Should source diversity be represented only descriptively?
- Or will Relationship Assessment eventually use it explicitly?
- How should multiple connected email accounts compare with different SourceTypes?

### Identity

- Should aggregation be primarily per `Service + IdentitySeed` instead of Service?
- How should unverified observed identities participate?
- How should aliases affect grouping?

### Account

- Does aggregation provide enough evidence to finally justify introducing `Account`?
- Could multiple Identity-specific Evidence clusters reveal separate accounts?
- Should that remain a downstream inference rather than aggregation responsibility?

### Service Resolution

- What happens when Entity Resolution changes after aggregation?
- How is Evidence moved between aggregates?
- How are ambiguous candidates represented efficiently?

### Persistence

- Should aggregates be materialized?
- How are they invalidated?
- Should they be rebuilt on demand?
- What scale would justify incremental materialization?

### Completeness

- How should ConnectedSource collection completeness be reflected?
- Should Relationship Assessment receive coverage information directly?
- Can Evidence Aggregate completeness ever be meaningfully defined?

### AI

- Is there any justified use of AI in basic aggregation?
- Should semantic correlation become a separate future component instead?

---

## 98. Findings from Contract Design

### Finding 1 - Aggregates Are Derived State

An Evidence Aggregate is not authoritative source information.

It must remain reconstructable from individual Evidence.

This strongly argues against making aggregate summaries the only persisted representation.

---

### Finding 2 - Service Is the Primary Aggregation Boundary, but Identity Must Be Preserved

The current domain is Service-oriented:

```text
Which Services appear connected to me?
```

Therefore Service is the natural primary grouping boundary.

However, Identity references must remain inside the aggregate because future Relationship or Account semantics may depend on them.

---

### Finding 3 - Unresolved Evidence Requires an Aggregation Path

Evidence semantics may be known before Service identity is resolved.

The system therefore needs an unresolved aggregation context rather than discarding such Evidence.

---

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

The aggregate should describe both dimensions independently.

It must not decide which is stronger.

---

### Finding 5 - Evidence Lifecycle Is Becoming Necessary

Reclassification and User correction raise the question of which Evidence represents the currently accepted interpretation.

The Domain Model currently does not define Evidence lifecycle states.

This issue may need to be resolved before persistence is finalized.

---

### Finding 6 - Account Remains a Candidate Concept

Identity-aware aggregation again exposes cases such as:

```text
Spotify

personal@example.com
oldmail@example.net
```

but still does not prove that two separate Accounts exist.

The `Account` abstraction should therefore remain a candidate for now.

---

### Finding 7 - Basic Aggregation Does Not Need AI

Grouping, counting, provenance preservation, source diversity and temporal summarization are deterministic operations.

Any future semantic correlation requiring richer reasoning should be justified separately rather than inserted into the base aggregator.

---

## 99. Decision Candidates

### Candidate Decision - Aggregate Is Derived State

```text
Evidence Aggregates should be treated as derived state based on individual
Evidence and must remain reconstructable where the underlying Evidence is
retained.
```

---

### Candidate Decision - Service-Level Aggregation with Identity Preservation

```text
Service should be the primary Evidence aggregation boundary for Service
Discovery, while Identity references associated with individual Evidence
must remain preserved.
```

---

### Candidate Decision - Evidence Frequency Is Descriptive

```text
Evidence frequency should be represented descriptively and must not
automatically determine Relationship strength.
```

---

### Candidate Decision - Preserve Source Diversity

```text
Evidence Aggregation should preserve ConnectedSource, SourceType and relevant
provider provenance so Relationship Assessment can distinguish repeated
Evidence from independent source support.
```

---

### Candidate Decision - Preserve Unresolved Evidence

```text
Evidence associated with unresolved or ambiguous Service candidates must not
be discarded solely because canonical Entity Resolution is incomplete.
```

---

### Candidate Decision - Aggregator Does Not Assess Relationship

```text
The Evidence Aggregator must structure Evidence for Relationship Assessment
but must not assign the final Relationship state or arbitrary numerical
Relationship Confidence.
```

---

### Candidate Decision - Deterministic Aggregation

```text
Basic Evidence aggregation should remain deterministic and local-first where
technically practical.

AI should not be a required dependency for grouping, counting, provenance
preservation or temporal summarization.
```

---

## 100. Current Contract Baseline

The initial Evidence Aggregator contract is:

```text
Evidence
Evidence
Evidence
    |
    v
AggregationRequest
    |
    v
EvidenceAggregator
    |
    v
AggregationResult
    |
    +-- processing_status
    |
    +-- aggregation_status
    |
    +-- aggregation_scope
    |
    +-- service_reference
    |
    +-- identity_references
    |
    +-- evidence_references
    |
    +-- evidence_summary
    |
    +-- source_summary
    |
    +-- temporal_summary
    |
    +-- conflict_summary
    |
    +-- aggregator_version
```

with the guarantees:

```text
individual Evidence preserved
Service-oriented aggregation
Identity provenance preserved
cross-source Evidence supported
source diversity preserved
Evidence frequency represented descriptively
temporal semantics preserved
conflicting Evidence retained
unresolved Evidence retained
ambiguous Evidence not arbitrarily assigned
no Relationship conclusion
no arbitrary Confidence
deterministic-first operation
no provider credentials
no permission escalation
re-aggregation supported
derived-state semantics
```

---

## 101. Next Interface Contract

The Discovery pipeline now has contracts for:

```text
                         Observation
                         /         \
                        /           \
                       v             v
        ServiceCandidateDetector   EvidenceClassifier
                       |             |
                       v             v
            CandidateIdentifier    Evidence
                       |
                       v
                 EntityResolver
                       |
                       v
                    Service
                       \             /
                        \           /
                         v         v
                    EvidenceAggregator
                            |
                            v
                     Evidence Aggregate
                            |
                            v
                   RelationshipAssessor
```

The next interface contract should define:

```text
RelationshipAssessor
```

Its responsibility is:

> Given an Evidence Aggregate, what can the framework justifiably conclude about the current or historical Relationship between the User or Identity and the Service?

The contract should establish:

- Relationship state;
- current vs historical Relationships;
- active vs unknown state;
- evidence sufficiency;
- conflicting Evidence;
- source diversity;
- temporal reasoning;
- account-related Evidence vs weaker communication Evidence;
- User-confirmed Relationships;
- Relationship explainability;
- reassessment after Evidence changes;
- whether Confidence is necessary at all;
- how `UNKNOWN`, `POSSIBLE`, `PROBABLE`, `CONFIRMED`, `HISTORICAL` and `REJECTED` should be treated;
- whether the model should distinguish existence of a Relationship from current status.

The Relationship Assessor must still avoid claiming what personal data the Service currently holds.
