from src.medtrack.models.user import User
from src.medtrack.services.auth_service import (
    authenticate,
    register_doctor,
    register_patient,
)


def login_ui() -> User | None:
    print("\n=== Авторизация ===")
    user = authenticate(input("Логин: "), input("Пароль: "))
    if not user:
        print("Неверный логин или пароль")
        return None
    print(f"Добро пожаловать, {user.full_name}!")
    return user


def _registration_fields() -> tuple[str, str, str | None, str, str]:
    name = input("Имя: ")
    surname = input("Фамилия: ")
    patronymic = input("Отчество (необязательно): ") or None
    login = input("Логин: ")
    password = input("Пароль: ")
    return name, surname, patronymic, login, password


def register_patient_ui() -> None:
    print("\n=== Регистрация пациента ===")
    try:
        register_patient(*_registration_fields())
        print("Пациент зарегистрирован")
    except ValueError as error:
        print(f"Ошибка: {error}")


def register_doctor_ui() -> None:
    print("\n=== Регистрация врача ===")
    try:
        register_doctor(*_registration_fields())
        print("Врач зарегистрирован")
    except ValueError as error:
        print(f"Ошибка: {error}")

