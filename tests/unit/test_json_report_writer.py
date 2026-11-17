import json
from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.application.services.discovery_report_builder import (
    DiscoveryReportBuilder,
)
from personal_data_governance.application.services.offline_vertical_runner import (
    OfflineVerticalConfiguration,
    OfflineVerticalRunner,
)
from personal_data_governance.infrastructure.persistence.json_report_writer import (
    JsonDiscoveryReportWriter,
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


def test_report_is_written_as_relationship_centric_json(
    tmp_path: Path,
) -> None:
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

    report = (
        DiscoveryReportBuilder()
        .build(
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
    )

    output_file = (
        tmp_path
        / "discovery-report.json"
    )

    JsonDiscoveryReportWriter().write(
        report=report,
        output_file=output_file,
    )

    assert output_file.exists()

    payload = json.loads(
        output_file.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload[
            "schema_version"
        ]
        == 2
    )

    assert (
        payload[
            "synthetic_data"
        ]
        is True
    )

    assert (
        payload[
            "summary"
        ][
            "observation_count"
        ]
        == 9
    )

    assert len(
        payload[
            "relationships"
        ]
    ) == 5

    assert len(
        payload[
            "unresolved_discoveries"
        ]
    ) == 1

    assert len(
        payload[
            "entries"
        ]
    ) == 9

    spotify = next(
        relationship
        for relationship in (
            payload[
                "relationships"
            ]
        )
        if (
            relationship[
                "service_id"
            ]
            == "service_spotify"
        )
    )

    assert (
        spotify[
            "service_name"
        ]
        == "Spotify"
    )

    assert (
        spotify[
            "relationship_status"
        ]
        == "ESTABLISHED"
    )

    assert (
        spotify[
            "evidence_count"
        ]
        == 2
    )
