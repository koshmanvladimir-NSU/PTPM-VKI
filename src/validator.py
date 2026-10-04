"""
Класс валидации регистрации — обёртка над логикой из Лабораторной работы №1.
"""

import re


class RegistrationValidator:
    """Инкапсулирует все правила проверки логина и пароля при регистрации."""

    BLACKLISTED_LOGINS = {"admin", "root", "test", "user", "guest", "administrator"}

    PHONE_PATTERN = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
    EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    PLAIN_LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")

    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{};:'\",.<>/?"
    PASSWORD_ALLOWED_PATTERN = re.compile(
        r"^[А-Яа-яЁё0-9" + re.escape(SPECIAL_CHARS) + r"]+$"
    )

    def validate(self, login: str, password: str, password_confirm: str):
        """
        Главный метод класса — точка входа для проверки.
        Возвращает (bool, str): результат и сообщение об ошибке.
        """
        ok, reason = self._validate_login(login)
        if not ok:
            return False, reason

        ok, reason = self._validate_password(password)
        if not ok:
            return False, reason

        if password != password_confirm:
            return False, "Пароль и подтверждение пароля не совпадают"

        return True, ""

    def _validate_login(self, login: str):
        if not login:
            return False, "Логин не может быть пустым"

        if login.startswith("+"):
            if self.PHONE_PATTERN.match(login):
                return True, ""
            return False, "Неверный формат телефона (ожидается +x-xxx-xxx-xxxx)"

        if "@" in login:
            if self.EMAIL_PATTERN.match(login):
                return True, ""
            return False, "Неверный формат email"

        if len(login) < 5:
            return False, "Логин должен содержать минимум 5 символов"

        if not self.PLAIN_LOGIN_PATTERN.match(login):
            return False, "Логин может содержать только латиницу, цифры и знак подчеркивания"

        if login.lower() in self.BLACKLISTED_LOGINS:
            return False, "Данный логин запрещен к использованию"

        return True, ""

    def _validate_password(self, password: str):
        if not password:
            return False, "Пароль не может быть пустым"

        if len(password) < 7:
            return False, "Пароль должен содержать минимум 7 символов"

        if not self.PASSWORD_ALLOWED_PATTERN.match(password):
            return False, "Пароль может содержать только кириллицу, цифры и спецсимволы"

        if not any(c.isupper() for c in password if c.isalpha()):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"

        if not any(c.islower() for c in password if c.isalpha()):
            return False, "Пароль должен содержать хотя бы одну строчную букву"

        if not any(c.isdigit() for c in password):
            return False, "Пароль должен содержать хотя бы одну цифру"

        if not any(c in self.SPECIAL_CHARS for c in password):
            return False, "Пароль должен содержать хотя бы один спецсимвол"

        return True, ""