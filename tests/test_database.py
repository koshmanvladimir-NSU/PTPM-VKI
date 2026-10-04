"""
Юнит-тесты для RegistrationDatabase.
Это НЕ дублирует тесты из Лабораторной работы №2 — там тестировалась
логика валидации, здесь тестируется только работа с базой данных
(add/get/delete), которой в Lab_2 не существовало вовсе.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from database import RegistrationDatabase


class TestRegistrationDatabase(unittest.TestCase):
    """Проверка CRUD-методов класса базы данных (без участия других классов)."""

    def setUp(self):
        # :memory: — база создаётся в оперативной памяти, не оставляет файлов
        self.database = RegistrationDatabase(":memory:")

    def tearDown(self):
        self.database.close()

    def test_add_and_get_record_returns_saved_data(self):
        self.database.add_record("ivan_petrov", "Пароль1!", "Пароль1!", True, "")
        record = self.database.get_record("ivan_petrov", "Пароль1!", "Пароль1!")
        self.assertEqual(record, {"result": True, "message": ""})

    def test_get_nonexistent_record_returns_none(self):
        record = self.database.get_record("nobody", "x", "x")
        self.assertIsNone(record)

    def test_delete_record_removes_it_from_database(self):
        self.database.add_record("ivan_petrov", "Пароль1!", "Пароль1!", True, "")
        self.database.delete_record("ivan_petrov", "Пароль1!", "Пароль1!")
        record = self.database.get_record("ivan_petrov", "Пароль1!", "Пароль1!")
        self.assertIsNone(record)

    def test_add_record_with_failure_result_stores_message(self):
        self.database.add_record(
            "admin", "Пароль1!", "Пароль1!", False, "Данный логин запрещен к использованию"
        )
        record = self.database.get_record("admin", "Пароль1!", "Пароль1!")
        self.assertEqual(record["result"], False)
        self.assertEqual(record["message"], "Данный логин запрещен к использованию")


if __name__ == "__main__":
    unittest.main()