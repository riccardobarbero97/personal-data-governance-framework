import json
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from personal_data_governance.application.results.discovery_report import (
    DiscoveryReport,
)


class JsonDiscoveryReportWriter:
    def write(
        self,
        report: DiscoveryReport,
        output_file: Path,
    ) -> None:
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        serialized_report = json.dumps(
            asdict(
                report
            ),
            indent=2,
            ensure_ascii=False,
            sort_keys=False,
        )

        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_file.parent,
            prefix="discovery_report_",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(
                serialized_report
            )
            temporary_file.write(
                "\n"
            )

            temporary_path = Path(
                temporary_file.name
            )

        temporary_path.replace(
            output_file
        )
