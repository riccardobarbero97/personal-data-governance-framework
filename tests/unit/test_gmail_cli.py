from pathlib import Path
from types import SimpleNamespace

import pytest

import personal_data_governance.gmail_cli as gmail_cli


def test_parser_requires_credentials() -> None:
    parser = gmail_cli.build_parser()

    with pytest.raises(
        SystemExit
    ):
        parser.parse_args(
            [
                "--account",
                "person@example.com",
            ]
        )


def test_parser_requires_account() -> None:
    parser = gmail_cli.build_parser()

    with pytest.raises(
        SystemExit
    ):
        parser.parse_args(
            [
                "--credentials",
                "credentials.json",
            ]
        )


def test_parser_uses_safe_defaults() -> None:
    parser = gmail_cli.build_parser()

    arguments = parser.parse_args(
        [
            "--credentials",
            "credentials.json",
            "--account",
            "person@example.com",
        ]
    )

    assert arguments.credentials == Path(
        "credentials.json"
    )

    assert (
        arguments.account
        == "person@example.com"
    )

    assert (
        arguments.limit
        == 100
    )

    assert (
        arguments.token_directory
        == Path(
            ".pdgf"
        )
        / "oauth_tokens"
    )

    assert (
        arguments.output
        == Path(
            "discovery-report-gmail.json"
        )
    )


@pytest.mark.parametrize(
    "invalid_limit",
    [
        "0",
        "-1",
        "501",
        "not-a-number",
    ],
)
def test_parser_rejects_invalid_message_limit(
    invalid_limit: str,
) -> None:
    parser = gmail_cli.build_parser()

    with pytest.raises(
        SystemExit
    ):
        parser.parse_args(
            [
                "--credentials",
                "credentials.json",
                "--account",
                "person@example.com",
                "--limit",
                invalid_limit,
            ]
        )


@pytest.mark.parametrize(
    "valid_limit",
    [
        "1",
        "100",
        "500",
    ],
)
def test_parser_accepts_valid_message_limit(
    valid_limit: str,
) -> None:
    parser = gmail_cli.build_parser()

    arguments = parser.parse_args(
        [
            "--credentials",
            "credentials.json",
            "--account",
            "person@example.com",
            "--limit",
            valid_limit,
        ]
    )

    assert (
        arguments.limit
        == int(
            valid_limit
        )
    )


def test_main_runs_real_gmail_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output_file = (
        tmp_path
        / "gmail-report.json"
    )

    captured: dict[
        str,
        object,
    ] = {}

    fake_summary = SimpleNamespace(
        candidate_count=3,
        resolved_count=2,
        unresolved_count=1,
        ambiguous_count=0,
        classified_count=2,
        unknown_classification_count=1,
        materialized_relationship_count=2,
    )

    fake_report = SimpleNamespace(
        summary=fake_summary
    )

    fake_result = SimpleNamespace(
        collection_status="COMPLETE",
        collected_observation_count=3,
        outcomes=(
            "outcome_001",
            "outcome_002",
            "outcome_003",
        ),
    )

    class FakeRunner:
        def __init__(
            self,
            configuration,
        ) -> None:
            captured[
                "configuration"
            ] = configuration

        def run(
            self,
        ):
            captured[
                "runner_called"
            ] = True

            return fake_result

    class FakeReportBuilder:
        def build(
            self,
            *,
            outcomes,
            source_mode,
            synthetic_data,
        ):
            captured[
                "outcomes"
            ] = outcomes

            captured[
                "source_mode"
            ] = source_mode

            captured[
                "synthetic_data"
            ] = synthetic_data

            return fake_report

    class FakeReportWriter:
        def write(
            self,
            report,
            output_file,
        ) -> None:
            captured[
                "written_report"
            ] = report

            captured[
                "output_file"
            ] = output_file

    monkeypatch.setattr(
        gmail_cli,
        "GmailVerticalRunner",
        FakeRunner,
    )

    monkeypatch.setattr(
        gmail_cli,
        "DiscoveryReportBuilder",
        FakeReportBuilder,
    )

    monkeypatch.setattr(
        gmail_cli,
        "JsonDiscoveryReportWriter",
        FakeReportWriter,
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "pdgf-gmail",
            "--credentials",
            "credentials.json",
            "--account",
            "person@example.com",
            "--limit",
            "25",
            "--token-directory",
            str(
                tmp_path
                / "tokens"
            ),
            "--output",
            str(
                output_file
            ),
        ],
    )

    exit_code = gmail_cli.main()

    assert exit_code == 0

    assert (
        captured[
            "runner_called"
        ]
        is True
    )

    configuration = captured[
        "configuration"
    ]

    assert (
        configuration
        .client_secrets_file
        == Path(
            "credentials.json"
        )
    )

    assert (
        configuration
        .token_directory
        == tmp_path
        / "tokens"
    )

    assert (
        configuration
        .account_reference
        == "person@example.com"
    )

    assert (
        configuration
        .message_limit
        == 25
    )

    assert (
        captured[
            "outcomes"
        ]
        == fake_result.outcomes
    )

    assert (
        captured[
            "source_mode"
        ]
        == "GMAIL_API_METADATA"
    )

    assert (
        captured[
            "synthetic_data"
        ]
        is False
    )

    assert (
        captured[
            "written_report"
        ]
        is fake_report
    )

    assert (
        captured[
            "output_file"
        ]
        == output_file
    )


def test_main_rejects_blank_account(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "pdgf-gmail",
            "--credentials",
            "credentials.json",
            "--account",
            "   ",
        ],
    )

    with pytest.raises(
        SystemExit
    ):
        gmail_cli.main()
