from src.medtrack.auth import login_ui, register_patient_ui
from src.medtrack.database.database import init_db
from src.medtrack.menu import admin_menu, doctor_menu, patient_menu
from src.medtrack.services.auth_service import (
    ADMIN_ROLE_ID,
    DOCTOR_ROLE_ID,
    PATIENT_ROLE_ID,
    create_default_admin,
)


def main() -> None:
    if init_db():
        print("База данных MedTrack создана.")
    create_default_admin()

    while True:
        print("\n===== MedTrack =====")
        print("1. Вход")
        print("2. Регистрация пациента")
        print("0. Выход")
        choice = input("Выберите действие: ")

        if choice == "1":
            user = login_ui()
            if not user:
                continue
            if user.role_id == PATIENT_ROLE_ID:
                patient_menu(user)
            elif user.role_id == DOCTOR_ROLE_ID:
                doctor_menu(user)
            elif user.role_id == ADMIN_ROLE_ID:
                admin_menu(user)
        elif choice == "2":
            register_patient_ui()
        elif choice == "0":
            print("До свидания!")
            return
        else:
            print("Неизвестная команда")


if __name__ == "__main__":
    main()

