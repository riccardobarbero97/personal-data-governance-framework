from datetime import datetime, timezone

from personal_data_governance.discovery.candidate_detection.deterministic import (
    DeterministicEmailCandidateDetector,
)
from personal_data_governance.discovery.candidate_detection.protocol import (
    CandidateDetectionContext,
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
from personal_data_governance.domain.values.identifiers import (
    ConnectedSourceId,
    ObservationId,
)
from personal_data_governance.domain.values.references import (
    SchemaVersion,
    SourceReference,
)


def build_email_observation(
    sender: str | None,
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
            sender=sender,
            recipients=(
                "user@example.com",
            ),
            subject="Verify your email address",
            thread_reference="gmail_thread_001",
            labels=(),
        ),
    )


def build_context() -> CandidateDetectionContext:
    return CandidateDetectionContext(
        detector_version="1",
    )


def test_external_sender_domain_becomes_candidate() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="no-reply@spotify.com"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.CANDIDATE
    assert result.method == DetectionMethod.RULE

    assert len(result.candidate_identifiers) == 1

    identifier = result.candidate_identifiers[0]

    assert (
        identifier.type
        == CandidateIdentifierType.EMAIL_DOMAIN
    )
    assert identifier.value == "spotify.com"
    assert identifier.source_attribute == "sender"

    assert result.reason_codes == (
        "EXTERNAL_SENDER_DOMAIN",
    )


def test_sender_display_name_is_supported() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="Spotify <no-reply@spotify.com>"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.CANDIDATE
    assert result.candidate_identifiers[0].value == "spotify.com"


def test_sender_domain_is_normalized_to_lowercase() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="No-Reply@SPOTIFY.COM"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.candidate_status == CandidateStatus.CANDIDATE
    assert result.candidate_identifiers[0].value == "spotify.com"


def test_generic_gmail_sender_is_not_candidate() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="someone@gmail.com"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.NOT_CANDIDATE
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "GENERIC_EMAIL_PROVIDER_DOMAIN",
    )


def test_generic_outlook_sender_is_not_candidate() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="someone@outlook.com"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.NOT_CANDIDATE
    assert result.candidate_identifiers == ()


def test_missing_sender_returns_unknown() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender=None
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.UNKNOWN
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "SENDER_UNAVAILABLE",
    )


def test_blank_sender_returns_unknown() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="   "
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.UNKNOWN
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "SENDER_UNAVAILABLE",
    )


def test_invalid_sender_returns_unknown() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="not-an-email-address"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.UNKNOWN
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "INVALID_SENDER_ADDRESS",
    )


def test_sender_without_public_domain_returns_unknown() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="notification@localhost"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.UNKNOWN
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "SENDER_DOMAIN_UNAVAILABLE",
    )


def test_unsupported_schema_version_is_reported() -> None:
    detector = DeterministicEmailCandidateDetector()

    observation = build_email_observation(
        sender="no-reply@spotify.com",
        schema_version=2,
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.UNSUPPORTED
    assert result.candidate_status is None
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "UNSUPPORTED_SCHEMA_VERSION",
    )


def test_generic_domain_policy_can_be_customized() -> None:
    detector = DeterministicEmailCandidateDetector(
        generic_email_domains=frozenset(
            {
                "examplemail.test",
            }
        )
    )

    observation = build_email_observation(
        sender="person@examplemail.test"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.NOT_CANDIDATE
    assert result.candidate_identifiers == ()
    assert result.reason_codes == (
        "GENERIC_EMAIL_PROVIDER_DOMAIN",
    )


def test_custom_policy_replaces_default_generic_domains() -> None:
    detector = DeterministicEmailCandidateDetector(
        generic_email_domains=frozenset(
            {
                "examplemail.test",
            }
        )
    )

    observation = build_email_observation(
        sender="service@gmail.com"
    )

    result = detector.detect(
        observation=observation,
        context=build_context(),
    )

    assert result.processing_status == ProcessingStatus.SUCCESS
    assert result.candidate_status == CandidateStatus.CANDIDATE
    assert result.candidate_identifiers[0].value == "gmail.com"
