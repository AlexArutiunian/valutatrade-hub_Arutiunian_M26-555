"""Настройки сервиса курсов"""

import os

BASE_CURRENCY = "USD"
FIAT_CURRENCIES = ["USD", "EUR", "RUB"]
CRYPTO_CURRENCIES = ["BTC", "ETH"]
CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
}
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
EXCHANGE_RATE_URL = "https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
REQUEST_TIMEOUT = 10
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY", "")
