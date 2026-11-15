# Relationship Assessor Contract

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
- `docs/interfaces/06-evidence-aggregator-contract.md`

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `RelationshipAssessor` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Relationship Assessor evaluates an EvidenceAggregate and determines what the framework can justifiably conclude about a possible current or historical Relationship between the User and a Service.

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

> Given the currently available Evidence, what can the framework reasonably say about the observed Relationship between this User and this Service?

Its responsibility is to interpret aggregated Evidence.

It does not determine:

- which Service an identifier represents;
- what an individual Observation means;
- how raw source information is collected;
- which personal data the Service currently holds;
- whether externally stored personal data has been deleted;
- what governance action should be performed.

The consolidated Domain Model defines the primary Relationship as:

```text
User
  |
  v
Relationship
  |
  v
Service
```

Relevant Identity references remain preserved as supporting Relationship context.

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
            CandidateIdentifier   Evidence
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
                    EvidenceAggregate
                    [Derived View]
                            |
                            v
                 RELATIONSHIP ASSESSOR
                            |
                            v
              RelationshipAssessmentResult
                    [Processing Result]
                            |
                            v
                    Application Layer
                            |
                            v
                       Relationship
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

A Relationship represents the framework's current assessment derived from accumulated current Evidence.

For example:

```text
ACCOUNT_VERIFICATION
PASSWORD_MANAGER_ENTRY
PAYMENT
SUBSCRIPTION
```

may support a different Relationship conclusion from:

```text
MARKETING
NEWSLETTER
```

The Relationship Assessor interprets that difference.

---

## 4. Relationship Is Not Current Data Possession

Even an ESTABLISHED Relationship must not be interpreted as proof that the Service currently holds specific personal data.

Therefore:

```text
RELATIONSHIP
        !=
CURRENT DATA POSSESSION
```

For example:

```text
RelationshipStatus:
ESTABLISHED

TemporalStatus:
HISTORICAL
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

The framework discovers digital Relationships, not only Accounts.

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
privacy communication
other digital interaction
```

Therefore:

```text
RELATIONSHIP != ACCOUNT
```

Account remains a Candidate Domain Concept rather than a mandatory part of the Discovery Domain.

---

## 6. Input Contract

The Relationship Assessor receives an EvidenceAggregate.

Conceptually:

```text
assess(
    evidence_aggregate,
    context
)
    ->
RelationshipAssessmentResult
```

The Assessor should not require direct access to:

- external Providers;
- Connector credentials;
- raw Provider objects;
- unrelated Observations;
- unrestricted source data.

It should reason primarily over structured Evidence and preserved provenance exposed by the Aggregate.

---

## 7. Assessment Context

The Assessor may require explicit supporting context.

Conceptually:

```text
RelationshipAssessmentContext

- assessment_policy
- evidence_semantics
- temporal_policy
- conflict_policy
- user_corrections
- coverage
```

The exact structure remains open.

The context must not hide arbitrary weighting or undocumented inference rules.

RelationshipStatus and TemporalStatus are defined by the Domain Model rather than supplied as arbitrary application-specific state models.

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
- method
- assessor_version
- assessment_policy_version
```

The consolidated Domain Model classifies:

```text
RelationshipAssessmentResult
```

as:

```text
Processing Result / Value Object
```

rather than a Core Domain Entity.

The application layer may use a successful assessment result to create or update the current Domain Relationship.

Therefore:

```text
RelationshipAssessmentResult
        !=
Relationship
```

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

> The Assessor successfully evaluated the available Evidence but could not justify a stronger Relationship conclusion.

This is different from:

```text
processing_status:
FAILED
```

Therefore:

```text
DOMAIN UNCERTAINTY
        !=
PROCESSING FAILURE
```

---

## 10. Relationship Status

The consolidated Domain Model defines:

```text
RelationshipStatus

UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

These states describe semantic support for the User-Service Relationship.

They are intentionally separate from temporal interpretation.

The previous provisional flat model:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
REJECTED
```

is no longer the current baseline because it mixed:

```text
support strength
```

with:

```text
temporal status
```

---

## 11. Relationship Status Model

The current RelationshipStatus model is:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

These states are part of the consolidated Discovery Domain Model.

They are not numerical probability buckets.

Their concrete assessment rules remain subject to empirical validation.

---

## 12. UNKNOWN

UNKNOWN means that available current Evidence is insufficient to justify that a meaningful User-Service Relationship existed.

Example:

```text
Evidence:
one ambiguous weak communication signal
```

may remain:

```text
UNKNOWN
```

This does not mean:

```text
Relationship does not exist.
```

It means:

> Current observed Evidence does not justify a stronger conclusion.

---

## 13. OBSERVED

OBSERVED means that the framework has Evidence of interaction or communication involving the Service but cannot justify the stronger ESTABLISHED state.

Examples may include:

```text
MARKETING
NEWSLETTER
PRIVACY_NOTICE
browser visit
```

depending on explicit assessment policy.

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

This state deliberately avoids claiming that an Account exists.

---

## 14. ESTABLISHED

ESTABLISHED means that available Evidence provides a justified basis for concluding that a meaningful User-Service Relationship existed.

Potential supporting Evidence may include:

```text
ACCOUNT_VERIFICATION
PASSWORD_MANAGER_ENTRY
SUBSCRIPTION
AUTHENTICATION
PAYMENT
PURCHASE
User confirmation
independent source support
```

However, Draft v0.1 does not define automatic rules such as:

```text
ACCOUNT_VERIFICATION = ESTABLISHED
```

or:

```text
two strong Evidence items = ESTABLISHED
```

Those rules require explicit assessment policy and empirical validation.

---

## 15. REJECTED

REJECTED represents an explicit conclusion that an apparent Relationship should not currently be attributed to the User.

Examples may include:

```text
User explicitly states:
"This was not my account."

verified misattribution

Evidence known to belong to another person

corrected Service association demonstrating that the Relationship was false
```

REJECTED should not normally be inferred merely from weak Evidence.

Explicit rejection requires justification and provenance.

---

## 16. Why POSSIBLE and PROBABLE Are Not in the Model

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

The consolidated model therefore uses:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

with explicit semantics rather than vague probability language.

---

## 17. Temporal Status

Relationship support and temporal interpretation are separate.

The consolidated Domain Model defines:

```text
TemporalStatus

UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

These states describe the framework's current temporal interpretation of the Relationship.

---

## 18. UNKNOWN Temporal Status

UNKNOWN means that the framework cannot safely determine whether the Relationship should be considered current or historical.

This may be common.

For example:

```text
PASSWORD_MANAGER_ENTRY
```

alone does not prove whether the related Account:

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

CURRENTLY_OBSERVED means that sufficiently recent Evidence indicates ongoing observable interaction.

This must not be interpreted as:

```text
ACTIVE ACCOUNT CONFIRMED
```

For example:

```text
recent SECURITY_NOTIFICATION
```

may support ongoing observable interaction.

Likewise:

```text
recent NEWSLETTER
```

may indicate continuing communication without proving current Account activity.

Therefore:

```text
CURRENTLY_OBSERVED
        !=
ACTIVE ACCOUNT
```

---

## 20. HISTORICAL

HISTORICAL means available Evidence supports that the Relationship existed in the past while current continuation is not established or Evidence indicates that it ended.

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

The exact temporal rules remain subject to assessment-policy validation.

---

## 21. Status Dimensions

Separating Relationship support and temporal interpretation allows combinations such as:

```text
ESTABLISHED + HISTORICAL

ESTABLISHED + UNKNOWN

OBSERVED + CURRENTLY_OBSERVED

REJECTED + UNKNOWN
```

instead of forcing everything into one flat state list.

This separation is formalized by:

```text
D-022 - Relationship Support and Temporal Status Are Separate
```

Therefore:

```text
RelationshipStatus
        !=
TemporalStatus
```

---

## 22. Evidence Sufficiency

The Relationship Assessor must determine whether available Evidence is sufficient for a given RelationshipStatus.

However, Draft v0.1 does not define arbitrary numerical weights.

For example, it must not initially use:

```text
ACCOUNT_VERIFICATION = 0.8
PASSWORD_MANAGER_ENTRY = 0.9
MARKETING = 0.1
```

The first implementation should prefer explicit Evidence-semantics rules.

---

## 23. Evidence Type Matters

Evidence frequency alone is insufficient.

For example:

```text
100 MARKETING
```

represents a different semantic basis from:

```text
1 ACCOUNT_VERIFICATION
+
1 PASSWORD_MANAGER_ENTRY
```

The Assessor must therefore reason about:

```text
EvidenceType
```

and not only:

```text
Evidence Count
```

---

## 24. Evidence Frequency Still Matters

Although frequency does not determine RelationshipStatus automatically, it may provide useful descriptive context.

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

## 25. Source Diversity

Evidence from multiple structurally different SourceTypes may provide different context from repeated Evidence from one source.

Example:

```text
Gmail:
ACCOUNT_VERIFICATION

Password Manager:
PASSWORD_MANAGER_ENTRY
```

represents cross-source support.

The Assessor may consider:

```text
SourceType diversity
```

as part of explicit assessment policy.

However:

```text
multiple SourceTypes
        !=
automatic ESTABLISHED
```

Evidence semantics still matter.

---

## 26. ConnectedSource Diversity

Evidence may come from multiple ConnectedSources of the same SourceType.

Example:

```text
Personal Gmail
Old Gmail
```

The Assessor should preserve that distinction.

However:

```text
two email ConnectedSources
```

are not necessarily equivalent to:

```text
two structurally independent SourceTypes
```

Therefore:

```text
ConnectedSource diversity
        !=
SourceType diversity
```

---

## 27. Provider Diversity

Evidence from:

```text
Gmail
Outlook
```

comes from different Providers but may still represent:

```text
SourceType:
EMAIL
```

Provider diversity may provide provenance context.

It should not automatically be treated as independent semantic validation.

---

## 28. Independent Evidence

The framework may eventually distinguish:

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
password-manager entry
```

may be structurally more independent than:

```text
registration email
+
welcome email
```

However, defining Evidence independence precisely requires empirical work.

Draft v0.1 therefore preserves:

- Evidence provenance;
- SourceType;
- ConnectedSource;
- chronology;
- EvidenceType;

rather than introducing an independence score.

---

## 29. Current vs Historical Reasoning

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

These Evidence timelines should not necessarily produce identical TemporalStatus values.

---

## 30. Account Deletion Evidence

ACCOUNT_DELETION is relevant to temporal interpretation.

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

The Assessor must preserve that uncertainty.

---

## 31. Deletion Followed by Later Activity

Consider:

```text
2024 ACCOUNT_DELETION
2026 AUTHENTICATION
```

Possible explanations include:

- Account recreated;
- deletion request failed;
- different Account;
- Evidence misclassification;
- source timestamps have different semantics.

The Assessor must not invent one explanation.

Possible result:

```text
relationship_status:
ESTABLISHED

temporal_status:
UNKNOWN

warnings:
- CONFLICTING_TEMPORAL_EVIDENCE
```

---

## 32. Historical Does Not Mean Irrelevant

A historical Relationship remains relevant to the Personal Data Governance Framework.

A historical Service may still:

- retain transaction history;
- retain data under legal obligations;
- retain backups;
- hold residual Account information;
- appear in later Personal Data Acquisition.

Therefore:

```text
HISTORICAL
       !=
REMOVE FROM SERVICE GRAPH
```

and:

```text
HISTORICAL
       !=
NO PERSONAL DATA REMAINS
```

---

## 33. Current Relationship Does Not Mean Account

Recent Evidence may support:

```text
CURRENTLY_OBSERVED
```

without proving:

```text
active Account
```

Example:

```text
recent newsletter
```

shows continued communication but not necessarily Account activity.

RelationshipStatus, TemporalStatus and Evidence semantics must remain independently interpretable.

---

## 34. Relationship and Identity

The consolidated Domain Model defines the primary Relationship as:

```text
User
  |
  v
Relationship
  |
  v
Service
```

Relevant IdentitySeeds remain associated with the Relationship as supporting context.

For example:

```text
User
 |
 v
Relationship
 |
 +-- Service: Spotify
 |
 +-- IdentityReference:
 |      personal@example.com
 |
 +-- EvidenceBasis
```

Identity information remains important.

It does not redefine the primary Relationship cardinality.

---

## 35. Multiple Identities

Evidence may involve:

```text
personal@example.com
oldmail@example.net
```

for the same Service.

The Assessor must not automatically conclude:

```text
two Accounts
```

or:

```text
one Account
```

Instead, the Relationship may preserve:

```text
IdentityReferences:
- personal@example.com
- oldmail@example.net
```

Account remains a separate Candidate Domain Concept.

---

## 36. Unknown Identity

Some Evidence may support a User-Service Relationship without a verified IdentitySeed.

For example, a Password Manager entry may expose an unconfirmed historical username.

The Assessor may still reason at:

```text
User <-> Service
```

level while preserving:

```text
Identity association:
UNKNOWN
```

A verified Identity association is not a prerequisite for every User-Service Relationship.

---

## 37. User-Level Relationship

The framework's primary User-facing question is:

> Which Services appear to have or have had a Relationship with me?

Therefore the primary Relationship is:

```text
User
  |
  v
Relationship
  |
  v
Service
```

This is now a consolidated Domain decision rather than an unresolved alternative.

---

## 38. Identity-Level Association

Some scenarios also require questions such as:

> Which Services were associated with `oldmail@example.net`?

Draft v0.3 addresses this by preserving Identity references within:

- Evidence;
- EvidenceAggregate;
- Relationship.

A future:

```text
IdentitySeed
     |
     v
IdentityServiceAssociation
     |
     v
Service
```

may eventually provide an explicit Domain representation if needed.

However:

```text
IdentityServiceAssociation
```

remains a:

```text
Candidate Domain Concept
```

and is not required by the current RelationshipAssessor contract.

---

## 39. Account Remains a Candidate Concept

Repeated contract design has exposed cases such as:

```text
Service:
Spotify

Identity:
personal@example.com

Identity:
oldmail@example.net
```

An Account concept could eventually explain these structures.

However, Relationship Assessment does not require Account to function.

Therefore:

```text
Account
=
Candidate Domain Concept
```

remains the correct Draft v0.3 classification.

---

## 40. Relationship Assessment Rules

The Assessor should use explicit rules or policy where practical.

Conceptually:

```text
EvidenceAggregate
      |
      v
Assessment Policy
      |
      v
RelationshipAssessmentResult
```

Rules should be:

- explicit;
- versionable;
- testable;
- explainable.

The framework should not hide Relationship semantics inside opaque application code.

---

## 41. No Arbitrary Scoring

The initial Discovery model does not use:

```text
relationship_score = 0.91
```

or formulas such as:

```text
0.8 * ACCOUNT_VERIFICATION
+
0.5 * PAYMENT
+
0.2 * MARKETING
```

without defined calibration.

Such a model would imply mathematical meaning that has not been established.

---

## 42. Numerical Confidence Is Outside the Initial Discovery Model

Numerical Relationship Confidence is explicitly outside the initial Discovery baseline.

A Relationship already has explainable dimensions:

```text
RelationshipStatus
TemporalStatus
EvidenceTypes
SourceTypes
ConnectedSources
Timeline
Conflicts
ReasonCodes
Warnings
```

These dimensions are preferred over an uncalibrated scalar score.

This is formalized by:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

---

## 43. Possible Future Confidence

A calibrated Confidence model may still become useful after empirical validation.

For example, future research may measure:

- true positives;
- false positives;
- false negatives;
- different Evidence combinations;
- User corrections;
- assessment-policy outcomes.

If introduced, numerical Confidence must:

- have explicit semantics;
- use representative validation data;
- be calibrated;
- provide measurable User value;
- remain distinct from RelationshipStatus.

It is not part of the initial implementation baseline.

---

## 44. User Confirmation

The User may explicitly confirm a Relationship.

Example:

```text
Framework:
OBSERVED

User:
Yes, I had a Spotify account.
```

This may provide a strong manual signal according to explicit assessment policy.

The framework must preserve:

```text
User Confirmation
```

as provenance.

It must not rewrite historical Evidence to make it appear that automated Discovery independently established the Relationship.

---

## 45. User Rejection

Similarly:

```text
Framework:
ESTABLISHED

User:
This account belonged to someone else.
```

may cause the current RelationshipStatus to become:

```text
REJECTED
```

according to assessment policy.

The original automated Evidence basis and assessment history should remain attributable.

---

## 46. Manual Relationships

A User may manually declare:

```text
I had an account with Example Service in 2018.
```

This can eventually produce:

```text
MANUAL_RELATIONSHIP_DECLARATION Observation
        |
        v
manual Evidence
        |
        v
EvidenceAggregate
        |
        v
RelationshipAssessor
```

Manual declarations should not require a completely separate Relationship model.

---

## 47. Relationship Assessment Provenance

Every assessment must remain traceable to:

```text
EvidenceAggregate
       |
       v
Assessment Policy
       |
       v
Assessor Version
       |
       v
RelationshipAssessmentResult
```

At minimum, the framework should be able to answer:

> Why is this Relationship currently classified this way?

---

## 48. Reason Codes

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
INCOMPLETE_SOURCE_COVERAGE
```

These are illustrative.

The final taxonomy should emerge from actual assessment rules.

---

## 49. Human-Readable Explanation

In addition to machine-readable reasons, the framework should eventually produce concise explanations.

Example:

```text
This Relationship is considered ESTABLISHED because:

- an account-verification event was observed;
- a password-manager entry was independently associated with the same Service;
- both Evidence items remain ACTIVE;
- both refer to the same User-Service context.
```

Or:

```text
This Relationship is OBSERVED rather than ESTABLISHED because
the current Evidence consists only of marketing and newsletter communication.
```

The explanation must remain derivable from structured Evidence and explicit rules.

---

## 50. Explainability Without Exposing Raw Data

The framework should not need to expose complete raw source content to justify a Relationship.

For example:

```text
ACCOUNT_VERIFICATION
observed on 2024-05-01
```

may be sufficient for an explanation.

This supports privacy by minimizing unnecessary display or transmission of source data.

---

## 51. Assessment Method

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

## 52. AI Boundary

Basic Relationship Assessment should not require AI.

Once Evidence has been normalized into structured categories, operations such as:

```text
inspect EvidenceTypes
inspect timeline
inspect source diversity
inspect conflicts
apply assessment policy
```

are deterministic.

An LLM should not be required simply to determine that:

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

## 53. AI for Complex Reasoning

Future Evidence structures may become substantially more complex.

AI might eventually provide value for:

- interpreting unusual conflicts;
- assisting User-facing explanations;
- proposing reassessment hypotheses;
- future advanced reasoning.

However, AI must not silently replace:

```text
RelationshipStatus
TemporalStatus
AssessmentPolicy
```

with opaque model judgment.

---

## 54. AI Must Not Invent Missing Evidence

If an Aggregate contains only:

```text
MARKETING
```

the Assessor must not use AI to infer:

```text
probably an Account exists
```

without supporting Evidence.

AI cannot substitute for missing source information.

---

## 55. Local-First Assessment

Relationship Assessment should be local-first.

The EvidenceAggregate may reveal a detailed map of the User's digital Relationships.

There is no default justification for transmitting that entire graph to a remote AI Provider when deterministic local assessment is sufficient.

---

## 56. No Permission Escalation

The RelationshipAssessor operates only on available aggregated Evidence.

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

## 57. Relationship Assessment and Progressive Permission

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

## 58. Relationship Assessment and Completeness

The Assessor evaluates:

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

## 59. Partial Collection

Suppose:

```text
Personal Gmail:
COMPLETE

Password Manager:
PARTIAL

Outlook:
FAILED
```

The Assessor may still evaluate available Evidence.

However, it should preserve warnings indicating incomplete source coverage where relevant.

It must not present the result as though all configured sources were fully analyzed.

---

## 60. Coverage Context

Relationship Assessment may consume:

```text
CoverageSummary
```

provided through the EvidenceAggregate or AssessmentContext.

It may describe:

- configured ConnectedSources;
- successfully analyzed sources;
- partial sources;
- failed sources;
- unavailable sources.

However:

```text
Incomplete Coverage
       !=
Weaker Relationship
```

in a simple mathematical sense.

Incomplete coverage primarily limits what the framework can claim about completeness.

---

## 61. Conflict Handling

The Assessor must evaluate conflicts reported by the EvidenceAggregate.

Possible policy outcomes include:

```text
retain RelationshipStatus with warning

set TemporalStatus to UNKNOWN

use a more conservative RelationshipStatus

request User review
```

The exact policy must be explicit.

The Assessor must not silently ignore conflicting Evidence.

---

## 62. Semantic Conflict vs Technical Conflict

Examples of semantic conflict include:

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

Therefore:

```text
Semantic Conflict
       !=
Coverage Limitation
```

---

## 63. Contradictory User Input

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

Current policy may prefer the User's explicit correction.

Historical provenance must remain.

---

## 64. Assessment Version

Every assessment should identify the Assessor version where practical.

Conceptually:

```text
assessor_version:
1
```

This supports reassessment when implementation logic evolves.

---

## 65. Policy Version

If Relationship rules are stored separately from Assessor code, the result should also preserve:

```text
assessment_policy_version
```

For example:

```text
assessor_version:
2

assessment_policy_version:
2026-11
```

This distinction improves reproducibility.

The exact versioning format remains open.

---

## 66. Reassessment

Relationships must be reassessable.

Conceptually:

```text
EvidenceAggregate
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

A new assessment does not rewrite the Evidence that originally supported previous assessments.

---

## 67. Reassessment Triggers

Reassessment may be required when:

```text
new ACTIVE Evidence arrives

Evidence is deleted

Evidence becomes SUPERSEDED

Evidence becomes REJECTED

Entity Resolution changes

Service merge occurs

Service split occurs

Identity association changes

User correction occurs

ConnectedSource data is removed

assessment policy changes

Assessor version changes

coverage information materially changes
```

The exact orchestration belongs to the application layer.

---

## 68. Relationship History

If assessments change over time, historical assessments may need to be preserved.

Example:

```text
2026-01:
OBSERVED + CURRENTLY_OBSERVED

2026-04:
ESTABLISHED + CURRENTLY_OBSERVED

2026-10:
ESTABLISHED + HISTORICAL
```

A future:

```text
RelationshipAssessmentHistory
```

may preserve this sequence.

The consolidated Domain Model classifies it as:

```text
Candidate Historical Concept
```

rather than a Core Domain Entity.

The initial implementation may instead persist versioned RelationshipAssessmentResults.

---

## 69. Current Relationship vs Assessment History

The Service Graph may expose:

```text
current Relationship
```

while preserving previous RelationshipAssessmentResults for:

- explainability;
- debugging;
- policy changes;
- auditability;
- reassessment comparison.

The exact persistence model remains undefined.

---

## 70. Relationship Persistence

The RelationshipAssessor determines Relationship semantics.

It does not automatically own:

```text
creating persistent Relationship IDs
saving current Relationship state
writing assessment history
triggering graph updates
```

Those responsibilities belong to application and repository boundaries.

Conceptually:

```text
RelationshipAssessor
       |
       v
RelationshipAssessmentResult
       |
       v
Application Layer
       |
       v
Relationship Repository / Service Graph
```

---

## 71. Relationship Materialization

The consolidated model does not require a separate `RelationshipCandidate` Domain concept.

The processing boundary is already represented by:

```text
RelationshipAssessmentResult
```

Conceptually:

```text
EvidenceAggregate
       |
       v
RelationshipAssessor
       |
       v
RelationshipAssessmentResult
[Processing Result]
       |
       v
Application Layer
       |
       v
Relationship
[Core Domain Entity]
```

The application layer may materialize or update the Relationship from a successful assessment.

No additional processing abstraction is required unless implementation demonstrates a concrete need.

---

## 72. Rejected Relationship and Evidence

A REJECTED Relationship does not imply Evidence deletion.

For example:

```text
Observation:
registration email

Evidence:
ACCOUNT_VERIFICATION
ACTIVE

User:
this belonged to someone else
```

The Evidence may remain valid as an interpretation of the Observation.

The current User-Service Relationship may become:

```text
REJECTED
```

with User correction provenance.

Therefore:

```text
EvidenceStatus.REJECTED
        !=
RelationshipStatus.REJECTED
```

---

## 73. Rejected Relationship and Future Evidence

If new Evidence later arrives:

```text
PASSWORD_MANAGER_ENTRY
```

for a previously REJECTED Relationship, the framework should not automatically override the rejection.

The Relationship must be reassessed according to explicit policy.

A future policy may require:

```text
USER REVIEW
```

without introducing a new RelationshipStatus unless empirical requirements justify it.

---

## 74. Relationship Removal

A Service should not necessarily disappear from the Service Graph because current Evidence becomes weak or historical.

A historical digital footprint is part of the framework's purpose.

Possible removal may require:

- User action;
- explicit lifecycle policy;
- source-data deletion;
- retention policy;
- corrected Service resolution.

The RelationshipAssessor itself should not silently delete Services or Relationships.

---

## 75. Relationship and Service Graph

The Service Graph consumes Domain Relationships produced or updated from assessment results.

Conceptually:

```text
        Service
          ^
          |
     Relationship
          ^
          |
         User
```

The Relationship should preserve links or traceability to its supporting Evidence basis.

Conceptually:

```text
User
 |
 v
Relationship
 |
 +------------> Service
 |
 +------------> Evidence Basis
                       |
                       v
                EvidenceAggregate
                 [Derived View]
                       |
                       v
                    Evidence
```

The Aggregate itself remains rebuildable derived state.

---

## 76. Service Graph Does Not Store Absolute Truth

The Service Graph represents:

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
+
Assessment policy
```

and relative to known source coverage.

---

## 77. RelationshipAssessor Interface

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

## 78. Relationship Assessment Context

Conceptually:

```text
RelationshipAssessmentContext {

    RelationshipPolicy relationshipPolicy

    TemporalPolicy temporalPolicy

    ConflictPolicy conflictPolicy

    UserCorrectionContext userCorrections

    CoverageSummary coverage

    AssessorVersion assessorVersion

    AssessmentPolicyVersion assessmentPolicyVersion
}
```

Not every implementation needs every field initially.

CoverageSummary may already be available through the EvidenceAggregate and need not necessarily be duplicated here.

The Implementation Model should determine the cleanest boundary.

---

## 79. Relationship Assessment Result

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

    Optional<AssessmentPolicyVersion> assessmentPolicyVersion
}
```

`RelationshipAssessmentResult` is classified as:

```text
Processing Result / Value Object
```

It is not the authoritative Domain Relationship.

---

## 80. Evidence Basis

The result must identify which Evidence formed the basis of the assessment.

Conceptually:

```text
evidence_basis:

- evidence_001
- evidence_002
- evidence_003
```

For the default current Discovery view, this Evidence basis should normally reference Evidence that participated in the current EvidenceAggregate under the active EvidenceStatePolicy.

This allows assessment to remain:

- explainable;
- recalculable;
- traceable.

---

## 81. RelationshipStatus and TemporalStatus Independence

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

The Assessor must not force temporal semantics into Relationship support states.

This separation is a consolidated Domain decision.

---

## 82. Relationship Assessor Invariants

### RA-INV-001

The Assessor must operate on structured EvidenceAggregates rather than raw Provider objects.

### RA-INV-002

Relationship Assessment must remain distinct from Evidence Classification.

### RA-INV-003

Relationship Assessment must remain distinct from Entity Resolution.

### RA-INV-004

Relationship Assessment must remain distinct from Evidence Aggregation.

### RA-INV-005

A Relationship must not imply current personal-data possession.

### RA-INV-006

A Relationship must not automatically imply an Account.

### RA-INV-007

The Assessor must support RelationshipStatus UNKNOWN.

### RA-INV-008

Technical processing failure must remain distinct from RelationshipStatus UNKNOWN.

### RA-INV-009

RelationshipStatus and TemporalStatus must remain distinct dimensions.

### RA-INV-010

Historical Relationships must remain representable.

### RA-INV-011

TemporalStatus HISTORICAL must not automatically remove the Service from the Service Graph.

### RA-INV-012

Evidence frequency alone must not determine RelationshipStatus.

### RA-INV-013

Source diversity alone must not determine RelationshipStatus.

### RA-INV-014

Provider diversity alone must not determine RelationshipStatus.

### RA-INV-015

Evidence semantics must contribute to Relationship Assessment.

### RA-INV-016

Conflicting Evidence must not be silently ignored.

### RA-INV-017

The Assessor must preserve the Evidence basis for every conclusion.

### RA-INV-018

The Assessor must preserve relevant Identity references.

### RA-INV-019

Multiple Identity references must not automatically imply multiple Accounts.

### RA-INV-020

User corrections must remain attributable to the User.

### RA-INV-021

User correction must not destructively rewrite source Observations or Evidence provenance.

### RA-INV-022

The Assessor must not require Provider credentials.

### RA-INV-023

The Assessor must not directly request additional source permissions.

### RA-INV-024

Basic Relationship Assessment must not require AI.

### RA-INV-025

AI must not invent missing Evidence.

### RA-INV-026

Assessment must remain relative to the observed footprint.

### RA-INV-027

Incomplete source coverage must not be presented as complete Discovery.

### RA-INV-028

Numerical Relationship Confidence is outside the initial Discovery model.

### RA-INV-029

Relationship reassessment must be possible without destructive modification of supporting Evidence.

### RA-INV-030

Changes to assessment policy or Assessor version must remain traceable where they materially affect Relationship state.

### RA-INV-031

The primary Relationship cardinality is User-to-Service.

### RA-INV-032

Identity references must remain preserved without automatically creating separate Relationships.

### RA-INV-033

RelationshipAssessmentResult must remain distinct from the Domain Relationship.

### RA-INV-034

Persistence of RelationshipAssessmentResult must not change its classification as a Processing Result / Value Object.

### RA-INV-035

The Assessor must not own Relationship persistence merely because it determines Relationship semantics.

### RA-INV-036

EvidenceStatus.REJECTED must remain distinct from RelationshipStatus.REJECTED.

### RA-INV-037

SUPERSEDED or REJECTED Evidence excluded by the active EvidenceStatePolicy must not silently re-enter current Relationship Assessment.

### RA-INV-038

Historical semantic events must remain distinguishable from Evidence lifecycle history.

### RA-INV-039

AssessmentPolicyVersion should remain traceable when policy changes materially affect assessment.

### RA-INV-040

No additional RelationshipCandidate Domain abstraction is required by the current contract.

---

## 83. Marketing-Only Example

Aggregate:

```text
Service:
Example Shop

Evidence:
MARKETING x 25
NEWSLETTER x 8

SourceTypes:
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

The Assessor does not conclude that the User has an Account.

---

## 84. Gmail Verification Example

Aggregate:

```text
Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION x 1

SourceTypes:
EMAIL
```

Possible assessment:

```text
relationship_status:
OBSERVED
```

or:

```text
relationship_status:
ESTABLISHED
```

depending on explicit assessment policy validated during implementation.

The Domain state vocabulary itself is already consolidated.

What remains to validate is the rule mapping Evidence to those states.

---

## 85. Gmail + Password Manager Example

Aggregate:

```text
Service:
Spotify

Evidence:
ACCOUNT_VERIFICATION      1
PASSWORD_MANAGER_ENTRY    1

SourceTypes:
EMAIL
PASSWORD_MANAGER

Identity:
personal@example.com
```

A future validated policy may justify:

```text
relationship_status:
ESTABLISHED
```

because two structurally different Evidence sources support the User-Service Relationship.

However, the exact policy must be explicit and empirically validated.

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

SourceTypes:
EMAIL
```

The Assessor may conclude that a meaningful commercial Relationship existed.

It must not automatically conclude:

```text
Account existed
```

because guest purchases may be possible.

This reinforces:

```text
RELATIONSHIP != ACCOUNT
```

---

## 87. Historical Relationship Example

Aggregate:

```text
Service:
Example Service

EvidenceTimeline:

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

SourceTypes:
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

The Password Manager entry does not prove that credentials currently work.

---

## 90. Unknown Relationship Example

Aggregate:

```text
Service:
Example Service

Evidence:
weak or insufficient semantic context
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
IdentityReferences:

- personal@example.com
- oldmail@example.net
```

within one User-Service Relationship.

It must not conclude:

```text
two Spotify Accounts
```

nor create separate Relationships merely because two Identity references exist.

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

if Evidence semantics justify that status.

But explanation should include:

```text
Discovery coverage is incomplete for some configured sources.
```

This prevents the framework from overstating completeness.

---

## 94. Reassessment Example

Initial Aggregate:

```text
MARKETING
NEWSLETTER
```

Assessment:

```text
OBSERVED
```

Later ACTIVE Evidence:

```text
PASSWORD_MANAGER_ENTRY
ACCOUNT_VERIFICATION
```

New Aggregate:

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

according to explicit policy.

Original Observations and Evidence remain unchanged.

---

## 95. Service Resolution Change Example

Initially:

```text
ServiceIdentifier:
oldservice.example

Service:
UNRESOLVED

Evidence:
PAYMENT
```

A canonical User-Service Relationship may not yet be materialized.

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

RelationshipStatus:
OBSERVED
```

and:

```text
Service B

RelationshipStatus:
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

Evidence must be re-aggregated.

The Relationship must then be reassessed.

The new RelationshipStatus must not simply copy either old state.

---

## 97. Open Questions

### Relationship Assessment Policy

The RelationshipStatus vocabulary is now consolidated:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

The remaining questions are:

- Which Evidence combinations justify ESTABLISHED?
- Is one ACCOUNT_VERIFICATION sufficient?
- Is one PASSWORD_MANAGER_ENTRY sufficient?
- Which communication-only combinations remain OBSERVED?
- When may User confirmation directly justify ESTABLISHED?
- Which situations justify REJECTED without explicit User rejection?
- Should an additional state ever be introduced between OBSERVED and ESTABLISHED?
- If so, can it be given precise semantics without becoming vague probability language?

### Temporal Status

The TemporalStatus vocabulary is now consolidated:

```text
UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

The remaining questions are:

- What exact rules justify CURRENTLY_OBSERVED?
- Does age alone ever make a Relationship HISTORICAL?
- Is ENDED semantically different enough from HISTORICAL to justify a future state?
- How should recent marketing interact with old Account deletion Evidence?
- How should Service reactivation be represented?
- Which conflicts force TemporalStatus UNKNOWN?

### User vs Identity Relationship

The primary Relationship is now:

```text
User -> Service
```

The remaining questions are:

- When is IdentityServiceAssociation required?
- Can one User-Service Relationship always preserve many Identity references?
- How should unverified observed identities be represented?
- Which Identity-specific queries require independent materialization?

### Account

- When should Account be promoted to a first-class Domain Entity?
- Should Account be inferred only when account-specific Evidence exists?
- How are guest purchases represented if Account exists?
- How should shared Accounts be represented?
- How should migrated or historical Accounts be represented?

### Evidence Sufficiency

- Which Evidence combinations justify ESTABLISHED?
- Is one account-verification event sufficient?
- Is one Password Manager entry sufficient?
- How should User confirmation affect automated Evidence?
- How are false positives measured?
- How should EvidenceStatus changes affect assessment?

### Evidence Independence

- How should independence between Evidence sources be defined?
- Does EMAIL + PASSWORD_MANAGER qualify as independent by default?
- How should multiple emails generated during one registration workflow be treated?
- Does ConnectedSource diversity add value independently from SourceType diversity?

### Temporal Reasoning

- What age makes Evidence historical, if age alone should matter at all?
- How should inactive-but-not-deleted Accounts be represented?
- How should Service reactivation be represented?
- How are source-specific timestamps compared safely?
- Which TemporalSemantics may contribute to Relationship TemporalStatus?

### Conflicts

- Which conflicts require TemporalStatus UNKNOWN?
- When should conflicts request User review?
- Which conflicts affect RelationshipStatus?
- Is a dedicated conflict-resolution capability eventually necessary?

### Confidence

Numerical Relationship Confidence is outside the initial Discovery baseline.

The remaining question is whether later empirical validation demonstrates that calibrated Confidence provides measurable value beyond:

```text
RelationshipStatus
TemporalStatus
Evidence basis
Source diversity
Reason codes
Warnings
```

If introduced later:

- what exactly will Confidence measure?
- what validation dataset will calibrate it?
- how will Users interpret it?
- how will it differ from RelationshipStatus?

### Manual Input

- How should User-confirmed Relationships interact with automated assessment?
- Can a User explicitly mark a Relationship historical?
- Can User correction override later automated Evidence permanently?
- How should conflicting later Evidence trigger reassessment?

### Persistence

- Should every RelationshipAssessmentResult be stored historically?
- Should only the current Relationship be materialized?
- How are superseded assessments represented?
- How are old assessment policies audited?
- How much provenance is required?
- Which repository owns Relationship persistence?

### Service Graph

- Does the Service Graph directly store Relationships?
- Is the Graph itself derived from current Relationship entities?
- How are historical Relationships represented?
- How are REJECTED Relationships represented?
- Should REJECTED Relationships be visible to normal User-facing queries?
- How are Service merge and split operations propagated?

### Coverage

- Should incomplete source coverage always be visible to the User?
- How should Relationship explanations distinguish incomplete Discovery from uncertain Relationship semantics?
- Is CollectionRun required to provide reliable coverage?
- At what granularity should CoverageSummary be persisted?

### Relationship History

- Is persistence of versioned RelationshipAssessmentResults sufficient?
- When would RelationshipAssessmentHistory deserve promotion to an explicit concept?
- How long should historical assessments be retained?

---

## 98. Findings from Contract Design

### Finding 1 - Relationship Support and Time Are Separate Dimensions

The earlier flat state model:

```text
UNKNOWN
POSSIBLE
PROBABLE
CONFIRMED
HISTORICAL
```

mixed:

```text
support strength
```

with:

```text
temporal interpretation
```

The consolidated Domain Model therefore defines:

```text
RelationshipStatus

UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

and separately:

```text
TemporalStatus

UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

This is now a consolidated Domain decision.

### Finding 2 - Numerical Confidence Is Not Required

The combination of:

```text
RelationshipStatus
TemporalStatus
EvidenceSummary
Source diversity
Timeline
Conflicts
ReasonCodes
Warnings
```

provides an explainable assessment model without requiring an uncalibrated numerical score.

Numerical Confidence is outside the initial Discovery baseline.

### Finding 3 - Relationship Does Not Mean Account

Scenario 001 and Scenario 002 demonstrate that the framework may discover meaningful Relationships without establishing a conventional Account.

Examples include:

```text
guest purchase
newsletter
privacy communication
historical interaction
```

Therefore Account remains optional rather than foundational.

### Finding 4 - User-Service Is the Primary Relationship

The framework primarily needs to answer:

> Which Services appear to have or have had a Relationship with me?

The consolidated Domain Model therefore defines:

```text
User -> Relationship -> Service
```

as the primary Relationship.

Identity references remain preserved as supporting context.

A future `IdentityServiceAssociation` may be introduced if implementation demonstrates that an independent Domain representation is required.

### Finding 5 - Assessment Policy Must Be Explicit and Versioned

Once the framework decides:

```text
OBSERVED
```

versus:

```text
ESTABLISHED
```

those rules become significant Domain policy.

They must therefore be:

- explicit;
- testable;
- explainable;
- versionable.

### Finding 6 - Evidence Independence Requires Empirical Validation

Multiple-source support appears useful, but the framework does not yet have a rigorous definition of independent Evidence.

This should be measured using real Discovery data rather than converted immediately into arbitrary weighting.

### Finding 7 - Relationship Assessment Remains Deterministic-First

Once Evidence has been normalized, initial Relationship Assessment is primarily structured reasoning.

No current scenario demonstrates that an LLM is required for basic assessment.

### Finding 8 - RelationshipAssessmentResult Is a Processing Result

The consolidated Domain Model classifies:

```text
RelationshipAssessmentResult
```

as:

```text
Processing Result / Value Object
```

rather than a Core Domain Entity.

The application layer may use it to create or update:

```text
Relationship
```

which is the Core Domain Entity.

### Finding 9 - Relationship Persistence Is Outside the Assessor

Determining Relationship semantics does not require RelationshipAssessor to own:

```text
Relationship IDs
repositories
Service Graph writes
assessment-history storage
```

These responsibilities belong to application and persistence boundaries.

### Finding 10 - Evidence Lifecycle Affects Reassessment

Current Relationship Assessment should normally depend on Evidence included in the current EvidenceAggregate.

When Evidence becomes:

```text
SUPERSEDED
```

or:

```text
REJECTED
```

the Aggregate and resulting Relationship may require recalculation.

---

## 99. Architecture Alignment and Remaining Decision Candidates

### Architecture Alignment - Separate RelationshipStatus and TemporalStatus

Relationship support and temporal interpretation are separate dimensions.

This is formalized by:

```text
D-022 - Relationship Support and Temporal Status Are Separate
```

### Architecture Alignment - User-Service Is the Primary Relationship

The primary Relationship is:

```text
User
  |
  v
Relationship
  |
  v
Service
```

Identity references remain associated with the Relationship.

`IdentityServiceAssociation` remains a Candidate Domain Concept.

### Architecture Alignment - Avoid Uncalibrated POSSIBLE / PROBABLE States

RelationshipStatus uses explicit semantic states:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

Terms such as POSSIBLE and PROBABLE are not part of the current model because they imply an undefined probability scale.

### Architecture Alignment - Relationship Does Not Imply Account

Service Discovery models Relationships independently from Accounts.

Account may later become an optional Domain concept if cross-scenario requirements justify it.

### Architecture Alignment - Relationship Assessment Is Explainable Policy

Relationship Assessment uses explicit, versioned and explainable policy rather than hidden weighting or opaque AI reasoning.

### Architecture Alignment - No Numerical Confidence

Numerical Relationship Confidence is outside the initial Discovery baseline.

This is formalized by:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

### Architecture Alignment - Historical Relationships Remain in the Graph

Historical Relationships remain part of the observed digital footprint.

They must not be removed merely because available Evidence suggests the active Relationship ended.

### Architecture Alignment - Reassessment Is Required

Relationships must be reassessable when:

```text
Evidence changes
EvidenceStatus changes
Entity Resolution changes
Identity association changes
User correction occurs
Service merge or split occurs
assessment policy changes
```

### Architecture Alignment - RelationshipAssessmentResult Is a Processing Result

The Assessor returns:

```text
RelationshipAssessmentResult
```

which is a Processing Result / Value Object.

The application layer owns materialization of the Core Domain:

```text
Relationship
```

### Remaining Decision Candidate - Relationship Assessment Policy

The Domain state model is now consolidated.

The exact rules mapping EvidenceAggregate content into:

```text
UNKNOWN
OBSERVED
ESTABLISHED
REJECTED
```

and:

```text
UNKNOWN
CURRENTLY_OBSERVED
HISTORICAL
```

remain to be validated empirically.

These rules should be defined during the Implementation Model and tested through the Gmail Vertical MVP.

### Remaining Decision Candidate - IdentityServiceAssociation

The primary User-Service Relationship is fixed for the current baseline.

A separate IdentityServiceAssociation should be introduced only if implementation or future scenarios demonstrate requirements that Identity references within Relationship and Evidence cannot satisfy.

---

## 100. Current Contract Baseline

The aligned RelationshipAssessor contract is:

```text
EvidenceAggregate
[Derived View]
       |
       v
RelationshipAssessor
       |
       v
RelationshipAssessmentResult
[Processing Result / Value Object]
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
       |
       +-- assessment_policy_version
       |
       v
Application Layer
       |
       v
Relationship
[Core Domain Entity]
       |
       +-- User
       |
       +-- Service
       |
       +-- RelationshipStatus
       |
       +-- TemporalStatus
       |
       +-- IdentityReferences
       |
       +-- EvidenceBasis
       |
       +-- AssessmentProvenance
```

with the guarantees:

```text
Evidence-based assessment

User-Service primary Relationship

Identity references preserved

Relationship separate from Evidence

Relationship separate from Account

Relationship separate from current data possession

RelationshipStatus separate from TemporalStatus

UNKNOWN supported

OBSERVED supported

ESTABLISHED supported

REJECTED supported

CURRENTLY_OBSERVED supported

HISTORICAL supported

historical Relationships retained

conflicting Evidence preserved

source diversity available but not automatically weighted

explicit explainable assessment policy

RelationshipAssessmentResult classified as Processing Result

Relationship persistence outside RelationshipAssessor

no arbitrary numerical Confidence

deterministic-first assessment

no Provider credentials

no direct permission escalation

reassessment supported

Evidence lifecycle changes trigger reassessment where relevant

observed-footprint semantics preserved
```

---

## 101. End-to-End Discovery Contract

With this contract, the first complete Identity and Service Discovery software flow is conceptually defined:

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
    |   CLASSIFICATION RESULT
    |        |
    |        v
    |   EVIDENCE CANDIDATE
    |        |
    |        v
    |     EVIDENCE
    |     [ACTIVE]
    v        |
CANDIDATE    |
IDENTIFIER   |
    |        |
    v        |
SERVICE      |
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
    [DERIVED VIEW]
         |
         v
RELATIONSHIP ASSESSOR
         |
         v
RELATIONSHIP ASSESSMENT RESULT
    [PROCESSING RESULT]
         |
         v
  APPLICATION LAYER
         |
         v
   RELATIONSHIP
   [CORE ENTITY]
         |
         v
    SERVICE GRAPH
```

The architecture defines explicit boundaries between:

```text
ConnectedSource
Connector
Observation
Candidate Detection
ServiceIdentifier
Entity Resolution
Service
Evidence Classification
Evidence
Evidence Aggregation
EvidenceAggregate
Relationship Assessment
Relationship
```

and preserves:

```text
Provider independence

source provenance

Evidence lifecycle

explicit uncertainty

reprocessing

re-resolution

re-aggregation

reassessment

Progressive Permission

local-first operation

deterministic-first processing
```

The seven primary Discovery contracts are now conceptually aligned with Architecture v0.3 and Domain Model v0.3.

---

## 102. Next Design Step

The first Identity and Service Discovery architecture-consolidation cycle is now complete.

The repository now contains aligned conceptual definitions for:

```text
Architecture v0.3
        |
        v
Domain Model v0.3
        |
        v
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

The next step is not to introduce another processing contract.

The next repository task is:

```text
README alignment
```

so that the repository entry point reflects the actual state of the project.

After README alignment, the project should move into:

```text
Implementation Model
```

which should translate the consolidated conceptual design into concrete software boundaries such as:

```text
Domain types
Value objects
Enums
Python Protocols or ABCs
Processing Result objects
Repository interfaces
ServiceRegistry interface
Observation payload types
Evidence taxonomy
Assessment policies
Application orchestration
Package dependencies
```

The Implementation Model must preserve the dependency direction established by the contracts rather than collapsing the system into Provider-specific application logic.

The first empirical implementation should then be:

```text
Gmail Vertical MVP
```

Conceptually:

```text
Gmail
  |
  v
GmailConnector
  |
  v
EMAIL_MESSAGE_METADATA Observation
  |
  +-------------------------+
  |                         |
  v                         v
Candidate Detection    Evidence Classification
  |                         |
  v                         v
ServiceIdentifier          Evidence
  |                         |
  v                         |
EntityResolver              |
  |                         |
  v                         |
Service --------------------+
            |
            v
EvidenceAggregator
            |
            v
EvidenceAggregate
            |
            v
RelationshipAssessor
            |
            v
Relationship
            |
            v
MVP Service Graph / Output
```

This Vertical MVP should validate the implementation model against real Gmail-derived data while preserving:

```text
metadata-first collection

Progressive Permission

Provider isolation

data minimization

deterministic-first processing

UNKNOWN / UNRESOLVED / AMBIGUOUS states

EvidenceStatus lifecycle

RelationshipStatus / TemporalStatus separation

no numerical Confidence

explainability

provenance
```

Any architecture refinement after that point should be driven primarily by implementation evidence and empirical Discovery behavior rather than by introducing additional abstractions in advance.

The Relationship Assessor Contract is now aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- User-Service as the primary Relationship;
- Identity references as supporting context;
- consolidated RelationshipStatus;
- consolidated TemporalStatus;
- D-022 separation of support and temporal state;
- EvidenceStatus lifecycle;
- EvidenceAggregate as a Derived View;
- RelationshipAssessmentResult as a Processing Result / Value Object;
- Relationship as a Core Domain Entity;
- reassessment semantics;
- D-023 exclusion of numerical Confidence;
- deterministic-first and local-first Discovery.

No additional Relationship Assessment abstraction is required before the Implementation Model phase.
