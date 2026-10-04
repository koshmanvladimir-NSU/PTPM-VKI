"""
Класс для хранения результатов регистрации в базе данных SQLite.
"""

import sqlite3
from typing import Optional, Dict


class RegistrationDatabase:
    """
    Хранит результаты проверок регистрации.
    Одна запись идентифицируется тройкой (логин, пароль, подтверждение пароля).
    """

    def __init__(self, db_path: str = ":memory:"):
        # ":memory:" — специальное значение sqlite3: база живёт только в
        # оперативной памяти, не создаёт файл на диске. Удобно для тестов —
        # каждый тест получает чистую, независимую базу.
        self.connection = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                password_confirm TEXT NOT NULL,
                result INTEGER NOT NULL,
                message TEXT NOT NULL,
                UNIQUE(login, password, password_confirm)
            )
            """
        )
        self.connection.commit()

    def add_record(self, login: str, password: str, password_confirm: str, result: bool, message: str):
        """Добавляет (или перезаписывает, если такая тройка уже есть) запись."""
        self.connection.execute(
            """
            INSERT OR REPLACE INTO registrations
                (login, password, password_confirm, result, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (login, password, password_confirm, int(result), message),
        )
        self.connection.commit()

    def get_record(self, login: str, password: str, password_confirm: str) -> Optional[Dict]:
        """Возвращает запись в виде словаря {"result": bool, "message": str}, либо None."""
        cursor = self.connection.execute(
            """
            SELECT result, message FROM registrations
            WHERE login = ? AND password = ? AND password_confirm = ?
            """,
            (login, password, password_confirm),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return {"result": bool(row[0]), "message": row[1]}

    def delete_record(self, login: str, password: str, password_confirm: str):
        """Удаляет запись по тройке (логин, пароль, подтверждение)."""
        self.connection.execute(
            """
            DELETE FROM registrations
            WHERE login = ? AND password = ? AND password_confirm = ?
            """,
            (login, password, password_confirm),
        )
        self.connection.commit()

    def close(self):
        """Закрывает соединение с базой данных."""
        self.connection.close()