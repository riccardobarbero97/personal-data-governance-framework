# Evidence Classifier Contract

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
- whether the User has a confirmed Relationship with that Service;
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
Relationship:
CONFIRMED ACCOUNT
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

- provider credentials;
- provider-specific raw objects;
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

`UNKNOWN` is a valid domain outcome.

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

An unsupported Observation Type represents a processing capability limitation.

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

This is different from:

```text
processing_status:
SUCCESS

classification_status:
UNKNOWN
```

Therefore:

```text
UNSUPPORTED
     !=
UNKNOWN
```

---

## 14. Evidence

An Evidence item represents a semantic interpretation supported by one or more Observations.

Conceptually:

```text
Evidence

- id
- type
- supporting_observation_references
- classification_method
- classifier_version
- created_at
- provenance
```

The final persistent structure remains undefined.

---

## 15. Evidence Type

`EvidenceType` identifies what the Observation semantically represents.

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

An important design question is whether Evidence Types should always be source-independent.

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
common semantic Evidence Types
```

and, where justified:

```text
source-specific Evidence Types
```

Source-specific categories should not be introduced merely because it is easier than semantic interpretation.

---

## 18. Observation Type Does Not Determine Evidence Type

The mapping is not:

```text
EMAIL_MESSAGE_METADATA
      =
one Evidence Type
```

The same Observation Type may produce many Evidence Types.

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

Similarly, future Observation Types may contribute Evidence Types already used by other sources.

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
```

and:

```text
PAYMENT
```

Therefore the classifier should not assume:

```text
1 Observation
      =
1 Evidence Type
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

The inverse relationship may also eventually be useful.

For example, several technically related Observations may together support one semantic Evidence item.

Conceptually:

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

Different Observation Types may require different strategies.

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
Observation Type
```

rather than:

```text
Provider
```

For example, equivalent Gmail and Outlook email metadata should be classifiable through the same semantic strategy when their Observation payload contracts are compatible.

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

unless concrete semantic differences make provider-specific behavior necessary.

---

## 26. Password Manager Classification

Scenario 002 demonstrates a case where classification may be mostly deterministic.

For example:

```text
Observation Type:
PASSWORD_MANAGER_ENTRY_METADATA
```

associated with a valid Service candidate may produce:

```text
PASSWORD_MANAGER_ENTRY
```

without requiring natural-language interpretation.

This reinforces:

> Classification complexity should follow the Observation semantics rather than forcing AI into every source.

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

The Evidence Classifier itself must not automatically retrieve the message body.

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
         |
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

Equivalent source semantics expressed in different languages should ideally map to the same canonical Evidence Type.

For example:

```text
Italian:
PASSWORD RESET semantic
```

and:

```text
English:
PASSWORD RESET semantic
```

should both produce:

```text
PASSWORD_RESET
```

rather than language-specific Evidence Types.

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
prompt or classifier policy version
```

However, this information must not create provider lock-in inside the core Evidence model.

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
    +-- classification method
    |
    +-- classifier version
```

must remain reconstructable.

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

The Evidence is still useful.

Therefore:

```text
EVIDENCE
   !=
REQUIRES RESOLVED SERVICE
```

An Evidence item may temporarily exist without a canonical Service reference.

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

The framework still learns:

> This Observation appears to describe a password-reset event associated with an unresolved Service candidate.

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

> The classifier interpreted the Observation as account-verification evidence.

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

Those conclusions require independent evidence.

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

where `SUBSCRIPTION` refers to a paid or Service subscription.

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

A future model may preserve:

```text
Automated Evidence
        |
        v
User Correction
        |
        v
Current Interpretation
```

The exact precedence model remains open.

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

The framework must eventually determine:

- which classification is current;
- whether historical classifications are retained;
- how derived Relationships are reassessed.

Draft v0.1 requires provenance but does not define the complete lifecycle.

---

## 58. Evidence Replacement vs Evidence Versioning

Reclassification raises a design question:

```text
Should Evidence be overwritten?
```

or:

```text
Should Evidence versions be retained?
```

Because explainability and auditing are important, silent destructive replacement is undesirable.

A future model may use:

```text
Evidence Version
```

or:

```text
ClassificationResult history
```

This remains open.

---

## 59. Duplicate Evidence

Repeated classification of the same unchanged Observation with the same classifier should not necessarily create uncontrolled duplicate Evidence.

Conceptually:

```text
Observation A
+ Classifier v1
+ same rule set
        |
        v
same logical classification
```

Persistence and idempotency semantics remain to be defined.

---

## 60. Evidence Identity

Evidence identity may depend on factors such as:

```text
supporting Observation
Evidence Type
Classifier Version
Classification Method
```

The exact identity model remains open.

The contract requires only that duplicate execution be distinguishable from genuinely new semantic Evidence.

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

Reason codes should improve explainability without becoming a substitute for the Evidence Type itself.

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

Technical failures must remain separate from semantic `UNKNOWN`.

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

rather than semantic `UNKNOWN`.

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

A classifier may not support a newly introduced Observation Type.

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

Observation Type and Schema Version must both be considered.

---

## 69. Batch Processing

An implementation may classify Observations in batches.

Conceptually:

```text
classify_many(observations)
```

may be useful for performance.

Each Observation must still receive independently traceable results.

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

However, Draft v0.1 keeps the Evidence Classifier primarily Observation-oriented.

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

For example, a provider may use unusual terminology that cannot be interpreted reliably without knowing the Service.

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
- provider-independent AI policy.

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

Some Observation Types may have restrictions preventing remote AI processing.

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

- Observation Type;
- sensitivity;
- User configuration;
- privacy policy.

The final policy mechanism remains undefined.

---

## 77. Classification Policy

A future `ClassificationPolicy` may describe:

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

---

## 81. Evidence Candidate

Before persistence as canonical Evidence, the classifier may conceptually return:

```text
EvidenceCandidate

- evidence_type
- supporting_observation_id
- method
- reason_codes
```

This allows classification output to remain distinct from Evidence persistence lifecycle.

Whether `EvidenceCandidate` becomes a formal software object remains an implementation decision.

---

## 82. Why EvidenceCandidate May Be Useful

The classifier should determine semantics.

It may not need responsibility for:

```text
generating persistent Evidence IDs
saving Evidence
versioning Evidence history
invalidating old Evidence
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
Evidence Lifecycle / Persistence
```

may provide a cleaner separation.

Draft v0.1 keeps this as a conceptual distinction rather than adding a new Domain Entity.

---

## 83. Evidence Classifier Invariants

### EC-INV-001

The classifier must operate on valid framework Observations rather than raw provider objects.

---

### EC-INV-002

Evidence Classification must remain distinct from Candidate Detection.

---

### EC-INV-003

Evidence Classification must remain distinct from Entity Resolution.

---

### EC-INV-004

Evidence Classification must remain distinct from Relationship Assessment.

---

### EC-INV-005

An Evidence Type must not be interpreted as a confirmed real-world event.

---

### EC-INV-006

The classifier must support `UNKNOWN`.

---

### EC-INV-007

`UNKNOWN` must remain distinct from technical failure.

---

### EC-INV-008

Unsupported Observation Types or Schema Versions must remain distinguishable from semantic `UNKNOWN`.

---

### EC-INV-009

The classifier must not fabricate missing Observation information.

---

### EC-INV-010

The classifier must not silently request additional source permissions.

---

### EC-INV-011

Deterministic classification should be preferred when adequate.

---

### EC-INV-012

AI availability must not be required for basic Evidence Classification.

---

### EC-INV-013

AI-assisted classification must respect existing authorization and privacy boundaries.

---

### EC-INV-014

Provider credentials must never be required by the Evidence Classifier.

---

### EC-INV-015

Every Evidence item must remain traceable to supporting Observations.

---

### EC-INV-016

One Observation may produce zero, one or multiple Evidence items.

---

### EC-INV-017

Multiple Evidence items from one Observation must be independently justified.

---

### EC-INV-018

Evidence Classification must not automatically generate implied Evidence Types.

---

### EC-INV-019

Reclassification must not require destructive modification of the source Observation.

---

### EC-INV-020

The classifier must preserve enough method and version provenance to support reprocessing and explanation.

---

### EC-INV-021

Provider identity should not determine classification strategy when Observation semantics are provider-neutral.

---

### EC-INV-022

Equivalent semantics expressed in different languages should map to the same canonical Evidence Type where appropriate.

---

### EC-INV-023

No arbitrary numerical Evidence Confidence is required in Draft v0.1.

---

### EC-INV-024

Evidence may exist even when Entity Resolution remains `UNRESOLVED`.

---

### EC-INV-025

A resolved Service does not require Evidence Classification to succeed.

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

This must not become semantic `UNKNOWN`.

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

The framework should be able to preserve:

```text
Observation
      |
      +--> Automated Classification
      |
      +--> User Correction
```

rather than destructively rewriting the Observation.

---

## 95. Open Questions

### Evidence Taxonomy

- What is the minimum common Evidence taxonomy?
- Which Evidence Types should be cross-source?
- Which Evidence Types should remain source-specific?
- Should Evidence Types form a flat list or hierarchy?
- How should taxonomy versions be managed?

### Evidence Identity

- Is Evidence itself versioned?
- Should reclassification create new Evidence records?
- How should superseded Evidence be represented?
- What constitutes duplicate Evidence?

### Classification Granularity

- Is `PASSWORD_RESET` sufficiently precise?
- Should request, completion and change events be distinct?
- Should `SUBSCRIPTION` distinguish start, renewal and cancellation?
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

- How should provider-specific terminology be handled?
- Can Service-specific dictionaries remain deterministic?
- At what point does specialization damage provider independence?

### Language

- Which languages should deterministic rules initially support?
- How should language be detected?
- Should language detection itself become explicit provenance?
- When should multilingual ambiguity escalate to AI?

### AI

- Which classification cases actually benefit from AI?
- Should AI return one Evidence Type or multiple candidates?
- Should AI ever create new taxonomy categories?
- How are model changes managed?
- Should some Observation Types prohibit remote AI completely?

### Privacy

- Which Observation Types may be sent to remote AI?
- Should classification policy depend on field-level sensitivity?
- Should some payload fields be redacted before AI processing?

### Service Context

- Should Evidence Classification receive resolved Service context?
- Under which exceptional scenarios is Service-specific classification justified?

### Persistence

- Should ClassificationResult be persisted?
- Should canonical Evidence alone be persisted?
- How much classifier provenance is necessary?
- How should reclassification affect downstream Relationships?

### Confidence

- Is numerical Evidence Confidence ever necessary?
- Could explicit Evidence Types, methods and provenance remain sufficient?
- If introduced later, how would Confidence be calibrated?

---

## 96. Findings from Contract Design

### Finding 1 - Evidence Classification Can Operate Independently from Entity Resolution

An Observation may be semantically classifiable even if the Service remains unresolved.

Likewise, a Service may be resolved while Evidence semantics remain unknown.

This confirms that the two operations should remain separate.

---

### Finding 2 - One Observation May Produce Multiple Evidence Items

The relationship:

```text
Observation -> Evidence
```

is not necessarily one-to-one.

The Domain Model must therefore avoid assuming exactly one Evidence item per Observation.

---

### Finding 3 - Evidence Taxonomy Needs Governance

Once multiple sources and classification strategies exist, Evidence Types cannot remain arbitrary strings created by individual Connectors or classifiers.

A controlled and versionable taxonomy will be required.

The final taxonomy should be derived from real scenarios rather than designed exhaustively in advance.

---

### Finding 4 - Evidence Should Stay Independent from Persistence Lifecycle

The classifier's responsibility is semantic interpretation.

It should not necessarily own:

```text
persistent ID generation
Evidence storage
Evidence replacement
Evidence version history
```

This suggests a useful conceptual distinction between:

```text
EvidenceCandidate
```

and canonical persisted:

```text
Evidence
```

without yet promoting EvidenceCandidate to a core Domain Entity.

---

### Finding 5 - AI Escalation Must Remain Optional

`UNKNOWN` is an acceptable outcome.

The framework does not need to send every ambiguous Observation to AI merely to maximize classification coverage.

---

### Finding 6 - Progressive Permission Remains Outside the Classifier

If available Observation data is insufficient, the classifier returns `UNKNOWN`.

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

---

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

---

## 97. Decision Candidates

### Candidate Decision - Classification Is Independent from Resolution

```text
Evidence Classification and Entity Resolution should operate as separate
Discovery concerns.

Either process may succeed while the other remains unresolved.
```

---

### Candidate Decision - Evidence Taxonomy Is Controlled

```text
Evidence Types should belong to a controlled and versionable framework
taxonomy rather than being arbitrary provider-specific strings.
```

---

### Candidate Decision - One Observation May Produce Multiple Evidence Items

```text
One Observation may produce zero, one or multiple Evidence items when each
semantic classification is independently supported.
```

---

### Candidate Decision - Unknown Is a Valid Classification

```text
Evidence Classification may return UNKNOWN when available authorized
information is insufficient.

The classifier must not fabricate a classification or silently request
additional source permissions.
```

---

### Candidate Decision - Deterministic Classification First

```text
Deterministic classification should be preferred when explicit rules can
reliably interpret the Observation.

AI should primarily address semantic ambiguity rather than replace reliable
deterministic classification.
```

---

### Candidate Decision - Semantic Types Are Provider-Neutral Where Possible

```text
Equivalent semantics from different providers should map to the same
Evidence Type where appropriate.

Provider-specific Evidence Types should be introduced only when the source
semantics genuinely cannot be represented through the common taxonomy.
```

---

### Candidate Decision - Reclassification Preserves Observation Provenance

```text
Classifier evolution must not require destructive modification of source
Observations.

Preserved Observations should support later reclassification where compatible.
```

---

## 98. Current Contract Baseline

The initial Evidence Classifier contract is:

```text
Observation
      |
      v
EvidenceClassifier
      |
      v
ClassificationResult
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
```

with the guarantees:

```text
Observation provenance preserved
classification independent from Entity Resolution
classification independent from Relationship Assessment
provider-neutral semantics where possible
controlled Evidence taxonomy
deterministic-first processing
optional AI escalation
UNKNOWN support
technical failure separated from semantic uncertainty
no silent permission escalation
zero / one / multiple Evidence items supported
no arbitrary numerical Confidence
reclassification-compatible design
```

---

## 99. Next Interface Contract

The Discovery pipeline now has contracts for:

```text
                   Observation
                   /         \
                  /           \
                 v             v
ServiceCandidateDetector   EvidenceClassifier
          |                     |
          v                     v
   CandidateIdentifier       Evidence
          |
          v
    EntityResolver
          |
          v
       Service
```

The next interface should define:

```text
EvidenceAggregator
```

Its responsibility is:

> Given Evidence associated with the same Service or discovery context, construct a structured aggregate suitable for Relationship Assessment without destroying individual Evidence provenance.

The next contract should establish:

- grouping boundaries;
- Service-level aggregation;
- Identity-aware aggregation;
- cross-source Evidence;
- deduplication;
- Evidence frequency;
- temporal information;
- conflicting Evidence;
- source diversity;
- historical Evidence;
- unresolved-Service Evidence;
- aggregation provenance;
- re-aggregation after reclassification or deletion.

The aggregator must not itself decide the final Relationship state.
