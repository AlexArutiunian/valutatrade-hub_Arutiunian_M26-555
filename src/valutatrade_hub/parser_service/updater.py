"""Обновление курсов валют"""

from datetime import datetime, timezone
from logging import getLogger

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.infra.settings import SettingsLoader

from .api_clients import CoinGeckoClient, ExchangeRateApiClient
from .config import BASE_CURRENCY
from .storage import RatesStorage

logger = getLogger("valutatrade_hub.rates")


class RatesUpdater:
    """Объединяет курсы из нескольких источников"""

    def __init__(self, clients=None):
        self.clients = clients or [ExchangeRateApiClient(), CoinGeckoClient()]
        self.settings = SettingsLoader()
        self.storage = RatesStorage()

    def run_update(self) -> dict:
        """Обновляет кэш и историю курсов"""
        current = self.storage.read(self.settings.rates_file, {})
        rates = dict(current.get("rates", {}))
        rate_updated_at = dict(current.get("rate_updated_at", {}))
        errors = []
        updated_codes = set()

        for client in self.clients:
            try:
                fresh_rates = client.fetch_rates()
                rates.update(fresh_rates)
                updated_codes.update(fresh_rates)

                logger.info(
                    "%s: обновлено курсов %s",
                    client.__class__.__name__,
                    len(fresh_rates),
                )
            except ApiRequestError as error:
                errors.append(str(error))
                logger.warning("%s", error)

        if not updated_codes:
            raise ApiRequestError("Не удалось обновить курсы ни из одного источника")

        now = datetime.now(timezone.utc).isoformat()
        rates[BASE_CURRENCY] = 1.0
        updated_codes.add(BASE_CURRENCY)

        for code in updated_codes:
            rate_updated_at[code] = now

        payload = {
            "base": BASE_CURRENCY,
            "updated_at": now,
            "last_refresh": now,
            "rate_updated_at": dict(sorted(rate_updated_at.items())),
            "rates": dict(sorted(rates.items())),
        }

        self.storage.atomic_write(self.settings.rates_file, payload)

        history = self.storage.read(self.settings.history_file, [])
        history.append(payload)
        self.storage.atomic_write(self.settings.history_file, history[-100:])

        return {"data": payload, "errors": errors}
