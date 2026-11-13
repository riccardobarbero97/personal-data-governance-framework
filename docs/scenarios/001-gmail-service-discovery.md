# Scenario 001 - Gmail Service Discovery

**Status:** Draft  
**Scenario ID:** SCN-001  
**Domain:** Identity and Service Discovery  
**Source:** Gmail  
**Primary Capability:** Service Discovery  

---

## 1. Purpose

This scenario validates whether the Personal Data Governance Framework can discover online services with which a user has or has had a relationship by analyzing evidence available in the user's Gmail account.

The objective is not to reconstruct the mailbox or understand every email.

The objective is to answer a narrower question:

> Which services appear to have a relationship with the user, and what evidence supports that conclusion?

A mailbox may contain years of interactions with online services, including:

- account creation and verification;
- authentication events;
- password resets;
- security notifications;
- purchases;
- invoices;
- subscriptions;
- payments;
- account updates;
- account deletion;
- privacy notices;
- newsletters;
- marketing communications.

This makes email a potentially valuable source for reconstructing part of the user's digital footprint.

At the same time, email may contain highly sensitive personal information.

The scenario must therefore demonstrate that useful service discovery can be performed while following the framework's principles of:

- data minimization;
- least privilege;
- local-first processing;
- progressive permission;
- explainability;
- provenance preservation;
- explicit representation of uncertainty.

---

## 2. User Scenario

The user connects a Gmail account containing several years of email history.

During that period, the user may have:

- created online accounts;
- subscribed to digital services;
- purchased products or services;
- joined mailing lists;
- received authentication or security notifications;
- changed passwords;
- cancelled subscriptions;
- abandoned accounts;
- deleted accounts;
- stopped interacting with services.

The user may no longer remember every service with which they have interacted.

The framework analyzes authorized Gmail data and generates a consolidated set of candidate services.

For each discovered service, the framework should preserve enough information to explain why the service was identified.

Example:

```text
Service: Spotify
Domain: spotify.com

Observed senders:
- no-reply@spotify.com
- accounts@spotify.com
- newsletter@spotify.com

Observed evidence:
- ACCOUNT_VERIFICATION
- SUBSCRIPTION
- PAYMENT
- MARKETING
```

Multiple emails from the same service must not be interpreted as independent service relationships.

Instead, observations should be normalized, resolved, classified and aggregated into a service-level representation.

---

## 3. Scope

Scenario 001 focuses specifically on:

```text
Gmail
  ->
Service Discovery
```

The scenario covers:

- Gmail authorization;
- metadata collection;
- sender and domain extraction;
- service candidate detection;
- entity resolution;
- evidence classification;
- evidence aggregation;
- relationship assessment;
- progressive permission;
- traceability to source observations;
- generation of service-level information suitable for the Service Graph.

The scenario does not attempt to solve:

- full mailbox semantic analysis;
- generic email search;
- automatic deletion of online accounts;
- automated Data Subject Access Requests;
- account credential discovery;
- password extraction;
- full personal-data classification inside message bodies;
- attachment analysis;
- final relationship confidence scoring;
- final Service Graph storage schema.

Some of these capabilities may be addressed by future scenarios.

---

## 4. Expected Outcome

At the end of the pipeline, the framework should produce a collection of service candidates suitable for inclusion in the Service Graph.

A discovered service should be associated, where available, with information such as:

```text
Service identity
Canonical domain
Observed domains
Observed senders
Evidence types
Evidence count
First observed interaction
Last observed interaction
Resolution status
Classification provenance
Relationship assessment
```

A simplified conceptual output could be:

```json
{
  "service": {
    "name": "Spotify",
    "canonical_domain": "spotify.com"
  },
  "source": "gmail",
  "observed_senders": [
    "no-reply@spotify.com",
    "accounts@spotify.com"
  ],
  "evidence": [
    {
      "type": "ACCOUNT_VERIFICATION",
      "classification_method": "RULE"
    },
    {
      "type": "SUBSCRIPTION",
      "classification_method": "RULE"
    }
  ],
  "relationship": {
    "status": "DISCOVERED"
  }
}
```

This structure is illustrative.

Scenario 001 does not define the final persistent schema of the Service Graph.

---

## 5. Gmail as a Source

### 5.1 Connector

Communication with Gmail should be isolated behind a source-specific Connector.

For this scenario:

```text
Gmail Account
     |
     v
Gmail API
     |
     v
GmailConnector
     |
     v
Framework Observations
```

The Gmail Connector is responsible for:

- OAuth authorization;
- interaction with Gmail APIs;
- retrieval of authorized information;
- pagination;
- handling source-specific errors;
- translating Gmail-specific data into framework observations.

Downstream components should avoid depending directly on Gmail API objects whenever reasonably possible.

This allows other sources to later produce observations consumed by the same discovery pipeline.

Possible future sources may include:

```text
Other email providers
Password managers
Browsers
Mobile devices
Financial records
User-provided exports
Other authorized data sources
```

The existence of these possible sources does not imply that they are currently supported.

---

## 6. Permission Model

The Gmail Connector follows a Progressive Permission model.

The core principle is:

> Request the minimum level of access required to perform a capability. Increase access only when lower-privilege information is insufficient and the user explicitly authorizes the operation.

Connecting a Gmail account must not automatically imply unrestricted access to all mailbox data.

Authorization should be tied to capabilities and required data.

Conceptually:

```text
Capability
    |
    v
Required Data
    |
    v
Minimum Required Permission
```

---

### 6.1 Level 0 - No Gmail Access

The framework has no authorization to access Gmail.

Result:

```text
Gmail Service Discovery = unavailable
```

Other discovery mechanisms may continue operating independently.

---

### 6.2 Level 1 - Metadata-Based Discovery

The preferred initial discovery mode uses message metadata rather than message bodies.

Potentially useful information includes:

```text
FROM
TO
SUBJECT
DATE
LABELS
THREAD
```

Derived information may also include:

```text
sender email
sender domain
```

For example:

```text
From:
no-reply@spotify.com

Subject:
Verify your email address
```

may provide sufficient information for:

```text
Service Candidate:
Spotify

Evidence:
ACCOUNT_VERIFICATION
```

without reading the message body.

The exact Gmail API permissions required for each capability must be validated against the Gmail API authorization model before implementation.

---

### 6.3 Level 2 - Message Content

Metadata may sometimes be insufficient.

Example:

```text
From:
no-reply@example.com

Subject:
Important information about your account
```

The subject suggests an account-related relationship but does not provide enough information to determine the nature of the event.

The framework should not automatically access the message body.

Instead, the observation can remain unresolved:

```json
{
  "evidence_type": "UNKNOWN",
  "requires_additional_context": true
}
```

If a capability requiring message content is introduced, the framework should:

1. determine that existing information is insufficient;
2. explain why additional access is required;
3. request the minimum additional permission;
4. continue only if the user explicitly authorizes the operation.

Where possible, message content analysis should follow the framework's local-first processing principles.

---

### 6.4 Level 3 - Attachments

Attachments may contain particularly sensitive information, including:

- invoices;
- contracts;
- identity documents;
- financial statements;
- tickets;
- medical information;
- personal documents;
- third-party personal data.

Attachment access must therefore be considered separately from metadata or message-body access.

Basic Service Discovery must not require attachment access.

Any future capability requiring attachments must justify why lower permission levels are insufficient.

---

## 7. Initial Processing Pipeline

The Gmail Service Discovery pipeline is:

```text
GMAIL ACCOUNT
      |
      v
OAuth Authorization
      |
      v
Gmail Connector
      |
      v
Metadata Collection
      |
      v
Observation Creation
      |
      v
Sender / Domain Extraction
      |
      v
Service Candidate Detection
      |
      v
Entity Resolution
      |
      v
Evidence Classification
      |
   +--+--+
   |     |
 Rules   AI
   |     |
   +--+--+
      |
      v
Evidence Aggregation
      |
      v
Relationship Assessment
      |
      v
SERVICE GRAPH
```

Each stage has a different responsibility.

### Gmail Connector

Communicates with Gmail and retrieves authorized information.

### Observation Creation

Represents information obtained from the source without immediately assuming its meaning.

### Service Candidate Detection

Identifies observations that may indicate interaction with an external service.

### Entity Resolution

Attempts to determine which service an observed identifier represents.

### Evidence Classification

Determines what an observation means in the context of a possible user-service relationship.

### Evidence Aggregation

Combines multiple pieces of evidence associated with the same service.

### Relationship Assessment

Evaluates what the complete set of evidence suggests about the user's relationship with the service.

### Service Graph

Stores or consumes the resulting service-level representation.

---

## 8. Observations

An Observation represents something detected in a source.

It should not be confused with the framework's interpretation of that information.

Example source information:

```text
From:
no-reply@spotify.com

Subject:
Verify your email address

Date:
2026-01-01
```

could produce a conceptual observation such as:

```json
{
  "source": "gmail",
  "sender": "no-reply@spotify.com",
  "sender_domain": "spotify.com",
  "subject": "Verify your email address",
  "observed_at": "2026-01-01"
}
```

At this stage, the framework has observed information.

It has not yet established what that information means.

Therefore:

```text
Observation != Evidence
```

This distinction allows classification logic to evolve without destroying or rewriting source-derived information.

---

## 9. Sender and Domain Extraction

Email sender addresses provide signals for service discovery.

For example:

```text
no-reply@spotify.com
accounts@spotify.com
newsletter@spotify.com
support@spotify.com
```

contain the common identifier:

```text
spotify.com
```

Basic normalization can therefore produce:

```text
no-reply@spotify.com
        |
        v
spotify.com
```

However, the framework must not assume that:

```text
sender domain = service
```

in every case.

The extracted domain is an identifier used during Entity Resolution.

It is not automatically a canonical service identity.

---

## 10. Service Candidate Detection

Not every external email represents an online service.

Examples that should not automatically become services include:

```text
Personal contacts
Individual employees
Generic consumer email accounts
Discussion groups
Mailing infrastructure
Automated forwarding systems
```

Service Candidate Detection determines whether an observation should enter the Service Discovery pipeline.

Conceptually:

```text
Observation
    |
    v
Candidate Detection
   / \
  /   \
yes   no
 |     |
 v     v
Entity  Ignore for
Resolution this capability
```

Ignoring an observation for Service Discovery does not necessarily mean deleting it or declaring it irrelevant to every other capability.

It means only that the observation does not currently provide useful evidence for this specific capability.

---

## 11. Entity Resolution

Entity Resolution converts observed identifiers into candidate canonical services.

Example:

```text
no-reply@spotify.com
accounts@spotify.com
newsletter@spotify.com
        |
        v
spotify.com
        |
        v
Spotify
```

The Entity Resolution Engine should support cases where multiple identifiers represent the same service.

Possible signals may include:

- sender email address;
- sender domain;
- domain normalization;
- sender display name;
- multiple observed addresses;
- service aliases;
- previously resolved entities;
- additional evidence available to the framework.

The implementation of the resolution algorithm is outside the scope of this scenario.

---

### 11.1 Preserve Resolution Provenance

Entity Resolution must preserve the relationship between observed and resolved values.

For example:

```text
Observed identifier:
no-reply@spotify.com

Extracted domain:
spotify.com

Resolved service:
Spotify
```

The original identifier should not be replaced destructively by the resolved entity.

This permits:

- explainability;
- correction;
- reprocessing;
- future improvements to Entity Resolution.

---

### 11.2 Subdomains

The framework must not assume that every hostname represents an independent service.

For example:

```text
mail.example.com
accounts.example.com
notifications.example.com
```

may all belong to the same underlying service.

Domain normalization must therefore be domain-aware rather than based on naïve string manipulation.

---

### 11.3 Shared Infrastructure

Many services use third-party infrastructure for:

- transactional email;
- marketing;
- customer support;
- notification delivery;
- cloud hosting.

The observed technical infrastructure may therefore belong to an intermediary rather than to the service with which the user has a relationship.

The framework must avoid automatically converting infrastructure providers into user-service relationships without sufficient evidence.

---

### 11.4 Brands, Services and Organizations

The architecture must not assume:

```text
one domain
    =
one service
    =
one company
```

A company may operate multiple services.

A service may use multiple domains.

A service may change ownership.

A service may change its name.

A company may use external infrastructure.

Domain identity, service identity and organizational identity are therefore related but distinct concepts.

Scenario 001 focuses primarily on Service Identity.

---

### 11.5 Unresolved Entities

Entity Resolution must be allowed to fail safely.

Example:

```json
{
  "observed_domain": "example-mail.net",
  "resolved_service": null,
  "resolution_status": "UNRESOLVED"
}
```

An unresolved service is preferable to an incorrect association.

Therefore:

> Uncertainty is a valid state.

---

## 12. Evidence Taxonomy

After an observation has been associated with a candidate service, the framework attempts to determine what the observation means.

The initial Evidence Taxonomy is:

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
UNKNOWN
```

This taxonomy is intentionally limited.

Additional categories should be introduced when real scenarios demonstrate that they are necessary.

---

### 12.1 ACCOUNT_CREATION

Evidence suggesting that an account was created.

Example:

```text
Welcome! Your account has been created.
```

This represents relatively strong evidence of an account relationship.

---

### 12.2 ACCOUNT_VERIFICATION

Evidence requesting or confirming verification of an account or email address.

Example:

```text
Verify your email address
```

This suggests that an account creation or account-linking process may have occurred.

---

### 12.3 AUTHENTICATION

Evidence related to authentication activity.

Examples:

```text
Your login code
Sign-in attempt
New sign-in detected
```

Authentication evidence may strongly suggest the existence of an account relationship.

---

### 12.4 PASSWORD_RESET

Evidence related to password recovery or reset.

Examples:

```text
Reset your password
Your password has been changed
```

This is generally significant evidence of an account-like relationship.

However, the framework must distinguish between observing a password-reset communication and proving that the reset operation was completed.

---

### 12.5 SECURITY_NOTIFICATION

Evidence related to security-relevant events.

Examples:

```text
New device detected
Suspicious login attempt
Security settings changed
```

---

### 12.6 PURCHASE

Evidence indicating a purchase or commercial transaction.

Example:

```text
Thank you for your order.
```

A purchase does not necessarily prove that a persistent account exists because guest purchases may be possible.

---

### 12.7 INVOICE

Evidence indicating the existence of an invoice.

Example:

```text
Your invoice is ready.
```

---

### 12.8 SUBSCRIPTION

Evidence related to a subscription.

Examples:

```text
Your subscription has started.
Your subscription has been renewed.
Your subscription will expire.
```

---

### 12.9 PAYMENT

Evidence related to a payment.

Examples:

```text
Payment received.
Your payment was successful.
```

Payment evidence must remain separate from account evidence.

A payment can occur without a persistent user account.

---

### 12.10 ACCOUNT_UPDATE

Evidence indicating a modification to account information or configuration.

Example:

```text
Your account information has been updated.
```

---

### 12.11 ACCOUNT_DELETION

Evidence indicating or suggesting that an account was deleted, closed or scheduled for closure.

Examples:

```text
Your account has been deleted.
We received your account closure request.
```

This category is particularly important because Service Discovery includes historical relationships.

A deleted account may still be relevant to understanding the user's digital footprint.

---

### 12.12 MARKETING

Promotional or commercial communication.

Example:

```text
50% off Premium this weekend!
```

Marketing alone is relatively weak evidence of an account relationship.

A user may receive marketing communications without maintaining an account with the sender.

---

### 12.13 NEWSLETTER

Recurring communication associated with a mailing list or informational subscription.

A newsletter subscription must not automatically be interpreted as evidence of a user account.

---

### 12.14 PRIVACY_NOTICE

Communication concerning:

- privacy policies;
- terms;
- data processing;
- privacy rights;
- related regulatory notices.

Example:

```text
We have updated our Privacy Policy.
```

A privacy notice may provide evidence of some type of relationship but does not independently prove that the user owns an account.

---

### 12.15 UNKNOWN

The observation appears potentially relevant but cannot safely be assigned to another evidence category.

Example:

```text
Important information about your account
```

`UNKNOWN` is a valid classification.

It is not a processing error.

---

## 13. Evidence Classification

The Evidence Classifier determines the semantic meaning of an observation.

Conceptually:

```text
Observation
    |
    v
Evidence Classifier
    |
    v
Evidence
```

For example:

```text
Observation:

From:
no-reply@spotify.com

Subject:
Verify your email address
```

may produce:

```json
{
  "evidence_type": "ACCOUNT_VERIFICATION"
}
```

Evidence classification should follow the principle:

> Use AI for ambiguity, not for everything.

---

## 14. Deterministic Classification

Clear patterns should be classified using deterministic rules where practical.

Example:

```text
Subject:
Verify your email address
```

could match a rule for:

```text
ACCOUNT_VERIFICATION
```

while:

```text
Subject:
Reset your password
```

could match:

```text
PASSWORD_RESET
```

Advantages of deterministic classification include:

- predictable behavior;
- explainability;
- repeatability;
- testability;
- low computational cost;
- limited disclosure of sensitive information;
- no dependency on an AI model.

Classification provenance should be preserved.

Example:

```json
{
  "evidence_type": "PASSWORD_RESET",
  "classification_method": "RULE"
}
```

---

## 15. Ambiguous Evidence

Not every observation can be safely interpreted through deterministic rules.

Example:

```text
Subject:
Important information about your account
```

The framework should be allowed to return:

```json
{
  "evidence_type": "UNKNOWN",
  "classification_method": "RULE",
  "requires_additional_context": true
}
```

The framework must not invent precision where insufficient information exists.

---

## 16. AI-Assisted Classification

AI may be used when deterministic classification cannot resolve an observation with sufficient reliability.

Conceptually:

```text
             Observation
                  |
                  v
        Deterministic Rules
                  |
            +-----+-----+
            |           |
       classified    ambiguous
            |           |
            |           v
            |     AI Classifier
            |           |
            +-----+-----+
                  |
                  v
               Evidence
```

The AI classifier should receive only the minimum data necessary for the classification task.

AI-derived classifications must preserve provenance.

Example:

```json
{
  "evidence_type": "SECURITY_NOTIFICATION",
  "classification_method": "AI"
}
```

AI availability must not be required for basic Service Discovery.

If AI processing is unavailable or disabled:

```text
Deterministic processing continues
        |
        v
Unresolved observations remain UNKNOWN
```

This provides graceful degradation.

---

## 17. AI Boundary

Scenario 001 establishes the following design principle:

> AI should handle ambiguity, not replace deterministic processing that already works reliably.

Therefore AI should not automatically be used for:

- domain extraction;
- email-address parsing;
- straightforward normalization;
- known deterministic patterns;
- basic aggregation;
- operations where explicit rules are sufficient.

AI may become useful for:

- ambiguous subjects;
- semantic classification;
- multilingual interpretation;
- complex contextual evidence;
- cases where deterministic rules would become excessively brittle.

The exact AI implementation remains outside the scope of Scenario 001.

---

## 18. Evidence Aggregation

Individual emails are observations.

They must not be interpreted as independent service relationships.

For example:

```text
100 Spotify emails
```

must not produce:

```text
100 Spotify relationships
```

The conceptual flow is:

```text
Messages
   |
   v
Observations
   |
   v
Evidence
   |
   v
Aggregated Service Evidence
```

Example:

```text
Service: Spotify

Evidence:

ACCOUNT_VERIFICATION    1
SECURITY_NOTIFICATION  3
SUBSCRIPTION           10
PAYMENT                18
MARKETING              68
```

Evidence count may be useful, but frequency alone must not determine relationship strength.

For example:

```text
1 ACCOUNT_VERIFICATION
```

may provide different information from:

```text
100 MARKETING
```

Therefore aggregation must preserve at least:

```text
evidence type
evidence frequency
temporal information
provenance
```

without prematurely defining a fixed scoring formula.

---

## 19. Relationship Assessment

Evidence Classification answers:

> What does this observation represent?

Relationship Assessment answers:

> What does the accumulated evidence suggest about the user's relationship with the service?

These are separate problems.

For example:

```text
ACCOUNT_VERIFICATION
PASSWORD_RESET
SUBSCRIPTION
PAYMENT
```

provides different relationship evidence from:

```text
MARKETING
MARKETING
NEWSLETTER
```

However, Scenario 001 does not define a final numerical relationship score.

Values such as:

```text
ACCOUNT_VERIFICATION = 0.87
```

should not be introduced until the meaning and calibration of such values can be justified.

The first implementation should preserve evidence rather than create arbitrary precision.

---

## 20. Temporal Dimension

Service relationships change over time.

For example:

```text
2021 ACCOUNT_CREATION
2022 PURCHASE
2023 PAYMENT
2024 ACCOUNT_DELETION
```

should not be interpreted in the same way as:

```text
2021 ACCOUNT_CREATION
2022 PURCHASE
2025 PASSWORD_RESET
2026 SECURITY_NOTIFICATION
```

Temporal information must therefore be preserved.

At minimum, aggregated service information should eventually support concepts equivalent to:

```text
first observed
last observed
evidence timeline
```

The final temporal relationship model remains to be defined.

---

## 21. Historical Relationships

Service Discovery is not limited to services currently used by the user.

A historical account may still be relevant to the Personal Data Governance Framework because:

- personal data may still exist with the provider;
- historical transactions may remain stored;
- regulatory retention obligations may apply;
- the user may incorrectly believe the relationship no longer exists;
- the service may still represent part of the user's digital footprint.

Therefore:

```text
Current Relationship
```

and:

```text
Historical Relationship
```

must remain distinguishable concepts.

Scenario 001 must not discard a service simply because account deletion evidence exists.

---

## 22. Expected Service-Level Output

After aggregation, a discovered service may conceptually look like:

```json
{
  "source": "gmail",
  "service": {
    "name": "Spotify",
    "canonical_domain": "spotify.com",
    "resolution_status": "RESOLVED"
  },
  "observed_identifiers": {
    "senders": [
      "no-reply@spotify.com",
      "accounts@spotify.com",
      "newsletter@spotify.com"
    ],
    "domains": [
      "spotify.com"
    ]
  },
  "evidence_summary": {
    "ACCOUNT_VERIFICATION": 1,
    "SECURITY_NOTIFICATION": 3,
    "SUBSCRIPTION": 10,
    "PAYMENT": 18,
    "MARKETING": 68
  },
  "first_observed": "YYYY-MM-DD",
  "last_observed": "YYYY-MM-DD",
  "relationship": {
    "status": "DISCOVERED"
  }
}
```

This structure is illustrative and must not be considered the final persistent data model.

The required architectural property is traceability:

```text
Service
   |
   v
Relationship Assessment
   |
   v
Aggregated Evidence
   |
   v
Individual Evidence
   |
   v
Observation
   |
   v
Source
```

---

## 23. Explainability

The framework should be able to answer:

> Why do you think I have or had a relationship with this service?

For example:

```text
Spotify was discovered because:

- messages were observed from addresses associated with spotify.com;
- spotify.com was resolved to Spotify;
- 1 ACCOUNT_VERIFICATION event was identified;
- 10 SUBSCRIPTION events were identified;
- 18 PAYMENT events were identified;
- additional supporting evidence exists in the analyzed Gmail source.
```

The framework should not need to expose irrelevant raw mailbox content to explain the discovery.

Explainability should be based on the minimum useful supporting evidence.

---

## 24. Edge Cases

### 24.1 Newsletter Without Account

The mailbox contains years of:

```text
NEWSLETTER
MARKETING
```

from a service.

The framework must not automatically conclude that the user owns an account.

---

### 24.2 Purchase Without Account

Evidence includes:

```text
PURCHASE
PAYMENT
INVOICE
```

The user may have completed a guest purchase.

The framework should recognize the commercial relationship without automatically asserting the existence of an account.

---

### 24.3 Deleted Account

Evidence includes:

```text
ACCOUNT_CREATION
ACCOUNT_VERIFICATION
ACCOUNT_DELETION
```

The service remains relevant as a historical relationship.

---

### 24.4 Multiple Sender Addresses

```text
support@example.com
no-reply@example.com
billing@example.com
security@example.com
```

may all represent the same service.

---

### 24.5 Multiple Domains

A single service may legitimately use multiple domains.

Entity Resolution must therefore support:

```text
domain-a.example
domain-b.example
domain-c.example
        |
        v
same service
```

when sufficient evidence supports that conclusion.

---

### 24.6 Shared Email Infrastructure

A service may use external infrastructure for sending email.

The framework must avoid incorrectly creating a service relationship with the infrastructure provider when the actual relationship is with another service.

---

### 24.7 Personal Emails

An email from:

```text
person@example.com
```

does not automatically mean that `example.com` represents a service used by the user.

Service Candidate Detection must distinguish service-oriented communication from ordinary personal correspondence where reasonably possible.

---

### 24.8 Generic Consumer Email Providers

Receiving an email from another person using a generic email provider does not constitute evidence that the user has a relationship with that provider.

For example:

```text
someone@gmail.com
```

must not cause Google Gmail to be discovered as a service relationship purely because the sender uses Gmail.

---

### 24.9 Mailing Lists

A mailing list may use infrastructure unrelated to the organization responsible for the content.

Mailing-list membership also does not necessarily imply the existence of a traditional user account.

---

### 24.10 Forwarded Messages

Forwarded messages may contain historical sender information inside the message content.

The framework should distinguish actual message metadata from quoted or forwarded content whenever applicable.

---

### 24.11 User Address Aliases

The user's address may appear in different forms, including:

```text
aliases
plus addressing
historical addresses
alternate domains
```

These variations must not be interpreted as external services.

---

### 24.12 Ambiguous Subjects

Subjects such as:

```text
Important update
Action required
Your request
Important information about your account
```

may not contain enough information for reliable classification.

The correct classification may remain:

```text
UNKNOWN
```

---

### 24.13 Multilingual Mailboxes

Equivalent evidence may appear in multiple languages.

For example:

```text
Verify your email address
Verifica il tuo indirizzo email
Vérifiez votre adresse e-mail
```

The classification architecture should not assume that the mailbox contains only one language.

Scenario 001 does not prescribe how multilingual classification must be implemented.

---

### 24.14 Duplicate Messages

Technical duplication may occur because of:

- forwarding;
- duplicate delivery;
- synchronization;
- imports;
- mailbox migrations.

Duplicate observations must not artificially increase perceived relationship strength.

---

### 24.15 Service Rebranding

A service may change its:

```text
name
domain
owner
branding
```

over time.

Historical observations should therefore remain preserved independently of the current canonical representation.

---

## 25. Failure Modes

### 25.1 OAuth Authorization Denied

The user refuses Gmail authorization.

Result:

```text
Gmail Service Discovery cannot run.
```

The rest of the framework must remain operational.

---

### 25.2 Authorization Revoked

The user revokes previously granted Gmail access.

The Connector must stop collecting new Gmail data.

Source authorization and lifecycle management of previously derived information are separate concerns.

The broader framework must define how previously collected information is handled after revocation.

---

### 25.3 Insufficient Permission

A capability requires information that is unavailable under the current permission level.

The system must not silently escalate access.

Expected flow:

```text
Insufficient Data
      |
      v
Additional Permission Required
      |
      v
Explain Why
      |
      v
User Decision
    /     \
 allow   deny
  |       |
  v       v
continue remain unresolved
```

---

### 25.4 Gmail API Failure

Possible failures include:

- network errors;
- temporary API unavailability;
- authorization expiration;
- rate limiting;
- interrupted synchronization;
- malformed or unexpected responses.

The Connector must isolate source failures from downstream domain state as much as reasonably possible.

Previously valid evidence must not be corrupted because a subsequent synchronization fails.

---

### 25.5 Entity Resolution Failure

The framework cannot reliably associate an identifier with a canonical service.

Expected result:

```text
resolution_status = UNRESOLVED
```

The original observation remains available.

---

### 25.6 Evidence Classification Failure

The framework cannot determine the evidence category.

Expected result:

```text
evidence_type = UNKNOWN
```

The observation must not disappear.

---

### 25.7 AI Unavailable

AI-assisted classification may be unavailable because of:

- user preference;
- deployment configuration;
- connectivity;
- model failure;
- privacy policy;
- unsupported environment.

The deterministic discovery pipeline must continue operating.

AI must not be a mandatory dependency of basic Gmail Service Discovery.

---

### 25.8 Partial Mailbox Analysis

Processing may stop before the entire Gmail account has been analyzed.

The framework must distinguish:

```text
No evidence found
```

from:

```text
Analysis incomplete
```

A partial scan must not be represented as complete.

---

## 26. Privacy and Security Requirements

Gmail may expose highly sensitive personal information.

The Gmail Connector must therefore be treated as a sensitive trust boundary.

---

### 26.1 Data Minimization

Only the information necessary for the requested capability should be retrieved.

If metadata is sufficient for Service Discovery, complete message content should not be retrieved merely because it is technically accessible.

---

### 26.2 Least Privilege

The Connector should request the narrowest permission capable of supporting the requested capability.

Authorization should not be broader than necessary simply to simplify implementation.

---

### 26.3 Progressive Permission

Permission escalation should occur only when:

1. the current capability requires additional information;
2. lower-privilege data is insufficient;
3. the additional access can be explained;
4. the user explicitly authorizes it.

---

### 26.4 Local-First Processing

Where technically possible and consistent with the architecture, sensitive source data should be processed locally.

Raw email content should not be transmitted to external AI services by default.

Any future remote-processing capability must explicitly document:

```text
what data leaves the local environment
why it is required
where it is sent
how it is processed
what the user authorizes
```

---

### 26.5 Provenance

Derived information must remain traceable to its origin.

The architecture should preserve enough information to determine:

```text
where the observation came from
when it was observed
how it was normalized
how it was classified
how the entity was resolved
how it contributed to a relationship assessment
```

---

### 26.6 Revocation

The user must be able to disconnect Gmail.

The following operations must remain conceptually distinct:

```text
Revoke Gmail access
Delete Connector credentials
Delete cached source data
Delete observations
Delete evidence
Delete derived service relationships
```

The exact lifecycle behavior remains part of the broader framework design.

---

## 27. Architectural Findings

Scenario 001 identifies several architectural concepts that should be reflected in the Identity and Service Discovery architecture.

---

### 27.1 Connector

A Connector encapsulates communication with an external data source.

For Scenario 001:

```text
GmailConnector
```

isolates Gmail-specific behavior from the rest of the framework.

---

### 27.2 Observation

An Observation represents information obtained from a source.

It does not represent a final interpretation.

Therefore:

```text
SOURCE
  |
  v
OBSERVATION
```

must be an explicit conceptual boundary.

---

### 27.3 Evidence Classifier

The Evidence Classifier interprets observations using:

```text
Deterministic Rules
        +
AI-Assisted Classification when necessary
```

The classifier must support `UNKNOWN` as a valid result.

---

### 27.4 Entity Resolution

Entity Resolution transforms observed technical identifiers into candidate Service entities.

It must preserve provenance and permit unresolved states.

---

### 27.5 Evidence Aggregation

Individual evidence items must be aggregated at the Service level before relationship assessment.

Message count alone is insufficient to describe a relationship.

---

### 27.6 Relationship Assessment

Relationship Assessment is distinct from Evidence Classification.

It operates on aggregated evidence rather than individual observations.

---

### 27.7 Progressive Permission

The scenario demonstrates the need for explicit access escalation.

A Connector must not assume that connecting a source implies permission to retrieve all information available from that source.

---

## 28. Architectural Boundaries

Scenario 001 establishes four important distinctions.

### 28.1 Source Is Not Observation

```text
SOURCE != OBSERVATION
```

Gmail is a Source.

A specific sender, subject and date retrieved from Gmail form part of an Observation.

---

### 28.2 Observation Is Not Evidence

```text
OBSERVATION != EVIDENCE
```

Example:

```text
Observation:
Subject = "Verify your email address"

Evidence:
ACCOUNT_VERIFICATION
```

---

### 28.3 Evidence Is Not Relationship

```text
EVIDENCE != RELATIONSHIP
```

Example:

```text
Evidence:
MARKETING

Relationship:
Unknown
```

Multiple evidence items must be considered before assessing the relationship.

---

### 28.4 Domain Is Not Service

```text
DOMAIN != SERVICE
```

Example:

```text
spotify.com
```

is an observed technical identifier.

```text
Spotify
```

is a resolved Service entity.

The mapping between them belongs to Entity Resolution.

---

## 29. Architectural Decisions Derived from Scenario 001

### D-010 - Progressive Permission

```text
Connectors should request the minimum level of access
required to perform a capability.

Access to more sensitive information should be requested
only when lower-privilege data is insufficient and the user
explicitly authorizes the operation.
```

#### Rationale

Data sources such as Gmail may expose substantially more sensitive information than is necessary for a specific capability.

Permissions should therefore be capability-driven.

---

### D-011 - AI for Ambiguity

```text
Deterministic processing should be preferred when observations
can be reliably interpreted using explicit rules.

AI-assisted processing should primarily be used when deterministic
processing cannot resolve ambiguity and when the required input data
is available within the user's authorized permission boundary.
```

#### Rationale

This reduces:

- unnecessary exposure of personal information;
- computational cost;
- model dependency;
- nondeterministic behavior.

It also improves explainability and testability.

---

### D-012 - Preserve Source Provenance

```text
Derived service information must remain traceable to the observations
and evidence from which it was produced.

Normalization, classification, aggregation and entity resolution
must not destroy the provenance required to explain or reprocess
derived information.
```

#### Rationale

Provenance is required for:

- explainability;
- auditing;
- user correction;
- reclassification;
- entity-resolution improvements;
- debugging.

---

### D-013 - Unknown Is a Valid State

```text
The framework must support unresolved entities, unknown evidence
types and uncertain relationships as valid states.

The absence of sufficient evidence must not be replaced by
fabricated certainty.
```

#### Rationale

A privacy-oriented discovery system should prefer uncertainty over incorrect claims.

---

## 30. Open Questions

Scenario 001 intentionally leaves some implementation and architectural decisions unresolved.

These should be addressed through implementation experiments or additional scenarios.

---

### OQ-001 - Exact Gmail Permission Mapping

What exact Gmail authorization scopes are required for each capability?

The final architecture should explicitly map:

```text
Capability
    |
    v
Required Gmail Data
    |
    v
Required OAuth Permission
```

This must be validated against the current Gmail API authorization model before implementation.

---

### OQ-002 - Local Storage

Which Gmail-derived information should be persisted locally?

Possible options include:

```text
Raw metadata
Normalized observations
Classified evidence
Aggregated evidence
Service Graph only
```

The design must balance:

```text
Data Minimization
       vs
Reprocessing Capability
```

---

### OQ-003 - Entity Resolution Mechanism

How should mappings such as:

```text
spotify.com -> Spotify
```

be resolved?

Possible mechanisms may include:

- deterministic normalization;
- curated service mappings;
- local knowledge bases;
- external datasets;
- AI-assisted resolution;
- combinations of the above.

Scenario 001 does not select a final implementation.

---

### OQ-004 - Relationship Model

How should the framework distinguish relationships such as:

```text
Active Account
Historical Account
Deleted Account
Subscription
Commercial Relationship
Newsletter Relationship
Unknown Relationship
```

without generating false certainty?

---

### OQ-005 - Evidence Strength

Should evidence categories eventually carry different relationship significance?

For example:

```text
ACCOUNT_VERIFICATION
```

may provide different evidence from:

```text
MARKETING
```

Any future weighting model must be defined and justified rather than arbitrarily assigned.

---

### OQ-006 - AI Execution Boundary

If AI-assisted classification requires message content, where should inference occur?

Possible approaches include:

```text
Local model
Remote model
Hybrid model
```

Any remote processing must be evaluated against:

- data minimization;
- privacy;
- transparency;
- user authorization;
- local-first principles.

---

### OQ-007 - Incremental Synchronization

After the initial mailbox analysis, how should the Connector identify only new or changed information?

A mature implementation should avoid repeatedly processing the entire mailbox when unnecessary.

---

### OQ-008 - Reclassification

If Evidence Classification improves, can historical observations be reprocessed?

The separation:

```text
Observation
    |
    v
Evidence
    |
    v
Relationship
```

should make controlled reclassification possible.

---

### OQ-009 - Entity Re-Resolution

If Entity Resolution improves, can previously unresolved or incorrectly resolved observations be processed again without retrieving the source data again?

This requirement influences the local persistence model.

---

### OQ-010 - User Correction

Should users be able to correct framework conclusions?

Example:

```text
Framework:
example.com -> Example Service

User:
This is not the same service.
```

User correction may become an important part of:

- Entity Resolution;
- service merging;
- service splitting;
- Evidence Classification;
- future relationship assessment.

---

### OQ-011 - Confidence

Should the framework expose confidence values?

If confidence is introduced, its semantics must be explicitly defined.

The framework should not generate arbitrary values such as:

```text
confidence = 0.87
```

without defining:

- what the value represents;
- how it is calculated;
- how it is calibrated;
- how users should interpret it.

---

## 31. Acceptance Criteria

Scenario 001 is considered architecturally supported when the framework can demonstrate the following behavior.

### Authorization

- [ ] The user can explicitly authorize Gmail access.
- [ ] The Connector requests only the access required by the capability.
- [ ] Additional permissions are not silently requested.
- [ ] The user can deny additional authorization without breaking unrelated framework functionality.

### Collection

- [ ] The Gmail Connector can retrieve the information required for metadata-based Service Discovery.
- [ ] Gmail-specific data can be translated into framework Observations.
- [ ] Partial collection can be distinguished from complete collection.

### Candidate Detection

- [ ] Sender identities can be analyzed without interpreting every sender as a Service.
- [ ] Personal correspondence does not automatically create Service entities.
- [ ] Generic email providers do not automatically become Service relationships.

### Entity Resolution

- [ ] Sender addresses can be normalized into useful identifiers.
- [ ] Multiple senders can potentially resolve to the same Service.
- [ ] Multiple domains can potentially resolve to the same Service.
- [ ] Entity Resolution can return `UNRESOLVED`.
- [ ] Original observed identifiers remain available after resolution.

### Evidence Classification

- [ ] Observations can be classified using the initial Evidence Taxonomy.
- [ ] Deterministic classification can operate without AI.
- [ ] Ambiguous observations can return `UNKNOWN`.
- [ ] AI-assisted classifications are distinguishable from deterministic classifications.
- [ ] AI unavailability does not prevent basic Service Discovery.

### Aggregation

- [ ] Multiple emails do not create multiple copies of the same relationship.
- [ ] Evidence can be aggregated at the Service level.
- [ ] Evidence type is preserved during aggregation.
- [ ] Temporal information is preserved.
- [ ] Provenance remains available.

### Relationship Assessment

- [ ] Marketing alone does not automatically imply an account.
- [ ] Newsletter subscription alone does not automatically imply an account.
- [ ] Purchase evidence does not automatically imply an account.
- [ ] Historical relationships can be represented.
- [ ] Account deletion evidence does not automatically remove the Service from the user's historical digital footprint.

### Privacy and Security

- [ ] Basic Service Discovery does not require attachment access.
- [ ] Message-body access is not assumed by default.
- [ ] Access escalation requires an explicit capability need.
- [ ] Access escalation requires explicit user authorization.
- [ ] Source-derived information remains traceable.

### Architecture

- [ ] Gmail-specific behavior is primarily isolated inside `GmailConnector`.
- [ ] `Source`, `Observation`, `Evidence`, `Relationship` and `Service` remain conceptually distinct.
- [ ] The resulting service-level information can be consumed by the Service Graph.

---

## 32. Scenario Result

Scenario 001 demonstrates that Gmail-based Service Discovery should not be modeled as:

```text
Email
  |
  v
AI
  |
  v
Service List
```

A more robust architecture is:

```text
Gmail
  |
  v
GmailConnector
  |
  v
Observations
  |
  v
Service Candidate Detection
  |
  v
Entity Resolution
  |
  v
Evidence Classification
  |
  +------------------+
  |                  |
  v                  v
Rules          AI for Ambiguity
  |                  |
  +--------+---------+
           |
           v
        Evidence
           |
           v
Evidence Aggregation
           |
           v
Relationship Assessment
           |
           v
Service Graph
```

The scenario also establishes the following conceptual boundaries:

```text
SOURCE != OBSERVATION

OBSERVATION != EVIDENCE

EVIDENCE != RELATIONSHIP

DOMAIN != SERVICE
```

and the following permission model:

```text
Minimum Permission
        |
        v
Attempt Capability
        |
   +----+----+
   |         |
Enough    Insufficient
   |         |
   v         v
Continue   Explain Need
             |
             v
       Request Additional
          Permission
          /      \
       allow     deny
         |         |
         v         v
      Continue   Remain
                Unresolved
```

The primary result of Scenario 001 is therefore not a Gmail implementation.

It is validation that Identity and Service Discovery should be designed around:

- source isolation through Connectors;
- capability-driven authorization;
- minimum-access collection;
- explicit Observations;
- Entity Resolution;
- Evidence Classification;
- deterministic processing where possible;
- AI-assisted handling of ambiguity;
- safe representation of uncertainty;
- evidence aggregation;
- temporal awareness;
- relationship assessment;
- provenance preservation;
- explainability;
- progressive permission.

These findings should be incorporated into the next revision of:

```text
docs/architecture/01-identity-and-service-discovery.md
```

before implementation-specific software interfaces are finalized.

---

## 33. References

Official Gmail API documentation should be treated as the authoritative source for Gmail-specific implementation details, especially OAuth scopes and message retrieval behavior.

- Gmail API - Choose Gmail API scopes  
  https://developers.google.com/workspace/gmail/api/auth/scopes

- Gmail API - `users.messages.list`  
  https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list

Implementation decisions concerning Gmail permissions must be verified against the current official Google documentation at implementation time.
