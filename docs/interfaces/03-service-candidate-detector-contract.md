# Service Candidate Detector Contract

**Status:** Draft v0.1  
**Scope:** Identity and Service Discovery  
**Last updated:** November 2026  
**Related Architecture:** `docs/architecture/01-identity-and-service-discovery.md`  
**Related Domain Model:** `docs/domain/01-discovery-domain-model.md`  
**Related Interfaces:**  
- `docs/interfaces/01-connector-contract.md`
- `docs/interfaces/02-observation-contract.md`

**Validated Against:** `SCN-001 Gmail Service Discovery`, `SCN-002 Password Manager Service Discovery`

---

## 1. Purpose

This document defines the initial software contract for the `ServiceCandidateDetector` within the Identity and Service Discovery capability of the Personal Data Governance Framework.

The Service Candidate Detector determines whether an Observation contains sufficient information to justify attempting to discover a Service.

Conceptually:

```text
Observation
     |
     v
Service Candidate Detector
     |
  +--+--+
  |     |
  v     v
Candidate   Not Candidate
  |
  v
Entity Resolution
```

The component does not determine which canonical Service an Observation represents.

That responsibility belongs to Entity Resolution.

The component instead answers:

> Should this Observation participate in Service Discovery?

---

## 2. Architectural Position

The Service Candidate Detector operates after Observation creation and before Entity Resolution.

```text
ConnectedSource
      |
      v
Connector
      |
      v
Observation
      |
      v
SERVICE CANDIDATE DETECTOR
      |
      +-----------------+
      |                 |
      v                 v
Candidate          Not Candidate
      |
      v
Identifier Extraction
      |
      v
Entity Resolution
      |
      v
Service
```

The Service Candidate Detector operates on framework Observations.

It must not require direct access to:

- provider APIs;
- provider authentication tokens;
- raw provider objects;
- source credentials.

---

## 3. Core Question

The detector answers:

> Does this Observation contain information that is sufficiently relevant to the Service Discovery capability to justify further processing?

It does not answer:

> Which Service is this?

It does not answer:

> Does the User definitely have an account?

It does not answer:

> Does this Service currently hold personal data?

It does not answer:

> What type of Evidence does this Observation represent?

These questions belong to other components.

---

## 4. Fundamental Distinction

The most important distinction introduced by this contract is:

```text
NOT A SERVICE CANDIDATE
```

versus:

```text
SERVICE CANDIDATE
BUT SERVICE MAY BE UNRESOLVED
```

For example:

```text
Observation:
email from a personal contact

Result:
NOT_CANDIDATE
```

while:

```text
Observation:
password-manager entry
URI: https://old-service.example

Result:
CANDIDATE
```

even if:

```text
Resolved Service:
UNKNOWN
```

The failure to resolve a Service must not retroactively mean that the Observation was not a valid Service candidate.

Therefore:

```text
CANDIDATE DETECTION
        !=
ENTITY RESOLUTION
```

---

## 5. Why Candidate Detection Exists

Without Candidate Detection, every Observation could enter Entity Resolution.

For an email source, this could include:

```text
personal emails
messages from friends
messages from colleagues
mailing infrastructure
automated forwarding
discussion groups
service communications
```

For a password manager, this could include:

```text
online Services
Wi-Fi credentials
routers
local applications
database credentials
servers
VPN credentials
test systems
secure notes
```

For a browser, this could eventually include:

```text
online Services
news sites
search-engine results
documentation
temporary links
local addresses
intranet resources
random websites
```

Not every Observation represents a useful Service Discovery candidate.

Candidate Detection therefore limits unnecessary downstream processing.

---

## 6. Provider Independence

The Service Candidate Detector must operate on framework Observation semantics rather than provider-specific objects.

For example:

```text
GmailConnector
       |
       v
EMAIL_MESSAGE_METADATA
       |
       v
ServiceCandidateDetector
```

and:

```text
OutlookConnector
       |
       v
EMAIL_MESSAGE_METADATA
       |
       v
Same ServiceCandidateDetector
```

The detector should not normally require:

```text
if provider == Gmail
```

or:

```text
if provider == Outlook
```

when equivalent observations share the same Observation Type.

Provider-specific logic should remain behind the Connector boundary unless concrete provider differences justify otherwise.

---

## 7. Source-Specific Detection Strategies

Provider independence does not mean that every Observation Type must use the same Candidate Detection logic.

Different source structures may require different strategies.

Conceptually:

```text
ServiceCandidateDetector
        |
        +-- EmailCandidateStrategy
        |
        +-- PasswordManagerCandidateStrategy
        |
        +-- BrowserCandidateStrategy
        |
        +-- FutureStrategy
```

The strategy should normally depend on:

```text
Observation Type
```

rather than:

```text
Provider
```

For example:

```text
EMAIL_MESSAGE_METADATA
```

may use email-specific candidate logic whether the Observation originated from Gmail, Outlook or another compatible email Connector.

---

## 8. Candidate Detection Input

The minimum input to Candidate Detection is an Observation.

Conceptually:

```text
detect(observation)
    ->
CandidateDetectionResult
```

The detector may also require read-only access to supporting reference information such as:

```text
known Identity Seeds
known generic email providers
known infrastructure patterns
known Service identifiers
local candidate-detection rules
```

However, such dependencies should remain explicit.

The detector must not silently access external sources unrelated to the Observation.

---

## 9. Candidate Detection Result

The detector must return a structured result rather than a simple Boolean.

A Boolean such as:

```text
true / false
```

would be insufficient because the framework needs to preserve:

- why the result was produced;
- which strategy produced it;
- which identifiers were observed;
- whether the result is ambiguous;
- whether downstream processing should continue.

The initial conceptual result is:

```text
CandidateDetectionResult

- observation_id
- status
- reason_codes
- candidate_identifiers
- method
- detector_version
```

This is conceptual and does not define the final persistent representation.

---

## 10. Detection Status

The initial status model should support at least:

```text
CANDIDATE

NOT_CANDIDATE

UNKNOWN
```

### CANDIDATE

The Observation contains sufficient information to justify further Service Discovery processing.

### NOT_CANDIDATE

The Observation can be reasonably excluded from Service Discovery.

### UNKNOWN

The detector cannot safely determine whether the Observation represents a useful Service candidate.

`UNKNOWN` is not an error.

---

## 11. Why UNKNOWN Is Required

A forced binary decision would violate the broader architectural principle:

```text
UNKNOWN IS VALID
```

For example:

```text
Observation Type:
EMAIL_MESSAGE_METADATA

Sender:
john@small-company.example

Subject:
Hello
```

Available information may be insufficient to determine whether this represents:

- personal correspondence;
- business communication;
- a Service interaction;
- another relevant relationship.

The detector should therefore be able to return:

```text
UNKNOWN
```

rather than fabricating certainty.

---

## 12. Candidate Detection Is Not Evidence Classification

Candidate Detection determines whether an Observation is useful for Service Discovery.

Evidence Classification determines what that Observation means.

Example:

```text
Observation:

From:
no-reply@spotify.com

Subject:
Verify your email address
```

Candidate Detection may produce:

```text
CANDIDATE
```

Evidence Classification may later produce:

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

## 13. Candidate Detection Is Not Entity Resolution

Candidate Detection may identify useful Service identifiers.

For example:

```text
spotify.com
```

But it should not normally conclude:

```text
Service:
Spotify
```

That belongs to Entity Resolution.

Conceptually:

```text
Observation
     |
     v
Candidate Detection
     |
     v
Candidate Identifier
     |
     v
Entity Resolution
     |
     v
Service
```

---

## 14. Candidate Identifiers

A positive Candidate Detection result may expose identifiers useful for downstream Entity Resolution.

Examples include:

```text
DOMAIN
HOSTNAME
URL
EMAIL_DOMAIN
SOURCE_SPECIFIC_IDENTIFIER
```

For example:

```text
Observation:

sender:
no-reply@spotify.com
```

may produce:

```text
candidate_identifier:

type:
EMAIL_DOMAIN

value:
spotify.com
```

Similarly:

```text
Observation:

URI:
https://accounts.spotify.com/login
```

may produce:

```text
candidate_identifier:

type:
HOSTNAME

value:
accounts.spotify.com
```

These remain identifiers.

They are not canonical Services.

---

## 15. Identifier Extraction Boundary

Candidate Detection and identifier extraction are closely related.

Draft v0.1 uses the following boundary:

```text
Observation
     |
     v
Candidate Detector
     |
     +-- determines relevance
     |
     +-- may extract candidate identifiers
     |
     v
Entity Resolver
```

This avoids creating a separate interface solely for simple deterministic identifier extraction before evidence demonstrates that such a component is necessary.

The boundary may be revised if future Observation Types require a reusable standalone Identifier Extractor.

---

## 16. Deterministic Processing

Candidate Detection should prefer deterministic processing whenever practical.

Examples include:

```text
parse email address
extract sender domain
parse URL
extract hostname
detect localhost
detect IP address
match known personal-email-provider patterns
detect known non-Service record types
```

These operations do not require an LLM.

Conceptually:

```text
Observation
     |
     v
Deterministic Candidate Logic
     |
  +--+--+
  |     |
Decision  Ambiguous
```

---

## 17. AI Boundary

AI should not be required for basic Candidate Detection.

AI may eventually assist when semantic context cannot be resolved through deterministic logic.

For example:

```text
Title:
My Music Account

URI:
UNKNOWN
```

may be ambiguous.

However, the preferred outcome may simply remain:

```text
UNKNOWN
```

if additional AI processing does not provide justified value.

The architecture must not assume:

```text
Ambiguous Candidate
        |
        v
Always ask AI
```

Instead:

```text
Ambiguous Candidate
        |
        +--> UNKNOWN
        |
        +--> AI if policy and capability justify it
```

Both are valid.

---

## 18. Detection Method

The result should identify how Candidate Detection was performed.

Potential conceptual methods include:

```text
RULE
AI
MANUAL
COMPOSITE
```

Most initial detection is expected to be:

```text
RULE
```

This improves:

- explainability;
- testing;
- reproducibility;
- privacy;
- performance.

---

## 19. Reason Codes

Candidate Detection should preserve structured reasons for its decision.

Examples might include:

```text
SERVICE_LIKE_DOMAIN
SERVICE_LIKE_URI
KNOWN_PERSONAL_EMAIL_PROVIDER
PERSONAL_CORRESPONDENCE_PATTERN
LOCAL_RESOURCE
INFRASTRUCTURE_RESOURCE
NON_SERVICE_RECORD_TYPE
INSUFFICIENT_INFORMATION
```

These are illustrative.

The final taxonomy should be developed through implementation and testing.

Reason codes should be machine-readable.

For example:

```text
status:
NOT_CANDIDATE

reason_codes:
- LOCAL_RESOURCE
```

is preferable to relying exclusively on free-form explanatory text.

---

## 20. Explainability

The framework should be able to explain Candidate Detection.

For example:

```text
This Observation was considered a Service candidate because:

- it originated from a password-manager entry;
- the entry contained the URI https://accounts.spotify.com;
- the URI represents an external web resource.
```

or:

```text
This Observation was excluded because:

- the record points to a private network address;
- the current Service Discovery capability focuses on external digital Services.
```

Candidate Detection must therefore preserve enough result provenance for explanation.

---

## 21. Email Candidate Detection

Scenario 001 demonstrated that not every email sender represents a Service.

An email candidate strategy may consider:

```text
sender address
sender domain
subject patterns
known personal-email-provider domains
known mailing infrastructure
message metadata
user Identity Seeds
```

However, the exact algorithm remains outside the contract.

---

## 22. Email Example: Strong Candidate

Observation:

```text
sender:
no-reply@spotify.com

subject:
Verify your email address
```

Possible detection result:

```text
status:
CANDIDATE

candidate_identifiers:
- EMAIL_DOMAIN: spotify.com

method:
RULE
```

This result does not yet assert:

```text
Service = Spotify
```

nor:

```text
Evidence = ACCOUNT_VERIFICATION
```

---

## 23. Email Example: Generic Consumer Email Provider

Observation:

```text
sender:
someone@gmail.com

subject:
Dinner tomorrow?
```

The framework must not infer:

```text
Google
```

as the Service merely because the sender uses Gmail.

A detection strategy may produce:

```text
status:
NOT_CANDIDATE
```

when available information indicates ordinary personal correspondence.

The exact heuristics remain implementation-specific.

---

## 24. Email Example: Ambiguous Sender

Observation:

```text
sender:
person@smallbusiness.example

subject:
Your request
```

The framework may not know whether this is:

```text
personal communication
business interaction
Service interaction
```

Possible result:

```text
status:
UNKNOWN
```

This is valid.

---

## 25. Password Manager Candidate Detection

Scenario 002 demonstrates that a password-manager record often provides stronger initial Service signals than a generic email.

However, records may represent:

```text
external Services
local systems
network devices
servers
databases
Wi-Fi passwords
software licenses
test environments
secure notes
```

The detector must therefore still evaluate relevance.

---

## 26. Password Manager Example: External Service

Observation:

```text
title:
Spotify

URI:
https://accounts.spotify.com
```

Possible result:

```text
status:
CANDIDATE

candidate_identifiers:
- HOSTNAME: accounts.spotify.com

method:
RULE
```

---

## 27. Password Manager Example: Local Router

Observation:

```text
title:
Home Router

URI:
http://192.168.1.1
```

Possible result:

```text
status:
NOT_CANDIDATE

reason_codes:
- LOCAL_RESOURCE

method:
RULE
```

This reflects the current scope of Personal Data Governance Service Discovery.

It does not mean the Observation is globally useless.

---

## 28. Password Manager Example: Missing URI

Observation:

```text
title:
Old Shopping Account

username:
user@example.com

URI:
UNKNOWN
```

Possible result:

```text
status:
UNKNOWN
```

or potentially:

```text
status:
CANDIDATE
```

if deterministic title-based logic provides sufficient reason.

Draft v0.1 does not prescribe the threshold.

This should be determined empirically.

---

## 29. Browser Candidate Detection

A future browser Observation may contain:

```text
url:
https://open.spotify.com
```

This may reasonably become:

```text
CANDIDATE
```

However:

```text
url:
https://www.google.com/search?q=spotify
```

does not necessarily imply a Relationship with Spotify.

Similarly:

```text
url:
http://localhost:8080
```

would normally not be an external Service candidate.

A browser strategy therefore requires source-aware candidate rules.

This reinforces the value of Observation-Type-specific strategies.

---

## 30. Manual Input

Manual User declarations may enter Candidate Detection differently.

For example:

```text
"I had a Spotify account."
```

has already been explicitly declared by the User as Service-related.

Candidate Detection may therefore treat certain manual Observation Types as:

```text
CANDIDATE
```

by construction.

However, manual input still requires:

- Entity Resolution;
- provenance;
- uncertainty handling.

A User declaration should not bypass the canonical Service model.

---

## 31. Known Generic Providers

Some domains represent generic infrastructure rather than the Service with which a Relationship should be inferred.

For example, in email:

```text
gmail.com
outlook.com
icloud.com
```

may identify the sender's email provider rather than the organization with which the User has a Relationship.

Candidate Detection may therefore require reference knowledge about generic infrastructure.

This knowledge should be:

- explicit;
- versionable;
- testable;
- provider-independent where possible.

The source Provider itself must not automatically become a discovered Service merely because its technical infrastructure appears in an Observation.

---

## 32. Shared Infrastructure

Service communication may use third-party infrastructure.

Examples may include:

```text
transactional email platforms
support platforms
marketing platforms
authentication platforms
payment infrastructure
cloud-hosting domains
```

A technical identifier associated with infrastructure may not identify the actual Service.

Candidate Detection should avoid prematurely treating every infrastructure identifier as a Service candidate.

In some cases the correct result may be:

```text
UNKNOWN
```

until additional context becomes available.

---

## 33. Local Resources

The current Service Discovery domain primarily concerns external digital Services relevant to the User's personal-data footprint.

Identifiers representing local resources may therefore be excluded.

Examples may include:

```text
localhost
127.0.0.1
::1
private network addresses
local device names
```

However, the exact definition of local or private resources must be deterministic and standards-aware in implementation.

The contract does not define the parsing algorithm.

---

## 34. Internal Corporate Resources

Corporate or organizational internal systems create a more difficult case.

For example:

```text
https://internal.company.example
```

may represent:

- a legitimate external Organization relationship;
- an employment-related internal system;
- a Service that holds personal data;
- a resource outside the intended consumer scope.

Candidate Detection should not permanently exclude these based solely on being "internal."

The current contract therefore does not define all corporate resources as `NOT_CANDIDATE`.

The result may depend on future scope and policy.

---

## 35. User Identity Protection

The detector must avoid interpreting the User's own identifiers as external Services.

For example:

```text
sender:
user@example.com
```

may correspond to a known Identity Seed.

Similarly, email aliases may appear in metadata.

Candidate Detection may require access to known Identity Seeds to prevent incorrect candidate generation.

However, Identity Seed matching must remain explicit and testable.

---

## 36. Candidate Detection and Phishing

A phishing message may contain a convincing Service identifier.

For example:

```text
subject:
Verify your PayPal account

sender:
security@paypal-verification.example
```

Candidate Detection may reasonably determine:

```text
CANDIDATE
```

because the Observation looks relevant to Service Discovery.

That does not mean the framework should resolve it to PayPal or treat it as valid account Evidence.

Therefore:

```text
CANDIDATE
      !=
LEGITIMATE SERVICE COMMUNICATION
```

Phishing detection and Service authenticity may require separate downstream logic or supporting signals.

The Candidate Detector should not be expected to solve every trust problem.

---

## 37. Candidate Detection and Evidence Strength

Candidate Detection must not assign Relationship strength.

For example:

```text
Marketing email
```

and:

```text
Password-manager record
```

may both be:

```text
CANDIDATE
```

while providing very different Evidence.

That difference belongs to:

```text
Evidence Classification
```

and:

```text
Relationship Assessment
```

not Candidate Detection.

---

## 38. Candidate Detection and Confidence

Draft v0.1 does not require a numerical Candidate Detection confidence score.

For example:

```text
candidate_confidence = 0.78
```

should not be introduced without defined semantics and calibration.

The initial model prefers:

```text
CANDIDATE
NOT_CANDIDATE
UNKNOWN
```

plus:

```text
reason codes
method
```

This is more explainable and avoids false precision.

---

## 39. CandidateDetectionResult

The current conceptual result is:

```text
CandidateDetectionResult

- observation_id
- status
- candidate_identifiers
- reason_codes
- method
- detector_version
```

Potential optional information may later include:

```text
warnings
policy_reference
explanation
```

The final representation remains open.

---

## 40. Candidate Identifier

A Candidate Identifier is information extracted from an Observation that may be useful to Entity Resolution.

Conceptually:

```text
CandidateIdentifier

- type
- value
- source_attribute
```

Example:

```text
type:
EMAIL_DOMAIN

value:
spotify.com

source_attribute:
sender
```

or:

```text
type:
HOSTNAME

value:
accounts.spotify.com

source_attribute:
uri
```

Preserving `source_attribute` improves provenance.

---

## 41. Multiple Candidate Identifiers

One Observation may expose multiple candidate identifiers.

For example:

```text
Email Observation

sender:
billing@example.com

reply-to:
support.example.net
```

or:

```text
Password Manager Observation

uris:
- https://example.com
- https://login.example.com
```

The detector may therefore return:

```text
candidate_identifiers:
- ...
- ...
```

Entity Resolution must later determine how these identifiers relate to canonical Services.

---

## 42. Conflicting Candidate Identifiers

An Observation may contain identifiers suggesting different entities.

For example:

```text
sender domain:
mailer-platform.example

subject/display information:
Example Service

link domain:
example-service.com
```

The detector must not arbitrarily select one canonical Service.

It may:

- return multiple candidate identifiers;
- mark the result for downstream ambiguity handling;
- return `UNKNOWN` if necessary.

Canonicalization belongs to Entity Resolution.

---

## 43. Status and Identifier Independence

A Candidate Detection status and identifier availability are related but not identical.

For example:

```text
status:
CANDIDATE

candidate_identifiers:
[]
```

may be valid for a manual declaration whose text clearly indicates a Service relationship but from which deterministic identifier extraction has not yet succeeded.

Similarly:

```text
status:
UNKNOWN

candidate_identifiers:
- DOMAIN: example.com
```

may occur when an identifier exists but its relevance is uncertain.

The contract should therefore not require:

```text
CANDIDATE <=> identifier exists
```

as an absolute rule.

---

## 44. Detector Version

The result should identify the version of the Candidate Detection strategy that produced it where practical.

Conceptually:

```text
detector_version:
1
```

This becomes important because detection logic will evolve.

For example:

```text
Detector v1:
UNKNOWN
```

may later become:

```text
Detector v2:
CANDIDATE
```

The Observation itself should not need to change.

---

## 45. Reprocessing

Candidate Detection should support reprocessing preserved Observations.

Conceptually:

```text
Observation
    |
    +--> CandidateDetector v1
    |           |
    |           v
    |        UNKNOWN
    |
    +--> CandidateDetector v2
                |
                v
            CANDIDATE
```

This reinforces the broader architecture:

```text
preserve source-derived information
        |
        v
allow derived conclusions to evolve
```

---

## 46. Persistence

Candidate Detection results may need to be persisted if doing so provides:

- explainability;
- reprocessing comparison;
- performance benefits;
- auditing;
- debugging.

However, Draft v0.1 does not require persistent CandidateDetectionResult storage.

An implementation may initially calculate results on demand.

Persistence should be justified rather than assumed.

---

## 47. Invalid Observation

The detector should not attempt to repair structurally invalid Observations.

Observation schema validation belongs upstream.

Conceptually:

```text
Invalid Observation
       |
       X
ServiceCandidateDetector
```

The expected pipeline is:

```text
Connector
   |
   v
Valid Observation
   |
   v
Candidate Detector
```

If invalid data reaches the detector due to an implementation error, this should be represented as a processing failure rather than `NOT_CANDIDATE`.

Therefore:

```text
INVALID INPUT
    !=
NOT_CANDIDATE
```

---

## 48. Unsupported Observation Type

A detector may not support every Observation Type.

For example:

```text
observation_type:
FUTURE_SOURCE_TYPE
```

may not yet have a registered detection strategy.

The result must distinguish:

```text
UNKNOWN
```

from:

```text
UNSUPPORTED_OBSERVATION_TYPE
```

The latter is a capability limitation rather than a semantic conclusion.

---

## 49. Candidate Detector Result vs Processing Error

The contract should distinguish domain outcomes from technical failures.

Domain outcomes:

```text
CANDIDATE
NOT_CANDIDATE
UNKNOWN
```

Processing outcomes may include:

```text
UNSUPPORTED_OBSERVATION_TYPE
INVALID_OBSERVATION
DETECTOR_FAILURE
```

These should not be collapsed into the same status.

A conceptual representation may therefore have:

```text
processing_status
```

and:

```text
candidate_status
```

as separate concepts.

---

## 50. Revised Result Model

To preserve this distinction, the preferred conceptual result is:

```text
CandidateDetectionResult

- observation_id
- processing_status
- candidate_status
- candidate_identifiers
- reason_codes
- method
- detector_version
```

where:

```text
processing_status:
SUCCESS
UNSUPPORTED
FAILED
```

and, when processing succeeds:

```text
candidate_status:
CANDIDATE
NOT_CANDIDATE
UNKNOWN
```

The final enumerations remain open.

---

## 51. Batch Processing

An implementation may process multiple Observations together for efficiency.

Conceptually:

```text
detect_many(observations)
```

may be useful.

However, each Observation must receive an independently traceable result.

Batch processing must not destroy one-to-one result provenance.

Conceptually:

```text
Observation A --> Result A
Observation B --> Result B
Observation C --> Result C
```

remains required even if execution is batched internally.

---

## 52. Statelessness

The detector should preferably behave as a deterministic function of:

```text
Observation
+
Detection Rules / Reference Data
+
Detector Version
```

where practical.

This improves:

- reproducibility;
- testing;
- reprocessing;
- debugging.

Mutable hidden state should be minimized.

External reference data may evolve, but its version should eventually be traceable if it materially affects results.

---

## 53. Reference Data

Candidate Detection may require reference data.

Examples include:

```text
generic email-provider domains
private-network definitions
known infrastructure patterns
known non-Service source structures
user Identity Seeds
```

Reference data should not be silently embedded in unversioned code if changes materially alter detection results.

A future implementation may require:

```text
RuleSetVersion
```

or:

```text
ReferenceDataVersion
```

The need should be evaluated during implementation.

---

## 54. Privacy

Candidate Detection should operate on the minimum Observation information necessary.

If:

```text
sender domain
```

is sufficient to determine candidate relevance, the detector should not request:

```text
email body
```

merely to increase certainty.

Similarly, candidate detection over password-manager metadata must not require password values.

The detector must respect the permission boundary under which the Observation was created.

---

## 55. No Permission Escalation

Candidate Detection itself must not silently request additional source permissions.

If an Observation is insufficient:

```text
UNKNOWN
```

is a valid result.

A future higher-level capability may decide whether additional information justifies a Progressive Permission request.

Therefore:

```text
Candidate Detector
      |
      X
request provider permissions directly
```

The detector operates on available authorized Observations.

---

## 56. Local-First

Candidate Detection should be executable locally where practical.

Most initial tasks involve:

- parsing;
- matching;
- rule evaluation;
- known-reference lookup.

These are well suited to local deterministic processing.

Remote AI should not be a default dependency.

---

## 57. Service Candidate Detector Contract

The initial language-independent contract is:

```text
interface ServiceCandidateDetector {

    CandidateDetectionResult detect(
        Observation observation,
        CandidateDetectionContext context
    )

}
```

This is pseudocode.

It is not the final Python interface.

---

## 58. CandidateDetectionContext

A detection context may provide explicitly authorized supporting information.

Conceptually:

```text
CandidateDetectionContext

- known_identity_seeds
- rule_set
- reference_data
- policy
```

The context should not contain:

- provider credentials;
- unrelated raw source data;
- arbitrary user information not required by the detector.

The exact structure remains open.

---

## 59. Conceptual Result Contract

```text
CandidateDetectionResult {

    ObservationId observationId

    ProcessingStatus processingStatus

    Optional<CandidateStatus> candidateStatus

    List<CandidateIdentifier> candidateIdentifiers

    List<ReasonCode> reasonCodes

    DetectionMethod method

    DetectorVersion detectorVersion
}
```

This is conceptual pseudocode.

---

## 60. Detector Invariants

### SCD-INV-001

The detector must receive a valid framework Observation rather than a provider-specific raw object.

---

### SCD-INV-002

The detector must not require provider credentials.

---

### SCD-INV-003

Candidate Detection must remain distinct from Entity Resolution.

---

### SCD-INV-004

Candidate Detection must remain distinct from Evidence Classification.

---

### SCD-INV-005

`NOT_CANDIDATE` must not mean `UNRESOLVED_SERVICE`.

---

### SCD-INV-006

`CANDIDATE` must not mean `CONFIRMED_RELATIONSHIP`.

---

### SCD-INV-007

`CANDIDATE` must not mean `VALID_OR_LEGITIMATE_SERVICE_COMMUNICATION`.

---

### SCD-INV-008

The detector must support `UNKNOWN`.

---

### SCD-INV-009

The detector must not fabricate missing identifiers.

---

### SCD-INV-010

Candidate identifiers must remain distinguishable from canonical Services.

---

### SCD-INV-011

Deterministic logic should be preferred when adequate.

---

### SCD-INV-012

AI availability must not be required for basic Candidate Detection.

---

### SCD-INV-013

Insufficient Observation information must not trigger silent source permission escalation.

---

### SCD-INV-014

Processing failure must remain distinguishable from `NOT_CANDIDATE`.

---

### SCD-INV-015

Unsupported Observation Types must remain distinguishable from semantic `UNKNOWN`.

---

### SCD-INV-016

Candidate Detection results must remain traceable to their source Observation.

---

### SCD-INV-017

Multiple candidate identifiers may be returned for one Observation.

---

### SCD-INV-018

Provider identity should not drive detection logic when Observation semantics are provider-neutral.

---

### SCD-INV-019

Reprocessing must not require modification of the original Observation.

---

### SCD-INV-020

Candidate Detection must not assign final Relationship Confidence.

---

## 61. Gmail-to-Candidate Example

```text
ConnectedSource:
Personal Gmail
      |
      v
GmailConnector
      |
      v
Observation

type:
EMAIL_MESSAGE_METADATA

sender:
no-reply@spotify.com

subject:
Verify your email address
      |
      v
ServiceCandidateDetector
      |
      v
CandidateDetectionResult

processing_status:
SUCCESS

candidate_status:
CANDIDATE

candidate_identifier:
EMAIL_DOMAIN = spotify.com

method:
RULE
      |
      v
Entity Resolver
```

The detector does not yet produce:

```text
Service:
Spotify
```

or:

```text
Evidence:
ACCOUNT_VERIFICATION
```

---

## 62. Password-Manager-to-Candidate Example

```text
ConnectedSource:
Primary Password Manager
      |
      v
PasswordManagerConnector
      |
      v
Observation

type:
PASSWORD_MANAGER_ENTRY_METADATA

title:
Spotify

URI:
https://accounts.spotify.com
      |
      v
ServiceCandidateDetector
      |
      v
CandidateDetectionResult

processing_status:
SUCCESS

candidate_status:
CANDIDATE

candidate_identifier:
HOSTNAME = accounts.spotify.com

method:
RULE
      |
      v
Entity Resolver
```

This demonstrates that the same contract supports structurally different sources.

---

## 63. Not-Candidate Example

```text
Observation

type:
PASSWORD_MANAGER_ENTRY_METADATA

title:
Home Router

URI:
http://192.168.1.1
      |
      v
ServiceCandidateDetector
      |
      v
CandidateDetectionResult

processing_status:
SUCCESS

candidate_status:
NOT_CANDIDATE

reason:
LOCAL_RESOURCE
```

The Observation remains available.

It is simply not used by the current Service Discovery capability.

---

## 64. Unknown Example

```text
Observation

type:
EMAIL_MESSAGE_METADATA

sender:
person@unknown.example

subject:
Your request
      |
      v
ServiceCandidateDetector
      |
      v
CandidateDetectionResult

processing_status:
SUCCESS

candidate_status:
UNKNOWN

reason:
INSUFFICIENT_INFORMATION
```

No Service is fabricated.

No additional permission is silently requested.

---

## 65. Unsupported Example

```text
Observation

type:
NEW_FUTURE_OBSERVATION_TYPE
      |
      v
ServiceCandidateDetector
      |
      v
CandidateDetectionResult

processing_status:
UNSUPPORTED

candidate_status:
N/A
```

This is a technical capability limitation, not a domain conclusion.

---

## 66. Open Questions

### Responsibility Boundary

- Should candidate identifier extraction remain part of Candidate Detection?
- Should a separate `ServiceIdentifierExtractor` eventually exist?
- At what complexity threshold would separation become justified?

### Candidate Status

- Are `CANDIDATE`, `NOT_CANDIDATE` and `UNKNOWN` sufficient?
- Is a concept such as `OUT_OF_SCOPE` required?
- Should explicit User rejection be represented here or later?

### Reason Codes

- What is the minimum initial reason-code vocabulary?
- Should reason codes be shared across Observation Types?
- Should strategies define their own namespaced reason codes?

### Rules

- Where are deterministic rules stored?
- Code?
- Configuration?
- Versioned rule packs?
- How should rule changes trigger reprocessing?

### Reference Data

- Which generic infrastructure lists are necessary?
- Which lists can be maintained locally?
- How are reference-data versions tracked?
- How do we prevent reference data from becoming another external dependency?

### AI

- Is AI Candidate Detection actually necessary?
- Would `UNKNOWN` plus later Evidence analysis be sufficient?
- Which real-world false negatives would justify AI at this stage?

### Identity Seeds

- Should all Candidate Detection strategies receive known Identity Seeds?
- How should aliases be represented?
- Should User identity filtering happen before Candidate Detection?

### Cross-Observation Context

- Should Candidate Detection operate only on single Observations?
- Could multiple related Observations jointly establish candidate relevance?
- If so, should that occur here or during Evidence Aggregation?

### Infrastructure

- How should shared email infrastructure be recognized?
- How should SaaS platforms serving multiple underlying Services be handled?
- Should infrastructure itself sometimes be a legitimate discovered Service?

### Scope

- Are corporate internal resources part of the Personal Data Governance footprint?
- Are government portals Services?
- Are financial institutions always Services?
- Are local self-hosted Services in scope?
- Should the definition of Service be user-configurable?

### Persistence

- Should CandidateDetectionResult be persisted?
- Or recomputed from Observations?
- How expensive will reprocessing become?
- How useful is historical detector provenance?

---

## 67. Findings from Contract Design

### Finding 1 - Candidate Detection Is a Distinct Stage

Scenario 001 and Scenario 002 both demonstrate that:

```text
Observation
       !=
Service Candidate
```

Some valid Observations should not enter Entity Resolution.

---

### Finding 2 - Candidate and Resolved Are Different States

An Observation may be a valid Service candidate even when no canonical Service can yet be identified.

Therefore:

```text
CANDIDATE
     !=
RESOLVED
```

---

### Finding 3 - Candidate Identifier Extraction Is Currently Small Enough to Remain Here

Email-domain and URI-hostname extraction are simple deterministic operations closely related to Candidate Detection.

Draft v0.1 therefore keeps:

```text
candidate identifier extraction
```

inside this contract.

A dedicated Identifier Extractor should be introduced only if future scenarios demonstrate sufficient independent complexity.

---

### Finding 4 - Detection Strategies Should Follow Observation Type

The preferred extensibility model is:

```text
Observation Type
       |
       v
Detection Strategy
```

rather than:

```text
Provider
   |
   v
Detection Strategy
```

This preserves provider independence.

---

### Finding 5 - UNKNOWN Avoids Premature AI Usage

Ambiguous Candidate Detection does not automatically justify AI.

Returning:

```text
UNKNOWN
```

is a valid privacy-preserving outcome.

---

### Finding 6 - Processing Status and Candidate Status Are Different

The detector must distinguish:

```text
I successfully determined that this is not a candidate.
```

from:

```text
I could not process this Observation.
```

Therefore:

```text
processing_status
```

and:

```text
candidate_status
```

must remain conceptually separate.

---

## 68. Decision Candidates

### Candidate Decision - Candidate Detection Is Explicit

```text
Service Candidate Detection should remain a distinct Discovery stage between
Observation creation and Entity Resolution.

Not every valid Observation should automatically enter Entity Resolution.
```

---

### Candidate Decision - Candidate Does Not Mean Resolved

```text
The framework must distinguish between an Observation being relevant to
Service Discovery and the framework being able to resolve that Observation
to a canonical Service.
```

---

### Candidate Decision - Detection Strategy Follows Observation Semantics

```text
Candidate Detection strategies should primarily be selected according to
Observation Type rather than provider identity.
```

---

### Candidate Decision - UNKNOWN Is Valid

```text
Candidate Detection may return UNKNOWN when available authorized information
is insufficient.

The detector must not fabricate relevance or escalate permissions silently.
```

---

### Candidate Decision - No Numerical Candidate Confidence Yet

```text
Candidate Detection should initially use explicit states and reason codes
rather than arbitrary numerical confidence values.
```

---

## 69. Current Contract Baseline

The initial Service Candidate Detector contract is:

```text
Observation
     |
     v
ServiceCandidateDetector
     |
     v
CandidateDetectionResult
     |
     +-- processing_status
     |
     +-- candidate_status
     |
     +-- candidate_identifiers
     |
     +-- reason_codes
     |
     +-- method
     |
     +-- detector_version
```

with the guarantees:

```text
provider-neutral input
Observation traceability
deterministic-first processing
UNKNOWN support
no canonical Service conclusion
no Evidence conclusion
no Relationship conclusion
no silent permission escalation
no arbitrary numerical confidence
technical failure separated from domain outcome
```

---

## 70. Next Interface Contract

With the following boundaries now defined:

```text
Connector
    |
    v
Observation
    |
    v
Service Candidate Detector
```

the next contract should define:

```text
EntityResolver
```

The Entity Resolver must answer:

> Given one or more candidate Service identifiers, which canonical Service, if any, do they represent?

The contract will need to establish distinctions such as:

```text
RESOLVED
UNRESOLVED
AMBIGUOUS
```

and determine how to preserve:

```text
original identifier
normalized identifier
canonical Service
resolution method
resolution provenance
```

without introducing arbitrary Confidence scores or losing cross-source traceability.
