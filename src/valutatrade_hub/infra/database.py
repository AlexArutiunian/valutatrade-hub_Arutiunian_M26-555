"""Работа с JSON-файлами"""

import json
from pathlib import Path

from valutatrade_hub.core.models import Portfolio, User

from .settings import SettingsLoader


class DatabaseManager:
    """Синглтон для работы с файлами данных"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.settings = SettingsLoader()
            cls._instance.settings.data_dir.mkdir(parents=True, exist_ok=True)
        return cls._instance

    @staticmethod
    def _read(path: Path, default):
        if not path.exists():
            return default

        with path.open(encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _write(path: Path, data) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def load_users(self) -> list[User]:
        """Загружает пользователей"""
        data = self._read(self.settings.users_file, [])
        return [User.from_dict(item) for item in data]

    def save_users(self, users: list[User]) -> None:
        """Сохраняет пользователей"""
        self._write(self.settings.users_file, [user.to_dict() for user in users])

    def load_portfolio(self, user: User) -> Portfolio:
        """Загружает портфель пользователя"""
        portfolios = self._read(self.settings.portfolios_file, {})
        rates = self.load_rates().get("rates", {})
        balances = portfolios.get(user.username, {})
        return Portfolio(user, balances, rates)

    def save_portfolio(self, portfolio: Portfolio) -> None:
        """Сохраняет портфель пользователя"""
        portfolios = self._read(self.settings.portfolios_file, {})
        portfolios[portfolio.user.username] = portfolio.to_dict()
        self._write(self.settings.portfolios_file, portfolios)

    def load_rates(self) -> dict:
        """Загружает кэш курсов"""
        return self._read(self.settings.rates_file, {})
