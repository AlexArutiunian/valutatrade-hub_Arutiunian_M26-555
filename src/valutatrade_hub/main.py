#!/usr/bin/env python3
"""Точка входа приложения"""

from .cli.interface import Interface
from .infra.logging_config import setup_logging


def main() -> None:
    """Запускает приложение"""
    setup_logging()
    Interface().run()


if __name__ == "__main__":
    main()
