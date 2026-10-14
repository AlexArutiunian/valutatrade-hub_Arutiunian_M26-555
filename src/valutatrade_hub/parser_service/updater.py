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
        errors = []
        has_updates = False

        for client in self.clients:
            try:
                fresh_rates = client.fetch_rates()
                if fresh_rates:
                    rates.update(fresh_rates)
                    has_updates = True

                logger.info(
                    "%s: обновлено курсов %s",
                    client.__class__.__name__,
                    len(fresh_rates),
                )
            except ApiRequestError as error:
                errors.append(str(error))
                logger.warning("%s", error)

        if not has_updates:
            raise ApiRequestError("Не удалось обновить курсы ни из одного источника")

        rates[BASE_CURRENCY] = 1.0
        now = datetime.now(timezone.utc).isoformat()
        payload = {
            "base": BASE_CURRENCY,
            "updated_at": now,
            "last_refresh": now,
            "rates": dict(sorted(rates.items())),
        }

        self.storage.atomic_write(self.settings.rates_file, payload)

        history = self.storage.read(self.settings.history_file, [])
        history.append(payload)
        self.storage.atomic_write(self.settings.history_file, history[-100:])

        return {"data": payload, "errors": errors}
