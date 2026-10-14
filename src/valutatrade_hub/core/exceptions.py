"""Исключения приложения"""


class ValutaTradeError(Exception):
    """Базовая ошибка приложения"""


class AuthenticationError(ValutaTradeError):
    """Ошибка входа пользователя"""


class InsufficientFundsError(ValutaTradeError):
    """Недостаточно средств в кошельке"""


class CurrencyNotFoundError(ValutaTradeError):
    """Валюта отсутствует в кэше курсов"""


class ApiRequestError(ValutaTradeError):
    """Ошибка запроса к внешнему API"""
