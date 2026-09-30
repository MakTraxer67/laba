from dataclasses import dataclass


@dataclass(slots=True)
class Medication:
    medication_id: int
    name: str
    form: str
    manufacturer: str | None = None

