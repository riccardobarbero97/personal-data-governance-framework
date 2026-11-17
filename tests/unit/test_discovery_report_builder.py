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


def build_report():
    outcomes = (
        OfflineVerticalRunner(
            OfflineVerticalConfiguration(
                fixture_file=(
                    FIXTURE_FILE
                ),
            )
        )
        .run()
        .outcomes
    )

    return DiscoveryReportBuilder().build(
        outcomes=outcomes,
        source_mode=(
            "OFFLINE_GMAIL_FIXTURE"
        ),
        synthetic_data=True,
        generated_at=datetime(
            2026,
            12,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_offline_results_build_privacy_safe_report() -> None:
    report = build_report()

    assert report.schema_version == 2

    assert (
        report.source_mode
        == "OFFLINE_GMAIL_FIXTURE"
    )

    assert (
        report.synthetic_data
        is True
    )

    assert (
        report.summary
        .observation_count
        == 9
    )

    assert (
        report.summary
        .candidate_count
        == 8
    )

    assert (
        report.summary
        .resolved_count
        == 7
    )

    assert (
        report.summary
        .unresolved_count
        == 1
    )

    assert (
        report.summary
        .materialized_relationship_count
        == 5
    )

    assert len(
        report.entries
    ) == 9


def test_report_contains_relationship_centric_view() -> None:
    report = build_report()

    assert len(
        report.relationships
    ) == 5

    relationships = {
        relationship.service_id: relationship
        for relationship in (
            report.relationships
        )
    }

    assert set(
        relationships
    ) == {
        "service_spotify",
        "service_netflix",
        "service_github",
        "service_linkedin",
        "service_dropbox",
    }

    spotify = relationships[
        "service_spotify"
    ]

    assert (
        spotify.service_name
        == "Spotify"
    )

    assert (
        spotify.relationship_status
        == "ESTABLISHED"
    )

    assert (
        spotify.temporal_status
        == "CURRENTLY_OBSERVED"
    )

    assert (
        spotify.evidence_count
        == 2
    )

    evidence_counts = {
        evidence.evidence_type: (
            evidence.evidence_count
        )
        for evidence in spotify.evidence
    }

    assert evidence_counts == {
        "ACCOUNT_VERIFICATION": 1,
        "PAYMENT": 1,
    }

    assert len(
        spotify.observation_ids
    ) == 3


def test_observed_relationship_is_preserved() -> None:
    report = build_report()

    relationships = {
        relationship.service_id: relationship
        for relationship in (
            report.relationships
        )
    }

    linkedin = relationships[
        "service_linkedin"
    ]

    assert (
        linkedin.relationship_status
        == "OBSERVED"
    )

    assert (
        linkedin.temporal_status
        == "CURRENTLY_OBSERVED"
    )

    assert linkedin.evidence == (
        linkedin.evidence[0],
    )

    assert (
        linkedin.evidence[0]
        .evidence_type
        == "MARKETING"
    )


def test_unresolved_discovery_is_preserved_separately() -> None:
    report = build_report()

    assert len(
        report.unresolved_discoveries
    ) == 1

    unresolved = (
        report.unresolved_discoveries[
            0
        ]
    )

    assert (
        "unknown-service.example"
        in unresolved.identifiers
    )

    assert (
        unresolved.evidence_types
        == (
            "PAYMENT",
        )
    )

    assert len(
        unresolved.observation_ids
    ) == 1

    assert (
        "CANONICAL_SERVICE_UNAVAILABLE"
        in unresolved.warnings
    )


def test_personal_sender_does_not_become_relationship() -> None:
    report = build_report()

    service_ids = {
        relationship.service_id
        for relationship in (
            report.relationships
        )
    }

    assert (
        "gmail.com"
        not in service_ids
    )

    assert len(
        report.relationships
    ) == 5
