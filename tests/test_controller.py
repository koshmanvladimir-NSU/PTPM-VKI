"""
Интеграционные тесты для Controller.

Это именно ИНТЕГРАЦИОННЫЕ тесты: Validator и Database используются
НАСТОЯЩИЕ (не подменяются), чтобы проверить, что они корректно
работают ВМЕСТЕ через Controller. Подменяются (через unittest.mock)
только UserInteraction и ExternalDependency — как и требует задание,
именно они имитируют пользовательский ввод и отправку данных наружу.
"""

import unittest
from unittest.mock import Mock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from validator import RegistrationValidator
from database import RegistrationDatabase
from controller import Controller


class TestControllerIntegration(unittest.TestCase):
    """
    Интеграционные тесты: проверяют совместную работу Controller,
    настоящего Validator и настоящей Database (в памяти).
    """

    def setUp(self):
        self.validator = RegistrationValidator()
        self.database = RegistrationDatabase(":memory:")
        self.mock_user_interaction = Mock()
        self.mock_external_dependency = Mock()
        self.controller = Controller(
            self.validator,
            self.database,
            self.mock_user_interaction,
            self.mock_external_dependency,
        )

    def tearDown(self):
        self.database.close()

    def test_new_registration_is_computed_and_saved_to_database(self):
        # Заглушка "пользователя" возвращает заранее заданные данные
        self.mock_user_interaction.get_credentials.return_value = (
            "ivan_petrov",
            "Пароль1!",
            "Пароль1!",
        )

        result, message = self.controller.register()

        self.assertTrue(result)
        # проверяем, что Validator и Database реально отработали вместе:
        # результат должен появиться в БД
        stored = self.database.get_record("ivan_petrov", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(stored)
        self.assertTrue(stored["result"])

    def test_second_call_with_same_data_uses_cached_database_result(self):
        self.mock_user_interaction.get_credentials.return_value = (
            "ivan_petrov",
            "Пароль1!",
            "Пароль1!",
        )

        self.controller.register()  # первый вызов — считает и сохраняет

        # подменяем validate "шпионом": он работает как обычно (wraps=...),
        # но мы можем проверить, был ли он вызван
        self.validator.validate = Mock(wraps=self.validator.validate)

        result, message = self.controller.register()  # второй вызов

        # главная проверка интеграции: Controller не должен был обратиться
        # к Validator повторно — значит, Database и Controller правильно
        # взаимодействуют через кэширование результата
        self.validator.validate.assert_not_called()
        self.assertTrue(result)

    def test_result_is_sent_to_external_dependency(self):
        self.mock_user_interaction.get_credentials.return_value = (
            "ivan_petrov",
            "Пароль1!",
            "Пароль1!",
        )

        self.controller.register()

        self.mock_external_dependency.send.assert_called_once()
        sent_text = self.mock_external_dependency.send.call_args[0][0]
        self.assertIn("ivan_petrov", sent_text)
        self.assertIn("успех", sent_text)

    def test_failed_validation_is_still_saved_and_sent(self):
        # логин из чёрного списка — Validator вернёт False,
        # но Controller всё равно должен сохранить это в БД и отправить
        self.mock_user_interaction.get_credentials.return_value = (
            "admin",
            "Пароль1!",
            "Пароль1!",
        )

        result, message = self.controller.register()

        self.assertFalse(result)
        stored = self.database.get_record("admin", "Пароль1!", "Пароль1!")
        self.assertIsNotNone(stored)
        self.assertFalse(stored["result"])

        sent_text = self.mock_external_dependency.send.call_args[0][0]
        self.assertIn("ошибка", sent_text)


if __name__ == "__main__":
    unittest.main()