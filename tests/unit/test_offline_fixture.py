import json
from datetime import datetime, timezone
from pathlib import Path

from personal_data_governance.connectors.gmail.offline_fixture import (
    load_offline_fixture_metadata,
)


def test_fixture_assessment_time_is_loaded(
    tmp_path: Path,
) -> None:
    fixture_file = (
        tmp_path
        / "fixture.json"
    )

    fixture_file.write_text(
        json.dumps(
            {
                "fixture_name": "fixture",
                "synthetic_data": True,
                "assessment_time": (
                    "2026-12-01T12:00:00+00:00"
                ),
                "messages": []
            }
        ),
        encoding="utf-8",
    )

    metadata = (
        load_offline_fixture_metadata(
            fixture_file
        )
    )

    assert (
        metadata.assessment_time
        == datetime(
            2026,
            12,
            1,
            12,
            0,
            tzinfo=timezone.utc,
        )
    )


def test_missing_assessment_time_is_rejected(
    tmp_path: Path,
) -> None:
    fixture_file = (
        tmp_path
        / "fixture.json"
    )

    fixture_file.write_text(
        json.dumps(
            {
                "fixture_name": "fixture",
                "synthetic_data": True,
                "messages": []
            }
        ),
        encoding="utf-8",
    )

    try:
        load_offline_fixture_metadata(
            fixture_file
        )
    except ValueError as error:
        assert "assessment_time" in str(
            error
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )


def test_naive_assessment_time_is_rejected(
    tmp_path: Path,
) -> None:
    fixture_file = (
        tmp_path
        / "fixture.json"
    )

    fixture_file.write_text(
        json.dumps(
            {
                "fixture_name": "fixture",
                "synthetic_data": True,
                "assessment_time": (
                    "2026-12-01T12:00:00"
                ),
                "messages": []
            }
        ),
        encoding="utf-8",
    )

    try:
        load_offline_fixture_metadata(
            fixture_file
        )
    except ValueError as error:
        assert "timezone-aware" in str(
            error
        )
    else:
        raise AssertionError(
            "Expected ValueError was not raised."
        )
