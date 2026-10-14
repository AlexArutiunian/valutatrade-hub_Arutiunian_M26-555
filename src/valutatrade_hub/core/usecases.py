"""Основные операции приложения"""

from datetime import datetime, timezone

from valutatrade_hub.infra.database import DatabaseManager
from valutatrade_hub.infra.decorators import log_action
from valutatrade_hub.infra.settings import SettingsLoader

from .exceptions import AuthenticationError, CurrencyNotFoundError
from .models import Portfolio, User


def _positive_amount(amount: float) -> float:
    try:
        value = float(amount)
    except (TypeError, ValueError) as error:
        raise ValueError("Сумма должна быть числом") from error

    if value <= 0:
        raise ValueError("Сумма должна быть больше нуля")

    return value


def _load_rates() -> tuple[dict[str, float], bool]:
    data = DatabaseManager().load_rates()
    rates = {
        code.upper(): float(rate) for code, rate in data.get("rates", {}).items()
    }

    if not rates:
        raise CurrencyNotFoundError("Кэш курсов пуст. Выполните update-rates")

    updated_at = data.get("updated_at")
    if not updated_at:
        return rates, True

    updated = datetime.fromisoformat(updated_at)
    age = (datetime.now(timezone.utc) - updated).total_seconds()
    stale = age > SettingsLoader().rates_ttl
    return rates, stale


def register(username: str, password: str) -> User:
    """Регистрирует пользователя"""
    db = DatabaseManager()
    users = db.load_users()

    if any(user.username == username.strip() for user in users):
        raise ValueError("Пользователь уже существует")

    user = User(username, password)
    users.append(user)
    db.save_users(users)

    portfolio = Portfolio(user, {"USD": SettingsLoader().start_balance_usd})
    db.save_portfolio(portfolio)
    return user


def login(username: str, password: str) -> User:
    """Проверяет данные и выполняет вход"""
    for user in DatabaseManager().load_users():
        if user.username == username and user.check_password(password):
            return user

    raise AuthenticationError("Неверное имя пользователя или пароль")


def get_rate(from_currency: str, to_currency: str) -> tuple[float, bool]:
    """Возвращает курс одной валюты к другой"""
    rates, stale = _load_rates()
    source = from_currency.upper()
    target = to_currency.upper()

    if source not in rates:
        raise CurrencyNotFoundError(f"Неизвестная валюта: {source}")
    if target not in rates:
        raise CurrencyNotFoundError(f"Неизвестная валюта: {target}")

    return rates[target] / rates[source], stale


@log_action("buy")
def buy(portfolio: Portfolio, currency: str, amount: float) -> float:
    """Покупает валюту за USD"""
    amount = _positive_amount(amount)
    code = currency.upper()

    if code == "USD":
        raise ValueError("USD уже является базовой валютой")

    rate, stale = get_rate("USD", code)
    if stale:
        raise ValueError("Курсы устарели. Выполните update-rates")

    cost_usd = amount / rate
    portfolio.add_currency("USD").withdraw(cost_usd)
    portfolio.add_currency(code).deposit(amount)
    DatabaseManager().save_portfolio(portfolio)
    return cost_usd


@log_action("sell")
def sell(portfolio: Portfolio, currency: str, amount: float) -> float:
    """Продаёт валюту за USD"""
    amount = _positive_amount(amount)
    code = currency.upper()

    if code == "USD":
        raise ValueError("USD уже является базовой валютой")

    rate, stale = get_rate("USD", code)
    if stale:
        raise ValueError("Курсы устарели. Выполните update-rates")

    revenue_usd = amount / rate
    portfolio.add_currency(code).withdraw(amount)
    portfolio.add_currency("USD").deposit(revenue_usd)
    DatabaseManager().save_portfolio(portfolio)
    return revenue_usd
