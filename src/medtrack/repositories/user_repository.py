from src.medtrack.database.database import get_connection
from src.medtrack.models.user import User


def _map(row) -> User:
    return User(
        user_id=row["user_id"],
        name=row["name"],
        surname=row["surname"],
        patronymic=row["patronymic"],
        login=row["login"],
        password_hash=row["password_hash"],
        role_id=row["role_id"],
        role_name=row["role_name"] if "role_name" in row.keys() else None,
    )


def create(name: str, surname: str, patronymic: str | None, login: str,
           password_hash: str, role_id: int) -> int:
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO users(name, surname, patronymic, login, password_hash, role_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, surname, patronymic, login, password_hash, role_id),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def get_by_login(login: str) -> User | None:
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT u.*, r.name AS role_name
            FROM users u
            JOIN user_roles r ON r.role_id = u.role_id
            WHERE u.login = ?
            """,
            (login,),
        ).fetchone()
        return _map(row) if row else None
    finally:
        connection.close()


def get_by_id(user_id: int) -> User | None:
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT u.*, r.name AS role_name
            FROM users u
            JOIN user_roles r ON r.role_id = u.role_id
            WHERE u.user_id = ?
            """,
            (user_id,),
        ).fetchone()
        return _map(row) if row else None
    finally:
        connection.close()


def get_all(role_id: int | None = None) -> list[User]:
    connection = get_connection()
    try:
        query = """
            SELECT u.*, r.name AS role_name
            FROM users u
            JOIN user_roles r ON r.role_id = u.role_id
        """
        params: tuple = ()
        if role_id is not None:
            query += " WHERE u.role_id = ?"
            params = (role_id,)
        query += " ORDER BY u.surname, u.name"
        return [_map(row) for row in connection.execute(query, params).fetchall()]
    finally:
        connection.close()

