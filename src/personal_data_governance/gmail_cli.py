import argparse
from pathlib import Path

from personal_data_governance.application.services.discovery_report_builder import (
    DiscoveryReportBuilder,
)
from personal_data_governance.application.services.gmail_vertical_runner import (
    GmailVerticalRunner,
    GmailVerticalRunnerConfiguration,
)
from personal_data_governance.infrastructure.persistence.json_report_writer import (
    JsonDiscoveryReportWriter,
)


DEFAULT_MESSAGE_LIMIT = 100
DEFAULT_TOKEN_DIRECTORY = (
    Path(".pdgf")
    / "oauth_tokens"
)
DEFAULT_OUTPUT_FILE = Path(
    "discovery-report-gmail.json"
)
REAL_GMAIL_SOURCE_MODE = (
    "GMAIL_API_METADATA"
)


def message_limit(
    raw_value: str,
) -> int:
    try:
        parsed_value = int(
            raw_value
        )
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "Message limit must be an integer."
        ) from exc

    if parsed_value < 1:
        raise argparse.ArgumentTypeError(
            "Message limit must be at least 1."
        )

    if parsed_value > 500:
        raise argparse.ArgumentTypeError(
            "Message limit must not exceed 500."
        )

    return parsed_value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run Personal Data Governance "
            "discovery against a real Gmail "
            "mailbox using metadata-only "
            "OAuth access."
        )
    )

    parser.add_argument(
        "--credentials",
        type=Path,
        required=True,
        help=(
            "Path to the Google OAuth "
            "Desktop application client "
            "secrets JSON file."
        ),
    )

    parser.add_argument(
        "--account",
        required=True,
        help=(
            "Local reference for the Gmail "
            "account. Normally this is the "
            "Gmail email address."
        ),
    )

    parser.add_argument(
        "--limit",
        type=message_limit,
        default=DEFAULT_MESSAGE_LIMIT,
        help=(
            "Maximum number of Gmail messages "
            "to process. Valid values are "
            "between 1 and 500. "
            "Default: 100."
        ),
    )

    parser.add_argument(
        "--token-directory",
        type=Path,
        default=DEFAULT_TOKEN_DIRECTORY,
        help=(
            "Local directory used to store "
            "Google OAuth tokens. "
            "Default: .pdgf/oauth_tokens."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=(
            "Path of the generated JSON "
            "discovery report. "
            "Default: "
            "discovery-report-gmail.json."
        ),
    )

    return parser


def main() -> int:
    parser = build_parser()

    arguments = parser.parse_args()

    account_reference = (
        arguments.account.strip()
    )

    if not account_reference:
        parser.error(
            "Gmail account reference "
            "must not be empty."
        )

    runner = GmailVerticalRunner(
        GmailVerticalRunnerConfiguration(
            client_secrets_file=(
                arguments.credentials
            ),
            token_directory=(
                arguments.token_directory
            ),
            account_reference=(
                account_reference
            ),
            message_limit=(
                arguments.limit
            ),
        )
    )

    result = runner.run()

    report = DiscoveryReportBuilder().build(
        outcomes=result.outcomes,
        source_mode=(
            REAL_GMAIL_SOURCE_MODE
        ),
        synthetic_data=False,
    )

    JsonDiscoveryReportWriter().write(
        report=report,
        output_file=arguments.output,
    )

    print()
    print(
        "Real Gmail Vertical Validation"
    )
    print(
        "=" * 60
    )

    print(
        "Source mode:",
        REAL_GMAIL_SOURCE_MODE,
    )

    print(
        "Synthetic data: NO"
    )

    print(
        "Collection status:",
        result.collection_status,
    )

    print(
        "Collected observations:",
        result.collected_observation_count,
    )

    print(
        "Candidates:",
        report.summary.candidate_count,
    )

    print(
        "Resolved:",
        report.summary.resolved_count,
    )

    print(
        "Unresolved:",
        report.summary.unresolved_count,
    )

    print(
        "Ambiguous:",
        report.summary.ambiguous_count,
    )

    print(
        "Classified:",
        report.summary.classified_count,
    )

    print(
        "Unknown classifications:",
        (
            report.summary
            .unknown_classification_count
        ),
    )

    print(
        "Materialized relationships:",
        (
            report.summary
            .materialized_relationship_count
        ),
    )

    print()
    print(
        "Discovery report:"
    )

    print(
        f"  {arguments.output.resolve()}"
    )

    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
