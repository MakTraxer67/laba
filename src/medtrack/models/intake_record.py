from dataclasses import dataclass


@dataclass(slots=True)
class IntakeRecord:
    intake_id: int
    prescription_id: int
    scheduled_at: str
    status_id: int
    taken_at: str | None
    comment: str | None
    status_name: str | None = None
    medication_name: str | None = None
    dosage: str | None = None
    patient_id: int | None = None

