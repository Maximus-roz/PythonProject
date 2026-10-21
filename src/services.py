import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.load_transactions_from_excel import read_operations_clean

logger = logging.getLogger(__name__)
base = Path(__file__).resolve().parent.parent
file_path = base / "data" / "operations.xlsx"


_DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "operations.xlsx"


def _load_transactions(file_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Загружает транзакции из Excel в список словарей с полями 'Дата операции' и 'Сумма операции'."""
    path = str(file_path) if file_path else str(_DEFAULT_PATH)
    df = read_operations_clean(path)

    # После нормализации в read_operations_clean колонки называются snake_case
    # 'дата_операции' и 'сумма_операции'. Приводим к единому формату для функции.
    result: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        result.append(
            {
                "Дата операции": row.get("дата_операции"),
                "Сумма операции": row.get("сумма_операции"),
            }
        )
    return result


def investment_bank(
    month: str,
    transactions: Optional[List[Dict[str, Any]]] = None,
    limit: int = 50,
    file_path: Optional[str] = None,
) -> float:
    """
    Рассчитывает сумму, которую удалось бы отложить в «Инвесткопилку»
    за указанный месяц при заданном шаге округления.

    Логика: каждая трата округляется вверх до ближайшего кратного ``limit``,
    разница (округлённая сумма − фактическая сумма) «падает» в копилку.

    Параметры:
        month (str): месяц в формате 'YYYY-MM'.
        transactions (List[Dict[str, Any]] | None): список транзакций с полями
            "Дата операции" (str 'YYYY-MM-DD' или datetime) и
            "Сумма операции" (число). Если None — данные загружаются из Excel.
        limit (int): шаг округления (10, 50 или 100 ₽).
        file_path (str | None): путь к Excel-файлу (если transactions не переданы).

    Возвращает:
        float: сумма, отложенная в «Инвесткопилку» (округлённая до 2 знаков).
    """
    # --- Валидация ---
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("limit должен быть положительным целым числом")

    try:
        pd.to_datetime(month, format="%Y-%m")
    except (ValueError, TypeError):
        raise ValueError("month должен быть в формате 'YYYY-MM'")

    # --- Загрузка данных, если не переданы ---
    if transactions is None:
        transactions = _load_transactions(file_path)
        logger.info("Загружено %d транзакций из Excel", len(transactions))

    total_saved = 0.0

    for tx in transactions:
        try:
            date_raw = tx["Дата операции"]
            amount_raw = tx["Сумма операции"]
        except KeyError as e:
            logger.warning("Пропущена транзакция без поля %s: %s", e, tx)
            continue

        # --- Парсинг даты ---
        try:
            tx_date = pd.to_datetime(date_raw, errors="coerce")
        except (ValueError, TypeError):
            tx_date = pd.NaT

        if pd.isna(tx_date):
            logger.warning("Некорректная дата '%s' в транзакции: %s", date_raw, tx)
            continue

        # Фильтр по месяцу
        if tx_date.strftime("%Y-%m") != month:
            continue

        # --- Парсинг суммы ---
        try:
            amount = float(amount_raw)
        except (ValueError, TypeError):
            logger.warning("Некорректная сумма '%s' в транзакции: %s", amount_raw, tx)
            continue

        if pd.isna(amount):
            continue

        if amount >= 0:
            continue

        # Округление отрицательной суммы "от нуля" до кратного limit:
        # -1712 при limit=50 -> -1750, saved = -1712 - (-1750) = 38
        rounded = (amount // limit) * limit
        saved = amount - rounded

        if saved > 0:
            total_saved += saved

    return round(total_saved, 2)


if __name__ == "__main__":

    # 1) С данными из Excel по умолчанию (data/operations.xlsx)
    saved = investment_bank("2021-12", limit=50)
    print(saved)

    # 2) С явным путём к файлу
    saved = investment_bank("2021-12", limit=100, file_path=file_path)
    print(saved)

    # 3) С готовым списком транзакций (как в исходном ТЗ)
    transactions = [
        {"Дата операции": "2024-05-01", "Сумма операции": -1712},
        {"Дата операции": "2024-05-15", "Сумма операции": -3001},
        {"Дата операции": "2024-06-02", "Сумма операции": -500},  # другой месяц
    ]
    saved = investment_bank("2024-05", transactions, limit=50)
    print(saved)  # 38.0 + 49.0 = 87.0