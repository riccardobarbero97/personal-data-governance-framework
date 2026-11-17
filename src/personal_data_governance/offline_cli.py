import argparse
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Personal Data Governance "
            "offline Gmail validation."
        )
    )

    parser.add_argument(
        "--fixture",
        type=Path,
        required=True,
        help=(
            "Path to the synthetic Gmail "
            "metadata fixture."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help=(
            "Maximum number of synthetic "
            "messages to process."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "discovery-report.json"
        ),
        help=(
            "Path of the JSON discovery report."
        ),
    )

    return parser


def print_counts(
    title: str,
    counts: tuple[
        tuple[str, int],
        ...,
    ],
) -> None:
    print()
    print(title)

    if not counts:
        print("  None")
        return

    for name, count in counts:
        print(
            f"  {name}: {count}"
        )


def main() -> int:
    parser = build_parser()

    arguments = parser.parse_args()

    runner = OfflineVerticalRunner(
        OfflineVerticalConfiguration(
            fixture_file=arguments.fixture,
            message_limit=arguments.limit,
        )
    )

    result = runner.run()

    report = DiscoveryReportBuilder().build(
        outcomes=result.outcomes,
        source_mode="OFFLINE_GMAIL_FIXTURE",
        synthetic_data=True,
    )

    JsonDiscoveryReportWriter().write(
        report=report,
        output_file=arguments.output,
    )

    print()
    print(
        "Offline Gmail Vertical Validation"
    )
    print(
        "=" * 60
    )
    print(
        "Synthetic data: YES"
    )
    print(
        "Collection status:",
        result.collection_status,
    )
    print(
        "Collected observations:",
        result.summary.collected_observations,
    )
    print(
        "Created Evidence:",
        result.summary.created_evidence,
    )
    print(
        "Unique Relationships:",
        result.summary.unique_relationships,
    )

    print_counts(
        "Candidate status",
        result.summary.candidate_status_counts,
    )

    print_counts(
        "Resolution status",
        result.summary.resolution_status_counts,
    )

    print_counts(
        "Classification status",
        result.summary.classification_status_counts,
    )

    print_counts(
        "Evidence types",
        result.summary.evidence_type_counts,
    )

    print()
    print(
        "Discovery report:"
    )
    print(
        f"  {arguments.output.resolve()}"
    )

    print()
    print(
        "Detailed outcomes"
    )
    print(
        "-" * 60
    )

    for index, outcome in enumerate(
        result.outcomes,
        start=1,
    ):
        print()
        print(
            f"Observation {index}"
        )

        print(
            "  Candidate:",
            outcome.candidate_result.candidate_status,
        )

        if outcome.resolution_result is not None:
            print(
                "  Resolution:",
                outcome.resolution_result.resolution_status,
            )

            print(
                "  Service:",
                outcome.resolution_result.resolved_service_id,
            )

        print(
            "  Classification:",
            (
                outcome.classification_result
                .classification_status
            ),
        )

        evidence_types = tuple(
            candidate.evidence_type.value
            for candidate in (
                outcome.classification_result
                .evidence_candidates
            )
        )

        print(
            "  Evidence types:",
            evidence_types,
        )

        if outcome.assessment_result is not None:
            print(
                "  Relationship:",
                outcome.assessment_result.relationship_status,
            )

            print(
                "  Temporal:",
                outcome.assessment_result.temporal_status,
            )

            print(
                "  Warnings:",
                outcome.assessment_result.warnings,
            )

        print(
            "  Materialized relationship:",
            outcome.relationship_id,
        )

    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
