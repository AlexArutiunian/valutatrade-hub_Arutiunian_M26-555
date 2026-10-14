"""Хранение курсов в JSON-файлах"""

import json
import os
from pathlib import Path


class RatesStorage:
    """Читает и безопасно записывает курсы"""

    @staticmethod
    def read(path: Path, default):
        """Читает JSON-файл"""
        if not path.exists():
            return default

        with path.open(encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def atomic_write(path: Path, data) -> None:
        """Атомарно записывает JSON-файл"""
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")

        with tmp.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        os.replace(tmp, path)
