"""
Лабораторная работа №1. Вариант 2.
Проверка данных пользователя при регистрации.
"""

import os
import re
import logging
import hashlib


# --------------------------------------------------------------------------
# 1. НАСТРОЙКА ЛОГИРОВАНИЯ
# --------------------------------------------------------------------------

def setup_logging():
    """Настраивает вывод логов одновременно в консоль и в файл logs/file_txt.log"""
    os.makedirs("logs", exist_ok=True)

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8"),
        ],
    )


def mask_password(password: str) -> str:
    """
    Возвращает безопасный для лога 'отпечаток' пароля.
    Одинаковые пароли дают одинаковый отпечаток, разные — разный,
    при этом сам пароль восстановить из отпечатка нельзя.
    """
    if password is None:
        return "<none>"
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return f"***{digest[:8]}"


# --------------------------------------------------------------------------
# 2. КОНСТАНТЫ ВАЛИДАЦИИ
# --------------------------------------------------------------------------

BLACKLISTED_LOGINS = {"admin", "root", "test", "user", "guest", "administrator"}

PHONE_PATTERN = re.compile(r"^\+\d-\d{3}-\d{3}-\d{4}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PLAIN_LOGIN_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")

SPECIAL_CHARS = "!@#$%^&*()_+-=[]{};:'\",.<>/?"
PASSWORD_ALLOWED_PATTERN = re.compile(
    r"^[А-Яа-яЁё0-9" + re.escape(SPECIAL_CHARS) + r"]+$"
)


# --------------------------------------------------------------------------
# 3. ВАЛИДАЦИЯ ЛОГИНА
# --------------------------------------------------------------------------

def validate_login(login: str):
    """Возвращает (True, '') либо (False, 'причина')."""
    if not login:
        return False, "Логин не может быть пустым"

    # Похоже на телефон
    if login.startswith("+"):
        if PHONE_PATTERN.match(login):
            return True, ""
        return False, "Неверный формат телефона (ожидается +x-xxx-xxx-xxxx)"

    # Похоже на email
    if "@" in login:
        if EMAIL_PATTERN.match(login):
            return True, ""
        return False, "Неверный формат email"

    # Обычная строка-логин
    if len(login) < 5:
        return False, "Логин должен содержать минимум 5 символов"

    if not PLAIN_LOGIN_PATTERN.match(login):
        return False, "Логин может содержать только латиницу, цифры и знак подчеркивания"

    if login.lower() in BLACKLISTED_LOGINS:
        return False, "Данный логин запрещен к использованию"

    return True, ""


# --------------------------------------------------------------------------
# 4. ВАЛИДАЦИЯ ПАРОЛЯ
# --------------------------------------------------------------------------

def validate_password(password: str):
    """Возвращает (True, '') либо (False, 'причина')."""
    if not password:
        return False, "Пароль не может быть пустым"

    if len(password) < 7:
        return False, "Пароль должен содержать минимум 7 символов"

    if not PASSWORD_ALLOWED_PATTERN.match(password):
        return False, "Пароль может содержать только кириллицу, цифры и спецсимволы"

    if not any(c.isupper() for c in password if c.isalpha()):
        return False, "Пароль должен содержать хотя бы одну заглавную букву"

    if not any(c.islower() for c in password if c.isalpha()):
        return False, "Пароль должен содержать хотя бы одну строчную букву"

    if not any(c.isdigit() for c in password):
        return False, "Пароль должен содержать хотя бы одну цифру"

    if not any(c in SPECIAL_CHARS for c in password):
        return False, "Пароль должен содержать хотя бы один спецсимвол"

    return True, ""


# --------------------------------------------------------------------------
# 5. ОСНОВНАЯ ФУНКЦИЯ РЕГИСТРАЦИИ
# --------------------------------------------------------------------------

def register_user(login: str, password: str, password_confirm: str):
    """
    Комплексная проверка данных при регистрации.
    Возвращает кортеж (bool_результат, строка_сообщение).
    """
    masked_pw = mask_password(password)
    masked_pw_confirm = mask_password(password_confirm)

    logging.debug(
        f"Запрос на регистрацию: login={login!r}, "
        f"password={masked_pw}, password_confirm={masked_pw_confirm}"
    )

    try:
        ok, reason = validate_login(login)
        if not ok:
            logging.error(f"Регистрация не удалась для login={login!r}: {reason}")
            return False, reason

        ok, reason = validate_password(password)
        if not ok:
            logging.error(
                f"Регистрация не удалась для login={login!r} "
                f"(password={masked_pw}): {reason}"
            )
            return False, reason

        if password != password_confirm:
            reason = "Пароль и подтверждение пароля не совпадают"
            logging.error(
                f"Регистрация не удалась для login={login!r}: {reason} "
                f"(password={masked_pw}, confirm={masked_pw_confirm})"
            )
            return False, reason

        logging.info(f"Регистрация успешна: login={login!r}, password={masked_pw}")
        return True, ""

    except Exception:
        logging.exception(f"Непредвиденная ошибка при регистрации login={login!r}")
        return False, "Внутренняя ошибка при обработке запроса"


# --------------------------------------------------------------------------
# 6. ТОЧКА ВХОДА
# --------------------------------------------------------------------------

def main():
    setup_logging()
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    test_cases = [
        ("ivan_petrov", "Пароль1!", "Пароль1!"),  # успех
        ("admin", "Пароль1!", "Пароль1!"),  # логин в черном списке
        ("+7-916-123-4567", "Пароль1!", "Пароль1!"),  # успех (телефон)
        ("test@example.com", "пароль1!", "пароль1!"),  # нет заглавной буквы
        ("ab", "Пароль1!", "Пароль1!"),  # логин короче 5 символов
        ("ivan_petrov", "Password1!", "Password1!"),  # латиница в пароле
        ("ivan_petrov", "Пароль1!", "Пароль2!"),  # пароли не совпадают
    ]

    for login, password, confirm in test_cases:
        result, message = register_user(login, password, confirm)
        print(f"login={login!r} -> result={result}, message={message!r}")

    logging.info("Приложение завершило работу")


if __name__ == "__main__":
    main()

