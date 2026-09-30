from src.medtrack.database.database import get_connection
from src.medtrack.models.prescription import Prescription


SELECT_DETAILS = """
    SELECT p.*,
           m.name AS medication_name,
           d.surname || ' ' || d.name AS doctor_name,
           u.surname || ' ' || u.name AS patient_name
    FROM prescriptions p
    JOIN medications m ON m.medication_id = p.medication_id
    JOIN users d ON d.user_id = p.doctor_id
    JOIN users u ON u.user_id = p.patient_id
"""


def _map(row) -> Prescription:
    return Prescription(
        prescription_id=row["prescription_id"],
        doctor_id=row["doctor_id"],
        patient_id=row["patient_id"],
        medication_id=row["medication_id"],
        dosage=row["dosage"],
        schedule_times=row["schedule_times"],
        start_date=row["start_date"],
        end_date=row["end_date"],
        instructions=row["instructions"],
        active=row["active"],
        created_at=row["created_at"],
        medication_name=row["medication_name"],
        doctor_name=row["doctor_name"],
        patient_name=row["patient_name"],
    )


def create(doctor_id: int, patient_id: int, medication_id: int, dosage: str,
           schedule_times: str, start_date: str, end_date: str,
           instructions: str | None) -> int:
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO prescriptions(
                doctor_id, patient_id, medication_id, dosage,
                schedule_times, start_date, end_date, instructions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doctor_id, patient_id, medication_id, dosage,
                schedule_times, start_date, end_date, instructions,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def get_by_id(prescription_id: int) -> Prescription | None:
    connection = get_connection()
    try:
        row = connection.execute(
            SELECT_DETAILS + " WHERE p.prescription_id = ?",
            (prescription_id,),
        ).fetchone()
        return _map(row) if row else None
    finally:
        connection.close()


def get_by_patient(patient_id: int, active_only: bool = False) -> list[Prescription]:
    connection = get_connection()
    try:
        query = SELECT_DETAILS + " WHERE p.patient_id = ?"
        if active_only:
            query += " AND p.active = 1"
        query += " ORDER BY p.created_at DESC"
        rows = connection.execute(query, (patient_id,)).fetchall()
        return [_map(row) for row in rows]
    finally:
        connection.close()


def get_by_doctor(doctor_id: int) -> list[Prescription]:
    connection = get_connection()
    try:
        rows = connection.execute(
            SELECT_DETAILS + " WHERE p.doctor_id = ? ORDER BY p.created_at DESC",
            (doctor_id,),
        ).fetchall()
        return [_map(row) for row in rows]
    finally:
        connection.close()


def deactivate(prescription_id: int) -> None:
    connection = get_connection()
    try:
        connection.execute(
            "UPDATE prescriptions SET active = 0 WHERE prescription_id = ?",
            (prescription_id,),
        )
        connection.commit()
    finally:
        connection.close()

