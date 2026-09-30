from src.medtrack.database.database import get_connection
from src.medtrack.models.intake_record import IntakeRecord


SELECT_DETAILS = """
    SELECT i.*, s.name AS status_name, m.name AS medication_name,
           p.dosage, p.patient_id
    FROM intake_records i
    JOIN intake_statuses s ON s.status_id = i.status_id
    JOIN prescriptions p ON p.prescription_id = i.prescription_id
    JOIN medications m ON m.medication_id = p.medication_id
"""


def _map(row) -> IntakeRecord:
    return IntakeRecord(
        intake_id=row["intake_id"],
        prescription_id=row["prescription_id"],
        scheduled_at=row["scheduled_at"],
        status_id=row["status_id"],
        taken_at=row["taken_at"],
        comment=row["comment"],
        status_name=row["status_name"],
        medication_name=row["medication_name"],
        dosage=row["dosage"],
        patient_id=row["patient_id"],
    )


def create_many(prescription_id: int, scheduled_values: list[str]) -> None:
    connection = get_connection()
    try:
        connection.executemany(
            """
            INSERT INTO intake_records(prescription_id, scheduled_at, status_id)
            VALUES (?, ?, 1)
            """,
            [(prescription_id, scheduled_at) for scheduled_at in scheduled_values],
        )
        connection.commit()
    finally:
        connection.close()


def get_by_id(intake_id: int) -> IntakeRecord | None:
    connection = get_connection()
    try:
        row = connection.execute(
            SELECT_DETAILS + " WHERE i.intake_id = ?",
            (intake_id,),
        ).fetchone()
        return _map(row) if row else None
    finally:
        connection.close()


def get_for_patient(patient_id: int, date_value: str | None = None) -> list[IntakeRecord]:
    connection = get_connection()
    try:
        query = SELECT_DETAILS + " WHERE p.patient_id = ?"
        params: list[object] = [patient_id]
        if date_value:
            query += " AND date(i.scheduled_at) = date(?)"
            params.append(date_value)
        query += " ORDER BY i.scheduled_at"
        rows = connection.execute(query, tuple(params)).fetchall()
        return [_map(row) for row in rows]
    finally:
        connection.close()


def update_status(intake_id: int, status_id: int, taken_at: str | None,
                  comment: str | None) -> None:
    connection = get_connection()
    try:
        connection.execute(
            """
            UPDATE intake_records
            SET status_id = ?, taken_at = ?, comment = ?
            WHERE intake_id = ?
            """,
            (status_id, taken_at, comment, intake_id),
        )
        connection.commit()
    finally:
        connection.close()


def get_statistics(patient_id: int) -> dict[str, int]:
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT s.name, COUNT(*) AS amount
            FROM intake_records i
            JOIN intake_statuses s ON s.status_id = i.status_id
            JOIN prescriptions p ON p.prescription_id = i.prescription_id
            WHERE p.patient_id = ?
            GROUP BY s.name
            """,
            (patient_id,),
        ).fetchall()
        return {row["name"]: row["amount"] for row in rows}
    finally:
        connection.close()

