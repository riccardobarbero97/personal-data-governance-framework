# Relationship Assessor Contract

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
- `docs/interfaces/06-evidence-aggregator-contract.md`

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `RelationshipAssessor` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Relationship Assessor evaluates an `EvidenceAggregate` and determines what the framework can justifiably conclude about a possible current or historical Relationship between the User or one or more Identity Seeds and a Service.

Conceptually:

```text
Evidence Aggregate
        |
        v
Relationship Assessor
        |
        v
Relationship Assessment
```

The Relationship Assessor answers:

> Given the currently available Evidence, what can the framework reasonably say about the observed Relationship with this Service?

Its responsibility is to interpret aggregated Evidence.

It does not determine:

- which Service an identifier represents;
- what an individual Observation means;
- how raw source information is collected;
- which personal data the Service currently holds;
- whether externally stored personal data has been deleted;
- what governance action should be performed.

---

## 2. Architectural Position

The Relationship Assessor is the final semantic stage of Identity and Service Discovery before information is represented in the Service Graph.

Conceptually:

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
                 RELATIONSHIP ASSESSOR
                            |
                            v
                 Relationship Assessment
                            |
                            v
                       Service Graph
```

---

## 3. Fundamental Boundary

The central distinction is:

```text
EVIDENCE != RELATIONSHIP
```

Evidence represents supporting information.

A Relationship represents an assessment derived from the accumulated Evidence.

For example:

```text
ACCOUNT_VERIFICATION
PASSWORD_MANAGER_ENTRY
PAYMENT
SUBSCRIPTION
```

may together support a stronger Relationship conclusion than:

```text
MARKETING
NEWSLETTER
```

The Relationship Assessor interprets that difference.

---

## 4. Relationship Is Not Current Data Possession

Even a strongly supported Relationship must not be interpreted as proof that the Service currently holds specific personal data.

Therefore:

```text
RELATIONSHIP
        !=
CURRENT DATA POSSESSION
```

For example:

```text
Relationship:
historically established
```

does not mean:

```text
Service currently stores:
name
email
phone number
payment information
```

Those questions belong to subsequent Personal Data Acquisition and Understanding capabilities.

---

## 5. Relationship Is Not Necessarily an Account

The framework discovers digital Relationships, not only accounts.

A Service Relationship may arise through:

```text
account
subscription
purchase
guest transaction
newsletter
mailing list
historical account
OAuth relationship
other digital interaction
```

Therefore:

```text
RELATIONSHIP != ACCOUNT
```

This is important because `Account` remains a candidate Domain Concept rather than a mandatory part of the Discovery Domain.

---

## 6. Input Contract

The Relationship Assessor receives an `EvidenceAggregate`.

Conceptually:

```text
assess(
    evidence_aggregate,
    context
)
    ->
RelationshipAssessmentResult
```

The assessor should not require direct access to:

- external providers;
- Connector credentials;
- raw provider objects;
- unrelated Observations;
- unrestricted source data.

It should reason primarily over structured Evidence and its preserved provenance.

---

## 7. Assessment Context

The assessor may require explicit supporting context.

Conceptually:

```text
RelationshipAssessmentContext

- assessment_policy
- relationship_state_model
- evidence_semantics
- temporal_policy
- conflict_policy
- user_corrections
```

The exact structure remains open.

The context must not hide arbitrary weighting or undocumented inference rules.

---

## 8. Assessment Result

The result must be structured and explainable.

Conceptually:

```text
RelationshipAssessmentResult

- processing_status
- relationship_status
- temporal_status
- evidence_basis
- identity_references
- service_reference
- reason_codes
- warnings
- assessor_version
```

This remains implementation-independent.

---

## 9. Processing Status

Technical processing state must remain separate from Relationship state.

Potential processing states include:

```text
SUCCESS
UNSUPPORTED
FAILED
```

For example:

```text
processing_status:
SUCCESS

relationship_status:
UNKNOWN
```

means:

> The assessor successfully evaluated the available Evidence but could not justify a stronger Relationship conclusion.

This is different from:

```text
processing_status:
FAILED
```

---

# 10. Relationship Status

Earlier architecture drafts considered states such as:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
REJECTED
```

However, these states mix different semantic dimensions.

In particular:

```text
CONFIRMED
```

describes support strength,

while:

```text
HISTORICAL
```

describes time.

These should not necessarily exist in one flat enumeration.

Draft v0.1 therefore separates:

```text
Relationship Status
```

from:

```text
Temporal Status
```

---

## 11. Relationship Status Model

The initial conceptual Relationship Status model is:

```text
UNKNOWN

OBSERVED

ESTABLISHED

REJECTED
```

These names are provisional but intentionally avoid numerical pseudo-precision.

---

## 12. UNKNOWN

`UNKNOWN` means that available Evidence is insufficient to justify that a meaningful Relationship existed.

Example:

```text
Evidence:
one ambiguous marketing Observation
```

may remain:

```text
UNKNOWN
```

This does not mean:

```text
Relationship does not exist.
```

It means only:

```text
Current Evidence does not justify a stronger conclusion.
```

---

## 13. OBSERVED

`OBSERVED` means that the framework has Evidence of interaction or communication involving the Service but cannot justify a stronger Relationship conclusion.

Examples may include:

```text
MARKETING

NEWSLETTER

PRIVACY_NOTICE

browser visit
```

depending on future Evidence semantics.

Conceptually:

```text
Evidence exists
      |
      v
Service interaction observed
      |
      v
OBSERVED
```

This state deliberately avoids claiming that an account exists.

---

## 14. ESTABLISHED

`ESTABLISHED` means that available Evidence provides a justified basis for concluding that a meaningful Relationship existed.

Possible supporting Evidence may eventually include combinations such as:

```text
ACCOUNT_VERIFICATION

PASSWORD_MANAGER_ENTRY

SUBSCRIPTION

AUTHENTICATION

PAYMENT
```

However, Draft v0.1 does not define an automatic rule such as:

```text
ACCOUNT_VERIFICATION = ESTABLISHED
```

or:

```text
two strong Evidence items = ESTABLISHED
```

These semantics require empirical validation.

---

## 15. REJECTED

`REJECTED` represents an explicit conclusion that an apparent Relationship should not currently be treated as belonging to the User.

Examples might include:

```text
User explicitly states:
"This was not my account."

Verified misattribution

Observation known to belong to another person
```

`REJECTED` should not normally be inferred merely from weak Evidence.

Explicit rejection requires strong justification and provenance.

---

# 16. Why POSSIBLE and PROBABLE Are Not in the Initial Model

Earlier conceptual models considered:

```text
POSSIBLE
PROBABLE
```

These terms appear intuitive but create an implicit probability scale.

Without calibration:

```text
possible
```

versus:

```text
probable
```

has no precise, testable framework meaning.

Draft v0.1 therefore prefers semantically defined states:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

until empirical testing demonstrates the need for intermediate confidence-like states.

---

# 17. Temporal Status

Relationship strength and temporal interpretation should remain separate.

The initial conceptual `TemporalStatus` is:

```text
UNKNOWN

CURRENTLY_OBSERVED

HISTORICAL
```

These values remain provisional.

---

## 18. UNKNOWN Temporal Status

`UNKNOWN` means that the framework cannot safely determine whether the Relationship should be considered current or historical.

This may be common.

For example:

```text
PASSWORD_MANAGER_ENTRY
```

alone does not prove whether the account:

- still exists;
- still works;
- is still used;
- was deleted.

Therefore:

```text
relationship_status:
ESTABLISHED

temporal_status:
UNKNOWN
```

may be valid.

---

## 19. CURRENTLY_OBSERVED

`CURRENTLY_OBSERVED` means that sufficiently recent Evidence exists indicating ongoing observable interaction.

This must not be interpreted as:

```text
ACTIVE ACCOUNT CONFIRMED
```

For example:

```text
recent SECURITY_NOTIFICATION
```

may support ongoing observable interaction.

But:

```text
current observation
```

and:

```text
account active
```

are not always equivalent.

---

## 20. HISTORICAL

`HISTORICAL` means available Evidence supports that the Relationship existed in the past but current continuation is not established or Evidence suggests the Relationship ended.

Example:

```text
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

may support:

```text
relationship_status:
ESTABLISHED

temporal_status:
HISTORICAL
```

However, the exact temporal rules remain to be validated.

---

# 21. Status Dimensions

Separating Relationship and temporal semantics allows states such as:

```text
ESTABLISHED + HISTORICAL
```

or:

```text
ESTABLISHED + UNKNOWN
```

or:

```text
OBSERVED + CURRENTLY_OBSERVED
```

instead of forcing everything into one flat state list.

This is more expressive than:

```text
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
```

where semantic dimensions overlap.

---

# 22. Evidence Sufficiency

The Relationship Assessor must determine whether available Evidence is sufficient for a given Relationship state.

However, Draft v0.1 does not define arbitrary weights.

For example, it must not initially use:

```text
ACCOUNT_VERIFICATION = 0.8

PASSWORD_MANAGER_ENTRY = 0.9

MARKETING = 0.1
```

The first implementation should prefer explicit Evidence-semantics rules.

---

# 23. Evidence Type Matters

Evidence frequency alone is insufficient.

For example:

```text
100 MARKETING
```

may represent a different Relationship basis from:

```text
1 ACCOUNT_VERIFICATION
+
1 PASSWORD_MANAGER_ENTRY
```

The assessor must therefore reason about:

```text
Evidence Type
```

and not only:

```text
Evidence Count
```

---

# 24. Evidence Frequency Still Matters

Although frequency does not determine Relationship strength automatically, it may still provide useful context.

For example:

```text
one marketing message
```

and:

```text
recurring marketing communication over six years
```

describe different observed communication patterns.

Frequency may therefore contribute context without becoming a hidden score.

---

# 25. Source Diversity

Evidence from multiple structurally different sources may provide stronger justification than repeated Evidence from one source.

Example:

```text
Gmail:
ACCOUNT_VERIFICATION

Password Manager:
PASSWORD_MANAGER_ENTRY
```

represents independent source support.

The assessor may eventually consider:

```text
SourceType diversity
```

as part of its reasoning.

However:

```text
multiple SourceTypes
        !=
automatic ESTABLISHED
```

The semantic Evidence still matters.

---

# 26. ConnectedSource Diversity

Evidence may come from multiple Connected Sources of the same type.

Example:

```text
Personal Gmail
Old Gmail
```

The assessor should preserve that distinction.

However, two email accounts are not necessarily equivalent to two structurally independent source categories.

Therefore:

```text
ConnectedSource diversity
        !=
SourceType diversity
```

---

# 27. Provider Diversity

Evidence from:

```text
Gmail
Outlook
```

comes from different providers but may still represent the same type of source:

```text
EMAIL
```

Provider diversity may provide provenance context but should not automatically be treated as independent semantic validation.

---

# 28. Independent Evidence

The framework should eventually distinguish:

```text
multiple messages generated by one event
```

from:

```text
independent Evidence produced through unrelated mechanisms
```

For example:

```text
registration email
+
password-manager credential
```

may be more independent than:

```text
registration email
+
welcome email
```

However, defining Evidence independence precisely requires empirical work.

Draft v0.1 therefore preserves source and Evidence provenance rather than introducing an independence score.

---

# 29. Current vs Historical Reasoning

Relationship Assessment must consider temporal Evidence.

Example A:

```text
2021 ACCOUNT_CREATION
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

Example B:

```text
2021 ACCOUNT_CREATION
2022 PAYMENT
2025 PASSWORD_RESET
2026 SECURITY_NOTIFICATION
```

These Evidence timelines should not produce identical temporal assessments.

---

# 30. Account Deletion Evidence

`ACCOUNT_DELETION` is relevant to temporal status.

However, it does not prove:

```text
all data deleted
```

nor necessarily:

```text
Relationship permanently ended
```

A later:

```text
AUTHENTICATION
```

or:

```text
PASSWORD_RESET
```

may conflict with the apparent deletion state.

The assessor must preserve such uncertainty.

---

# 31. Deletion Followed by Later Activity

Consider:

```text
2024 ACCOUNT_DELETION

2026 AUTHENTICATION
```

Possible explanations include:

- account recreated;
- deletion request failed;
- different account;
- Evidence misclassification;
- source timestamps have different semantics.

The assessor should not invent one explanation.

Possible result:

```text
relationship_status:
ESTABLISHED

temporal_status:
UNKNOWN

warnings:
CONFLICTING_TEMPORAL_EVIDENCE
```

---

# 32. Historical Does Not Mean Irrelevant

A historical Relationship remains relevant to the Personal Data Governance Framework.

For example, a historical Service may still:

- retain transaction history;
- retain data under legal obligations;
- retain backups;
- hold residual account information;
- appear in later personal-data acquisition.

Therefore:

```text
HISTORICAL
       !=
REMOVE FROM SERVICE GRAPH
```

---

# 33. Current Relationship Does Not Mean Account

Recent Evidence may support:

```text
CURRENTLY_OBSERVED
```

without proving:

```text
active account
```

Example:

```text
recent newsletter
```

shows continued communication but not necessarily account activity.

Relationship status and Evidence semantics must remain combined carefully.

---

# 34. Relationship and Identity

The Domain Model currently allows Evidence to reference one or more Identity Seeds.

The Relationship Assessor should preserve Identity-specific conclusions where supported.

Example:

```text
Spotify

Evidence:
ACCOUNT_VERIFICATION

Identity:
personal@example.com
```

may support a Relationship associated with that Identity.

---

# 35. Multiple Identities

Evidence may involve:

```text
personal@example.com

oldmail@example.net
```

for the same Service.

The assessor must not automatically conclude:

```text
two Accounts
```

or:

```text
one Account
```

It may instead preserve:

```text
Relationship with Service
supported through multiple Identity references
```

until `Account` becomes formally modeled.

---

# 36. Unknown Identity

Some Evidence may support a Service Relationship without a verified Identity Seed.

For example, a password-manager entry may expose an unconfirmed historical username.

The assessor may still reason at:

```text
User <-> Service
```

level while preserving:

```text
Identity association:
UNKNOWN
```

The exact Relationship cardinality remains an open Domain question.

---

# 37. User-Level Relationship

The framework's ultimate user-facing question is:

> Which Services appear to have or have had a Relationship with me?

Therefore a User-level Relationship view is necessary.

Conceptually:

```text
User
  |
  v
Relationship
  |
  v
Service
```

Identity-level details can remain supporting context.

---

# 38. Identity-Level Relationship

Some scenarios also require:

```text
IdentitySeed
     |
     v
Relationship
     |
     v
Service
```

For example:

```text
Which Services were associated with oldmail@example.net?
```

The architecture may therefore eventually require both:

```text
User-Service Relationship
```

and:

```text
Identity-Service Association
```

rather than forcing one entity to perform both roles.

Draft v0.1 does not finalize this model.

---

# 39. Account Remains a Candidate Concept

Repeated contract design has exposed cases such as:

```text
Service:
Spotify

Identity:
personal@example.com

Identity:
oldmail@example.net
```

An `Account` concept could eventually explain these structures.

However, the Relationship Assessor still does not require `Account` to function.

Therefore:

```text
Account = CANDIDATE DOMAIN CONCEPT
```

remains appropriate.

---

# 40. Relationship Assessment Rules

The assessor should use explicit rules or policy where practical.

Conceptually:

```text
Evidence Aggregate
      |
      v
Assessment Policy
      |
      v
Relationship Assessment
```

Rules should be:

- explicit;
- versionable;
- testable;
- explainable.

The framework should not hide Relationship semantics inside opaque application code.

---

# 41. No Arbitrary Scoring

Draft v0.1 does not use:

```text
relationship_score = 0.91
```

or formulas such as:

```text
0.8 * account_verification
+
0.5 * payment
+
0.2 * marketing
```

without defined calibration.

Such a model would imply mathematical meaning that has not yet been established.

---

# 42. Confidence Is Not Required Yet

A Relationship already has several explainable dimensions:

```text
Relationship Status
Temporal Status
Evidence Types
Source Types
Connected Sources
Timeline
Conflicts
Reason Codes
```

These may provide more useful information than a single numeric Confidence score.

Draft v0.1 therefore does not require Confidence.

---

# 43. Possible Future Confidence

A calibrated Confidence model may still become useful in the future.

For example, after measuring:

- true positives;
- false positives;
- false negatives;
- source reliability;
- Evidence combinations;
- User corrections.

If introduced, Confidence must have explicit semantics.

It must not simply restate the Relationship Status numerically.

---

# 44. User Confirmation

The User may explicitly confirm a Relationship.

Example:

```text
Framework:
OBSERVED

User:
Yes, I have a Spotify account.
```

This may provide a strong manual signal.

However, the framework should preserve:

```text
User Confirmation
```

as provenance.

It should not rewrite historical Evidence to make it appear as though automated Discovery independently established the Relationship.

---

# 45. User Rejection

Similarly:

```text
Framework:
ESTABLISHED

User:
This account belonged to someone else.
```

may cause the current Relationship to become:

```text
REJECTED
```

depending on future correction policy.

The original automated assessment should remain auditable.

---

# 46. Manual Relationships

A User may manually declare:

```text
I had an account with Example Service in 2018.
```

This can eventually create manual Evidence and feed the same Relationship Assessor.

Manual declarations should not require a completely separate Relationship model.

---

# 47. Relationship Assessment Provenance

Every assessment must remain traceable to:

```text
Evidence Aggregate
       |
       v
Assessment Policy
       |
       v
Assessor Version
       |
       v
Relationship Assessment
```

At minimum, the framework should eventually be able to answer:

> Why is this Relationship currently classified this way?

---

# 48. Reason Codes

Relationship Assessment should expose structured reason codes.

Potential examples include:

```text
ACCOUNT_RELATED_EVIDENCE

MULTI_SOURCE_SUPPORT

COMMUNICATION_ONLY

MARKETING_ONLY

USER_CONFIRMED

USER_REJECTED

HISTORICAL_DELETION_EVIDENCE

RECENT_ACTIVITY_EVIDENCE

CONFLICTING_TEMPORAL_EVIDENCE

INSUFFICIENT_EVIDENCE
```

These are illustrative.

The final taxonomy should emerge from actual assessment rules.

---

# 49. Human-Readable Explanation

In addition to machine-readable reasons, the framework should eventually produce concise explanations.

Example:

```text
This Relationship is considered ESTABLISHED because:

- an account-verification event was observed;
- a password-manager entry was independently associated with the same Service;
- both sources reference the same User identity.
```

Or:

```text
This Relationship is OBSERVED rather than ESTABLISHED because the available
Evidence consists only of marketing and newsletter communication.
```

The explanation must remain derivable from structured Evidence and rules.

---

# 50. Explainability Without Exposing Raw Data

The framework should not need to expose complete raw source content to justify a Relationship.

For example:

```text
ACCOUNT_VERIFICATION observed on 2024-05-01
```

may be sufficient for an explanation.

This supports privacy by minimizing unnecessary display or transmission of source data.

---

# 51. Assessment Method

Potential assessment methods include:

```text
RULE
MANUAL
COMPOSITE
AI
```

Draft v0.1 expects basic Relationship Assessment to remain primarily:

```text
RULE
```

because it operates on already structured Evidence.

---

# 52. AI Boundary

Basic Relationship Assessment should not require AI.

Once Evidence has been normalized into structured categories, operations such as:

```text
inspect Evidence Types
inspect timeline
inspect source diversity
inspect conflicts
apply assessment policy
```

are deterministic.

An LLM should not be required simply to decide:

```text
ACCOUNT_VERIFICATION
+
PASSWORD_MANAGER_ENTRY
```

has different semantics from:

```text
MARKETING
```

---

# 53. AI for Complex Reasoning

Future Evidence structures may become substantially more complex.

AI might eventually provide value for:

- interpreting complex conflicts;
- explaining unusual Evidence combinations;
- assisting User-facing explanations;
- proposing reassessment hypotheses.

However, AI should not silently replace the explicit Relationship state model.

---

# 54. AI Must Not Invent Missing Evidence

If the aggregate contains:

```text
MARKETING
```

the assessor must not use AI to infer:

```text
probably an account exists
```

without supporting Evidence.

AI cannot substitute for missing source information.

---

# 55. Local-First Assessment

Relationship Assessment should be local-first.

The Evidence Aggregate may reveal a detailed map of the User's digital relationships.

There is no default justification for transmitting that entire graph to a remote AI provider when deterministic local assessment is sufficient.

---

# 56. No Permission Escalation

The Relationship Assessor operates only on available aggregated Evidence.

It must not directly request:

```text
Gmail body access
Password Manager secrets
Browser history expansion
```

If Evidence is insufficient:

```text
UNKNOWN
```

is a valid outcome.

A higher-level capability may separately decide whether additional source access is justified.

---

# 57. Relationship Assessment and Progressive Permission

A possible future flow is:

```text
Relationship Assessment
        |
        v
Evidence insufficient
        |
        v
UNKNOWN
        |
        v
Higher-Level Capability
        |
        v
Would additional authorized information materially help?
        |
    +---+---+
    |       |
   no      yes
    |       |
    v       v
 stop    User Permission Decision
```

The Assessor itself does not perform the escalation.

---

# 58. Relationship Assessment and Completeness

The assessor evaluates:

```text
available Evidence
```

not:

```text
all Evidence that exists in the world
```

Therefore every conclusion is relative to the observed footprint.

Conceptually:

```text
Relationship Assessment
       =
Assessment based on currently available observed Evidence
```

not:

```text
absolute truth
```

---

# 59. Partial Collection

Suppose:

```text
Personal Gmail:
COMPLETE

Password Manager:
PARTIAL

Outlook:
FAILED
```

The assessor may still evaluate available Evidence.

However, it should preserve warnings indicating incomplete source coverage when relevant.

It must not present the result as though all configured sources were fully analyzed.

---

# 60. Coverage Context

A future Assessment Context may include:

```text
CoverageSummary
```

describing:

- configured Connected Sources;
- successfully analyzed sources;
- partial sources;
- failed sources.

This context may influence explanation.

However:

```text
Incomplete Coverage
       !=
Weaker Relationship
```

in a simple mathematical sense.

It primarily limits what the framework can claim about completeness.

---

# 61. Conflict Handling

The assessor must evaluate conflicts reported by the Evidence Aggregate.

Possible outcomes include:

```text
retain current Relationship state with warning

move temporal status to UNKNOWN

reduce conclusion strength

request User review
```

The exact policy must be explicit.

The assessor must not silently ignore conflicting Evidence.

---

# 62. Semantic Conflict vs Technical Conflict

Examples of semantic conflict:

```text
ACCOUNT_DELETION
followed by
AUTHENTICATION
```

Technical issues such as:

```text
partial source collection
```

are not semantic Evidence conflicts.

These concepts must remain separate.

---

# 63. Contradictory User Input

The User may provide correction conflicting with automated Evidence.

Example:

```text
Evidence:
ACCOUNT_VERIFICATION
PASSWORD_MANAGER_ENTRY

User:
I never had this account.
```

The framework should preserve both:

```text
automated Evidence basis
```

and:

```text
User rejection
```

Current policy may prefer the User's explicit correction, but historical provenance must remain.

---

# 64. Assessment Version

Every assessment should identify the Assessor version where practical.

Conceptually:

```text
assessor_version:
1
```

This supports reassessment when policies evolve.

---

# 65. Policy Version

If Relationship rules are stored separately from Assessor code, the result may also require:

```text
assessment_policy_version
```

For example:

```text
assessor_version:
2

policy_version:
2026-11
```

The exact versioning format remains open.

---

# 66. Reassessment

Relationships must be reassessable.

Conceptually:

```text
Evidence Aggregate
       |
       +--> Assessor v1
       |       |
       |       v
       |    OBSERVED
       |
       +--> Assessor v2
               |
               v
           ESTABLISHED
```

The underlying Evidence remains preserved.

---

# 67. Reassessment Triggers

Reassessment may be required when:

```text
new Evidence arrives

Evidence is deleted

Evidence is reclassified

Entity Resolution changes

Service merge occurs

Service split occurs

Identity association changes

User correction occurs

ConnectedSource data is removed

assessment policy changes

Assessor version changes
```

The exact orchestration belongs to the application layer.

---

# 68. Relationship History

If assessments change over time, historical assessments may need to be preserved.

Example:

```text
2026-01
OBSERVED

2026-04
ESTABLISHED

2026-10
ESTABLISHED + HISTORICAL
```

The framework may eventually need:

```text
RelationshipAssessmentHistory
```

This is not yet promoted to a Domain Entity.

---

# 69. Current Relationship vs Assessment History

The Service Graph may expose:

```text
current assessment
```

while preserving previous assessments for:

- explainability;
- debugging;
- policy changes;
- auditability.

The exact persistence model remains undefined.

---

# 70. Relationship Persistence

The assessor should determine Relationship semantics.

It does not necessarily need responsibility for:

```text
creating persistent Relationship IDs

saving Relationship state

writing assessment history

triggering graph updates
```

These may belong to the application or persistence layer.

---

# 71. Relationship Candidate

Analogous to the `EvidenceCandidate` concept, the assessor may conceptually return a:

```text
RelationshipAssessmentCandidate
```

which is later materialized into the Domain `Relationship`.

This could separate:

```text
semantic assessment
```

from:

```text
Relationship persistence lifecycle
```

Draft v0.1 does not promote this to a Domain Entity.

---

# 72. Rejected Relationship and Evidence

A `REJECTED` Relationship does not imply Evidence deletion.

For example:

```text
Observation:
registration email

Evidence:
ACCOUNT_VERIFICATION

User:
this belonged to someone else
```

The Evidence remains historically valid as an Observation interpretation.

The current Relationship may become:

```text
REJECTED
```

with User correction provenance.

---

# 73. Rejected Relationship and Future Evidence

If new Evidence later arrives:

```text
PASSWORD_MANAGER_ENTRY
```

for a previously rejected Relationship, the framework should not automatically override the rejection.

The Relationship should be reassessed according to explicit policy.

Potentially:

```text
USER REVIEW REQUIRED
```

may eventually be useful.

Draft v0.1 does not define such a status yet.

---

# 74. Relationship Removal

A Service should not necessarily disappear from the Service Graph because current Evidence becomes weak or historical.

A historical digital footprint is part of the framework's purpose.

Possible removal may require:

- User action;
- explicit rejection;
- source-data deletion;
- retention policy;
- graph lifecycle policy.

The Relationship Assessor itself should not silently delete Services.

---

# 75. Relationship and Service Graph

The Service Graph consumes Relationship assessment results.

Conceptually:

```text
Service
  ^
  |
Relationship
  ^
  |
User / Identity
```

The graph should preserve links to supporting Evidence.

Conceptually:

```text
User
 |
 v
Relationship
 |
 +------------> Service
 |
 +------------> Evidence Aggregate
                         |
                         v
                     Evidence
```

This supports explainability.

---

# 76. Service Graph Does Not Store Absolute Truth

The Service Graph should represent:

```text
Observed and assessed digital Relationships
```

not:

```text
objective complete reality
```

Every Relationship should therefore remain grounded in:

```text
Evidence
+
Assessment provenance
```

---

# 77. RelationshipAssessor Interface

The language-independent contract is:

```text
interface RelationshipAssessor {

    RelationshipAssessmentResult assess(
        EvidenceAggregate aggregate,
        RelationshipAssessmentContext context
    )

}
```

This is pseudocode.

It is not the final Python interface.

---

# 78. Relationship Assessment Context

Conceptually:

```text
RelationshipAssessmentContext {

    RelationshipPolicy relationshipPolicy

    TemporalPolicy temporalPolicy

    ConflictPolicy conflictPolicy

    UserCorrectionContext userCorrections

    CoverageSummary coverage

    AssessorVersion assessorVersion
}
```

Not every implementation needs every field initially.

---

# 79. Relationship Assessment Result

Conceptually:

```text
RelationshipAssessmentResult {

    ProcessingStatus processingStatus

    Optional<RelationshipStatus> relationshipStatus

    Optional<TemporalStatus> temporalStatus

    Optional<ServiceReference> serviceReference

    List<IdentityReference> identityReferences

    List<EvidenceReference> evidenceBasis

    List<ReasonCode> reasonCodes

    List<Warning> warnings

    AssessmentMethod method

    AssessorVersion assessorVersion
}
```

---

# 80. Evidence Basis

The result must identify which Evidence formed the basis of the assessment.

Conceptually:

```text
evidence_basis:

- evidence_001
- evidence_002
- evidence_003
```

This allows the assessment to remain explainable and recalculable.

---

# 81. Relationship Status and Temporal Status Independence

The contract must support combinations such as:

```text
relationship_status:
ESTABLISHED

temporal_status:
HISTORICAL
```

or:

```text
relationship_status:
ESTABLISHED

temporal_status:
UNKNOWN
```

or:

```text
relationship_status:
OBSERVED

temporal_status:
CURRENTLY_OBSERVED
```

The assessor must not force temporal semantics into Relationship support states.

---

# 82. Relationship Assessor Invariants

### RA-INV-001

The assessor must operate on structured Evidence Aggregates rather than raw provider objects.

---

### RA-INV-002

Relationship Assessment must remain distinct from Evidence Classification.

---

### RA-INV-003

Relationship Assessment must remain distinct from Entity Resolution.

---

### RA-INV-004

Relationship Assessment must remain distinct from Evidence Aggregation.

---

### RA-INV-005

A Relationship must not imply current personal-data possession.

---

### RA-INV-006

A Relationship must not automatically imply an Account.

---

### RA-INV-007

The assessor must support `UNKNOWN`.

---

### RA-INV-008

Technical processing failure must remain distinct from Relationship `UNKNOWN`.

---

### RA-INV-009

Relationship support state and temporal state must remain conceptually distinct.

---

### RA-INV-010

Historical Relationships must remain representable.

---

### RA-INV-011

Historical Relationship status must not remove the Service automatically from the Service Graph.

---

### RA-INV-012

Evidence frequency alone must not determine Relationship state.

---

### RA-INV-013

Source diversity alone must not determine Relationship state.

---

### RA-INV-014

Provider diversity alone must not determine Relationship state.

---

### RA-INV-015

Evidence semantics must contribute to Relationship Assessment.

---

### RA-INV-016

Conflicting Evidence must not be silently ignored.

---

### RA-INV-017

The assessor must preserve the Evidence basis for every conclusion.

---

### RA-INV-018

The assessor must preserve relevant Identity references.

---

### RA-INV-019

Multiple Identity references must not automatically imply multiple Accounts.

---

### RA-INV-020

User corrections must remain attributable to the User.

---

### RA-INV-021

User correction must not destructively rewrite source Evidence.

---

### RA-INV-022

The assessor must not require provider credentials.

---

### RA-INV-023

The assessor must not directly request additional source permissions.

---

### RA-INV-024

Basic Relationship Assessment must not require AI.

---

### RA-INV-025

AI must not invent missing Evidence.

---

### RA-INV-026

Assessment must remain relative to the observed footprint.

---

### RA-INV-027

Incomplete source coverage must not be presented as complete discovery.

---

### RA-INV-028

No arbitrary numerical Confidence score is required in Draft v0.1.

---

### RA-INV-029

Relationship reassessment must be possible without destructive modification of supporting Evidence.

---

### RA-INV-030

Changes to assessment policy or Assessor version must remain traceable where they materially affect Relationship state.

---

## 83. Marketing-Only Example

Aggregate:

```text
Service:
Example Shop

Evidence:
MARKETING x 25
NEWSLETTER x 8

Source Types:
EMAIL
```

Possible assessment:

```text
processing_status:
SUCCESS

relationship_status:
OBSERVED

temporal_status:
CURRENTLY_OBSERVED

reason_codes:
- COMMUNICATION_ONLY
```

The assessor does not conclude that the User has an account.

---

## 84. Gmail Verification Example

Aggregate:

```text
Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION x 1

Source Types:
EMAIL
```

Possible assessment:

```text
relationship_status:
OBSERVED
or
ESTABLISHED
```

depending on the future explicit assessment policy.

Draft v0.1 intentionally does not freeze this rule.

This example demonstrates why empirical validation is still required.

---

## 85. Gmail + Password Manager Example

Aggregate:

```text
Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION      1
PASSWORD_MANAGER_ENTRY    1

Source Types:
EMAIL
PASSWORD_MANAGER

Identity:
personal@example.com
```

A future policy may justify:

```text
relationship_status:
ESTABLISHED
```

because two structurally different Evidence sources support an account-style Relationship.

However, the exact rule must be explicit and empirically validated before implementation.

---

## 86. Purchase Without Account Example

Aggregate:

```text
Service:
Example Shop

Evidence:
PURCHASE    1
PAYMENT     1
INVOICE     1

Source Types:
EMAIL
```

The assessor may conclude that a meaningful commercial Relationship existed.

It must not automatically conclude:

```text
Account existed
```

because guest purchases may be possible.

This reinforces:

```text
Relationship != Account
```

---

## 87. Historical Relationship Example

Aggregate:

```text
Service:
Example Service

Evidence Timeline:

2021 ACCOUNT_CREATION
2021 ACCOUNT_VERIFICATION
2022 PAYMENT
2024 ACCOUNT_DELETION
```

Possible assessment:

```text
relationship_status:
ESTABLISHED

temporal_status:
HISTORICAL

reason_codes:
- ACCOUNT_RELATED_EVIDENCE
- HISTORICAL_DELETION_EVIDENCE
```

This still does not imply:

```text
Personal Data Held:
NONE
```

---

## 88. Conflicting Temporal Example

Aggregate:

```text
2021 ACCOUNT_CREATION

2024 ACCOUNT_DELETION

2026 AUTHENTICATION
```

Possible assessment:

```text
relationship_status:
ESTABLISHED

temporal_status:
UNKNOWN

warnings:
- CONFLICTING_TEMPORAL_EVIDENCE
```

No unsupported narrative is fabricated.

---

## 89. Password Manager Only Example

Aggregate:

```text
Service:
GitHub

Evidence:
PASSWORD_MANAGER_ENTRY 1

Source Types:
PASSWORD_MANAGER
```

Possible assessment may eventually be:

```text
relationship_status:
ESTABLISHED

temporal_status:
UNKNOWN
```

or a more conservative state depending on validated policy.

The password-manager record does not prove that credentials currently work.

---

## 90. Unknown Relationship Example

Aggregate:

```text
Service:
Example Service

Evidence:
UNKNOWN / weak semantic context
```

Assessment:

```text
processing_status:
SUCCESS

relationship_status:
UNKNOWN

temporal_status:
UNKNOWN

reason_codes:
- INSUFFICIENT_EVIDENCE
```

This is a valid outcome.

---

## 91. Rejected Relationship Example

Aggregate:

```text
Service:
Example Service

Automated Evidence:
ACCOUNT_VERIFICATION

User Correction:
This belonged to another person.
```

Possible assessment:

```text
relationship_status:
REJECTED

temporal_status:
UNKNOWN

reason_codes:
- USER_REJECTED
```

The original Observation and automated Evidence remain preserved.

---

## 92. Multi-Identity Example

Aggregate:

```text
Service:
Spotify

Evidence:
PASSWORD_MANAGER_ENTRY

Identity:
personal@example.com

Evidence:
PASSWORD_MANAGER_ENTRY

Identity:
oldmail@example.net
```

Relationship Assessment may preserve:

```text
Identity References:
personal@example.com
oldmail@example.net
```

without concluding:

```text
two Spotify Accounts
```

---

## 93. Partial Coverage Example

Aggregate:

```text
Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION
PASSWORD_MANAGER_ENTRY

Coverage:

Personal Gmail:
COMPLETE

Password Manager:
PARTIAL

Outlook:
FAILED
```

Assessment may still be:

```text
ESTABLISHED
```

if Evidence justifies it.

But explanation should include:

```text
Discovery coverage is incomplete for some configured sources.
```

This prevents the framework from overstating completeness.

---

## 94. Reassessment Example

Initial aggregate:

```text
MARKETING
NEWSLETTER
```

Assessment:

```text
OBSERVED
```

Later Evidence:

```text
PASSWORD_MANAGER_ENTRY
ACCOUNT_VERIFICATION
```

New aggregate:

```text
MARKETING
NEWSLETTER
PASSWORD_MANAGER_ENTRY
ACCOUNT_VERIFICATION
```

Reassessment may become:

```text
ESTABLISHED
```

depending on explicit policy.

The original Observations and Evidence remain unchanged.

---

## 95. Service Resolution Change Example

Initially:

```text
Identifier:
oldservice.example

Service:
UNRESOLVED

Evidence:
PAYMENT
```

Relationship Assessment may not yet create a canonical Service Relationship.

Later:

```text
oldservice.example
    ->
Service X
```

The Evidence is re-aggregated under Service X.

Relationship Assessment runs again.

No source retrieval is required if preserved Evidence is sufficient.

---

## 96. Service Merge Example

Initially:

```text
Service A
Relationship:
OBSERVED

Service B
Relationship:
ESTABLISHED
```

Later:

```text
Service A
+
Service B
    |
    v
Service C
```

Evidence must be re-aggregated and the Relationship reassessed.

The new Relationship state must not simply copy either old state.

---

## 97. Open Questions

### Relationship State Model

- Are `UNKNOWN`, `OBSERVED`, `ESTABLISHED`, `REJECTED` the right states?
- Is another state between `OBSERVED` and `ESTABLISHED` necessary?
- How should such a state be defined without becoming vague probability language?
- Should User-confirmed Relationships have a separate status?

### Temporal Status

- Are `UNKNOWN`, `CURRENTLY_OBSERVED`, `HISTORICAL` sufficient?
- Does `CURRENTLY_OBSERVED` communicate the right semantics?
- Is `ENDED` different from `HISTORICAL`?
- Can a Relationship be both historical and recently observed through marketing?

### User vs Identity Relationship

- Is the core Relationship between User and Service?
- Should Identity-Service associations become separate entities?
- Can one User-Service Relationship contain many associated Identity Seeds?
- How should unverified observed identities be represented?

### Account

- Has the framework now accumulated enough evidence to justify `Account`?
- Or can Account remain outside basic Discovery?
- Should Account be inferred only when specific account-related Evidence exists?
- How are guest purchases represented if Account exists as an entity?

### Evidence Sufficiency

- Which Evidence combinations justify `ESTABLISHED`?
- Is one account-verification event sufficient?
- Is one password-manager entry sufficient?
- Should User confirmation override automated Evidence?
- How are false positives measured?

### Evidence Independence

- How should independence between Evidence sources be defined?
- Does email + password manager qualify as independent by default?
- How should multiple emails generated during one registration workflow be treated?

### Temporal Reasoning

- What age makes Evidence historical?
- Should age matter without deletion Evidence?
- How should inactive-but-not-deleted accounts be represented?
- How should Service reactivation be represented?

### Conflicts

- Which conflicts require temporal status `UNKNOWN`?
- When should conflicts request User review?
- Is a dedicated conflict-resolution contract eventually necessary?

### Confidence

- Is Confidence necessary at all?
- Would Relationship Status + Temporal Status + Evidence explanation be more useful?
- If Confidence is introduced later, what exactly will it measure?

### Manual Input

- How should User-confirmed Relationships interact with automated assessment?
- Can a User explicitly mark a Relationship historical?
- Can User corrections override later automated Evidence?

### Persistence

- Should each assessment be stored historically?
- Should only the current Relationship state be materialized?
- How should old assessment policies be audited?
- How much provenance is required?

### Service Graph

- Does the Service Graph store Relationships or current Relationship assessments?
- How are historical states represented?
- How are rejected Services represented?

### Coverage

- Should incomplete source coverage always be visible to the User?
- How should Relationship explanations distinguish incomplete discovery from uncertain Relationship semantics?

---

## 98. Findings from Contract Design

### Finding 1 - Relationship Strength and Time Are Separate Dimensions

The earlier state model:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
```

mixes:

```text
support strength
```

with:

```text
temporal status
```

The contract therefore proposes separating:

```text
RelationshipStatus
```

from:

```text
TemporalStatus
```

This is a material Domain Model finding.

---

### Finding 2 - Confidence May Not Be Necessary

The combination of:

```text
Relationship Status
Temporal Status
Evidence Summary
Source Diversity
Timeline
Conflicts
Explainability
```

may be more meaningful than a numerical score.

Confidence should not be introduced simply because other classification systems commonly use it.

---

### Finding 3 - Relationship Does Not Mean Account

Scenario 001 and Scenario 002 demonstrate that the framework may discover meaningful Relationships without establishing a conventional account.

Examples include:

```text
guest purchase
newsletter
privacy communication
historical interaction
```

Therefore `Account` remains optional rather than foundational.

---

### Finding 4 - User-Level and Identity-Level Views May Need Separation

The framework ultimately needs to answer:

```text
Which Services are connected to me?
```

while also preserving:

```text
Which Identity was involved?
```

This may eventually justify separating:

```text
User-Service Relationship
```

from:

```text
Identity-Service Association
```

rather than forcing one entity to represent both.

---

### Finding 5 - Assessment Policy Must Be Explicit and Versioned

Once the framework begins deciding:

```text
OBSERVED
```

versus:

```text
ESTABLISHED
```

those rules become significant domain policy.

They must therefore be:

- explicit;
- testable;
- explainable;
- versionable.

---

### Finding 6 - Evidence Independence Requires Empirical Validation

Multiple source support appears important, but the framework does not yet have a rigorous definition of independent Evidence.

This should be measured using real Discovery data rather than converted immediately into arbitrary weighting.

---

### Finding 7 - Relationship Assessment Remains Deterministic-First

Once Evidence has been normalized, initial Relationship Assessment is primarily structured reasoning.

No current scenario demonstrates that an LLM is required for basic assessment.

---

## 99. Decision Candidates

### Candidate Decision - Separate Relationship and Temporal Status

```text
Relationship support and temporal status should be represented as separate
dimensions.

A Relationship may therefore be ESTABLISHED while its temporal status is
HISTORICAL, UNKNOWN or another future temporal state.
```

---

### Candidate Decision - Avoid Uncalibrated Possible/Probable States

```text
Relationship states should have explicit semantic definitions.

Terms such as POSSIBLE and PROBABLE should not be introduced unless the
framework defines clear and testable semantics for them.
```

---

### Candidate Decision - Relationship Does Not Imply Account

```text
Service Discovery should model Relationships independently from Accounts.

An Account may later become an optional Domain concept when account-specific
Evidence justifies it.
```

---

### Candidate Decision - Relationship Assessment Is Explainable Policy

```text
Relationship Assessment should use explicit, versioned and explainable policy
rather than hidden weighting or opaque AI reasoning.
```

---

### Candidate Decision - No Numerical Confidence Yet

```text
Draft v0.1 should not require numerical Relationship Confidence.

Relationship Status, Temporal Status, structured Evidence and explanation
should be evaluated before introducing a calibrated Confidence model.
```

---

### Candidate Decision - Historical Relationships Remain in the Graph

```text
Historical Relationships remain part of the observed digital footprint and
should not be removed merely because available Evidence suggests the active
Relationship ended.
```

---

### Candidate Decision - Reassessment Is Required

```text
Relationships must be reassessable when Evidence, Entity Resolution,
Identity association, User correction or assessment policy changes.
```

---

## 100. Current Contract Baseline

The initial Relationship Assessor contract is:

```text
Evidence Aggregate
       |
       v
RelationshipAssessor
       |
       v
RelationshipAssessmentResult
       |
       +-- processing_status
       |
       +-- relationship_status
       |
       +-- temporal_status
       |
       +-- service_reference
       |
       +-- identity_references
       |
       +-- evidence_basis
       |
       +-- reason_codes
       |
       +-- warnings
       |
       +-- method
       |
       +-- assessor_version
```

with the guarantees:

```text
Evidence-based assessment
Relationship separate from Evidence
Relationship separate from Account
Relationship separate from current data possession
support state separate from temporal state
UNKNOWN supported
historical Relationships supported
conflicting Evidence preserved
source diversity available but not automatically weighted
Identity provenance preserved
explicit explainable policy
no arbitrary numerical Confidence
deterministic-first assessment
no provider credentials
no direct permission escalation
reassessment supported
observed-footprint semantics preserved
```

---

## 101. End-to-End Discovery Contract

With this contract, the first complete Identity and Service Discovery software flow is now defined conceptually:

```text
CONNECTED SOURCE
       |
       v
CONNECTOR
       |
       v
OBSERVATION
      / \
     /   \
    v     v
SERVICE   EVIDENCE
CANDIDATE CLASSIFIER
DETECTOR     |
    |        v
    |     EVIDENCE
    v        |
CANDIDATE    |
IDENTIFIER   |
    |        |
    v        |
ENTITY       |
RESOLVER     |
    |        |
    v        |
 SERVICE     |
     \       /
      \     /
       v   v
 EVIDENCE AGGREGATOR
         |
         v
  EVIDENCE AGGREGATE
         |
         v
RELATIONSHIP ASSESSOR
         |
         v
   RELATIONSHIP
         |
         v
    SERVICE GRAPH
```

The architecture now defines the responsibilities and boundaries of each primary component in the initial Discovery pipeline.

---

## 102. Next Design Step

The first set of Discovery software contracts is now conceptually complete.

The next step should not be to add another processing contract automatically.

Instead, the architecture, Domain Model and seven interface contracts should be reviewed together for:

```text
contradictions
duplicated responsibilities
missing domain concepts
premature abstractions
unclear ownership
inconsistent state models
persistence assumptions
privacy boundary violations
```

Particular attention should be given to findings that emerged during interface design:

```text
ConnectedSource
    -> already promoted to Core Domain Entity

Evidence lifecycle
    -> unresolved

RelationshipStatus vs TemporalStatus
    -> new Domain Model finding

User-Service Relationship vs Identity-Service Association
    -> unresolved

Service Registry ownership
    -> unresolved

Account
    -> still Candidate Domain Concept

ResolutionResult
    -> still Candidate Value Concept

CollectionRun
    -> possible future concept

EvidenceCandidate
    -> possible interface-level concept

RelationshipAssessment history
    -> possible future concept
```

After this consistency review, the Domain Model and Identity & Service Discovery architecture should be updated only where the interface contracts have produced sufficiently strong cross-cutting findings.

The software implementation should begin only after those inconsistencies have been resolved or explicitly documented as deliberate open questions.
