"""Клиенты внешних API курсов"""

import requests

from valutatrade_hub.core.exceptions import ApiRequestError

from .config import (
    COINGECKO_URL,
    CRYPTO_ID_MAP,
    EXCHANGE_RATE_API_KEY,
    EXCHANGE_RATE_URL,
    FIAT_CURRENCIES,
    REQUEST_TIMEOUT,
)


class BaseApiClient:
    """Базовый интерфейс API-клиента"""

    def fetch_rates(self) -> dict[str, float]:
        """Возвращает курсы относительно USD"""
        raise NotImplementedError

    @staticmethod
    def _json(response: requests.Response) -> dict:
        if response.status_code == 429:
            raise ApiRequestError("API временно ограничил число запросов (429)")
        if response.status_code in {401, 403}:
            raise ApiRequestError("API отклонил ключ доступа")
        if not response.ok:
            raise ApiRequestError(f"Ошибка API: HTTP {response.status_code}")

        try:
            return response.json()
        except ValueError as error:
            raise ApiRequestError("API вернул некорректный JSON") from error


class CoinGeckoClient(BaseApiClient):
    """Получает курсы криптовалют из CoinGecko"""

    def fetch_rates(self) -> dict[str, float]:
        """Загружает курсы криптовалют"""
        ids = ",".join(CRYPTO_ID_MAP.values())

        try:
            response = requests.get(
                COINGECKO_URL,
                params={"ids": ids, "vs_currencies": "usd"},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as error:
            raise ApiRequestError(f"CoinGecko недоступен: {error}") from error

        data = self._json(response)
        rates = {}

        for code, coin_id in CRYPTO_ID_MAP.items():
            usd_price = data.get(coin_id, {}).get("usd")
            if usd_price:
                rates[code] = 1 / float(usd_price)

        return rates


class ExchangeRateApiClient(BaseApiClient):
    """Получает курсы обычных валют из ExchangeRate-API"""

    def fetch_rates(self) -> dict[str, float]:
        """Загружает курсы обычных валют"""
        if not EXCHANGE_RATE_API_KEY:
            raise ApiRequestError("Не задан EXCHANGE_RATE_API_KEY")

        try:
            response = requests.get(
                EXCHANGE_RATE_URL.format(api_key=EXCHANGE_RATE_API_KEY),
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as error:
            raise ApiRequestError(f"ExchangeRate-API недоступен: {error}") from error

        data = self._json(response)
        conversion_rates = data.get("conversion_rates")

        if not isinstance(conversion_rates, dict):
            raise ApiRequestError("ExchangeRate-API вернул неожиданный ответ")

        return {
            code: float(conversion_rates[code])
            for code in FIAT_CURRENCIES
            if code in conversion_rates
        }
