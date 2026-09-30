from src.medtrack.database.database import get_connection
from src.medtrack.models.medication import Medication


def _map(row) -> Medication:
    return Medication(
        medication_id=row["medication_id"],
        name=row["name"],
        form=row["form"],
        manufacturer=row["manufacturer"],
    )


def create(name: str, form: str, manufacturer: str | None) -> int:
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO medications(name, form, manufacturer) VALUES (?, ?, ?)",
            (name, form, manufacturer),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def get_by_id(medication_id: int) -> Medication | None:
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT * FROM medications WHERE medication_id = ?",
            (medication_id,),
        ).fetchone()
        return _map(row) if row else None
    finally:
        connection.close()


def get_by_name_and_form(name: str, form: str) -> Medication | None:
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT * FROM medications
            WHERE lower(name) = lower(?) AND lower(form) = lower(?)
            """,
            (name, form),
        ).fetchone()
        return _map(row) if row else None
    finally:
        connection.close()


def get_all() -> list[Medication]:
    connection = get_connection()
    try:
        rows = connection.execute(
            "SELECT * FROM medications ORDER BY name, form"
        ).fetchall()
        return [_map(row) for row in rows]
    finally:
        connection.close()


def has_prescriptions(medication_id: int) -> bool:
    connection = get_connection()
    try:
        row = connection.execute(
            "SELECT 1 FROM prescriptions WHERE medication_id = ? LIMIT 1",
            (medication_id,),
        ).fetchone()
        return row is not None
    finally:
        connection.close()


def delete(medication_id: int) -> None:
    connection = get_connection()
    try:
        connection.execute(
            "DELETE FROM medications WHERE medication_id = ?",
            (medication_id,),
        )
        connection.commit()
    finally:
        connection.close()

