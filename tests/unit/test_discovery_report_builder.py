from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.application.services.discovery_report_builder import (
    DiscoveryReportBuilder,
)
from personal_data_governance.application.services.offline_vertical_runner import (
    OfflineVerticalConfiguration,
    OfflineVerticalRunner,
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


def test_offline_results_build_privacy_safe_report() -> None:
    outcomes = OfflineVerticalRunner(
        OfflineVerticalConfiguration(
            fixture_file=FIXTURE_FILE,
        )
    ).run().outcomes

    report = DiscoveryReportBuilder().build(
        outcomes=outcomes,
        source_mode="OFFLINE_GMAIL_FIXTURE",
        synthetic_data=True,
        generated_at=datetime(
            2026,
            11,
            17,
            18,
            0,
            tzinfo=timezone.utc,
        ),
    )

    assert report.schema_version == 1

    assert (
        report.source_mode
        == "OFFLINE_GMAIL_FIXTURE"
    )

    assert report.synthetic_data is True

    assert report.summary.observation_count == 9
    assert report.summary.candidate_count == 8
    assert report.summary.resolved_count == 7
    assert report.summary.unresolved_count == 1
    assert report.summary.ambiguous_count == 0
    assert report.summary.classified_count == 7

    assert (
        report.summary
        .unknown_classification_count
        == 2
    )

    assert (
        report.summary
        .materialized_relationship_count
        == 5
    )

    assert len(report.entries) == 9

    first_entry = report.entries[0]

    assert (
        first_entry.resolved_service_id
        == "service_spotify"
    )

    assert (
        first_entry.relationship_status
        == "ESTABLISHED"
    )

    assert (
        first_entry.temporal_status
        == "CURRENTLY_OBSERVED"
    )
