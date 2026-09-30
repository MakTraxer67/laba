from datetime import date, datetime, timedelta

from src.medtrack.models.prescription import Prescription
from src.medtrack.repositories import (
    intake_repository,
    medication_repository,
    prescription_repository,
    user_repository,
)
from src.medtrack.services.auth_service import DOCTOR_ROLE_ID, PATIENT_ROLE_ID


def _parse_date(value: str, field_name: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as error:
        raise ValueError(f"{field_name}: используйте формат ГГГГ-ММ-ДД") from error


def _normalize_times(value: str) -> list[str]:
    result: list[str] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            parsed = datetime.strptime(item, "%H:%M")
        except ValueError as error:
            raise ValueError(f"Некорректное время: {item}. Используйте ЧЧ:ММ") from error
        normalized = parsed.strftime("%H:%M")
        if normalized not in result:
            result.append(normalized)
    if not result:
        raise ValueError("Укажите хотя бы одно время приёма")
    return sorted(result)


def _build_schedule(start: date, end: date, times: list[str]) -> list[str]:
    result: list[str] = []
    current = start
    while current <= end:
        result.extend(f"{current.isoformat()} {time_value}:00" for time_value in times)
        current += timedelta(days=1)
    return result


def create_prescription(doctor_id: int, patient_id: int, medication_id: int,
                        dosage: str, schedule_times: str, start_date: str,
                        end_date: str, instructions: str | None = None) -> int:
    doctor = user_repository.get_by_id(doctor_id)
    patient = user_repository.get_by_id(patient_id)
    medication = medication_repository.get_by_id(medication_id)
    if not doctor or doctor.role_id != DOCTOR_ROLE_ID:
        raise ValueError("Назначение может создать только врач")
    if not patient or patient.role_id != PATIENT_ROLE_ID:
        raise ValueError("Пациент не найден")
    if not medication:
        raise ValueError("Препарат не найден")
    dosage = dosage.strip()
    if not dosage:
        raise ValueError("Дозировка обязательна")

    start = _parse_date(start_date, "Дата начала")
    end = _parse_date(end_date, "Дата окончания")
    if end < start:
        raise ValueError("Дата окончания не может быть раньше даты начала")
    if (end - start).days > 366:
        raise ValueError("Период назначения не может превышать 366 дней")
    times = _normalize_times(schedule_times)

    prescription_id = prescription_repository.create(
        doctor_id=doctor_id,
        patient_id=patient_id,
        medication_id=medication_id,
        dosage=dosage,
        schedule_times=", ".join(times),
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        instructions=instructions.strip() if instructions else None,
    )
    intake_repository.create_many(
        prescription_id, _build_schedule(start, end, times)
    )
    return prescription_id


def get_patient_prescriptions(patient_id: int, active_only: bool = False) -> list[Prescription]:
    return prescription_repository.get_by_patient(patient_id, active_only)


def get_doctor_prescriptions(doctor_id: int) -> list[Prescription]:
    return prescription_repository.get_by_doctor(doctor_id)


def deactivate_prescription(prescription_id: int, doctor_id: int) -> None:
    prescription = prescription_repository.get_by_id(prescription_id)
    if not prescription:
        raise ValueError("Назначение не найдено")
    if prescription.doctor_id != doctor_id:
        raise ValueError("Можно завершить только собственное назначение")
    prescription_repository.deactivate(prescription_id)

