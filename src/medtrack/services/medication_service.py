from src.medtrack.models.medication import Medication
from src.medtrack.repositories import medication_repository


def create_medication(name: str, form: str, manufacturer: str | None = None) -> int:
    name = name.strip()
    form = form.strip()
    manufacturer = manufacturer.strip() if manufacturer else None
    if not name or not form:
        raise ValueError("Название и форма препарата обязательны")
    if medication_repository.get_by_name_and_form(name, form):
        raise ValueError("Такой препарат уже существует")
    return medication_repository.create(name, form, manufacturer)


def get_all_medications() -> list[Medication]:
    return medication_repository.get_all()


def delete_medication(medication_id: int) -> None:
    if not medication_repository.get_by_id(medication_id):
        raise ValueError("Препарат не найден")
    if medication_repository.has_prescriptions(medication_id):
        raise ValueError("Нельзя удалить препарат, используемый в назначениях")
    medication_repository.delete(medication_id)

