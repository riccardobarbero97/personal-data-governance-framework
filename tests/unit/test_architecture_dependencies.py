import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOMAIN_ROOT = (
    PROJECT_ROOT
    / "src"
    / "personal_data_governance"
    / "domain"
)


FORBIDDEN_DOMAIN_IMPORT_PREFIXES = (
    "personal_data_governance.application",
    "personal_data_governance.connectors",
    "personal_data_governance.discovery",
    "personal_data_governance.infrastructure",
)


def collect_python_files(
    root: Path,
) -> tuple[Path, ...]:
    return tuple(
        sorted(
            root.rglob("*.py")
        )
    )


def collect_imported_modules(
    file_path: Path,
) -> tuple[str, ...]:
    source = file_path.read_text(
        encoding="utf-8"
    )

    tree = ast.parse(
        source,
        filename=str(file_path),
    )

    imported_modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.append(
                    alias.name
                )

        if isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imported_modules.append(
                    node.module
                )

    return tuple(
        imported_modules
    )


def test_domain_does_not_depend_on_outer_layers() -> None:
    violations: list[str] = []

    for file_path in collect_python_files(
        DOMAIN_ROOT
    ):
        imported_modules = (
            collect_imported_modules(
                file_path
            )
        )

        for module in imported_modules:
            if module.startswith(
                FORBIDDEN_DOMAIN_IMPORT_PREFIXES
            ):
                relative_path = (
                    file_path.relative_to(
                        PROJECT_ROOT
                    )
                )

                violations.append(
                    f"{relative_path}: {module}"
                )

    assert violations == [], (
        "Domain layer contains forbidden dependencies:\n"
        + "\n".join(violations)
    )
