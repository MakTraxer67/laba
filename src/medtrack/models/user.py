from dataclasses import dataclass


@dataclass(slots=True)
class User:
    user_id: int
    name: str
    surname: str
    patronymic: str | None
    login: str
    password_hash: str
    role_id: int
    role_name: str | None = None

    @property
    def full_name(self) -> str:
        parts = [self.surname, self.name, self.patronymic or ""]
        return " ".join(part for part in parts if part)

