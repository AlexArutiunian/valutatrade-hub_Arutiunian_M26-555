"""Настройки приложения"""

import os
from pathlib import Path


class SettingsLoader:
    """Синглтон с настройками приложения"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        self.project_root = Path(__file__).resolve().parents[3]
        self.data_dir = self.project_root / "data"
        self.users_file = self.data_dir / "users.json"
        self.portfolios_file = self.data_dir / "portfolios.json"
        self.rates_file = self.data_dir / "rates.json"
        self.history_file = self.data_dir / "exchange_rates.json"
        self.log_file = self.project_root / "logs" / "valutatrade.log"
        self.rates_ttl = int(os.getenv("RATES_TTL_SECONDS", "3600"))
        self.start_balance_usd = float(os.getenv("START_BALANCE_USD", "1000"))
