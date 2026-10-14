"""Модели пользователя, кошелька и портфеля"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone

from .exceptions import InsufficientFundsError


class User:
    """Пользователь приложения"""

    def __init__(
        self,
        username: str,
        password: str | None = None,
        *,
        salt: str | None = None,
        password_hash: str | None = None,
        registered_at: str | None = None,
    ):
        username = username.strip()
        if not username:
            raise ValueError("Имя пользователя не может быть пустым")

        self.__username = username
        self.__salt = salt or os.urandom(16).hex()
        self.__registered_at = registered_at or datetime.now(timezone.utc).isoformat()

        if password_hash is not None:
            self.__password_hash = password_hash
        elif password is not None:
            self.set_password(password)
        else:
            raise ValueError("Нужен пароль")

    @property
    def username(self) -> str:
        """Возвращает имя пользователя"""
        return self.__username

    @property
    def registered_at(self) -> str:
        """Возвращает дату регистрации"""
        return self.__registered_at

    def set_password(self, password: str) -> None:
        """Устанавливает пароль"""
        if len(password) < 6:
            raise ValueError("Пароль должен содержать минимум 6 символов")
        self.__password_hash = self._hash_password(password)

    def check_password(self, password: str) -> bool:
        """Проверяет пароль"""
        return self._hash_password(password) == self.__password_hash

    def _hash_password(self, password: str) -> str:
        value = f"{self.__salt}:{password}".encode()
        return hashlib.sha256(value).hexdigest()

    def get_user_info(self) -> dict[str, str]:
        """Возвращает данные пользователя без пароля"""
        return {
            "username": self.__username,
            "registered_at": self.__registered_at,
        }

    def to_dict(self) -> dict[str, str]:
        """Преобразует пользователя в словарь"""
        return {
            "username": self.__username,
            "salt": self.__salt,
            "password_hash": self.__password_hash,
            "registered_at": self.__registered_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> User:
        """Создаёт пользователя из словаря"""
        return cls(
            data["username"],
            salt=data["salt"],
            password_hash=data["password_hash"],
            registered_at=data["registered_at"],
        )


class Wallet:
    """Кошелёк одной валюты"""

    def __init__(self, currency: str, balance: float = 0):
        self.currency = currency.upper()
        self.balance = balance

    @property
    def balance(self) -> float:
        """Возвращает баланс"""
        return self.__balance

    @balance.setter
    def balance(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError("Баланс должен быть числом")
        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")
        self.__balance = float(value)

    def deposit(self, amount: float) -> None:
        """Пополняет кошелёк"""
        self._validate_amount(amount)
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Списывает средства"""
        self._validate_amount(amount)
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Недостаточно {self.currency}: доступно {self.balance:g}"
            )
        self.balance -= amount

    def get_balance_info(self) -> str:
        """Возвращает баланс в читаемом виде"""
        return f"{self.currency}: {self.balance:.8g}"

    @staticmethod
    def _validate_amount(amount: float) -> None:
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError("Сумма должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма должна быть больше нуля")


class Portfolio:
    """Валютный портфель пользователя"""

    def __init__(
        self,
        user: User,
        balances: dict[str, float] | None = None,
        rates: dict[str, float] | None = None,
    ):
        self.__user = user
        self.__wallets: dict[str, Wallet] = {}
        self.__rates = {
            code.upper(): float(rate) for code, rate in (rates or {}).items()
        }

        for currency, balance in (balances or {}).items():
            self.__wallets[currency.upper()] = Wallet(currency, balance)

    @property
    def user(self) -> User:
        """Возвращает владельца портфеля"""
        return self.__user

    @property
    def wallets(self) -> dict[str, Wallet]:
        """Возвращает копию словаря кошельков"""
        return self.__wallets.copy()

    def add_currency(self, currency: str) -> Wallet:
        """Возвращает кошелёк или создаёт новый"""
        code = currency.upper()
        if code not in self.__wallets:
            self.__wallets[code] = Wallet(code)
        return self.__wallets[code]

    def get_total_value(self, base: str = "USD") -> float:
        """Считает стоимость портфеля в выбранной валюте"""
        base = base.upper()
        if base not in self.__rates:
            raise ValueError(f"Нет курса для {base}")

        total_usd = 0.0
        for currency, wallet in self.__wallets.items():
            if currency not in self.__rates:
                raise ValueError(f"Нет курса для {currency}")
            total_usd += wallet.balance / self.__rates[currency]

        return total_usd * self.__rates[base]

    def to_dict(self) -> dict[str, float]:
        """Преобразует портфель в словарь"""
        return {code: wallet.balance for code, wallet in self.__wallets.items()}
