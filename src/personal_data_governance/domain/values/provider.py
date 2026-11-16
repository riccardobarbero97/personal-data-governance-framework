from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Provider:
    id: str
    display_name: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Provider id must not be empty.")

        if not self.display_name.strip():
            raise ValueError("Provider display name must not be empty.")
