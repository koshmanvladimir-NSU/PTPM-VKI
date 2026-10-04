"""
Класс сторонней зависимости.
Реализован как абстрактный интерфейс (через модуль abc) + конкретная
реализация, имитирующая отправку данных на внешний email-сервер.
"""

from abc import ABC, abstractmethod


class ExternalDependencyInterface(ABC):
    """
    Абстрактный интерфейс для отправки данных стороннему процессу.
    Любая конкретная реализация (email, SMS, веб-хук) должна
    реализовать метод send().
    """

    @abstractmethod
    def send(self, data: str) -> bool:
        """Должен отправить data и вернуть True/False — успех или неудача."""
        raise NotImplementedError


class EmailNotifier(ExternalDependencyInterface):
    """
    Имитация отправки уведомления на email-сервер.
    Реального сетевого запроса не делает — только выводит сообщение
    в консоль, как и требует задание ("внутри класса реализуется
    исключительно имитация передачи данных").
    """

    def send(self, data: str) -> bool:
        print(f"[EmailNotifier] Отправка данных на сервер: {data}")
        return True