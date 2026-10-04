"""
Класс взаимодействия с пользователем.
Реализован как абстрактный интерфейс (через модуль abc) + конкретная
реализация через консоль (input()).
"""

from abc import ABC, abstractmethod


class UserInteractionInterface(ABC):
    """
    Абстрактный интерфейс для получения данных от пользователя.
    Любая конкретная реализация (консоль, GUI, веб-форма) должна
    реализовать метод get_credentials().
    """

    @abstractmethod
    def get_credentials(self):
        """Должен вернуть кортеж (login, password, password_confirm)."""
        raise NotImplementedError


class ConsoleUserInteraction(UserInteractionInterface):
    """Получает логин, пароль и подтверждение пароля через консоль."""

    def get_credentials(self):
        login = input("Введите логин: ")
        password = input("Введите пароль: ")
        password_confirm = input("Повторите пароль: ")
        return login, password, password_confirm