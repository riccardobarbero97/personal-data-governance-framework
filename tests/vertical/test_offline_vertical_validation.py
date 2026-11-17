from pathlib import Path

from personal_data_governance.application.services.offline_vertical_runner import (
    OfflineVerticalConfiguration,
    OfflineVerticalRunner,
)
from personal_data_governance.domain.enums.evidence import EvidenceType
from personal_data_governance.domain.enums.processing import (
    CandidateStatus,
    ClassificationStatus,
    ResolutionStatus,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]

FIXTURE_FILE = (
    PROJECT_ROOT
    / "examples"
    / "fixtures"
    / "offline_gmail_mailbox.json"
)


def test_offline_fixture_runs_complete_discovery_pipeline() -> None:
    runner = OfflineVerticalRunner(
        OfflineVerticalConfiguration(
            fixture_file=FIXTURE_FILE,
            message_limit=100,
        )
    )

    result = runner.run()

    assert result.collection_status == "COMPLETE"

    assert (
        result.summary.collected_observations
        == 9
    )

    candidate_counts = dict(
        result.summary.candidate_status_counts
    )

    assert candidate_counts[
        CandidateStatus.CANDIDATE.value
    ] == 8

    assert candidate_counts[
        CandidateStatus.NOT_CANDIDATE.value
    ] == 1

    resolution_counts = dict(
        result.summary.resolution_status_counts
    )

    assert resolution_counts[
        ResolutionStatus.RESOLVED.value
    ] == 7

    assert resolution_counts[
        ResolutionStatus.UNRESOLVED.value
    ] == 1

    classification_counts = dict(
        result.summary.classification_status_counts
    )

    assert classification_counts[
        ClassificationStatus.CLASSIFIED.value
    ] == 7

    assert classification_counts[
        ClassificationStatus.UNKNOWN.value
    ] == 2

    evidence_counts = dict(
        result.summary.evidence_type_counts
    )

    assert evidence_counts[
        EvidenceType.ACCOUNT_VERIFICATION.value
    ] == 1

    assert evidence_counts[
        EvidenceType.PASSWORD_RESET.value
    ] == 1

    assert evidence_counts[
        EvidenceType.SECURITY_NOTIFICATION.value
    ] == 1

    assert evidence_counts[
        EvidenceType.MARKETING.value
    ] == 1

    assert evidence_counts[
        EvidenceType.NEWSLETTER.value
    ] == 1

    assert evidence_counts[
        EvidenceType.PAYMENT.value
    ] == 2

    assert result.summary.created_evidence == 7

    assert (
        result.summary.unique_relationships
        == 5
    )


def test_spotify_is_reassessed_cumulatively() -> None:
    runner = OfflineVerticalRunner(
        OfflineVerticalConfiguration(
            fixture_file=FIXTURE_FILE,
            message_limit=100,
        )
    )

    result = runner.run()

    spotify_payment_outcome = (
        result.outcomes[-1]
    )

    assert (
        spotify_payment_outcome
        .resolution_result
        is not None
    )

    assert (
        spotify_payment_outcome
        .resolution_result
        .resolved_service_id
        is not None
    )

    assert (
        spotify_payment_outcome
        .resolution_result
        .resolved_service_id
        .value
        == "service_spotify"
    )

    assert (
        spotify_payment_outcome
        .aggregation_result
        is not None
    )

    assert (
        spotify_payment_outcome
        .aggregation_result
        .aggregate
        is not None
    )

    aggregate = (
        spotify_payment_outcome
        .aggregation_result
        .aggregate
    )

    assert (
        aggregate
        .evidence_summary
        .total_evidence_count
        == 2
    )

    assert (
        aggregate
        .evidence_summary
        .evidence_count_by_type[
            EvidenceType.ACCOUNT_VERIFICATION
        ]
        == 1
    )

    assert (
        aggregate
        .evidence_summary
        .evidence_count_by_type[
            EvidenceType.PAYMENT
        ]
        == 1
    )
