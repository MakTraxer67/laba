from dataclasses import dataclass


@dataclass(slots=True)
class Prescription:
    prescription_id: int
    doctor_id: int
    patient_id: int
    medication_id: int
    dosage: str
    schedule_times: str
    start_date: str
    end_date: str
    instructions: str | None
    active: int
    created_at: str
    medication_name: str | None = None
    doctor_name: str | None = None
    patient_name: str | None = None

