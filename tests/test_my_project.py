"""
Юнит-тесты для main.py (Лабораторная работа №1, Вариант 2 — валидация регистрации).
Запуск всех тестов: python -m unittest discover -v
"""

import unittest
import sys
import os

# Добавляем папку src в путь поиска модулей, чтобы можно было импортировать main.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from main import register_user


class TestLoginValidation(unittest.TestCase):
    """Тесты, связанные с проверкой логина."""

    def test_empty_login_fails(self):
        result, message = register_user("", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertEqual(message, "Логин не может быть пустым")

    def test_login_too_short_fails(self):
        result, message = register_user("ab", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertEqual(message, "Логин должен содержать минимум 5 символов")

    def test_login_with_invalid_characters_fails(self):
        # пробел и дефис не входят в число разрешённых символов
        result, message = register_user("ivan petrov", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertEqual(
            message,
            "Логин может содержать только латиницу, цифры и знак подчеркивания",
        )

    def test_blacklisted_login_fails(self):
        result, message = register_user("admin", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertEqual(message, "Данный логин запрещен к использованию")

    def test_blacklisted_login_case_insensitive(self):
        # чёрный список должен работать независимо от регистра
        result, message = register_user("Admin", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertEqual(message, "Данный логин запрещен к использованию")

    def test_invalid_phone_format_fails(self):
        # не хватает одной группы цифр в номере
        result, message = register_user("+7-916-1234", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertIn("телефон", message.lower())

    def test_invalid_email_format_fails(self):
        # нет точки после @
        result, message = register_user("ivan@mail", "Пароль1!", "Пароль1!")
        self.assertFalse(result)
        self.assertIn("email", message.lower())

    def test_valid_plain_login_passes_validation(self):
        # если логин прошёл, а пароль и подтверждение верны — регистрация успешна
        result, message = register_user("ivan_petrov", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_valid_phone_login_passes_validation(self):
        result, message = register_user("+7-916-123-4567", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_valid_email_login_passes_validation(self):
        result, message = register_user("ivan@example.com", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(message, "")


class TestPasswordValidation(unittest.TestCase):
    """Тесты, связанные с проверкой пароля."""

    def test_empty_password_fails(self):
        result, message = register_user("ivan_petrov", "", "")
        self.assertFalse(result)
        self.assertEqual(message, "Пароль не может быть пустым")

    def test_password_too_short_fails(self):
        result, message = register_user("ivan_petrov", "Па1!", "Па1!")
        self.assertFalse(result)
        self.assertEqual(message, "Пароль должен содержать минимум 7 символов")

    def test_password_with_latin_letters_fails(self):
        # по условию пароль должен содержать ТОЛЬКО кириллицу, цифры и спецсимволы
        result, message = register_user("ivan_petrov", "Password1!", "Password1!")
        self.assertFalse(result)
        self.assertEqual(
            message, "Пароль может содержать только кириллицу, цифры и спецсимволы"
        )

    def test_password_missing_uppercase_fails(self):
        result, message = register_user("ivan_petrov", "пароль1!", "пароль1!")
        self.assertFalse(result)
        self.assertEqual(
            message, "Пароль должен содержать хотя бы одну заглавную букву"
        )

    def test_password_missing_lowercase_fails(self):
        result, message = register_user("ivan_petrov", "ПАРОЛЬ1!", "ПАРОЛЬ1!")
        self.assertFalse(result)
        self.assertEqual(
            message, "Пароль должен содержать хотя бы одну строчную букву"
        )

    def test_password_missing_digit_fails(self):
        result, message = register_user("ivan_petrov", "Пароль!!", "Пароль!!")
        self.assertFalse(result)
        self.assertEqual(message, "Пароль должен содержать хотя бы одну цифру")

    def test_password_missing_special_char_fails(self):
        result, message = register_user("ivan_petrov", "Пароль12", "Пароль12")
        self.assertFalse(result)
        self.assertEqual(
            message, "Пароль должен содержать хотя бы один спецсимвол"
        )

    def test_password_exactly_seven_chars_passes(self):
        # граничный случай: ровно минимально допустимая длина (7 символов)
        password = "Прл123!"  # П-р-л-1-2-3-! = 7 символов
        self.assertEqual(len(password), 7)
        result, message = register_user("ivan_petrov", password, password)
        self.assertTrue(result)
        self.assertEqual(message, "")

    def test_password_with_all_requirements_passes(self):
        result, message = register_user("ivan_petrov", "Секрет9#", "Секрет9#")
        self.assertTrue(result)
        self.assertEqual(message, "")


class TestPasswordConfirmation(unittest.TestCase):
    """Тесты, связанные со сравнением пароля и подтверждения."""

    def test_passwords_do_not_match_fails(self):
        result, message = register_user("ivan_petrov", "Пароль1!", "Пароль2!")
        self.assertFalse(result)
        self.assertEqual(message, "Пароль и подтверждение пароля не совпадают")

    def test_passwords_differ_only_by_case_fails(self):
        # пароли должны совпадать буквально, а не "почти"
        result, message = register_user("ivan_petrov", "Пароль1!", "пароль1!")
        self.assertFalse(result)
        self.assertEqual(message, "Пароль и подтверждение пароля не совпадают")

    def test_matching_passwords_pass(self):
        result, message = register_user("ivan_petrov", "Пароль1!", "Пароль1!")
        self.assertTrue(result)
        self.assertEqual(message, "")


class TestSuccessfulRegistration(unittest.TestCase):
    """Тесты полного успешного сценария регистрации."""

    def test_successful_registration_returns_true_and_empty_message(self):
        result, message = register_user("new_user_1", "Пароль12!", "Пароль12!")
        self.assertEqual((result, message), (True, ""))

    def test_successful_registration_with_underscore_login(self):
        result, message = register_user("test_user_99", "Пароль12!", "Пароль12!")
        self.assertTrue(result)

    def test_successful_registration_with_digits_in_login(self):
        result, message = register_user("user12345", "Секрет42$", "Секрет42$")
        self.assertTrue(result)

    def test_login_check_happens_before_password_check(self):
        # если логин некорректен, ошибка должна быть именно про логин,
        # даже если пароль тоже был бы некорректным
        result, message = register_user("ab", "bad", "bad")
        self.assertFalse(result)
        self.assertEqual(message, "Логин должен содержать минимум 5 символов")


if __name__ == "__main__":
    unittest.main()