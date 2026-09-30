import os
import tempfile
import unittest
from pathlib import Path

from src.medtrack.database.database import init_db
from src.medtrack.repositories import intake_repository
from src.medtrack.services import (
    auth_service,
    intake_service,
    medication_service,
    prescription_service,
    user_service,
)


class MedTrackWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        os.environ["MEDTRACK_DB_PATH"] = str(
            Path(self.temp_directory.name) / "test_medtrack.db"
        )
        init_db()
        auth_service.create_default_admin()
        self.patient_id = auth_service.register_patient(
            "Анна", "Иванова", None, "patient", "secret"
        )
        self.doctor_id = auth_service.register_doctor(
            "Иван", "Петров", "Сергеевич", "doctor", "secret"
        )
        self.medication_id = medication_service.create_medication(
            "Тестовый препарат", "таблетки", "Учебная лаборатория"
        )

    def tearDown(self) -> None:
        os.environ.pop("MEDTRACK_DB_PATH", None)
        self.temp_directory.cleanup()

    def test_complete_intake_workflow(self) -> None:
        prescription_id = prescription_service.create_prescription(
            doctor_id=self.doctor_id,
            patient_id=self.patient_id,
            medication_id=self.medication_id,
            dosage="1 таблетка",
            schedule_times="08:00, 20:00",
            start_date="2026-09-29",
            end_date="2026-09-29",
            instructions="После еды",
        )

        prescription = prescription_service.get_patient_prescriptions(
            self.patient_id
        )[0]
        self.assertEqual(prescription.prescription_id, prescription_id)
        self.assertEqual(prescription.medication_name, "Тестовый препарат")

        schedule = intake_service.get_patient_schedule(
            self.patient_id, "2026-09-29"
        )
        self.assertEqual(len(schedule), 2)

        intake_service.mark_intake(
            schedule[0].intake_id, self.patient_id, "taken", "Принято вовремя"
        )
        updated = intake_repository.get_by_id(schedule[0].intake_id)
        self.assertEqual(updated.status_name, "Taken")
        self.assertIsNotNone(updated.taken_at)

        stats = intake_service.get_adherence(self.patient_id)
        self.assertEqual(stats["taken"], 1)
        self.assertEqual(stats["planned"], 1)
        self.assertEqual(stats["adherence_percent"], 100.0)

    def test_duplicate_login_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "уже существует"):
            auth_service.register_patient(
                "Другой", "Пациент", None, "patient", "secret"
            )

    def test_invalid_schedule_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Некорректное время"):
            prescription_service.create_prescription(
                self.doctor_id,
                self.patient_id,
                self.medication_id,
                "1 таблетка",
                "утром",
                "2026-09-29",
                "2026-09-30",
            )

    def test_patient_cannot_change_another_patients_record(self) -> None:
        other_patient_id = auth_service.register_patient(
            "Мария", "Сидорова", None, "patient2", "secret"
        )
        prescription_service.create_prescription(
            self.doctor_id,
            self.patient_id,
            self.medication_id,
            "1 таблетка",
            "08:00",
            "2026-09-29",
            "2026-09-29",
        )
        record = intake_service.get_patient_schedule(
            self.patient_id, "2026-09-29"
        )[0]
        with self.assertRaisesRegex(ValueError, "чужую запись"):
            intake_service.mark_intake(
                record.intake_id, other_patient_id, "taken"
            )

    def test_users_are_separated_by_roles(self) -> None:
        patients = user_service.get_patients()
        self.assertEqual([item.user_id for item in patients], [self.patient_id])
        self.assertIsNotNone(auth_service.authenticate("doctor", "secret"))
        self.assertIsNone(auth_service.authenticate("doctor", "wrong"))


if __name__ == "__main__":
    unittest.main()

