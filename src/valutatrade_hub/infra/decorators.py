"""Декораторы приложения"""

from functools import wraps
from logging import getLogger

logger = getLogger("valutatrade_hub.actions")


def log_action(action: str):
    """Логирует успешное выполнение операции"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            logger.info("Операция %s выполнена", action)
            return result

        return wrapper

    return decorator
