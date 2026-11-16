from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceReference:
    value: str


@dataclass(frozen=True, slots=True)
class SchemaVersion:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            raise ValueError("SchemaVersion must be greater than or equal to 1.")
