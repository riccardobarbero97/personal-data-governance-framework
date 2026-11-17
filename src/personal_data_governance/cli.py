import argparse
from pathlib import Path

from personal_data_governance.application.services.gmail_vertical_runner import (
    GmailVerticalRunner,
    GmailVerticalRunnerConfiguration,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Personal Data Governance "
            "Gmail discovery vertical."
        )
    )

    parser.add_argument(
        "--credentials",
        type=Path,
        required=True,
        help=(
            "Path to the Google OAuth Desktop App "
            "credentials JSON file."
        ),
    )

    parser.add_argument(
        "--tokens",
        type=Path,
        default=Path(
            ".oauth_tokens"
        ),
        help=(
            "Directory used for local OAuth tokens."
        ),
    )

    parser.add_argument(
        "--account",
        required=True,
        help=(
            "User-facing Gmail account reference."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help=(
            "Maximum number of Gmail messages "
            "to collect in the first page."
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()

    arguments = parser.parse_args()

    configuration = (
        GmailVerticalRunnerConfiguration(
            client_secrets_file=(
                arguments.credentials
            ),
            token_directory=(
                arguments.tokens
            ),
            account_reference=(
                arguments.account
            ),
            message_limit=(
                arguments.limit
            ),
        )
    )

    runner = GmailVerticalRunner(
        configuration
    )

    result = runner.run()

    print()
    print(
        "Gmail Vertical MVP"
    )
    print(
        "=" * 60
    )

    print(
        "Collection status:",
        result.collection_status,
    )

    print(
        "Collected observations:",
        result.collected_observation_count,
    )

    print()

    for index, outcome in enumerate(
        result.outcomes,
        start=1,
    ):
        print(
            f"Observation {index}"
        )

        print(
            "  Observation ID:",
            outcome.observation_id.value,
        )

        print(
            "  Candidate status:",
            (
                outcome.candidate_result
                .candidate_status
            ),
        )

        if outcome.resolution_result is not None:
            print(
                "  Resolution status:",
                outcome.resolution_result.resolution_status,
            )

            print(
                "  Resolved Service:",
                (
                    outcome.resolution_result
                    .resolved_service_id
                ),
            )

        print(
            "  Classification status:",
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
                "  Relationship status:",
                (
                    outcome.assessment_result
                    .relationship_status
                ),
            )

            print(
                "  Temporal status:",
                (
                    outcome.assessment_result
                    .temporal_status
                ),
            )

        print(
            "  Relationship materialized:",
            (
                outcome.relationship_id is not None
            ),
        )

        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
