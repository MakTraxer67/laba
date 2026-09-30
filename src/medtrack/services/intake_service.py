from datetime import datetime

from src.medtrack.models.intake_record import IntakeRecord
from src.medtrack.repositories import intake_repository


TAKEN_STATUS_ID = 2
SKIPPED_STATUS_ID = 3
POSTPONED_STATUS_ID = 4
STATUS_BY_ACTION = {
    "taken": TAKEN_STATUS_ID,
    "skipped": SKIPPED_STATUS_ID,
    "postponed": POSTPONED_STATUS_ID,
}


def get_patient_schedule(patient_id: int, date_value: str) -> list[IntakeRecord]:
    try:
        datetime.strptime(date_value, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("Используйте формат даты ГГГГ-ММ-ДД") from error
    return intake_repository.get_for_patient(patient_id, date_value)


def get_patient_history(patient_id: int) -> list[IntakeRecord]:
    return intake_repository.get_for_patient(patient_id)


def mark_intake(intake_id: int, patient_id: int, action: str,
                comment: str | None = None) -> None:
    record = intake_repository.get_by_id(intake_id)
    if not record:
        raise ValueError("Запись приёма не найдена")
    if record.patient_id != patient_id:
        raise ValueError("Нельзя изменить чужую запись приёма")
    status_id = STATUS_BY_ACTION.get(action.lower())
    if status_id is None:
        raise ValueError("Неизвестный результат приёма")
    taken_at = datetime.now().isoformat(sep=" ", timespec="seconds") \
        if status_id == TAKEN_STATUS_ID else None
    intake_repository.update_status(
        intake_id, status_id, taken_at, comment.strip() if comment else None
    )


def get_adherence(patient_id: int) -> dict[str, int | float]:
    values = intake_repository.get_statistics(patient_id)
    taken = values.get("Taken", 0)
    skipped = values.get("Skipped", 0)
    resolved = taken + skipped
    percent = round(taken * 100 / resolved, 1) if resolved else 0.0
    return {
        "planned": values.get("Planned", 0),
        "taken": taken,
        "skipped": skipped,
        "postponed": values.get("Postponed", 0),
        "adherence_percent": percent,
    }

