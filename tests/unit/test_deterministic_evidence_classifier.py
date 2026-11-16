from datetime import datetime, timezone

from personal_data_governance.discovery.evidence_classification.deterministic import (
    DeterministicEmailEvidenceClassifier,
    SubjectClassificationRule,
)
from personal_data_governance.discovery.evidence_classification.protocol import (
    ClassificationContext,
)
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.observation import ObservationType
from personal_data_governance.domain.enums.processing import (
    ClassificationMethod,
    ClassificationStatus,
    ProcessingStatus,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)


def build_email_observation(
    subject: str | None,
    schema_version: int = 1,
) -> Observation:
    return Observation(
        id=ObservationId("observation_001"),
        connected_source_id=ConnectedSourceId(
            "source_gmail_personal"
        ),
        observation_type=ObservationType.EMAIL_MESSAGE_METADATA,
        schema_version=SchemaVersion(schema_version),
        source_reference=SourceReference(
            "gmail_message_123"
        ),
        observed_at=None,
        collected_at=datetime.now(timezone.utc),
        payload=EmailMessageMetadataV1(
            sender="no-reply@spotify.com",
            recipients=(
                "user@example.com",
            ),
            subject=subject,
            thread_reference="gmail_thread_001",
            labels=(),
        ),
    )


def build_context() -> ClassificationContext:
    return ClassificationContext(
        classifier_version="1",
    )


def classify_subject(
    subject: str | None,
):
    classifier = DeterministicEmailEvidenceClassifier()

    observation = build_email_observation(
        subject=subject
    )

    return classifier.classify(
        observation=observation,
        context=build_context(),
    )


def test_email_verification_subject_is_classified() -> None:
    result = classify_subject(
        "Verify your email address"
    )

    assert result.processing_status == ProcessingStatus.SUCCESS

    assert (
        result.classification_status
        == ClassificationStatus.CLASSIFIED
    )

    assert result.method == ClassificationMethod.RULE
    assert len(result.evidence_candidates) == 1

    candidate = result.evidence_candidates[0]

    assert (
        candidate.evidence_type
        == EvidenceType.ACCOUNT_VERIFICATION
    )

    assert candidate.observation_ids == (
        ObservationId("observation_001"),
    )

    assert candidate.method == ClassificationMethod.RULE

    assert candidate.reason_codes == (
        "ACCOUNT_VERIFICATION_SUBJECT",
    )

    assert result.reason_codes == (
        "ACCOUNT_VERIFICATION_SUBJECT",
    )


def test_password_reset_subject_is_classified() -> None:
    result = classify_subject(
        "Reset your password"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.PASSWORD_RESET
    )


def test_security_alert_subject_is_classified() -> None:
    result = classify_subject(
        "Security alert: new sign-in detected"
    )

    evidence_types = {
        candidate.evidence_type
        for candidate in result.evidence_candidates
    }

    assert EvidenceType.SECURITY_NOTIFICATION in evidence_types


def test_authentication_code_subject_is_classified() -> None:
    result = classify_subject(
        "Your sign-in code"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.AUTHENTICATION
    )


def test_account_creation_subject_is_classified() -> None:
    result = classify_subject(
        "Welcome to Example Service"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.ACCOUNT_CREATION
    )


def test_payment_subject_is_classified() -> None:
    result = classify_subject(
        "Your payment was successful"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.PAYMENT
    )


def test_invoice_subject_is_classified() -> None:
    result = classify_subject(
        "Your invoice is available"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.INVOICE
    )


def test_purchase_subject_is_classified() -> None:
    result = classify_subject(
        "Order confirmation"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.PURCHASE
    )


def test_subscription_subject_is_classified() -> None:
    result = classify_subject(
        "Your subscription has been renewed"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.SUBSCRIPTION
    )


def test_privacy_notice_subject_is_classified() -> None:
    result = classify_subject(
        "Changes to our privacy policy"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.PRIVACY_NOTICE
    )


def test_newsletter_subject_is_classified() -> None:
    result = classify_subject(
        "Your weekly newsletter"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.NEWSLETTER
    )


def test_marketing_subject_is_classified() -> None:
    result = classify_subject(
        "Exclusive offer: save 20%"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.MARKETING
    )


def test_subject_matching_is_case_insensitive() -> None:
    result = classify_subject(
        "VERIFY YOUR EMAIL ADDRESS"
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.ACCOUNT_VERIFICATION
    )


def test_subject_whitespace_is_normalized() -> None:
    result = classify_subject(
        "  Verify   your   email   address  "
    )

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.ACCOUNT_VERIFICATION
    )


def test_unknown_subject_returns_unknown() -> None:
    result = classify_subject(
        "Important information about your account"
    )

    assert result.processing_status == ProcessingStatus.SUCCESS

    assert (
        result.classification_status
        == ClassificationStatus.UNKNOWN
    )

    assert result.evidence_candidates == ()
    assert result.method == ClassificationMethod.RULE

    assert result.reason_codes == (
        "NO_CLASSIFICATION_RULE_MATCH",
    )


def test_missing_subject_returns_unknown() -> None:
    result = classify_subject(None)

    assert result.processing_status == ProcessingStatus.SUCCESS

    assert (
        result.classification_status
        == ClassificationStatus.UNKNOWN
    )

    assert result.evidence_candidates == ()
    assert result.method == ClassificationMethod.RULE

    assert result.reason_codes == (
        "SUBJECT_UNAVAILABLE",
    )


def test_blank_subject_returns_unknown() -> None:
    result = classify_subject("   ")

    assert result.processing_status == ProcessingStatus.SUCCESS

    assert (
        result.classification_status
        == ClassificationStatus.UNKNOWN
    )

    assert result.evidence_candidates == ()

    assert result.reason_codes == (
        "SUBJECT_UNAVAILABLE",
    )


def test_unsupported_schema_version_is_reported() -> None:
    classifier = DeterministicEmailEvidenceClassifier()

    observation = build_email_observation(
        subject="Verify your email address",
        schema_version=2,
    )

    result = classifier.classify(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.UNSUPPORTED
    assert result.classification_status is None
    assert result.evidence_candidates == ()
    assert result.method is None

    assert result.reason_codes == (
        "UNSUPPORTED_SCHEMA_VERSION",
    )


def test_multiple_evidence_types_can_be_classified() -> None:
    result = classify_subject(
        "Payment confirmed: your invoice is available"
    )

    assert (
        result.classification_status
        == ClassificationStatus.CLASSIFIED
    )

    evidence_types = {
        candidate.evidence_type
        for candidate in result.evidence_candidates
    }

    assert evidence_types == {
        EvidenceType.INVOICE,
        EvidenceType.PAYMENT,
    }


def test_duplicate_matches_for_same_type_are_deduplicated() -> None:
    rules = (
        SubjectClassificationRule(
            rule_id="PAYMENT_RULE_ONE",
            evidence_type=EvidenceType.PAYMENT,
            patterns=(
                r"\bpayment confirmed\b",
            ),
            priority=10,
        ),
        SubjectClassificationRule(
            rule_id="PAYMENT_RULE_TWO",
            evidence_type=EvidenceType.PAYMENT,
            patterns=(
                r"\bconfirmed payment\b",
            ),
            priority=20,
        ),
    )

    classifier = DeterministicEmailEvidenceClassifier(
        rules=rules
    )

    observation = build_email_observation(
        subject="Payment confirmed and confirmed payment"
    )

    result = classifier.classify(
        observation=observation,
        context=build_context(),
    )

    assert len(result.evidence_candidates) == 1

    assert (
        result.evidence_candidates[0].evidence_type
        == EvidenceType.PAYMENT
    )

    assert result.evidence_candidates[0].reason_codes == (
        "PAYMENT_RULE_ONE",
    )


def test_custom_rules_replace_default_rules() -> None:
    custom_rules = (
        SubjectClassificationRule(
            rule_id="CUSTOM_MEMBERSHIP_RULE",
            evidence_type=EvidenceType.SUBSCRIPTION,
            patterns=(
                r"\bmembership started\b",
            ),
            priority=10,
        ),
    )

    classifier = DeterministicEmailEvidenceClassifier(
        rules=custom_rules
    )

    custom_observation = build_email_observation(
        subject="Your membership started"
    )

    custom_result = classifier.classify(
        observation=custom_observation,
        context=build_context(),
    )

    assert (
        custom_result.classification_status
        == ClassificationStatus.CLASSIFIED
    )

    assert (
        custom_result.evidence_candidates[0].evidence_type
        == EvidenceType.SUBSCRIPTION
    )

    default_observation = build_email_observation(
        subject="Verify your email address"
    )

    default_result = classifier.classify(
        observation=default_observation,
        context=build_context(),
    )

    assert (
        default_result.classification_status
        == ClassificationStatus.UNKNOWN
    )

    assert default_result.evidence_candidates == ()


def test_classifier_version_is_preserved() -> None:
    classifier = DeterministicEmailEvidenceClassifier()

    observation = build_email_observation(
        subject="Verify your email address"
    )

    context = ClassificationContext(
        classifier_version="classifier_1.0"
    )

    result = classifier.classify(
        observation=observation,
        context=context,
    )

    assert result.classifier_version == "classifier_1.0"

    assert (
        result.evidence_candidates[0].classifier_version
        == "classifier_1.0"
    )
