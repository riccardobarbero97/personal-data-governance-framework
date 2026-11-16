from dataclasses import dataclass

from personal_data_governance.domain.values.identifiers import UserId


@dataclass(slots=True)
class User:
    id: UserId
