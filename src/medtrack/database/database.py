import os
import sqlite3
from pathlib import Path


DEFAULT_DB_NAME = "medtrack.db"


def get_db_path() -> Path:
    configured = os.environ.get("MEDTRACK_DB_PATH")
    return Path(configured) if configured else Path(DEFAULT_DB_NAME)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> bool:
    """Создаёт схему при первом запуске и возвращает True для новой БД."""
    db_path = get_db_path()
    is_new = not db_path.exists()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    schema_path = Path(__file__).with_name("schema.sql")
    with schema_path.open("r", encoding="utf-8") as schema_file:
        schema = schema_file.read()

    connection = get_connection()
    try:
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()

    return is_new

