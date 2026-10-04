"""
Класс-контроллер — связывает все остальные классы в единый сквозной сценарий:
1. Запрашивает данные у пользователя.
2. Проверяет, есть ли уже результат в базе данных.
3. Если нет — вычисляет через валидатор и сохраняет в базу.
4. Отправляет результат сторонней зависимости.
5. Возвращает итоговый результат.
"""


class Controller:
    """
    Не содержит бизнес-логики проверки сама по себе — лишь оркестрирует
    (координирует по порядку) вызовы остальных компонентов.
    Все зависимости передаются через конструктор (dependency injection) —
    это и позволяет подменять их на тестовые заглушки при тестировании.
    """

    def __init__(self, validator, database, user_interaction, external_dependency):
        self.validator = validator
        self.database = database
        self.user_interaction = user_interaction
        self.external_dependency = external_dependency

    def register(self):
        """Выполняет полный сценарий регистрации. Возвращает (bool, str)."""

        # Шаг 1: запрашиваем данные у пользователя
        login, password, password_confirm = self.user_interaction.get_credentials()

        # Шаг 2: проверяем, нет ли уже готового результата в базе
        record = self.database.get_record(login, password, password_confirm)

        if record is not None:
            # Шаг 2а: результат уже есть — берём из базы, повторно не считаем
            result, message = record["result"], record["message"]
        else:
            # Шаг 2б: результата ещё нет — считаем и сохраняем
            result, message = self.validator.validate(login, password, password_confirm)
            self.database.add_record(login, password, password_confirm, result, message)

        # Шаг 3: отправляем результат сторонней зависимости
        status_text = "успех" if result else f"ошибка: {message}"
        self.external_dependency.send(f"Регистрация '{login}': {status_text}")

        # Шаг 4: возвращаем итоговый результат
        return result, message