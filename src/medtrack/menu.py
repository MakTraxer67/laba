from datetime import date

from src.medtrack.auth import register_doctor_ui
from src.medtrack.models.user import User
from src.medtrack.services import (
    intake_service,
    medication_service,
    prescription_service,
    user_service,
)


STATUS_NAMES = {
    "Planned": "Запланировано",
    "Taken": "Принято",
    "Skipped": "Пропущено",
    "Postponed": "Перенесено",
}


def _read_id(prompt: str) -> int:
    try:
        return int(input(prompt))
    except ValueError as error:
        raise ValueError("ID должен быть целым числом") from error


def _print_medications() -> None:
    medications = medication_service.get_all_medications()
    if not medications:
        print("Справочник препаратов пуст")
        return
    for item in medications:
        manufacturer = f", {item.manufacturer}" if item.manufacturer else ""
        print(f"{item.medication_id}. {item.name} — {item.form}{manufacturer}")


def _print_patients() -> None:
    patients = user_service.get_patients()
    if not patients:
        print("Пациенты не зарегистрированы")
        return
    for patient in patients:
        print(f"{patient.user_id}. {patient.full_name} ({patient.login})")


def _print_prescriptions(items) -> None:
    if not items:
        print("Назначений нет")
        return
    for item in items:
        state = "активно" if item.active else "завершено"
        print(
            f"{item.prescription_id}. {item.medication_name}, {item.dosage}; "
            f"{item.schedule_times}; {item.start_date}–{item.end_date}; {state}"
        )
        if item.patient_name:
            print(f"   Пациент: {item.patient_name}; врач: {item.doctor_name}")
        if item.instructions:
            print(f"   Инструкция: {item.instructions}")


def _print_intakes(items) -> None:
    if not items:
        print("Записей приёма нет")
        return
    for item in items:
        status = STATUS_NAMES.get(item.status_name or "", item.status_name)
        taken = f", фактически: {item.taken_at}" if item.taken_at else ""
        comment = f", комментарий: {item.comment}" if item.comment else ""
        print(
            f"{item.intake_id}. {item.scheduled_at} — {item.medication_name} "
            f"({item.dosage}), {status}{taken}{comment}"
        )


def medications_menu() -> None:
    while True:
        print("\n===== Препараты =====")
        print("1. Показать препараты")
        print("2. Добавить препарат")
        print("3. Удалить препарат")
        print("0. Назад")
        choice = input("Выберите действие: ")
        try:
            if choice == "1":
                _print_medications()
            elif choice == "2":
                medication_service.create_medication(
                    input("Название: "),
                    input("Форма (таблетки, капли и т. п.): "),
                    input("Производитель (необязательно): ") or None,
                )
                print("Препарат добавлен")
            elif choice == "3":
                medication_service.delete_medication(_read_id("ID препарата: "))
                print("Препарат удалён")
            elif choice == "0":
                return
            else:
                print("Неизвестная команда")
        except ValueError as error:
            print(f"Ошибка: {error}")


def patient_menu(user: User) -> None:
    while True:
        print(f"\n===== Пациент: {user.full_name} =====")
        print("1. Мои назначения")
        print("2. Расписание на дату")
        print("3. Отметить результат приёма")
        print("4. История приёма")
        print("0. Выход из учётной записи")
        choice = input("Выберите действие: ")
        try:
            if choice == "1":
                _print_prescriptions(
                    prescription_service.get_patient_prescriptions(user.user_id)
                )
            elif choice == "2":
                value = input(f"Дата [{date.today().isoformat()}]: ") \
                    or date.today().isoformat()
                _print_intakes(intake_service.get_patient_schedule(user.user_id, value))
            elif choice == "3":
                value = input(f"Дата [{date.today().isoformat()}]: ") \
                    or date.today().isoformat()
                _print_intakes(intake_service.get_patient_schedule(user.user_id, value))
                intake_id = _read_id("ID записи приёма: ")
                print("1. Принято  2. Пропущено  3. Перенесено")
                action = {"1": "taken", "2": "skipped", "3": "postponed"}.get(
                    input("Результат: ")
                )
                if not action:
                    raise ValueError("Неизвестный результат")
                intake_service.mark_intake(
                    intake_id, user.user_id, action,
                    input("Комментарий (необязательно): ") or None,
                )
                print("Результат сохранён")
            elif choice == "4":
                _print_intakes(intake_service.get_patient_history(user.user_id))
            elif choice == "0":
                return
            else:
                print("Неизвестная команда")
        except ValueError as error:
            print(f"Ошибка: {error}")


def _create_prescription_ui(doctor: User) -> None:
    print("\n=== Новое назначение ===")
    _print_patients()
    patient_id = _read_id("ID пациента: ")
    _print_medications()
    medication_id = _read_id("ID препарата: ")
    prescription_service.create_prescription(
        doctor_id=doctor.user_id,
        patient_id=patient_id,
        medication_id=medication_id,
        dosage=input("Дозировка: "),
        schedule_times=input("Время приёма через запятую (например, 08:00, 20:00): "),
        start_date=input("Дата начала (ГГГГ-ММ-ДД): "),
        end_date=input("Дата окончания (ГГГГ-ММ-ДД): "),
        instructions=input("Инструкция (необязательно): ") or None,
    )
    print("Назначение и расписание созданы")


def _adherence_ui() -> None:
    _print_patients()
    patient_id = _read_id("ID пациента: ")
    _print_intakes(intake_service.get_patient_history(patient_id))
    stats = intake_service.get_adherence(patient_id)
    print("\nСтатистика:")
    print(f"Запланировано: {stats['planned']}")
    print(f"Принято: {stats['taken']}")
    print(f"Пропущено: {stats['skipped']}")
    print(f"Перенесено: {stats['postponed']}")
    print(f"Соблюдение завершённых приёмов: {stats['adherence_percent']}%")


def doctor_menu(user: User) -> None:
    while True:
        print(f"\n===== Врач: {user.full_name} =====")
        print("1. Список пациентов")
        print("2. Препараты")
        print("3. Создать назначение")
        print("4. Мои назначения")
        print("5. Завершить назначение")
        print("6. История и статистика пациента")
        print("0. Выход из учётной записи")
        choice = input("Выберите действие: ")
        try:
            if choice == "1":
                _print_patients()
            elif choice == "2":
                medications_menu()
            elif choice == "3":
                _create_prescription_ui(user)
            elif choice == "4":
                _print_prescriptions(
                    prescription_service.get_doctor_prescriptions(user.user_id)
                )
            elif choice == "5":
                _print_prescriptions(
                    prescription_service.get_doctor_prescriptions(user.user_id)
                )
                prescription_service.deactivate_prescription(
                    _read_id("ID назначения: "), user.user_id
                )
                print("Назначение завершено")
            elif choice == "6":
                _adherence_ui()
            elif choice == "0":
                return
            else:
                print("Неизвестная команда")
        except ValueError as error:
            print(f"Ошибка: {error}")


def admin_menu(user: User) -> None:
    while True:
        print(f"\n===== Администратор: {user.full_name} =====")
        print("1. Зарегистрировать врача")
        print("2. Показать пользователей")
        print("3. Препараты")
        print("0. Выход из учётной записи")
        choice = input("Выберите действие: ")
        if choice == "1":
            register_doctor_ui()
        elif choice == "2":
            for item in user_service.get_all_users():
                print(
                    f"{item.user_id}. {item.full_name} — "
                    f"{item.role_name} ({item.login})"
                )
        elif choice == "3":
            medications_menu()
        elif choice == "0":
            return
        else:
            print("Неизвестная команда")

