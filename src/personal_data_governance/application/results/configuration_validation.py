from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConfigurationSectionValidation:
    name: str
    version: str | None
    valid: bool
    metrics: tuple[
        tuple[str, int],
        ...,
    ]
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ConfigurationValidationResult:
    valid: bool
    sections: tuple[
        ConfigurationSectionValidation,
        ...,
    ]

    @property
    def errors(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            error
            for section in self.sections
            for error in section.errors
        )

    @property
    def warnings(
        self,
    ) -> tuple[str, ...]:
        return tuple(
            warning
            for section in self.sections
            for warning in section.warnings
        )
