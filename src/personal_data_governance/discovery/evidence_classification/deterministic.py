import re
from dataclasses import dataclass

from personal_data_governance.application.results.classification import (
    ClassificationResult,
    EvidenceCandidate,
)
from personal_data_governance.discovery.evidence_classification.protocol import (
    ClassificationContext,
    EvidenceClassifier,
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


@dataclass(frozen=True, slots=True)
class SubjectClassificationRule:
    rule_id: str
    evidence_type: EvidenceType
    patterns: tuple[str, ...]
    priority: int

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError(
                "Classification rule id must not be empty."
            )

        if not self.patterns:
            raise ValueError(
                "Classification rule requires at least "
                "one pattern."
            )

        if self.priority < 0:
            raise ValueError(
                "Classification rule priority "
                "must not be negative."
            )


DEFAULT_SUBJECT_RULES: tuple[SubjectClassificationRule, ...] = (
    SubjectClassificationRule(
        rule_id="ACCOUNT_DELETION_SUBJECT",
        evidence_type=EvidenceType.ACCOUNT_DELETION,
        patterns=(
            r"\baccount deletion\b",
            r"\bdelete your account\b",
            r"\baccount has been deleted\b",
            r"\baccount was deleted\b",
            r"\baccount closure\b",
            r"\baccount has been closed\b",
        ),
        priority=10,
    ),
    SubjectClassificationRule(
        rule_id="PASSWORD_RESET_SUBJECT",
        evidence_type=EvidenceType.PASSWORD_RESET,
        patterns=(
            r"\breset your password\b",
            r"\bpassword reset\b",
            r"\bforgot your password\b",
            r"\bchange your password\b",
            r"\bpassword recovery\b",
        ),
        priority=20,
    ),
    SubjectClassificationRule(
        rule_id="ACCOUNT_VERIFICATION_SUBJECT",
        evidence_type=EvidenceType.ACCOUNT_VERIFICATION,
        patterns=(
            r"\bverify your email\b",
            r"\bverify your email address\b",
            r"\bconfirm your email\b",
            r"\bconfirm your email address\b",
            r"\bemail verification\b",
            r"\bverification email\b",
            r"\bactivate your account\b",
        ),
        priority=30,
    ),
    SubjectClassificationRule(
        rule_id="SECURITY_NOTIFICATION_SUBJECT",
        evidence_type=EvidenceType.SECURITY_NOTIFICATION,
        patterns=(
            r"\bsecurity alert\b",
            r"\bsecurity notification\b",
            r"\bsuspicious activity\b",
            r"\bunusual activity\b",
            r"\bnew login detected\b",
            r"\bnew sign-in\b",
            r"\bnew sign in\b",
            r"\bsecurity warning\b",
        ),
        priority=40,
    ),
    SubjectClassificationRule(
        rule_id="AUTHENTICATION_SUBJECT",
        evidence_type=EvidenceType.AUTHENTICATION,
        patterns=(
            r"\bsign-in code\b",
            r"\bsign in code\b",
            r"\blogin code\b",
            r"\bone-time code\b",
            r"\bone time code\b",
            r"\bverification code\b",
            r"\bauthentication code\b",
        ),
        priority=50,
    ),
    SubjectClassificationRule(
        rule_id="ACCOUNT_CREATION_SUBJECT",
        evidence_type=EvidenceType.ACCOUNT_CREATION,
        patterns=(
            r"\bwelcome to\b",
            r"\byour account has been created\b",
            r"\baccount created\b",
            r"\bregistration complete\b",
            r"\bthanks for signing up\b",
            r"\bthank you for signing up\b",
        ),
        priority=60,
    ),
    SubjectClassificationRule(
        rule_id="PAYMENT_SUBJECT",
        evidence_type=EvidenceType.PAYMENT,
        patterns=(
            r"\bpayment successful\b",
            r"\bpayment received\b",
            r"\bpayment confirmed\b",
            r"\bpayment confirmation\b",
            r"\bpayment completed\b",
            r"\bpayment failed\b",
            r"\bpayment declined\b",
        ),
        priority=70,
    ),
    SubjectClassificationRule(
        rule_id="INVOICE_SUBJECT",
        evidence_type=EvidenceType.INVOICE,
        patterns=(
            r"\byour invoice\b",
            r"\binvoice available\b",
            r"\bnew invoice\b",
            r"\binvoice number\b",
            r"\bmonthly invoice\b",
        ),
        priority=80,
    ),
    SubjectClassificationRule(
        rule_id="PURCHASE_SUBJECT",
        evidence_type=EvidenceType.PURCHASE,
        patterns=(
            r"\border confirmation\b",
            r"\border confirmed\b",
            r"\bpurchase confirmation\b",
            r"\bthank you for your purchase\b",
            r"\byour order\b",
        ),
        priority=90,
    ),
    SubjectClassificationRule(
        rule_id="SUBSCRIPTION_SUBJECT",
        evidence_type=EvidenceType.SUBSCRIPTION,
        patterns=(
            r"\bsubscription confirmed\b",
            r"\bsubscription confirmation\b",
            r"\bsubscription renewed\b",
            r"\bsubscription renewal\b",
            r"\bsubscription cancelled\b",
            r"\bsubscription canceled\b",
            r"\bmembership renewed\b",
            r"\bmembership activated\b",
        ),
        priority=100,
    ),
    SubjectClassificationRule(
        rule_id="ACCOUNT_UPDATE_SUBJECT",
        evidence_type=EvidenceType.ACCOUNT_UPDATE,
        patterns=(
            r"\baccount updated\b",
            r"\bprofile updated\b",
            r"\bemail address changed\b",
            r"\baccount information changed\b",
            r"\bpersonal information updated\b",
        ),
        priority=110,
    ),
    SubjectClassificationRule(
        rule_id="PRIVACY_NOTICE_SUBJECT",
        evidence_type=EvidenceType.PRIVACY_NOTICE,
        patterns=(
            r"\bprivacy notice\b",
            r"\bprivacy policy\b",
            r"\bprivacy update\b",
            r"\bupdated privacy policy\b",
            r"\bchanges to our privacy policy\b",
            r"\bdata protection notice\b",
        ),
        priority=120,
    ),
    SubjectClassificationRule(
        rule_id="NEWSLETTER_SUBJECT",
        evidence_type=EvidenceType.NEWSLETTER,
        patterns=(
            r"\bnewsletter\b",
            r"\bweekly digest\b",
            r"\bmonthly digest\b",
            r"\bdaily digest\b",
            r"\bweekly update\b",
        ),
        priority=130,
    ),
    SubjectClassificationRule(
        rule_id="MARKETING_SUBJECT",
        evidence_type=EvidenceType.MARKETING,
        patterns=(
            r"\bspecial offer\b",
            r"\blimited time offer\b",
            r"\bexclusive offer\b",
            r"\bdiscount\b",
            r"\bsale\b",
            r"\bpromo code\b",
            r"\bsave \d+%\b",
            r"\b\d+% off\b",
        ),
        priority=140,
    ),
)


class DeterministicEmailEvidenceClassifier(
    EvidenceClassifier,
):
    def __init__(
        self,
        rules: tuple[SubjectClassificationRule, ...] | None = None,
    ) -> None:
        configured_rules = (
            rules
            if rules is not None
            else DEFAULT_SUBJECT_RULES
        )

        self._rules = tuple(
            sorted(
                configured_rules,
                key=lambda rule: (
                    rule.priority,
                    rule.rule_id,
                ),
            )
        )

    def classify(
        self,
        observation: Observation,
        context: ClassificationContext,
    ) -> ClassificationResult:
        if (
            observation.observation_type
            != ObservationType.EMAIL_MESSAGE_METADATA
        ):
            return ClassificationResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.UNSUPPORTED,
                classification_status=None,
                evidence_candidates=(),
                method=None,
                reason_codes=(
                    "UNSUPPORTED_OBSERVATION_TYPE",
                ),
                classifier_version=context.classifier_version,
            )

        if observation.schema_version.value != 1:
            return ClassificationResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.UNSUPPORTED,
                classification_status=None,
                evidence_candidates=(),
                method=None,
                reason_codes=(
                    "UNSUPPORTED_SCHEMA_VERSION",
                ),
                classifier_version=context.classifier_version,
            )

        if not isinstance(
            observation.payload,
            EmailMessageMetadataV1,
        ):
            return ClassificationResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.FAILED,
                classification_status=None,
                evidence_candidates=(),
                method=None,
                reason_codes=(
                    "INVALID_EMAIL_METADATA_PAYLOAD",
                ),
                classifier_version=context.classifier_version,
            )

        subject = observation.payload.subject

        if subject is None or not subject.strip():
            return ClassificationResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.SUCCESS,
                classification_status=ClassificationStatus.UNKNOWN,
                evidence_candidates=(),
                method=ClassificationMethod.RULE,
                reason_codes=(
                    "SUBJECT_UNAVAILABLE",
                ),
                classifier_version=context.classifier_version,
            )

        normalized_subject = self._normalize_subject(subject)

        matching_rules = self._find_matching_rules(
            normalized_subject
        )

        if not matching_rules:
            return ClassificationResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.SUCCESS,
                classification_status=ClassificationStatus.UNKNOWN,
                evidence_candidates=(),
                method=ClassificationMethod.RULE,
                reason_codes=(
                    "NO_CLASSIFICATION_RULE_MATCH",
                ),
                classifier_version=context.classifier_version,
            )

        selected_rules = self._select_rules_by_evidence_type(
            matching_rules
        )

        evidence_candidates = tuple(
            EvidenceCandidate(
                evidence_type=rule.evidence_type,
                observation_ids=(
                    observation.id,
                ),
                method=ClassificationMethod.RULE,
                reason_codes=(
                    rule.rule_id,
                ),
                classifier_version=context.classifier_version,
            )
            for rule in selected_rules
        )

        return ClassificationResult(
            observation_id=observation.id,
            processing_status=ProcessingStatus.SUCCESS,
            classification_status=ClassificationStatus.CLASSIFIED,
            evidence_candidates=evidence_candidates,
            method=ClassificationMethod.RULE,
            reason_codes=tuple(
                rule.rule_id
                for rule in selected_rules
            ),
            classifier_version=context.classifier_version,
        )

    def _find_matching_rules(
        self,
        normalized_subject: str,
    ) -> tuple[SubjectClassificationRule, ...]:
        return tuple(
            rule
            for rule in self._rules
            if self._rule_matches(
                rule=rule,
                normalized_subject=normalized_subject,
            )
        )

    @staticmethod
    def _rule_matches(
        rule: SubjectClassificationRule,
        normalized_subject: str,
    ) -> bool:
        return any(
            re.search(
                pattern,
                normalized_subject,
                flags=re.IGNORECASE,
            )
            is not None
            for pattern in rule.patterns
        )

    @staticmethod
    def _select_rules_by_evidence_type(
        matching_rules: tuple[
            SubjectClassificationRule,
            ...,
        ],
    ) -> tuple[SubjectClassificationRule, ...]:
        selected_rules: dict[
            EvidenceType,
            SubjectClassificationRule,
        ] = {}

        for rule in matching_rules:
            if rule.evidence_type not in selected_rules:
                selected_rules[rule.evidence_type] = rule

        return tuple(
            selected_rules[evidence_type]
            for evidence_type in sorted(
                selected_rules,
                key=lambda item: item.value,
            )
        )

    @staticmethod
    def _normalize_subject(
        subject: str,
    ) -> str:
        normalized = subject.strip().lower()

        normalized = re.sub(
            r"\s+",
            " ",
            normalized,
        )

        return normalized
