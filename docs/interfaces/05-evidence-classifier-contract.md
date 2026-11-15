# Evidence Classifier Contract

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

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `EvidenceClassifier` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Evidence Classifier interprets an Observation and determines what semantic Evidence, if any, that Observation provides about a possible Relationship between the User and a Service.

Conceptually:

```text
Observation
      |
      v
Evidence Classifier
      |
  +---+----------------+
  |                    |
  v                    v
Evidence             UNKNOWN
```

For example:

```text
Observation:

Subject:
Verify your email address
```

may produce:

```text
Evidence:
ACCOUNT_VERIFICATION
```

Similarly:

```text
Observation:
Password Manager Entry

URI:
https://accounts.spotify.com
```

may produce:

```text
Evidence:
PASSWORD_MANAGER_ENTRY
```

The Evidence Classifier answers:

> What does this Observation appear to mean in the context of Service Discovery?

It does not determine:

- whether the Observation is relevant to Service Discovery;
- which canonical Service the Observation refers to;
- whether the User has an ESTABLISHED Relationship with that Service;
- the overall strength of the Relationship;
- what personal data the Service currently holds.

---

## 2. Architectural Position

Evidence Classification operates on Observations after they have crossed the Connector boundary.

It forms a semantic-processing branch separate from Entity Resolution.

Conceptually:

```text
                         Observation
                         /         \
                        /           \
                       v             v
          Candidate Detection    Evidence Classification
                       |             |
                       v             v
            CandidateIdentifier    Evidence
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
                            |
                            v
                   Relationship Assessment
```

Entity Resolution asks:

> Which Service does this appear to represent?

Evidence Classification asks:

> What does this Observation appear to tell us about the Relationship?

These questions must remain separate.

---

## 3. Fundamental Boundary

The central distinction is:

```text
OBSERVATION != EVIDENCE
```

An Observation represents source-derived information.

Evidence represents the framework's semantic interpretation of that information.

For example:

```text
Observation

sender:
no-reply@spotify.com

subject:
Your password has been changed
```

may produce:

```text
Evidence

type:
PASSWORD_RESET
```

The original Observation must remain preserved independently from its interpretation.

---

## 4. Evidence Classification Is Not Candidate Detection

Candidate Detection asks:

> Should this Observation participate in Service Discovery?

Evidence Classification asks:

> What does this Observation mean?

Example:

```text
Observation:

sender:
no-reply@spotify.com

subject:
Verify your email address
```

Candidate Detection:

```text
CANDIDATE
```

Evidence Classification:

```text
ACCOUNT_VERIFICATION
```

Therefore:

```text
CANDIDATE STATUS
        !=
EVIDENCE TYPE
```

---

## 5. Evidence Classification Is Not Entity Resolution

Consider:

```text
Observation:

sender:
no-reply@spotify.com

subject:
Verify your email address
```

Entity Resolution may determine:

```text
spotify.com
      |
      v
Spotify
```

Evidence Classification may determine:

```text
Verify your email address
      |
      v
ACCOUNT_VERIFICATION
```

These conclusions are independent.

Therefore:

```text
SERVICE IDENTITY
       !=
EVIDENCE SEMANTICS
```

---

## 6. Evidence Classification Is Not Relationship Assessment

An individual Evidence item does not determine the complete Relationship.

For example:

```text
Evidence:
MARKETING
```

does not imply:

```text
RelationshipStatus:
ESTABLISHED
```

Similarly:

```text
Evidence:
PASSWORD_MANAGER_ENTRY
```

does not independently prove:

```text
ACTIVE ACCOUNT
```

Relationship Assessment operates later on accumulated Evidence.

Therefore:

```text
EVIDENCE != RELATIONSHIP
```

---

## 7. Input Contract

The minimum Evidence Classifier input is a valid framework Observation.

Conceptually:

```text
classify(
    observation,
    context
)
    ->
ClassificationResult
```

The classifier should consume only the minimum information necessary to interpret the Observation.

It must not require:

- Provider credentials;
- Provider-specific raw objects;
- unrelated Observations;
- unrestricted ConnectedSource access.

---

## 8. Classification Context

Some classification may require explicit supporting context.

Conceptually:

```text
ClassificationContext

- taxonomy
- rules
- language_context
- policy
- model_configuration
```

The exact structure remains open.

The context should not provide unrestricted access to unrelated User data.

---

## 9. Classification Result

A simple:

```text
EvidenceType
```

is insufficient.

The framework should also preserve:

- processing success;
- classification status;
- method;
- reason codes;
- classifier version;
- resulting Evidence items.

The initial conceptual result is:

```text
ClassificationResult

- observation_id
- processing_status
- classification_status
- evidence_items
- method
- reason_codes
- classifier_version
```

This is implementation-independent.

The consolidated Domain Model classifies:

```text
ClassificationResult
```

as:

```text
Processing Result
```

rather than a Core Domain Entity.

A ClassificationResult may be persisted for provenance, reprocessing comparison, debugging or auditability without changing this classification.

---

## 10. Processing Status

Technical processing state must remain separate from semantic classification state.

Potential conceptual processing states include:

```text
SUCCESS
UNSUPPORTED
FAILED
```

For example:

```text
processing_status:
SUCCESS

classification_status:
UNKNOWN
```

means:

> The classifier successfully processed the Observation but could not determine its semantic meaning.

This is different from:

```text
processing_status:
FAILED
```

---

## 11. Classification Status

The minimum classification states are:

```text
CLASSIFIED
UNKNOWN
```

Additional states may eventually become justified.

### CLASSIFIED

One or more semantic Evidence items were produced.

### UNKNOWN

The Observation was successfully processed, but available information was insufficient for justified classification.

`UNKNOWN` is a valid Domain outcome.

---

## 12. UNKNOWN Is Not Failure

The framework must preserve the architectural principle:

```text
UNKNOWN IS VALID
```

For example:

```text
Subject:
Important information about your account
```

may be insufficient to distinguish between:

```text
SECURITY_NOTIFICATION
ACCOUNT_UPDATE
PRIVACY_NOTICE
OTHER
```

The correct outcome may therefore be:

```text
processing_status:
SUCCESS

classification_status:
UNKNOWN
```

rather than forcing one category.

---

## 13. Unsupported Is Not UNKNOWN

An unsupported ObservationType represents a processing capability limitation.

Example:

```text
observation_type:
FUTURE_FINANCIAL_RECORD
```

when no classification strategy exists.

The correct outcome may be:

```text
processing_status:
UNSUPPORTED
```

This differs from:

```text
processing_status:
SUCCESS

classification_status:
UNKNOWN
```

Therefore:

```text
UNSUPPORTED != UNKNOWN
```

---

## 14. Evidence

An Evidence item represents a semantic interpretation supported by one or more Observations.

Evidence is a Core Domain Entity.

Conceptually:

```text
Evidence

- id
- evidence_type
- evidence_status
- supporting_observation_references
- service_reference
- identity_references
- classification_method
- classifier_version
- reason_codes
- temporal_values
- created_at
- provenance
```

The final persistent structure remains undefined.

Evidence answers:

> What does the observed information appear to tell the framework about a possible User-Service Relationship?

It does not represent objective truth.

Therefore:

```text
OBSERVATION != EVIDENCE

EVIDENCE != CONFIRMED FACT

EVIDENCE != RELATIONSHIP
```

The `evidence_status` field represents whether a particular Evidence interpretation participates in the current Discovery assessment.

The consolidated initial lifecycle states are:

```text
ACTIVE
SUPERSEDED
REJECTED
```

---

### 14.1 Evidence Lifecycle

Evidence has an explicit lifecycle independent from the Observation that supports it.

The consolidated initial model is:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

#### ACTIVE

`ACTIVE` means that the Evidence represents a currently accepted semantic interpretation.

Only ACTIVE Evidence should normally participate in:

```text
Current Evidence Aggregation
        |
        v
Relationship Assessment
```

#### SUPERSEDED

`SUPERSEDED` means that an Evidence interpretation has been replaced by a newer accepted interpretation.

Example:

```text
Observation
    |
    +--> Evidence A
    |      EvidenceType: MARKETING
    |      EvidenceStatus: SUPERSEDED
    |
    +--> Evidence B
           EvidenceType: PRIVACY_NOTICE
           EvidenceStatus: ACTIVE
```

Evidence A remains available for provenance.

It must not normally be counted as simultaneous current Evidence.

#### REJECTED

`REJECTED` means that an Evidence interpretation has been explicitly invalidated.

Possible reasons may include:

- User correction;
- classification error;
- invalid source association;
- processing defect;
- later information demonstrating that the interpretation was incorrect.

Rejected Evidence may remain preserved where required for provenance.

It must not participate in current Relationship Assessment.

Therefore:

```text
EvidenceStatus.REJECTED
        !=
RelationshipStatus.REJECTED
```

The first refers to acceptance of an Evidence interpretation.

The second refers to attribution of the User-Service Relationship.

The exact lifecycle-transition policy remains open.

---

## 15. Evidence Type

EvidenceType identifies what the Observation semantically represents.

Examples emerging from Scenario 001 include:

```text
ACCOUNT_CREATION
ACCOUNT_VERIFICATION
AUTHENTICATION
PASSWORD_RESET
SECURITY_NOTIFICATION
PURCHASE
INVOICE
SUBSCRIPTION
PAYMENT
ACCOUNT_UPDATE
ACCOUNT_DELETION
MARKETING
NEWSLETTER
PRIVACY_NOTICE
```

Scenario 002 introduced:

```text
PASSWORD_MANAGER_ENTRY
```

These examples do not yet define the universal or final Evidence taxonomy.

---

## 16. Evidence Taxonomy

The framework needs a controlled Evidence taxonomy.

Conceptually:

```text
Evidence Taxonomy

ACCOUNT
  |
  +-- ACCOUNT_CREATION
  +-- ACCOUNT_VERIFICATION
  +-- ACCOUNT_UPDATE
  +-- ACCOUNT_DELETION

AUTHENTICATION
  |
  +-- AUTHENTICATION
  +-- PASSWORD_RESET
  +-- SECURITY_NOTIFICATION

COMMERCIAL
  |
  +-- PURCHASE
  +-- INVOICE
  +-- PAYMENT
  +-- SUBSCRIPTION

COMMUNICATION
  |
  +-- MARKETING
  +-- NEWSLETTER
  +-- PRIVACY_NOTICE

SOURCE-SPECIFIC
  |
  +-- PASSWORD_MANAGER_ENTRY
```

This hierarchy is illustrative.

Draft v0.1 does not establish a finalized hierarchical taxonomy.

---

## 17. Common vs Source-Specific Evidence Types

An important design question is whether EvidenceTypes should always be source-independent.

Some categories are naturally semantic and cross-source:

```text
ACCOUNT_VERIFICATION
PAYMENT
SUBSCRIPTION
ACCOUNT_DELETION
```

Others may describe the existence of a source record itself:

```text
PASSWORD_MANAGER_ENTRY
```

The framework should therefore permit both:

```text
common semantic EvidenceTypes
```

and, where justified:

```text
source-specific EvidenceTypes
```

Source-specific categories should not be introduced merely because it is easier than semantic interpretation.

---

## 18. Observation Type Does Not Determine Evidence Type

The mapping is not:

```text
EMAIL_MESSAGE_METADATA
      =
one EvidenceType
```

The same ObservationType may produce many EvidenceTypes.

For example:

```text
EMAIL_MESSAGE_METADATA
        |
        +-- ACCOUNT_VERIFICATION
        |
        +-- PASSWORD_RESET
        |
        +-- SECURITY_NOTIFICATION
        |
        +-- PAYMENT
        |
        +-- MARKETING
        |
        +-- UNKNOWN
```

Similarly, future ObservationTypes may contribute EvidenceTypes already used by other sources.

---

## 19. One Observation May Produce Multiple Evidence Items

A single Observation may provide more than one semantic signal.

For example:

```text
Subject:
Your subscription was renewed and payment received
```

could potentially support:

```text
SUBSCRIPTION
PAYMENT
```

Therefore the classifier should not assume:

```text
1 Observation = 1 EvidenceType
```

The result may contain:

```text
evidence_items:
- SUBSCRIPTION
- PAYMENT
```

when multiple classifications are independently justified.

---

## 20. Multiple Evidence Items Must Be Independently Justified

The classifier must not produce multiple categories merely because they are related.

For example:

```text
ACCOUNT_VERIFICATION
```

must not automatically imply:

```text
ACCOUNT_CREATION
```

unless the Observation itself justifies both conclusions.

Likewise:

```text
PAYMENT
```

does not automatically imply:

```text
PURCHASE
```

Semantic implications should not be silently fabricated.

---

## 21. One Evidence Item from Multiple Observations

The inverse relationship may eventually be useful.

For example:

```text
Observation A
Observation B
      |
      v
Evidence
```

However, Draft v0.1 keeps the classifier primarily Observation-oriented.

Cross-Observation reasoning may belong more naturally to:

```text
Evidence Aggregation
```

or a future correlation stage.

The boundary should be revisited only when real scenarios require it.

---

## 22. Deterministic Classification

Clear semantic patterns should be classified deterministically whenever practical.

Example:

```text
Subject:
Verify your email address
```

may match:

```text
ACCOUNT_VERIFICATION
```

Similarly:

```text
Subject:
Reset your password
```

may match:

```text
PASSWORD_RESET
```

Benefits include:

- predictable behavior;
- reproducibility;
- explainability;
- testability;
- low computational cost;
- privacy;
- offline operation.

---

## 23. Rule-Based Classification

A deterministic classifier may use:

```text
exact matches
normalized string matches
regular expressions
token rules
source-aware patterns
language-specific rules
structured payload attributes
```

Rules should be:

- explicit;
- versionable;
- testable;
- traceable.

Material changes to rules should allow reclassification of preserved Observations.

---

## 24. Classification Strategy by Observation Type

Different ObservationTypes may require different strategies.

Conceptually:

```text
EvidenceClassifier
        |
        +-- EmailMetadataClassifier
        |
        +-- PasswordManagerEntryClassifier
        |
        +-- BrowserObservationClassifier
        |
        +-- ManualObservationClassifier
```

Strategy should generally follow:

```text
ObservationType
```

rather than:

```text
Provider
```

Equivalent Gmail and Outlook email metadata should be classifiable through the same semantic strategy when their Observation payload contracts are compatible.

---

## 25. Provider Independence

The preferred model is:

```text
GmailConnector --------+
                       |
OutlookConnector ------+
                       |
ICloudConnector -------+--> EMAIL_MESSAGE_METADATA
                       |            |
ProtonConnector -------+            v
                              Email Evidence Classifier
```

not:

```text
GmailEvidenceClassifier
OutlookEvidenceClassifier
ICloudEvidenceClassifier
ProtonEvidenceClassifier
```

unless concrete semantic differences make Provider-specific behavior necessary.

---

## 26. Password Manager Classification

Scenario 002 demonstrates a case where classification may be mostly deterministic.

For example:

```text
ObservationType:
PASSWORD_MANAGER_ENTRY_METADATA
```

associated with a valid Service candidate may produce:

```text
PASSWORD_MANAGER_ENTRY
```

without requiring natural-language interpretation.

This reinforces:

> Classification complexity should follow Observation semantics rather than forcing AI into every source.

---

## 27. AI-Assisted Classification

AI may assist when deterministic logic cannot safely classify semantic ambiguity.

Conceptually:

```text
Observation
      |
      v
Deterministic Classifier
      |
  +---+---+
  |       |
  v       v
Classified Ambiguous
          |
          v
     AI Classifier
          |
      +---+---+
      |       |
      v       v
 Classified UNKNOWN
```

AI is an escalation mechanism for ambiguity.

It is not the default classifier for all Observations.

---

## 28. AI Is Optional

Core Discovery must function without AI.

If AI is:

- unavailable;
- disabled;
- rejected by the User;
- unsupported;
- incompatible with privacy policy;

deterministic classification continues.

Ambiguous Observations may remain:

```text
UNKNOWN
```

This is acceptable.

---

## 29. AI Input Minimization

AI-assisted classification must receive only the minimum required information.

For example:

```text
sender
subject
```

may be sufficient for an ambiguous email classification.

The classifier should not automatically send:

```text
entire mailbox
full message history
all User identities
password-manager data
unrelated email bodies
```

to a model.

Provider credentials must never be AI input.

---

## 30. AI and Progressive Permission

AI classification must not silently trigger permission escalation.

Suppose metadata contains:

```text
Subject:
Important information about your account
```

and cannot be classified.

The classifier may return:

```text
UNKNOWN
```

The EvidenceClassifier itself must not automatically retrieve the message body.

Conceptually:

```text
EvidenceClassifier
       |
       X
request Gmail body permission
```

If additional source information is justified, a higher-level capability may initiate a Progressive Permission decision.

---

## 31. Message Content as Separate Observation

If the User later authorizes access to message content, the preferred architecture is not:

```text
Classifier secretly retrieves body
```

Instead:

```text
Additional Permission
      |
      v
Connector
      |
      v
EMAIL_MESSAGE_CONTENT Observation
      |
      v
EvidenceClassifier
```

This preserves:

- authorization boundaries;
- provenance;
- reprocessing;
- explainability.

---

## 32. Metadata and Content Correlation

A metadata Observation and content Observation may refer to the same underlying source message.

Conceptually:

```text
EMAIL_MESSAGE_METADATA
         |
         +-- source_reference = message_123

EMAIL_MESSAGE_CONTENT
         |
         +-- source_reference = message_123
```

A future correlation mechanism may allow richer classification.

The exact correlation contract remains outside Draft v0.1.

---

## 33. Attachments

Attachments should not be automatically consumed for Evidence Classification when metadata or content is sufficient.

If a future capability requires attachment interpretation:

```text
Attachment
     |
     v
authorized Observation
     |
     v
classifier
```

should remain permission-controlled.

Basic Service Discovery does not currently require attachment content.

---

## 34. Language Detection

Email and other textual Observations may be multilingual.

For example:

```text
Verify your email address
Verifica il tuo indirizzo email
Vérifiez votre adresse e-mail
```

may all represent:

```text
ACCOUNT_VERIFICATION
```

Classification should therefore eventually support multilingual input.

Language detection may be:

- deterministic;
- library-based;
- model-assisted;
- inferred from source information.

Draft v0.1 does not prescribe the implementation.

---

## 35. Language Must Not Change Evidence Semantics

Equivalent source semantics expressed in different languages should ideally map to the same canonical EvidenceType.

For example:

```text
Italian:
PASSWORD RESET semantic

English:
PASSWORD RESET semantic
```

should both produce:

```text
PASSWORD_RESET
```

rather than language-specific EvidenceTypes.

---

## 36. Classification Method

Every classified Evidence item should preserve the method used.

Potential conceptual methods include:

```text
RULE
AI
MANUAL
COMPOSITE
```

For deterministic rule-based classification:

```text
classification_method:
RULE
```

For AI-assisted semantic classification:

```text
classification_method:
AI
```

If deterministic logic and AI jointly produce the result:

```text
classification_method:
COMPOSITE
```

may eventually be appropriate.

---

## 37. Classifier Version

Classification results should preserve the classifier version where practical.

Conceptually:

```text
classifier_version:
1
```

This supports reclassification.

Example:

```text
Classifier v1:
UNKNOWN

Classifier v2:
PRIVACY_NOTICE
```

The Observation remains unchanged.

A new classifier version producing a different accepted semantic interpretation should normally result in a new Evidence interpretation rather than destructive replacement of existing Evidence.

The Evidence lifecycle then determines which interpretation is current.

---

## 38. Rule Version

If the classifier relies on rule packs whose evolution materially changes classifications, rule version may also need provenance.

Conceptually:

```text
classifier_version:
2

rule_set_version:
2026-11
```

Draft v0.1 does not require a specific versioning format.

The principle is that materially different classification logic should remain traceable.

---

## 39. Model Version

AI-assisted classification may similarly require model provenance.

Potential information includes:

```text
provider type
model identifier
model version
classifier policy version
```

However, this information must not create Provider lock-in inside the core Evidence model.

A generic classification provenance structure may be preferable.

---

## 40. Evidence Provenance

Every Evidence item must remain traceable to its source Observation.

Conceptually:

```text
ConnectedSource
       |
       v
Observation
       |
       v
Evidence Classification
       |
       v
Evidence
```

At minimum:

```text
Evidence
    |
    +-- supporting Observation
    |
    +-- EvidenceType
    |
    +-- EvidenceStatus
    |
    +-- classification method
    |
    +-- classifier version
```

must remain reconstructable.

The current Evidence lifecycle state must also remain attributable.

---

## 41. Service Reference

Evidence may eventually reference the Service to which it applies.

However, Entity Resolution and Evidence Classification may complete independently.

Possible situation:

```text
Evidence Classification:
ACCOUNT_VERIFICATION

Entity Resolution:
UNRESOLVED
```

The Evidence remains useful.

Therefore:

```text
EVIDENCE
   !=
REQUIRES RESOLVED SERVICE
```

An Evidence item may temporarily exist without a canonical Service reference.

Association with a Service and Evidence lifecycle are independent concerns.

Therefore:

```text
ACTIVE Evidence
+
UNRESOLVED Service
```

is a valid state.

---

## 42. Resolved Service Later

If Entity Resolution later succeeds:

```text
previous Evidence
       |
       v
associate with
       |
       v
Service
```

should be possible without reclassifying the original Observation if its Evidence semantics have not changed.

This separation is an important architectural property.

---

## 43. Classification Before Resolution

Evidence Classification may execute before Entity Resolution.

Example:

```text
Observation:

Subject:
Reset your password

Sender:
unknown@oldservice.example
```

Classification:

```text
PASSWORD_RESET
```

Resolution:

```text
UNRESOLVED
```

The framework still learns that the Observation appears to describe a password-reset event associated with an unresolved Service candidate.

This is valid.

---

## 44. Resolution Before Classification

The reverse is also possible.

Example:

```text
sender:
billing@spotify.com
```

Entity Resolution may establish:

```text
Spotify
```

while the subject remains:

```text
Important update
```

Evidence may remain:

```text
UNKNOWN
```

Again, this is valid.

The two components must therefore not depend unnecessarily on each other's successful output.

---

## 45. Evidence Validity

Evidence represents interpretation rather than objective truth.

For example:

```text
Evidence:
ACCOUNT_VERIFICATION
```

means:

> The classifier interpreted the Observation as account-verification Evidence.

It does not mean:

> The User definitely created and verified an account.

Therefore:

```text
EVIDENCE TYPE
      !=
CONFIRMED REAL-WORLD EVENT
```

This distinction must remain explicit.

---

## 46. Account Creation vs Verification

A verification message may follow account creation.

However:

```text
ACCOUNT_VERIFICATION
```

must not automatically generate:

```text
ACCOUNT_CREATION
```

unless the Observation independently justifies that classification.

The classifier must avoid converting likely real-world sequences into unsupported facts.

---

## 47. Password Reset Evidence

Similarly:

```text
PASSWORD_RESET
```

may represent:

```text
reset requested
reset link issued
password changed
```

depending on source semantics.

The initial Evidence taxonomy may eventually require more granular types if scenarios demonstrate that these distinctions matter.

Draft v0.1 does not prematurely introduce them.

---

## 48. Marketing

Marketing communication may produce:

```text
MARKETING
```

This is valid Evidence of communication.

It is not automatically Evidence of:

```text
ACTIVE ACCOUNT
SUBSCRIPTION
PURCHASE
```

Those conclusions require independent Evidence.

---

## 49. Newsletter

A recurring newsletter may produce:

```text
NEWSLETTER
```

Newsletter membership should not automatically be interpreted as:

```text
ACCOUNT
```

or:

```text
SUBSCRIPTION
```

where SUBSCRIPTION refers to a paid or Service subscription.

Taxonomy semantics must remain explicit to avoid semantic overlap.

---

## 50. Payment and Purchase

Payment-related communication may represent:

```text
PAYMENT
```

while order confirmation may represent:

```text
PURCHASE
```

These categories may overlap in one Observation but should not be treated as synonyms.

A guest transaction may produce:

```text
PURCHASE
PAYMENT
```

without proving:

```text
ACCOUNT_CREATION
```

---

## 51. Privacy Notice

A privacy communication may produce:

```text
PRIVACY_NOTICE
```

This may be relevant to the User's Relationship with the Service.

However, it does not independently prove:

```text
active account
current personal-data possession
```

Those are downstream concerns.

---

## 52. Account Deletion

Evidence such as:

```text
Your account has been deleted
```

may produce:

```text
ACCOUNT_DELETION
```

This Evidence is particularly relevant for historical Relationship Assessment.

However, it does not independently prove:

```text
all personal data erased
```

or:

```text
no legal retention remains
```

Those questions belong to later framework capabilities.

---

## 53. Password Manager Entry

A valid Service-oriented password-manager record may produce:

```text
PASSWORD_MANAGER_ENTRY
```

This indicates that the authorized source contains a credential-style entry associated with the Service candidate.

It does not independently prove:

```text
credentials still valid
account currently active
User exclusively owns account
Service still stores personal data
```

---

## 54. Manual Classification

Some Evidence may be introduced or corrected manually by the User.

Potential method:

```text
MANUAL
```

For example:

```text
User:
"This email was actually a newsletter."
```

could eventually override or supplement an automated classification.

User corrections must remain attributable to the User.

---

## 55. User Correction

Suppose:

```text
Classifier v1:
MARKETING
```

and the User corrects:

```text
NEWSLETTER
```

The framework must not destroy:

```text
original Observation

original automated classification provenance
```

The consolidated Evidence lifecycle allows the framework to preserve:

```text
Automated Evidence
EvidenceType: MARKETING
EvidenceStatus: SUPERSEDED or REJECTED
        |
        v
User Correction
        |
        v
Current Evidence
EvidenceType: NEWSLETTER
EvidenceStatus: ACTIVE
```

The exact rule determining whether the earlier Evidence becomes:

```text
SUPERSEDED
```

or:

```text
REJECTED
```

remains part of the Evidence lifecycle policy.

User corrections must remain attributable to the User.

---

## 56. Reclassification

Preserved Observations should support later reclassification.

Conceptually:

```text
Observation
    |
    +--> Classifier v1
    |         |
    |         v
    |      UNKNOWN
    |
    +--> Classifier v2
              |
              v
       SECURITY_NOTIFICATION
```

This must not require destructive modification of the Observation.

If a later classifier produces a new accepted semantic interpretation, the previous accepted Evidence should normally cease to participate as current Evidence.

Conceptually:

```text
Classifier v1
      |
      v
Evidence A
      |
      v
SUPERSEDED / REJECTED

Classifier v2
      |
      v
Evidence B
SECURITY_NOTIFICATION
      |
      v
ACTIVE
```

The exact transition depends on why the previous interpretation is no longer accepted.

---

## 57. Changed Classification

A later classifier may disagree with an earlier classifier.

Example:

```text
Classifier v1:
MARKETING

Classifier v2:
PRIVACY_NOTICE
```

The framework must preserve both processing histories while identifying which semantic interpretation is currently accepted.

The consolidated lifecycle representation is conceptually:

```text
Observation
    |
    +--> Evidence A
    |      type: MARKETING
    |      status: SUPERSEDED
    |
    +--> Evidence B
           type: PRIVACY_NOTICE
           status: ACTIVE
```

Alternatively, when the previous interpretation is determined to be invalid rather than merely replaced:

```text
Evidence A
type: MARKETING
status: REJECTED
```

may be appropriate.

Therefore the framework distinguishes between:

```text
historical interpretation
```

and:

```text
current accepted interpretation
```

Downstream current aggregation should normally consume only ACTIVE Evidence.

---

## 58. Evidence Replacement and Lifecycle

Reclassification should normally preserve historical Evidence rather than destructively overwrite it.

Conceptually:

```text
Observation
    |
    +--> Evidence A
    |      EvidenceType: MARKETING
    |      EvidenceStatus: SUPERSEDED
    |
    +--> Evidence B
           EvidenceType: PRIVACY_NOTICE
           EvidenceStatus: ACTIVE
```

The exact persistence mechanism remains open.

Possible implementation strategies may eventually include:

```text
separate Evidence records

versioned Evidence records

ClassificationResult history
+
materialized current Evidence
```

However, the semantic requirement is established:

```text
historical interpretation
        !=
currently accepted interpretation
```

and:

```text
SUPERSEDED Evidence
        !=
ACTIVE Evidence
```

Silent destructive replacement is incompatible with the framework's provenance requirements.

The Implementation Model must choose a persistence mechanism that preserves this distinction.

---

## 59. Duplicate Evidence

Repeated classification of the same unchanged Observation with the same classifier should not necessarily create uncontrolled duplicate Evidence.

Conceptually:

```text
Observation A
+
Classifier v1
+
same rule set
        |
        v
same logical classification
```

Persistence and idempotency semantics remain to be defined.

Evidence lifecycle and duplicate detection must remain separate.

For example:

```text
Evidence A:
PAYMENT / ACTIVE

Evidence B:
PAYMENT / SUPERSEDED
```

does not necessarily represent two payment events.

Likewise, two independently ACTIVE Evidence items must not automatically be deduplicated solely because they share the same EvidenceType.

---

## 60. Evidence Identity

Evidence identity may depend on factors such as:

```text
supporting Observation
EvidenceType
Classifier Version
Classification Method
```

The exact identity model remains open.

The contract requires only that duplicate execution be distinguishable from genuinely new semantic Evidence.

EvidenceStatus should normally not define Evidence identity by itself.

A lifecycle transition such as:

```text
ACTIVE -> SUPERSEDED
```

does not necessarily create a different semantic source event.

The exact persistent identity rules remain an Implementation Model decision.

---

## 61. Classification Reason Codes

Classification results should support machine-readable reason codes where useful.

Potential examples include:

```text
EXACT_SUBJECT_PATTERN
SEMANTIC_RULE_MATCH
STRUCTURED_SOURCE_TYPE
MULTIPLE_MATCHES
INSUFFICIENT_INFORMATION
AMBIGUOUS_LANGUAGE
AI_CLASSIFICATION
USER_CORRECTION
```

These are illustrative.

Reason codes should improve explainability without becoming a substitute for EvidenceType itself.

---

## 62. Rule Match Provenance

For deterministic classifications, it may be useful to retain which rule produced the classification.

Conceptually:

```text
method:
RULE

rule_id:
EMAIL_ACCOUNT_VERIFICATION_001
```

This supports:

- debugging;
- testing;
- explanation;
- rule updates.

Rule identifiers should not encode sensitive Observation content.

---

## 63. AI Classification Provenance

For AI-assisted classification, provenance may need to include:

```text
classification_method:
AI

classifier_policy_version:
...

model_reference:
...
```

The full prompt or raw Observation content should not automatically be retained solely for provenance.

Privacy and reproducibility must be balanced.

---

## 64. No Chain-of-Thought Requirement

AI classification provenance should capture:

- input category;
- output;
- model reference where appropriate;
- classifier policy version;
- reason code or concise explanation where useful.

It should not depend on storing private internal reasoning from an AI model.

Explainability should be based on observable inputs, rules, outputs and concise justifications.

---

## 65. Classification Errors

Technical failures must remain separate from semantic UNKNOWN.

Examples include:

```text
rule engine failure
corrupt taxonomy
model invocation failure
invalid payload
unsupported schema
unexpected classifier exception
```

These should produce:

```text
processing_status:
FAILED
```

or:

```text
UNSUPPORTED
```

rather than semantic UNKNOWN.

A technical classification failure must not automatically change the lifecycle state of previously valid Evidence.

For example:

```text
Existing Evidence:
ACTIVE

New Classification Attempt:
FAILED
```

must not implicitly become:

```text
Existing Evidence:
REJECTED
```

Lifecycle transitions require explicit semantic or policy justification.

---

## 66. Invalid Observation

Structurally invalid Observations should normally be rejected before classification.

Conceptually:

```text
Invalid Observation
       |
       X
EvidenceClassifier
```

If an invalid Observation reaches the classifier, this is a processing problem.

It must not be interpreted as:

```text
UNKNOWN Evidence
```

---

## 67. Unsupported Observation Type

A classifier may not support a newly introduced ObservationType.

For example:

```text
FINANCIAL_TRANSACTION_METADATA
```

before a corresponding strategy exists.

The result should distinguish:

```text
processing_status:
UNSUPPORTED
```

from:

```text
classification_status:
UNKNOWN
```

---

## 68. Unsupported Schema Version

A classifier may support:

```text
EMAIL_MESSAGE_METADATA v1
```

but not yet:

```text
EMAIL_MESSAGE_METADATA v3
```

This should be represented as an unsupported processing case rather than misclassifying the payload.

ObservationType and SchemaVersion must both be considered.

---

## 69. Batch Processing

An implementation may classify Observations in batches.

Conceptually:

```text
classify_many(observations)
```

may be useful for performance.

Each Observation must still receive independently traceable Results.

Batch processing must not destroy:

```text
Observation -> ClassificationResult
```

provenance.

---

## 70. Statelessness

Where practical, classification should behave as a function of:

```text
Observation
+
Classification Context
+
Classifier Version
```

This supports reproducibility.

Hidden mutable state should be minimized.

---

## 71. Cross-Observation Context

Some classifications may eventually benefit from related Observations.

For example:

```text
Email A:
Your trial has started

Email B:
Your subscription payment succeeded
```

Together they may provide richer context.

However, Draft v0.1 keeps the EvidenceClassifier primarily Observation-oriented.

Cross-Observation reasoning should initially remain in:

```text
Evidence Aggregation
```

or a future correlation component.

This avoids making the classifier responsible for mailbox-wide reasoning.

---

## 72. Classification and Service Context

Evidence Classification should generally rely on Observation semantics rather than canonical Service identity.

For example:

```text
Verify your email address
```

remains:

```text
ACCOUNT_VERIFICATION
```

whether the Service is:

```text
Spotify
GitHub
Example Service
```

This improves generalization.

---

## 73. Service-Aware Rules

Some future classifications may require Service-specific semantics.

For example, a Service may use unusual terminology that cannot be interpreted reliably without knowing the Service.

If such cases arise, Service context may be passed explicitly.

However, Service-specific classification should remain the exception rather than the default.

Otherwise the framework risks accumulating:

```text
if service == X
if service == Y
if service == Z
```

throughout the classifier.

---

## 74. Privacy

Evidence Classification may operate on sensitive Observation payloads.

The classifier must therefore follow:

- data minimization;
- local-first processing;
- capability-specific authorization;
- no silent permission escalation;
- Provider-independent AI policy.

The classifier must not assume that because data exists in an Observation it may freely be transmitted externally.

---

## 75. Local-First Classification

Deterministic classification should normally execute locally.

Potential local capabilities include:

```text
string normalization
rule matching
language-aware patterns
structured source rules
taxonomy mapping
```

Local AI models may also eventually be supported.

Remote AI should remain optional.

---

## 76. Sensitive Observation Types

Some ObservationTypes may have restrictions preventing remote AI processing.

For example:

```text
EMAIL_MESSAGE_CONTENT
```

may carry more sensitive information than:

```text
EMAIL_MESSAGE_METADATA
```

A classification policy should eventually be able to determine:

```text
AI allowed locally
AI allowed remotely
AI prohibited
```

depending on:

- ObservationType;
- sensitivity;
- User configuration;
- privacy policy.

The final policy mechanism remains undefined.

---

## 77. Classification Policy

A future ClassificationPolicy may describe:

```text
allowed methods
AI availability
local-only requirement
maximum information disclosure
fallback behavior
```

Draft v0.1 includes policy conceptually in ClassificationContext but does not define its schema.

---

## 78. Classification Fallback

The preferred fallback hierarchy is:

```text
Deterministic Rule
       |
       +---- success ----> CLASSIFIED
       |
       v
Ambiguous
       |
       +---- AI allowed? ---- yes ----> AI Classifier
       |                              /           \
       |                         classified      unknown
       |                             |              |
       |                             v              v
       |                         CLASSIFIED       UNKNOWN
       |
       no
       |
       v
     UNKNOWN
```

The framework should never require:

```text
classification at all costs
```

---

## 79. Language-Independent Contract

The initial conceptual interface is:

```text
interface EvidenceClassifier {

    ClassificationResult classify(
        Observation observation,
        ClassificationContext context
    )
}
```

This is pseudocode.

It is not the final Python interface.

---

## 80. Classification Result Contract

Conceptually:

```text
ClassificationResult {

    ObservationId observationId

    ProcessingStatus processingStatus

    Optional<ClassificationStatus> classificationStatus

    List<EvidenceCandidate> evidenceItems

    ClassificationMethod method

    List<ReasonCode> reasonCodes

    ClassifierVersion classifierVersion
}
```

`ClassificationResult` is classified as:

```text
Processing Result
```

It describes one classifier execution.

It must remain distinct from:

```text
EvidenceCandidate
```

and:

```text
Evidence
```

Conceptually:

```text
EvidenceClassifier
      |
      v
ClassificationResult
[Processing Result]
      |
      +-- EvidenceCandidate
             |
             v
Application Layer
             |
             v
Evidence
[Core Domain Entity]
```

---

## 81. Evidence Candidate

Before materialization as Domain Evidence, the classifier may return:

```text
EvidenceCandidate

- evidence_type
- supporting_observation_references
- method
- reason_codes
- classifier_version
```

The consolidated Domain Model classifies `EvidenceCandidate` as:

```text
Interface Value Object / Processing Output
```

It is not a Core Domain Entity.

An EvidenceCandidate communicates the semantic result of classification across the classifier boundary.

The application layer may materialize an accepted EvidenceCandidate into:

```text
Evidence
```

with an initial lifecycle state normally equivalent to:

```text
EvidenceStatus.ACTIVE
```

The exact materialization and persistence mechanism remains an Implementation Model decision.

---

## 82. Why EvidenceCandidate Is Useful

The classifier should determine semantics.

It does not automatically need responsibility for:

```text
generating persistent Evidence IDs
saving Evidence
versioning Evidence history
managing Evidence lifecycle
```

Those responsibilities may belong to an application or repository layer.

Therefore:

```text
Classifier
     |
     v
EvidenceCandidate
     |
     v
Application Layer
     |
     v
Evidence Lifecycle / Persistence
```

provides a cleaner separation.

The consolidated Domain Model formalizes:

```text
EvidenceCandidate
=
Interface Value Object / Processing Output
```

while:

```text
Evidence
=
Core Domain Entity
```

Therefore EvidenceCandidate must not be promoted into a Core Domain Entity merely because it crosses the classifier boundary.

---

## 83. Evidence Classifier Invariants

### EC-INV-001

The classifier must operate on valid framework Observations rather than raw Provider objects.

### EC-INV-002

Evidence Classification must remain distinct from Candidate Detection.

### EC-INV-003

Evidence Classification must remain distinct from Entity Resolution.

### EC-INV-004

Evidence Classification must remain distinct from Relationship Assessment.

### EC-INV-005

An EvidenceType must not be interpreted as a confirmed real-world event.

### EC-INV-006

The classifier must support UNKNOWN.

### EC-INV-007

UNKNOWN must remain distinct from technical failure.

### EC-INV-008

Unsupported ObservationTypes or SchemaVersions must remain distinguishable from semantic UNKNOWN.

### EC-INV-009

The classifier must not fabricate missing Observation information.

### EC-INV-010

The classifier must not silently request additional source permissions.

### EC-INV-011

Deterministic classification should be preferred when adequate.

### EC-INV-012

AI availability must not be required for basic Evidence Classification.

### EC-INV-013

AI-assisted classification must respect existing authorization and privacy boundaries.

### EC-INV-014

Provider credentials must never be required by the EvidenceClassifier.

### EC-INV-015

Every Evidence item must remain traceable to supporting Observations.

### EC-INV-016

One Observation may produce zero, one or multiple Evidence items.

### EC-INV-017

Multiple Evidence items from one Observation must be independently justified.

### EC-INV-018

Evidence Classification must not automatically generate implied EvidenceTypes.

### EC-INV-019

Reclassification must not require destructive modification of the source Observation.

### EC-INV-020

The classifier must preserve enough method and version provenance to support reprocessing and explanation.

### EC-INV-021

Provider identity should not determine classification strategy when Observation semantics are Provider-neutral.

### EC-INV-022

Equivalent semantics expressed in different languages should map to the same canonical EvidenceType where appropriate.

### EC-INV-023

Numerical Evidence Classification Confidence is outside the initial Discovery model.

### EC-INV-024

Evidence may exist even when Entity Resolution remains UNRESOLVED.

### EC-INV-025

A resolved Service does not require Evidence Classification to succeed.

### EC-INV-026

Newly materialized accepted Evidence should normally enter the Evidence lifecycle as ACTIVE.

### EC-INV-027

Reclassification must not cause an older superseded interpretation and its replacement to participate simultaneously as current Evidence.

### EC-INV-028

Evidence lifecycle state changes must preserve supporting Observation provenance.

### EC-INV-029

SUPERSEDED Evidence must remain distinguishable from REJECTED Evidence.

### EC-INV-030

`EvidenceStatus.REJECTED` must remain distinct from `RelationshipStatus.REJECTED`.

### EC-INV-031

A failed classification attempt must not automatically invalidate previously ACTIVE Evidence.

### EC-INV-032

ClassificationResult must remain classified as a Processing Result even when persisted.

### EC-INV-033

EvidenceCandidate must remain an Interface Value Object / Processing Output rather than a Core Domain Entity.

---

## 84. Gmail Example - Deterministic Classification

Observation:

```text
type:
EMAIL_MESSAGE_METADATA

sender:
no-reply@spotify.com

subject:
Verify your email address
```

Classification:

```text
processing_status:
SUCCESS

classification_status:
CLASSIFIED

evidence_items:
- ACCOUNT_VERIFICATION

method:
RULE

reason_codes:
- EXACT_SUBJECT_PATTERN
```

Entity Resolution may independently determine:

```text
Spotify
```

---

## 85. Gmail Example - Password Reset

Observation:

```text
type:
EMAIL_MESSAGE_METADATA

subject:
Reset your password
```

Classification:

```text
classification_status:
CLASSIFIED

evidence_items:
- PASSWORD_RESET

method:
RULE
```

The classifier does not assert that the password was actually changed.

---

## 86. Gmail Example - Ambiguous Metadata

Observation:

```text
type:
EMAIL_MESSAGE_METADATA

subject:
Important information about your account
```

Deterministic rules cannot safely classify it.

If AI is unavailable or prohibited:

```text
processing_status:
SUCCESS

classification_status:
UNKNOWN

reason_codes:
- INSUFFICIENT_INFORMATION
```

This is a valid outcome.

---

## 87. Gmail Example - AI-Assisted Classification

Observation:

```text
type:
EMAIL_MESSAGE_METADATA

subject:
Your security settings were updated
```

Assume deterministic rules remain ambiguous and policy permits AI.

Possible result:

```text
processing_status:
SUCCESS

classification_status:
CLASSIFIED

evidence_items:
- SECURITY_NOTIFICATION

method:
AI
```

The actual model and implementation are not defined by this contract.

---

## 88. Password Manager Example

Observation:

```text
type:
PASSWORD_MANAGER_ENTRY_METADATA

title:
Spotify

URI:
https://accounts.spotify.com
```

Classification:

```text
processing_status:
SUCCESS

classification_status:
CLASSIFIED

evidence_items:
- PASSWORD_MANAGER_ENTRY

method:
RULE
```

No password value is required.

---

## 89. Multi-Evidence Example

Observation:

```text
type:
EMAIL_MESSAGE_METADATA

subject:
Your subscription was renewed and your payment was successful
```

A classifier may produce:

```text
classification_status:
CLASSIFIED

evidence_items:
- SUBSCRIPTION
- PAYMENT
```

only if both classifications are independently supported by the observed information.

---

## 90. Unknown Service Example

Observation:

```text
sender:
billing@unknown-service.example

subject:
Your payment was successful
```

Evidence Classification:

```text
PAYMENT
```

Entity Resolution:

```text
UNRESOLVED
```

Combined state:

```text
Evidence:
PAYMENT

Service:
UNRESOLVED
```

This is valid.

---

## 91. Resolved Service but Unknown Evidence Example

Observation:

```text
sender:
info@spotify.com

subject:
Important update
```

Entity Resolution:

```text
Spotify
```

Evidence Classification:

```text
UNKNOWN
```

Combined state:

```text
Service:
Spotify

Evidence:
UNKNOWN
```

This is also valid.

---

## 92. Unsupported Example

Observation:

```text
type:
FUTURE_SOURCE_METADATA
```

No classifier exists.

Result:

```text
processing_status:
UNSUPPORTED

classification_status:
N/A
```

This must not become semantic UNKNOWN.

---

## 93. Failure Example

Observation is valid, but the classifier encounters an internal processing failure.

Result:

```text
processing_status:
FAILED

classification_status:
N/A
```

Again:

```text
FAILED != UNKNOWN
```

---

## 94. Manual Correction Example

Automated classification:

```text
MARKETING
```

User correction:

```text
NEWSLETTER
```

A possible lifecycle representation is:

```text
Observation
      |
      +--> Automated Evidence
      |      type: MARKETING
      |      status: SUPERSEDED or REJECTED
      |
      +--> User-Corrected Evidence
             type: NEWSLETTER
             status: ACTIVE
```

The original Observation and automated classification provenance remain preserved.

The exact choice between SUPERSEDED and REJECTED depends on correction policy.

---

## 95. Open Questions

### Evidence Taxonomy

- What is the minimum common Evidence taxonomy?
- Which EvidenceTypes should be cross-source?
- Which EvidenceTypes should remain source-specific?
- Should EvidenceTypes form a flat list or hierarchy?
- How should taxonomy versions be managed?

### Evidence Identity and Lifecycle

The Domain Model now defines:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

The remaining questions are:

- Should reclassification create a new Evidence record every time?
- Can one Evidence record change EvidenceStatus while preserving identity?
- What exact transitions are permitted?
- Can REJECTED Evidence ever become ACTIVE again?
- When should an older Evidence become SUPERSEDED rather than REJECTED?
- How are User corrections represented?
- What constitutes duplicate logical Evidence?
- How long should SUPERSEDED and REJECTED Evidence be retained?
- Should lifecycle-transition provenance be represented explicitly?

### Classification Granularity

- Is PASSWORD_RESET sufficiently precise?
- Should request, completion and change events be distinct?
- Should SUBSCRIPTION distinguish start, renewal and cancellation?
- Should commercial events be modeled more granularly later?

### Multiple Evidence Types

- When may one Observation produce multiple Evidence items?
- Should there be rules preventing semantically redundant combinations?
- Who validates taxonomy consistency?

### Cross-Observation Classification

- Should classification ever reason across multiple Observations?
- Or should that remain strictly inside Evidence Aggregation?
- Is a separate correlation layer eventually required?

### Provider-Specific Semantics

- How should Provider-specific terminology be handled?
- Can Service-specific dictionaries remain deterministic?
- At what point does specialization damage Provider independence?

### Language

- Which languages should deterministic rules initially support?
- How should language be detected?
- Should language detection itself become explicit provenance?
- When should multilingual ambiguity escalate to AI?

### AI

- Which classification cases actually benefit from AI?
- Should AI return one EvidenceType or multiple candidates?
- Should AI ever create new taxonomy categories?
- How are model changes managed?
- Should some ObservationTypes prohibit remote AI completely?

### Privacy

- Which ObservationTypes may be sent to remote AI?
- Should classification policy depend on field-level sensitivity?
- Should some payload fields be redacted before AI processing?

### Service Context

- Should Evidence Classification receive resolved Service context?
- Under which exceptional scenarios is Service-specific classification justified?

### Persistence

- Should ClassificationResult be persisted?
- Should EvidenceCandidate ever be persisted independently?
- Which Evidence records are persisted?
- How much classifier provenance is necessary?
- How is EvidenceStatus persisted?
- How is lifecycle transition provenance stored?
- How should reclassification trigger downstream re-aggregation and Relationship reassessment?

### Confidence

Numerical Evidence Classification Confidence is outside the initial Discovery baseline.

The remaining question is whether future empirical validation demonstrates a justified need for it.

If introduced later:

- what exactly will Confidence measure?
- how will it be calibrated?
- what validation dataset will support it?
- how will it differ from CLASSIFIED / UNKNOWN?
- how should Users interpret it?

---

## 96. Findings from Contract Design

### Finding 1 - Evidence Classification Can Operate Independently from Entity Resolution

An Observation may be semantically classifiable even if the Service remains unresolved.

Likewise, a Service may be resolved while Evidence semantics remain unknown.

This confirms that the two operations should remain separate.

### Finding 2 - One Observation May Produce Multiple Evidence Items

The relationship:

```text
Observation -> Evidence
```

is not necessarily one-to-one.

The Domain Model must therefore avoid assuming exactly one Evidence item per Observation.

### Finding 3 - Evidence Taxonomy Needs Governance

Once multiple sources and classification strategies exist, EvidenceTypes cannot remain arbitrary strings created by individual Connectors or classifiers.

A controlled and versionable taxonomy will be required.

The final taxonomy should be derived from real scenarios rather than designed exhaustively in advance.

### Finding 4 - EvidenceCandidate and Evidence Have Different Lifecycle Responsibilities

The classifier's responsibility is semantic interpretation.

It does not automatically own:

```text
persistent Evidence ID generation
Evidence storage
Evidence lifecycle transitions
Evidence replacement history
```

The consolidated Domain Model therefore distinguishes:

```text
EvidenceCandidate
=
Interface Value Object / Processing Output
```

from:

```text
Evidence
=
Core Domain Entity
```

The application layer materializes accepted classifier output into Domain Evidence.

### Finding 5 - AI Escalation Must Remain Optional

UNKNOWN is an acceptable outcome.

The framework does not need to send every ambiguous Observation to AI merely to maximize classification coverage.

### Finding 6 - Progressive Permission Remains Outside the Classifier

If available Observation data is insufficient, the classifier returns UNKNOWN.

It does not independently gain access to more sensitive source information.

Additional authorized information must enter through the normal:

```text
ConnectedSource
     |
     v
Connector
     |
     v
Observation
```

path.

### Finding 7 - Metadata and Content Should Remain Distinct Observation Types

Progressive Permission is easier to preserve if:

```text
EMAIL_MESSAGE_METADATA
```

and:

```text
EMAIL_MESSAGE_CONTENT
```

remain separate Observation semantics rather than progressively expanding one opaque email object.

### Finding 8 - Evidence Requires Explicit Lifecycle State

Reclassification and User correction require the framework to distinguish:

```text
currently accepted interpretation
```

from:

```text
historical replaced interpretation
```

and:

```text
explicitly invalidated interpretation
```

The consolidated Domain Model therefore introduces:

```text
EvidenceStatus

ACTIVE
SUPERSEDED
REJECTED
```

Current Evidence Aggregation should normally consume only ACTIVE Evidence.

### Finding 9 - ClassificationResult Is a Processing Result

The consolidated Domain Model classifies ClassificationResult as:

```text
Processing Result
```

rather than a Core Domain Entity.

It may be persisted for provenance without becoming authoritative Domain Evidence.

---

## 97. Architecture Alignment and Remaining Decision Candidates

### Architecture Alignment - Classification Is Independent from Resolution

Evidence Classification and Entity Resolution operate as independent Discovery concerns.

Either may succeed while the other remains unresolved.

This is formalized by:

```text
D-020 - Entity Resolution and Evidence Classification Are Independent
```

### Architecture Alignment - Evidence Taxonomy Is Controlled

EvidenceTypes belong to a controlled and versionable framework taxonomy rather than being arbitrary Provider-specific strings.

The final taxonomy remains empirically extensible.

### Architecture Alignment - One Observation May Produce Multiple Evidence Items

One Observation may produce:

```text
zero
one
multiple
```

Evidence items when each semantic interpretation is independently justified.

### Architecture Alignment - UNKNOWN Is a Valid Classification

Evidence Classification may return:

```text
UNKNOWN
```

when available authorized information is insufficient.

The classifier must not fabricate a classification or silently request additional source permissions.

### Architecture Alignment - Deterministic Classification First

Deterministic classification is preferred when explicit rules can reliably interpret an Observation.

AI should primarily address semantic ambiguity.

### Architecture Alignment - Semantic Types Are Provider-Neutral Where Possible

Equivalent semantics from different Providers should map to the same EvidenceType where appropriate.

Provider-specific EvidenceTypes should be introduced only where common semantic types cannot represent the source meaning.

### Architecture Alignment - Evidence Lifecycle

Evidence has an explicit lifecycle:

```text
ACTIVE
SUPERSEDED
REJECTED
```

Historical classification provenance may remain preserved without all historical interpretations participating simultaneously in current assessment.

### Architecture Alignment - Reclassification Preserves Observation Provenance

Classifier evolution must not require destructive modification of source Observations.

Reclassification changes interpretation, not what was originally observed.

### Architecture Alignment - No Numerical Evidence Confidence

Numerical Evidence Classification Confidence is outside the initial Discovery baseline.

This aligns with:

```text
D-023 - No Numerical Confidence in Initial Discovery Model
```

### Remaining Decision Candidate - Evidence Lifecycle Persistence

The lifecycle semantics are defined.

The persistence mechanism is not.

The Implementation Model must determine how ACTIVE, SUPERSEDED and REJECTED Evidence and their lifecycle transitions are stored.

---

## 98. Current Contract Baseline

The aligned Evidence Classifier contract is:

```text
Observation
      |
      v
EvidenceClassifier
      |
      v
ClassificationResult
[Processing Result]
      |
      +-- processing_status
      |
      +-- classification_status
      |
      +-- evidence_items
      |
      +-- method
      |
      +-- reason_codes
      |
      +-- classifier_version
      |
      v
EvidenceCandidate
[Interface Value Object]
      |
      v
Application Layer
      |
      v
Evidence
[Core Domain Entity]
      |
      +-- EvidenceType
      |
      +-- EvidenceStatus
             |
             +-- ACTIVE
             +-- SUPERSEDED
             +-- REJECTED
```

with the guarantees:

```text
Observation provenance preserved

classification independent from Entity Resolution

classification independent from Relationship Assessment

Provider-neutral semantics where possible

controlled Evidence taxonomy

deterministic-first processing

optional AI escalation

UNKNOWN support

technical failure separated from semantic uncertainty

zero / one / multiple Evidence items supported

EvidenceCandidate distinct from Evidence

ClassificationResult classified as Processing Result

Evidence lifecycle explicit

ACTIVE / SUPERSEDED / REJECTED distinguished

reclassification preserves historical provenance

only currently accepted Evidence normally participates downstream

no numerical Confidence in the initial baseline

no silent permission escalation
```

---

## 99. Downstream Contract

The next contract in the Discovery pipeline is:

```text
EvidenceAggregator
```

and has already been defined in:

```text
docs/interfaces/06-evidence-aggregator-contract.md
```

The relevant dependency is:

```text
Observation
      |
      v
EvidenceClassifier
      |
      v
ClassificationResult
      |
      v
EvidenceCandidate
      |
      v
Application Layer
      |
      v
ACTIVE Evidence
      |
      v
EvidenceAggregator
```

while Entity Resolution remains an independent branch:

```text
                     Observation
                     /         \
                    /           \
                   v             v
       Candidate Detection    Evidence Classification
                   |             |
                   v             v
          CandidateIdentifier  EvidenceCandidate
                   |             |
                   v             v
           Entity Resolution   Evidence
                   |             |
                   v             |
                Service          |
                   \             /
                    \           /
                     v         v
                 EvidenceAggregator
```

The EvidenceAggregator must consume Evidence lifecycle according to explicit aggregation policy.

For the default current Discovery view:

```text
ACTIVE
      -> normally included

SUPERSEDED
      -> normally excluded

REJECTED
      -> excluded
```

The Evidence Classifier Contract is now aligned with:

- Architecture Draft v0.3;
- Domain Model Draft v0.3;
- D-020 parallel Entity Resolution / Evidence Classification;
- Evidence as a Core Domain Entity;
- EvidenceCandidate as an Interface Value Object;
- ClassificationResult as a Processing Result;
- EvidenceStatus lifecycle;
- ACTIVE / SUPERSEDED / REJECTED semantics;
- reclassification provenance;
- D-023 exclusion of numerical Confidence.

No additional Evidence Classification abstraction is required before the Implementation Model phase.
