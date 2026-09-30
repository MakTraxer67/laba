import hashlib
import hmac
import secrets

from src.medtrack.models.user import User
from src.medtrack.repositories import user_repository


PATIENT_ROLE_ID = 1
DOCTOR_ROLE_ID = 2
ADMIN_ROLE_ID = 3
PBKDF2_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    if len(password) < 4:
        raise ValueError("Пароль должен содержать не менее 4 символов")
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITERATIONS
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored_value: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored_value.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def authenticate(login: str, password: str) -> User | None:
    user = user_repository.get_by_login(login.strip())
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def _register(name: str, surname: str, patronymic: str | None, login: str,
              password: str, role_id: int) -> int:
    name = name.strip()
    surname = surname.strip()
    login = login.strip()
    patronymic = patronymic.strip() if patronymic else None

    if not name or not surname:
        raise ValueError("Имя и фамилия обязательны")
    if len(login) < 3:
        raise ValueError("Логин должен содержать не менее 3 символов")
    if user_repository.get_by_login(login):
        raise ValueError("Пользователь с таким логином уже существует")

    return user_repository.create(
        name, surname, patronymic, login, hash_password(password), role_id
    )


def register_patient(name: str, surname: str, patronymic: str | None,
                     login: str, password: str) -> int:
    return _register(name, surname, patronymic, login, password, PATIENT_ROLE_ID)


def register_doctor(name: str, surname: str, patronymic: str | None,
                    login: str, password: str) -> int:
    return _register(name, surname, patronymic, login, password, DOCTOR_ROLE_ID)


def create_default_admin() -> None:
    if user_repository.get_by_login("admin"):
        return
    user_repository.create(
        "Системный", "Администратор", None, "admin",
        hash_password("admin"), ADMIN_ROLE_ID,
    )

