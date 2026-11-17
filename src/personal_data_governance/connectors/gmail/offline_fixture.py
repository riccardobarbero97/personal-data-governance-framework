import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class OfflineGmailFixtureMetadata:
    fixture_name: str
    synthetic_data: bool
    assessment_time: datetime

    def __post_init__(self) -> None:
        if not self.fixture_name.strip():
            raise ValueError(
                "Offline fixture name must not be empty."
            )

        if self.synthetic_data is not True:
            raise ValueError(
                "Offline fixture must be explicitly "
                "marked as synthetic data."
            )

        if (
            self.assessment_time.tzinfo is None
            or self.assessment_time.utcoffset()
            is None
        ):
            raise ValueError(
                "Offline fixture assessment_time "
                "must be timezone-aware."
            )


def load_offline_fixture_metadata(
    fixture_file: Path,
) -> OfflineGmailFixtureMetadata:
    if not fixture_file.exists():
        raise FileNotFoundError(
            "Offline Gmail fixture not found: "
            f"{fixture_file}"
        )

    payload = json.loads(
        fixture_file.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Offline Gmail fixture root "
            "must be an object."
        )

    fixture_name = payload.get(
        "fixture_name"
    )

    if (
        not isinstance(fixture_name, str)
        or not fixture_name.strip()
    ):
        raise ValueError(
            "Offline Gmail fixture_name "
            "must be a non-empty string."
        )

    if payload.get(
        "synthetic_data"
    ) is not True:
        raise ValueError(
            "Offline fixture must be explicitly "
            "marked as synthetic data."
        )

    raw_assessment_time = payload.get(
        "assessment_time"
    )

    if (
        not isinstance(
            raw_assessment_time,
            str,
        )
        or not raw_assessment_time.strip()
    ):
        raise ValueError(
            "Offline Gmail assessment_time "
            "must be a non-empty ISO-8601 string."
        )

    try:
        assessment_time = (
            datetime.fromisoformat(
                raw_assessment_time
            )
        )
    except ValueError as error:
        raise ValueError(
            "Offline Gmail assessment_time "
            "must be valid ISO-8601."
        ) from error

    return OfflineGmailFixtureMetadata(
        fixture_name=(
            fixture_name.strip()
        ),
        synthetic_data=True,
        assessment_time=assessment_time,
    )
