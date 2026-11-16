from email.utils import parseaddr

from personal_data_governance.application.results.candidate_detection import (
    CandidateDetectionResult,
)
from personal_data_governance.application.values.candidate_identifier import (
    CandidateIdentifier,
)
from personal_data_governance.discovery.candidate_detection.protocol import (
    CandidateDetectionContext,
    ServiceCandidateDetector,
)
from personal_data_governance.domain.entities.observation import Observation
from personal_data_governance.domain.enums.observation import ObservationType
from personal_data_governance.domain.enums.processing import (
    CandidateIdentifierType,
    CandidateStatus,
    DetectionMethod,
    ProcessingStatus,
)
from personal_data_governance.domain.values.email_message_metadata import (
    EmailMessageMetadataV1,
)


DEFAULT_GENERIC_EMAIL_DOMAINS = frozenset(
    {
        "gmail.com",
        "googlemail.com",
        "outlook.com",
        "hotmail.com",
        "live.com",
        "msn.com",
        "yahoo.com",
        "yahoo.it",
        "icloud.com",
        "me.com",
        "mac.com",
        "proton.me",
        "protonmail.com",
        "aol.com",
    }
)


class DeterministicEmailCandidateDetector(
    ServiceCandidateDetector,
):
    def __init__(
        self,
        generic_email_domains: frozenset[str] | None = None,
    ) -> None:
        configured_domains = (
            generic_email_domains
            if generic_email_domains is not None
            else DEFAULT_GENERIC_EMAIL_DOMAINS
        )

        self._generic_email_domains = frozenset(
            domain.strip().lower()
            for domain in configured_domains
            if domain.strip()
        )

    def detect(
        self,
        observation: Observation,
        context: CandidateDetectionContext,
    ) -> CandidateDetectionResult:
        if (
            observation.observation_type
            != ObservationType.EMAIL_MESSAGE_METADATA
        ):
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.UNSUPPORTED,
                candidate_status=None,
                candidate_identifiers=(),
                reason_codes=(
                    "UNSUPPORTED_OBSERVATION_TYPE",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        if observation.schema_version.value != 1:
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.UNSUPPORTED,
                candidate_status=None,
                candidate_identifiers=(),
                reason_codes=(
                    "UNSUPPORTED_SCHEMA_VERSION",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        if not isinstance(
            observation.payload,
            EmailMessageMetadataV1,
        ):
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.FAILED,
                candidate_status=None,
                candidate_identifiers=(),
                reason_codes=(
                    "INVALID_EMAIL_METADATA_PAYLOAD",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        sender = observation.payload.sender

        if sender is None or not sender.strip():
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.SUCCESS,
                candidate_status=CandidateStatus.UNKNOWN,
                candidate_identifiers=(),
                reason_codes=(
                    "SENDER_UNAVAILABLE",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        sender_address = self._extract_sender_address(sender)

        if sender_address is None:
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.SUCCESS,
                candidate_status=CandidateStatus.UNKNOWN,
                candidate_identifiers=(),
                reason_codes=(
                    "INVALID_SENDER_ADDRESS",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        sender_domain = self._extract_domain(sender_address)

        if sender_domain is None:
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.SUCCESS,
                candidate_status=CandidateStatus.UNKNOWN,
                candidate_identifiers=(),
                reason_codes=(
                    "SENDER_DOMAIN_UNAVAILABLE",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        if sender_domain in self._generic_email_domains:
            return CandidateDetectionResult(
                observation_id=observation.id,
                processing_status=ProcessingStatus.SUCCESS,
                candidate_status=CandidateStatus.NOT_CANDIDATE,
                candidate_identifiers=(),
                reason_codes=(
                    "GENERIC_EMAIL_PROVIDER_DOMAIN",
                ),
                method=DetectionMethod.RULE,
                detector_version=context.detector_version,
            )

        candidate_identifier = CandidateIdentifier(
            type=CandidateIdentifierType.EMAIL_DOMAIN,
            value=sender_domain,
            source_attribute="sender",
        )

        return CandidateDetectionResult(
            observation_id=observation.id,
            processing_status=ProcessingStatus.SUCCESS,
            candidate_status=CandidateStatus.CANDIDATE,
            candidate_identifiers=(
                candidate_identifier,
            ),
            reason_codes=(
                "EXTERNAL_SENDER_DOMAIN",
            ),
            method=DetectionMethod.RULE,
            detector_version=context.detector_version,
        )

    @staticmethod
    def _extract_sender_address(
        sender: str,
    ) -> str | None:
        _, parsed_address = parseaddr(sender)

        normalized_address = parsed_address.strip().lower()

        if not normalized_address:
            return None

        if normalized_address.count("@") != 1:
            return None

        local_part, domain = normalized_address.rsplit(
            "@",
            maxsplit=1,
        )

        if not local_part or not domain:
            return None

        return normalized_address

    @staticmethod
    def _extract_domain(
        email_address: str,
    ) -> str | None:
        _, domain = email_address.rsplit(
            "@",
            maxsplit=1,
        )

        normalized_domain = domain.strip().lower().rstrip(".")

        if not normalized_domain:
            return None

        if "." not in normalized_domain:
            return None

        if normalized_domain.startswith("."):
            return None

        if normalized_domain.endswith("."):
            return None

        if ".." in normalized_domain:
            return None

        return normalized_domain
