"""Настройка логирования"""

import logging
from logging.handlers import RotatingFileHandler

from .settings import SettingsLoader


def setup_logging() -> None:
    """Настраивает логирование приложения"""
    settings = SettingsLoader()
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=500_000,
        backupCount=2,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )

    logger = logging.getLogger("valutatrade_hub")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
