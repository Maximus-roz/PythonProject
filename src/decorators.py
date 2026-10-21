"""
Декоратор для функций-отчётов.

Без параметра — пишет результат в файл с именем по умолчанию:
    <имя_функции>_report_<YYYY-MM-DD_HH-MM-SS>.json

С параметром — пишет в файл с заданным именем:
    @report_to_file("my_report.json")
"""
import json
import logging
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, Any, Union

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
DEFAULT_REPORTS_DIR.mkdir(exist_ok=True)


def _serialize(obj: Any) -> Any:
    """Превращает DataFrame/Series/даты в JSON-совместимые объекты."""
    if isinstance(obj, pd.DataFrame):
        # даты приводим к строкам, чтобы json не падал
        return json.loads(obj.to_json(orient="records", date_format="iso", force_ascii=False))
    if isinstance(obj, pd.Series):
        return json.loads(obj.to_json(date_format="iso", force_ascii=False))
    if isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    return obj


def _write_report(result: Any, file_path: Path) -> None:
    """Сохраняет результат в файл (json, если объект сериализуем, иначе — str)."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        payload = {"generated_at": datetime.now().isoformat(), "data": _serialize(result)}
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info("Отчёт сохранён: %s", file_path)
    except (TypeError, ValueError) as exc:
        # fallback — пишем как текст
        logger.warning("JSON-сериализация не удалась (%s), пишем как текст", exc)
        with file_path.open("w", encoding="utf-8") as f:
            f.write(str(result))


def report_to_file(filename: Union[str, None] = None) -> Callable:
    """
    Универсальный декоратор.

    Использование:
        @report_to_file()                      # имя по умолчанию
        @report_to_file("my_report.json")      # своё имя
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if filename:
                file_path = Path(filename)
                if not file_path.is_absolute():
                    file_path = DEFAULT_REPORTS_DIR / file_path
                if file_path.suffix == "":
                    file_path = file_path.with_suffix(".json")
            else:
                ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                file_path = DEFAULT_REPORTS_DIR / f"{func.__name__}_report_{ts}.json"

            _write_report(result, file_path)
            return result
        return wrapper
    return decorator