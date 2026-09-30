from src.medtrack.models.user import User
from src.medtrack.repositories import user_repository
from src.medtrack.services.auth_service import PATIENT_ROLE_ID


def get_all_users() -> list[User]:
    return user_repository.get_all()


def get_patients() -> list[User]:
    return user_repository.get_all(PATIENT_ROLE_ID)


def get_patient(patient_id: int) -> User | None:
    user = user_repository.get_by_id(patient_id)
    return user if user and user.role_id == PATIENT_ROLE_ID else None

